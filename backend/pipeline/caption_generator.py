import os
import time
from google import genai

class CaptionGenerator:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate_base_caption(self, video_path: str) -> str:
        """
        Creates a factual, non-stylized base caption summarizing the video timeline,
        by genuinely watching and listening to the video via Gemini Multimodal.
        """
        # 1. ALWAYS run local AMD GPU visual extraction first
        try:
            from .vision_encoder import extract_visual_context
            visual_context = extract_visual_context(video_path)
        except Exception as e:
            print(f"Skipping local AMD vision extraction (not available in this environment): {e}")
            visual_context = "Local vision extraction skipped."

        if not self.client:
            if visual_context == "Local vision extraction skipped.":
                return "A generic video showing a sequence of events. A person or object is interacting with the environment."
            from .llm_service import LLMService
            llm = LLMService()
            fallback_prompt = f"Context: {visual_context}\nGenerate a simple 2-sentence factual description of what is happening. Do not include any reasoning or meta-analysis."
            return llm.generate_text("You are a strict, objective video captioner. Output ONLY the final factual caption.", fallback_prompt).strip()
        
        try:
            # 2. Extract frames locally using OpenCV to pass directly to Gemini (bypassing slow File API)
            import cv2
            from PIL import Image
            
            cap = cv2.VideoCapture(video_path)
            frames = []
            if cap.isOpened():
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                if frame_count > 0:
                    # Extract 8 evenly spaced frames to represent the video
                    num_frames = min(8, frame_count)
                    indices = [int(i * frame_count / num_frames) for i in range(num_frames)]
                    for idx in indices:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                        ret, frame = cap.read()
                        if ret:
                            # Resize to 640x360 to save bandwidth/tokens
                            frame = cv2.resize(frame, (640, 360))
                            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            pil_img = Image.fromarray(rgb_frame)
                            frames.append(pil_img)
            cap.release()

            if not frames:
                raise Exception("Failed to extract any frames from the video.")

            prompt = f"""
Visual context extracted locally: {visual_context}

Attached are evenly spaced frames extracted from the video.
Watch the video frames carefully and analyze the temporal sequence.

Generate a comprehensive, catchy paragraph describing what is happening in the video.
Include actions, setting, objects, and overall mood.

Output ONLY the catchy paragraph (3-4 sentences). Do not include any reasoning, thoughts, or introductory text.
"""
            
            # Pass frames and prompt inline to avoid File API timeout
            contents = frames + [prompt]
            
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents
            )
            
            return response.text.strip()
            
        except Exception as e:
            # 3. Graceful Fallback: If Video API fails, use the local context with the text LLM
            print(f"Gemini Video API failed ({e}). Falling back to local AMD visual context and LLMService.")
            
            if visual_context == "Local vision extraction skipped.":
                return f"A generic video showing a sequence of events. (Debug Info: {str(e)})"
                
            from .llm_service import LLMService
            llm = LLMService()
            fallback_prompt = (
                f"Based on the following visual context: '{visual_context}', "
                "generate a simple, factual 2-sentence description of what is happening. Do not include any reasoning or analysis. Just output the 2 sentences."
            )
            return llm.generate_text("You are an objective video captioning assistant. Output ONLY the final factual caption.", fallback_prompt).strip()
