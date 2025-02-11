import whisper
from transformers import pipeline
model = whisper.load_model("medium")
result = model.transcribe("K.  lyrics edit  #cas #audio #lyrics #overlayedit #explore #foryou #edit.mp3")
transcript=result["text"]
with open('transcription.txt', 'w',encoding="utf-8") as f:
    f.write(transcript)
summarizer=pipeline("summarization",model="facebook/bart-large-cnn")
summary=summarizer(transcript,max_length=150,min_length=50,do_sample=False)[0]["summary_text"]
with open('summary.txt', 'w',encoding="utf-8") as f:
    f.write(summary)
print("Transcription saved successfully to transcription.txt")
print("Summary saved successfully to summary.txt")
