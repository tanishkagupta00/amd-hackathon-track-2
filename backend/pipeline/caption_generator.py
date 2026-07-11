import os
import io
import time
import base64
import logging
from google import genai
from google.genai import types

logger = logging.getLogger("captionforge.caption_generator")

CAPTION_PROMPT = (
    "These are evenly-spaced frames extracted from a video. Study them carefully in order.\n\n"
    "Write a detailed, factual description of exactly what happens in the video:\n"
    "- WHO is in the video (people, animals, specific objects as main subjects)\n"
    "- WHAT specific actions occur — be precise, not vague\n"
    "- WHERE it takes place (environment, setting, background details)\n"
    "- HOW events unfold and change across the frames\n"
    "- Any notable objects, text visible on screen, or significant details\n\n"
    "Write 3-4 rich, concrete sentences describing what you actually see. "
    "Do NOT be generic — never say 'a sequence of events' or 'an entity'. "
    "Describe the real, specific content visible in these frames.\n\n"
    "Output ONLY the factual description paragraph. No headers, bullets, or reasoning."
)


class CaptionGenerator:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate_base_caption(self, video_path: str) -> str:
        """
        Generates a detailed factual base caption by having Gemini watch the video.

        Strategy:
          1. Try Gemini File API (best — handles large files, any codec via transcoding)
          2. If File API fails, extract frames using PyAV (bundles its own FFmpeg, no system deps)
             and send as inline images to Gemini
          3. Raise with clear message if both fail
        """
        if not self.client:
            raise Exception(
                "No GEMINI_API_KEY configured. Please add it to Vercel environment variables."
            )

        # Strategy 1: Gemini File API
        try:
            return self._caption_via_file_api(video_path)
        except Exception as e:
            logger.warning(f"[Strategy 1 - File API] Failed: {e}. Trying frame extraction...")

        # Strategy 2: PyAV frame extraction → inline images to Gemini
        try:
            return self._caption_via_frames(video_path)
        except Exception as e2:
            logger.error(f"[Strategy 2 - Frames] Also failed: {e2}")
            raise Exception(
                f"Could not process this video with any method. "
                f"Please try uploading an MP4 (H.264) video. Detail: {e2}"
            )

    # ------------------------------------------------------------------ #
    #  Strategy 1 — Gemini File API (primary)                              #
    # ------------------------------------------------------------------ #
    def _caption_via_file_api(self, video_path: str) -> str:
        logger.info(f"[File API] Uploading: {os.path.basename(video_path)}")
        video_file = self.client.files.upload(file=video_path)

        max_wait = 180
        waited = 0
        while video_file.state.name == "PROCESSING":
            if waited >= max_wait:
                raise Exception(f"File API timed out after {max_wait}s.")
            time.sleep(4)
            waited += 4
            video_file = self.client.files.get(name=video_file.name)
            logger.info(f"  Waited {waited}s — state: {video_file.state.name}")

        if video_file.state.name == "FAILED":
            try:
                self.client.files.delete(name=video_file.name)
            except Exception:
                pass
            raise Exception("Gemini File API returned FAILED (unsupported codec).")

        logger.info("[File API] Processing done. Generating caption...")
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[video_file, CAPTION_PROMPT],
            config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=600),
        )
        try:
            self.client.files.delete(name=video_file.name)
        except Exception:
            pass

        caption = response.text.strip()
        logger.info(f"[File API] Done: {caption[:80]}...")
        return caption

    # ------------------------------------------------------------------ #
    #  Strategy 2 — PyAV frame extraction → inline images                  #
    # ------------------------------------------------------------------ #
    def _caption_via_frames(self, video_path: str) -> str:
        """
        Use PyAV (bundled FFmpeg, no system deps) to extract frames, then
        send them as inline JPEG images to Gemini.
        """
        import av  # PyAV — bundles its own FFmpeg binary

        logger.info(f"[Frames] Extracting frames from: {os.path.basename(video_path)}")

        container = av.open(video_path)
        stream = container.streams.video[0]

        total_frames = stream.frames or 0
        duration_secs = float(stream.duration * stream.time_base) if stream.duration else 0

        # Extract up to 10 evenly-spaced keyframes
        target_count = 10
        image_parts = []

        # Seek-based extraction
        if duration_secs > 0:
            timestamps = [duration_secs * i / target_count for i in range(target_count)]
            seen = set()
            for ts in timestamps:
                try:
                    container.seek(int(ts * av.time_base ** -1), stream=stream)
                    for frame in container.decode(video=0):
                        frame_key = frame.pts
                        if frame_key in seen:
                            continue
                        seen.add(frame_key)
                        img = frame.to_image()
                        img.thumbnail((640, 360))
                        buf = io.BytesIO()
                        img.save(buf, format="JPEG", quality=75)
                        image_parts.append(
                            types.Part.from_bytes(
                                data=buf.getvalue(),
                                mime_type="image/jpeg"
                            )
                        )
                        break
                except Exception:
                    pass
        
        # Fallback: decode sequentially if seek didn't work
        if not image_parts:
            container.seek(0)
            frame_interval = max(1, (total_frames or 100) // target_count)
            for i, frame in enumerate(container.decode(video=0)):
                if i % frame_interval == 0:
                    img = frame.to_image()
                    img.thumbnail((640, 360))
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=75)
                    image_parts.append(
                        types.Part.from_bytes(
                            data=buf.getvalue(),
                            mime_type="image/jpeg"
                        )
                    )
                if len(image_parts) >= target_count:
                    break

        container.close()

        if not image_parts:
            raise Exception("Could not extract any frames from this video file.")

        logger.info(f"[Frames] Extracted {len(image_parts)} frames. Sending to Gemini...")

        contents = image_parts + [CAPTION_PROMPT]
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=600),
        )

        caption = response.text.strip()
        logger.info(f"[Frames] Done: {caption[:80]}...")
        return caption
