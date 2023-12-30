from fastapi import FastAPI, HTTPException
from pytube import YouTube
import moviepy.editor as mp
import speech_recognition as sr
from transformers import pipeline
app = FastAPI()

def download_video(youtube_url, video_path):
    yt = YouTube(youtube_url)
    video_stream = yt.streams.filter(file_extension="mp4").first()
    video_stream.download(filename=video_path)

def extract_audio(video_path, audio_path):
    video_clip = mp.VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(audio_path)
    audio_clip.close()
    video_clip.close()

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_text = recognizer.recognize_google(audio_data=recognizer.record(source), language='en-US')
    return audio_text
def summarize(audio_text):
    summarizer = pipeline("summarization", "google/pegasus-xsum")
    tokenizer_kwargs = {'truncation':True,'max_length':512}
    text_summerization = summarizer(audio_text, min_length=30, do_sample=False,**tokenizer_kwargs)
    return text_summerization
@app.get("/get_video_text")
async def get_video_text(youtube_url: str):
    try:
        video_path = "temp_video.mp4"
        download_video(youtube_url, video_path)

        audio_path = "temp_audio.wav"
        extract_audio(video_path, audio_path)

        video_text = transcribe_audio(audio_path)

        text_summerization=summarize(video_text)

        return {"videosummary":text_summerization}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

