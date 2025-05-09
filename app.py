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
from pydub import AudioSegment, effects

# Initialize FastAPI
app = FastAPI()

# Configure thread executor
executor = ThreadPoolExecutor()

async def run_blocking(fn, *args):
    return await asyncio.get_event_loop().run_in_executor(executor, fn, *args)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load models
whisper_model = whisper.load_model("base")  # Consider "medium" or "large-v3" for better accuracy
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Directories and constraints
os.makedirs("temp", exist_ok=True)
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a"}
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB

# Utilities
def sanitize_filename(filename: str) -> str:
    return re.sub(r'[^\w.-]', '_', filename)

def chunk_text(text, max_tokens=900):
    words = text.split()
    return [" ".join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]

def summarize_chunk(chunk):
    word_count = len(chunk.split())
    max_len = min(130, word_count)
    min_len = max(15, int(max_len * 0.4))
    summary = summarizer(chunk, max_length=max_len, min_length=min_len, do_sample=False)
    return summary[0]["summary_text"]

def preprocess_audio(file_path: str) -> str:
    try:
        audio = AudioSegment.from_file(file_path)
        audio = effects.normalize(audio)
        cleaned_path = file_path.replace(".", "_cleaned.", 1)
        audio.export(cleaned_path, format="mp3")
        return cleaned_path
    except Exception as e:
        logging.error(f"Audio preprocessing failed: {e}")
        raise HTTPException(status_code=500, detail="Audio preprocessing failed.")

# Endpoints
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
        with open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)

        logging.info(f"Saved file: {file.filename}")

        # Preprocess audio
        cleaned_path = preprocess_audio(file_path)

        # Transcribe with Whisper
        transcription_result = await run_blocking(whisper_model.transcribe, cleaned_path)
        transcription = transcription_result["text"]
        transcription_length = len(transcription.split())

        # Summarize in chunks
        chunks = chunk_text(transcription)
        summaries = [summarize_chunk(chunk) for chunk in chunks]
        final_summary = " ".join(summaries)
        summary_length = len(final_summary.split())

        processing_time = round(time.time() - start_time, 2)
        logging.info(f"Transcription & summary completed in {processing_time}s")

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
        for path in [file_path, file_path.replace(".", "_cleaned.", 1)]:
            if os.path.exists(path):
                os.remove(path)
