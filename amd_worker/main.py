import os
import cv2
import base64
import tempfile
import subprocess
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amd_worker")

app = FastAPI()

FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY")
if not FIREWORKS_API_KEY:
    logger.warning("FIREWORKS_API_KEY not found in environment!")

client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=FIREWORKS_API_KEY
)

def get_ffmpeg_binary() -> str:
    try:
        import imageio_ffmpeg
        path = imageio_ffmpeg.get_ffmpeg_exe()
        if path and os.path.exists(path):
            return path
    except ImportError:
        pass
    return "ffmpeg"

def extract_audio(video_path: str, output_audio_path: str):
    ffmpeg_bin = get_ffmpeg_binary()
    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", video_path,
        "-q:a", "0",
        "-map", "a",
        output_audio_path
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def extract_keyframes(video_path: str, num_frames=6):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("Failed to open video")
    
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count <= 0:
        raise Exception("Video has no frames")
        
    import numpy as np
    indices = np.linspace(0, frame_count - 1, min(num_frames, frame_count), dtype=int)
    
    base64_frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            # Resize frame to save bandwidth and compute
            frame = cv2.resize(frame, (512, 512), interpolation=cv2.INTER_AREA)
            _, buffer = cv2.imencode('.jpg', frame)
            base64_frames.append(base64.b64encode(buffer).decode('utf-8'))
            
    cap.release()
    return base64_frames

@app.post("/generate_base_caption")
async def generate_base_caption(video: UploadFile = File(...)):
    """
    Receives a video file, extracts audio and frames locally on the AMD instance,
    and calls Fireworks AI (whisper + vision) to generate the caption.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, video.filename)
        with open(video_path, "wb") as f:
            f.write(await video.read())
            
        logger.info(f"Processing video: {video.filename}")
        
        # 1. Extract and transcribe audio
        audio_path = os.path.join(tmpdir, "audio.mp3")
        transcript_text = "No audio found or transcription failed."
        if extract_audio(video_path, audio_path) and os.path.getsize(audio_path) > 0:
            logger.info("Audio extracted. Transcribing with Whisper-v3...")
            try:
                with open(audio_path, "rb") as af:
                    transcription = client.audio.transcriptions.create(
                        model="accounts/fireworks/models/whisper-v3",
                        file=af
                    )
                if transcription.text:
                    transcript_text = transcription.text
                    logger.info("Transcription complete.")
            except Exception as e:
                logger.error(f"Whisper transcription failed: {e}")
                
        # 2. Extract frames
        logger.info("Extracting keyframes via OpenCV...")
        try:
            b64_frames = extract_keyframes(video_path, num_frames=6)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Frame extraction failed: {str(e)}")
            
        # 3. Call Vision Model
        logger.info("Calling Fireworks Vision Model (kimi-k2p6)...")
        
        prompt = (
            "Watch this sequence of frames from a video carefully. "
            "Also, consider the following audio transcript from the video: \n"
            f"\"{transcript_text}\"\n\n"
            "Write a detailed, factual description:\n"
            "- WHO is in the video (people, animals, objects)\n"
            "- WHAT specific actions occur\n"
            "- WHERE it takes place\n"
            "- HOW events unfold over time\n"
            "- Incorporate the audio transcript context if it adds to the description\n\n"
            "Write 3-4 rich, concrete sentences. "
            "Never use vague terms like 'a sequence of events'. "
            "Output ONLY the factual description. No headers, bullets, or reasoning."
        )
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        for frame in b64_frames:
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame}"
                }
            })
            
        try:
            # We use kimi-k2p6 as recommended for advanced vision
            response = client.chat.completions.create(
                model="accounts/fireworks/models/kimi-k2p6",
                messages=messages,
                max_tokens=600,
                temperature=0.2
            )
            caption = response.choices[0].message.content.strip()
            logger.info("Caption generated successfully.")
            return {"caption": caption}
        except Exception as e:
            logger.error(f"Vision model generation failed: {e}")
            raise HTTPException(status_code=500, detail=f"Vision model failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
