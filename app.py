from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException
import whisper
from transformers import pipeline
import os
import re
import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
# Initialize FastAPIexecutor = ThreadPoolExecutor()
executor = ThreadPoolExecutor()
async def run_blocking(fn, *args):
    return await asyncio.get_event_loop().run_in_executor(executor, fn, *args)

def chunk_text(text, max_tokens=900):
    words = text.split()
    return [" ".join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Or ["*"] for all (less secure)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load AI models
whisper_model = whisper.load_model("base")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Ensure temp directory exists
os.makedirs("temp", exist_ok=True)

# Allowed audio file extensions
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a"}

# Max file size (in bytes) → 200MB (approx. 2-hour podcast)
MAX_FILE_SIZE = 200 * 1024 * 1024

def sanitize_filename(filename: str) -> str:
    """Removes special characters from filename to prevent issues."""
    return re.sub(r'[^\w.-]', '_', filename)

@app.get("/")
def read_root():
    return {"message": "API is running!"}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    start_time = time.time()
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    safe_filename = sanitize_filename(file.filename)
    file_path = os.path.join("temp", safe_filename)

    try:
        # Save file in chunks (better memory usage)
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                buffer.write(chunk)

        logging.info(f"Saved file: {file.filename}")

        # Run Whisper transcription in background thread
        transcription_result = await run_blocking(whisper_model.transcribe, file_path)
        transcription = transcription_result["text"]
        transcription_length = len(transcription.split())

        # Split and summarize in chunks
        chunks = chunk_text(transcription)
        summaries = [summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]["summary_text"]
                     for chunk in chunks]
        final_summary = " ".join(summaries)

        summary_length = len(final_summary.split())
        logging.info(f"Transcription & summary done in {time.time() - start_time:.2f}s")
        processing_time = round(time.time() - start_time, 2)

        return {
            "transcription": transcription,
            "summary": final_summary,
            "transcription_length": transcription_length,
            "summary_length": summary_length,
            "processing_time": processing_time
        }

    except Exception as e:
        logging.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error during transcription.")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)