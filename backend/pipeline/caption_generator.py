import os
import io
import math
import base64
import logging
import tempfile
import subprocess
from PIL import Image
import numpy as np
import imageio
import imageio_ffmpeg
from openai import OpenAI

logger = logging.getLogger("captionforge.caption_generator")


def extract_audio_lightweight(video_path: str, output_audio_path: str) -> bool:
    """
    Extracts the audio track from a video as an MP3 file using static ffmpeg from imageio-ffmpeg.
    """
    try:
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as e:
        logger.error(f"Could not locate imageio-ffmpeg binary: {e}")
        return False

    cmd = [
        ffmpeg_bin,
        "-y",
        "-i", video_path,
        "-vn",                      # Disable video recording
        "-acodec", "libmp3lame",    # Convert to MP3
        "-ar", "16000",             # 16kHz for Whisper
        "-q:a", "4",                # Good quality compression
        output_audio_path
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Lightweight ffmpeg audio extraction failed: {e}")
        return False


def extract_keyframes_lightweight(video_path: str, num_frames=6) -> list[str]:
    """
    Reads video frames using imageio and extracts base64 encoded JPEG keyframes.
    Runs on CPU without requiring OpenCV or PyTorch, making it perfect for Vercel.
    """
    logger.info(f"Extracting keyframes from: {os.path.basename(video_path)}")
    try:
        reader = imageio.get_reader(video_path)
    except Exception as e:
        raise Exception(f"Failed to open video reader: {e}")

    meta = reader.get_meta_data()
    n_frames = meta.get("nframes", 0)

    # Check if n_frames is invalid (NaN, Inf, or <= 0)
    is_invalid = True
    try:
        is_invalid = n_frames <= 0 or math.isnan(n_frames) or math.isinf(n_frames)
    except Exception:
        pass

    selected_frames = []
    try:
        if is_invalid:
            logger.info("Metadata nframes is missing or invalid (NaN/Inf). Scanning frames iteratively...")
            # First pass: count total frames
            n_frames = 0
            try:
                for _ in reader:
                    n_frames += 1
            except Exception:
                pass
            reader.close()

            # Second pass: reopen and read only the selected indices
            reader = imageio.get_reader(video_path)
            if num_frames <= 1 or n_frames <= 1:
                indices = {0}
            else:
                indices = set(int(i * (n_frames - 1) / (num_frames - 1)) for i in range(min(num_frames, n_frames)))

            try:
                for idx, frame in enumerate(reader):
                    if idx in indices:
                        selected_frames.append(frame)
            except Exception:
                pass
        else:
            if num_frames <= 1 or n_frames <= 1:
                indices = [0]
            else:
                indices = [int(i * (n_frames - 1) / (num_frames - 1)) for i in range(min(num_frames, n_frames))]
            
            for idx in indices:
                try:
                    frame = reader.get_data(idx)
                    selected_frames.append(frame)
                except IndexError:
                    pass
    finally:
        try:
            reader.close()
        except Exception:
            pass

    # Convert NumPy arrays to resized base64 JPEGs
    base64_frames = []
    for frame in selected_frames:
        pil_img = Image.fromarray(frame)
        pil_img.thumbnail((512, 512))  # Resize to fit model prompt limits and speed up upload
        buffered = io.BytesIO()
        pil_img.save(buffered, format="JPEG")
        b64_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        base64_frames.append(b64_str)

    logger.info(f"Successfully extracted {len(base64_frames)} keyframes.")
    return base64_frames


def clean_kimi_reasoning(text: str) -> str:
    """
    Cleans up any leaked chain-of-thought or internal monologue
    prepended by models like Kimi or DeepSeek in the response.
    """
    text_clean = text.strip()
    
    # If the response contains headers indicating refinement or final output
    markers = [
        "Refining:", "Refinement:", "Final caption:", "Final description:", 
        "Factual description:", "Here is the factual description:"
    ]
    for marker in markers:
        if marker in text_clean:
            parts = text_clean.split(marker, 1)
            candidate = parts[1].strip()
            if len(candidate) > 20:
                return candidate
                
    # If there is a block of reasoning lines at the start, filter them out
    lines = text_clean.split("\n")
    cleaned_lines = []
    skip_mode = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Common signs of internal monologue
        monologue_patterns = [
            "the user wants", "let me analyze", "requirements:", "factual description:",
            "audio transcript:", "first frame:", "second frame:", "third frame:",
            "fourth frame:", "fifth frame:", "sixth frame:"
        ]
        is_monologue = any(pattern in stripped.lower() for pattern in monologue_patterns)
        
        if is_monologue:
            continue
        cleaned_lines.append(line)
        
    result = "\n".join(cleaned_lines).strip()
    return result if result else text


class CaptionGenerator:
    def __init__(self):
        pass

    def generate_base_caption(self, video_path: str) -> str:
        """
        Extracts frames and audio locally in Vercel using pure CPU libraries,
        and uses Fireworks AI APIs (running on AMD MI300X cloud GPUs) to
        transcribe audio and generate the detailed video description.
        """
        fireworks_api_key = os.environ.get("FIREWORKS_API_KEY")
        if not fireworks_api_key:
            raise Exception("FIREWORKS_API_KEY not found in environment variables.")

        client = OpenAI(
            base_url="https://api.fireworks.ai/inference/v1",
            api_key=fireworks_api_key
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Audio Extraction & Transcription
            audio_path = os.path.join(tmpdir, "extracted_audio.mp3")
            transcript_text = "No speech detected or audio transcription failed."
            
            logger.info("Extracting audio stream...")
            if extract_audio_lightweight(video_path, audio_path) and os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                logger.info("Transcribing audio using Fireworks whisper-v3 (running on AMD MI300X)...")
                try:
                    with open(audio_path, "rb") as af:
                        transcription = client.audio.transcriptions.create(
                            model="whisper-v3",
                            file=af
                        )
                    if transcription.text:
                        transcript_text = transcription.text.strip()
                        logger.info(f"Speech Transcription: {transcript_text[:80]}...")
                except Exception as e:
                    logger.error(f"Whisper transcription failed: {e}")
            else:
                logger.info("No audio track detected or extraction skipped.")

            # 2. Keyframe Extraction
            logger.info("Extracting visual keyframes...")
            try:
                b64_frames = extract_keyframes_lightweight(video_path, num_frames=6)
            except Exception as e:
                raise Exception(f"Failed to extract video frames: {str(e)}")

            # 3. Vision API Call to Fireworks
            logger.info("Synthesizing caption using Fireworks Vision Model (kimi-k2p6)...")
            
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
                    "role": "system",
                    "content": (
                        "You are a precise, factual video analysis assistant. "
                        "Your job is to write a single paragraph description of the video frames. "
                        "You must output ONLY the final description. "
                        "Do NOT output any thoughts, reasoning steps, frame listings, "
                        "scratchpad notes, intro headers (like 'Here is...'), or concluding notes."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt}
                    ]
                }
            ]

            for frame in b64_frames:
                messages[1]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{frame}"
                    }
                })

            try:
                response = client.chat.completions.create(
                    model="accounts/fireworks/models/kimi-k2p6",
                    messages=messages,
                    max_tokens=10000,
                    temperature=0.2
                )
                raw_caption = response.choices[0].message.content.strip()
                caption = clean_kimi_reasoning(raw_caption)
                logger.info("Base caption generated successfully via Fireworks Vision Model.")
                return caption
            except Exception as e:
                logger.error(f"Fireworks Vision Model call failed: {e}")
                raise Exception(f"Vision model caption generation failed: {str(e)}")
