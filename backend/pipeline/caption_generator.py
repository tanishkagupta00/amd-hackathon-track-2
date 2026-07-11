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
        from .vision_encoder import extract_visual_context
        from .llm_service import LLMService

        # 1. ALWAYS run local AMD GPU visual extraction first
        visual_context = extract_visual_context(video_path)

        if not self.client:
            llm = LLMService()
            return llm.generate_text("You are a factual video captioner.", f"Based on this visual context extracted locally: '{visual_context}', generate a factual 2-sentence description of what might be happening.")
        
        try:
            # 2. Try Gemini Video File API for deep temporal understanding
            video_file = self.client.files.upload(file=video_path)
            
            while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = self.client.files.get(name=video_file.name)
            
            if video_file.state.name == "FAILED":
                raise Exception("Gemini File API returned FAILED state.")

            prompt = f"""
Visual context extracted locally using AMD GPU:

{visual_context}

Now watch the ENTIRE video carefully.

Generate a factual description including:

- actions
- setting
- objects
- emotions
- speech
"""
            
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[video_file, prompt]
            )
            
            try:
                self.client.files.delete(name=video_file.name)
            except:
                pass
                
            return response.text.strip()
            
        except Exception as e:
            # 3. Graceful Fallback: If Video API fails, use the local context with the text LLM
            print(f"Gemini Video API failed ({e}). Falling back to local AMD visual context and LLMService.")
            llm = LLMService()
            fallback_prompt = (
                f"Video processing failed, but we extracted this visual context locally using an AMD GPU: '{visual_context}'. "
                "Generate a factual, objective 2-sentence description of what might be happening in this video. Do not apologize or mention the failure."
            )
            return llm.generate_text("You are an objective video captioning assistant. Output ONLY the factual caption.", fallback_prompt).strip()
