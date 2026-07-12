import os
import requests
import logging

logger = logging.getLogger("captionforge.caption_generator")

class CaptionGenerator:
    def __init__(self):
        pass

    def generate_base_caption(self, video_path: str) -> str:
        """
        Sends the video to the AMD Worker instance which extracts frames,
        audio, and calls Fireworks AI to generate the base caption.
        """
        # Default to localhost if running locally, otherwise configure via Vercel env variables
        amd_worker_url = os.environ.get("AMD_WORKER_URL", "http://localhost:8000/generate_base_caption")
        
        file_size = os.path.getsize(video_path)
        logger.info(f"Forwarding video ({file_size / (1024*1024):.2f} MB) to AMD Worker at {amd_worker_url}...")

        if file_size < 10_000:
            raise Exception("Video file is too small (under 10KB) — likely corrupted or download expired.")

        try:
            with open(video_path, "rb") as f:
                files = {"video": (os.path.basename(video_path), f, "video/mp4")}
                # Use a generous timeout since video upload, extraction, and API calls take time
                response = requests.post(amd_worker_url, files=files, timeout=300)
                
            response.raise_for_status()
            data = response.json()
            
            if "caption" not in data:
                raise Exception(f"AMD Worker returned malformed response: {data}")
                
            caption = data["caption"]
            logger.info(f"[AMD Worker] Base caption: {caption[:80]}...")
            return caption
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to communicate with AMD Worker: {e}")
            raise Exception(f"Could not generate base caption via AMD Worker: {str(e)}")
