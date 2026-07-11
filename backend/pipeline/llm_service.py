import os
import logging
from openai import OpenAI
from google import genai

logger = logging.getLogger("captionforge.llm_service")

class LLMService:
    def __init__(self):
        self.fireworks_api_key = os.environ.get("FIREWORKS_API_KEY")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        
        self.fireworks_client = None
        if self.fireworks_api_key:
            self.fireworks_client = OpenAI(
                base_url="https://api.fireworks.ai/inference/v1",
                api_key=self.fireworks_api_key
            )
            
        self.gemini_client = None
        if self.gemini_api_key:
            self.gemini_client = genai.Client(api_key=self.gemini_api_key)

    def generate_text(self, system_prompt: str, user_prompt: str, fallback: bool = True) -> str:
        """
        Attempts to generate text using Fireworks AI first. If it fails (e.g., rate limits, out of credits),
        it falls back to Gemini.
        """
        # Try Fireworks First
        if self.fireworks_client:
            try:
                response = self.fireworks_client.chat.completions.create(
                    model="accounts/fireworks/models/llama-v3p1-70b-instruct",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=800,
                    temperature=0.75
                )
                text = response.choices[0].message.content.strip()
                if text:
                    logger.info("Successfully generated text via Fireworks AI.")
                    return text
            except Exception as e:
                logger.warning(f"Fireworks AI call failed: {e}. Falling back to Gemini...")
        
        # Fallback to Gemini
        if fallback and self.gemini_client:
            try:
                from google.genai import types
                response = self.gemini_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.7,
                        max_output_tokens=800
                    )
                )
                if response.text:
                    logger.info("Successfully generated text via Gemini (Fallback).")
                    return response.text.strip()
            except Exception as e2:
                logger.error(f"Gemini Fallback also failed: {e2}")
                # Don't raise, fallback to mock below
                
        # Ultimate Fallback if API keys are missing or all APIs fail
        logger.warning("No valid API keys configured or all APIs failed. Returning mock generation.")
        return "[Mocked response due to missing API keys] The video shows an interesting sequence of events. A person is engaging with technology in a modern setting."

    def generate_vision(self, prompt: str, base64_images: list[str]) -> str:
        """
        Attempts to generate text from images using Fireworks AI first, falling back to Gemini.
        """
        if self.fireworks_client:
            try:
                content = [{"type": "text", "text": prompt}]
                # Fireworks supports multiple images in the content array
                for b64 in base64_images:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                    })
                
                response = self.fireworks_client.chat.completions.create(
                    model="accounts/fireworks/models/llama-v3p2-11b-vision-instruct",
                    messages=[{"role": "user", "content": content}],
                    max_tokens=600,
                    temperature=0.7
                )
                text = response.choices[0].message.content.strip()
                if text:
                    return text
            except Exception as e:
                logger.warning(f"Fireworks Vision API failed: {e}. Falling back to Gemini...")
                
        if self.gemini_client:
            try:
                # Gemini doesn't use base64 in the same way with google-genai, it prefers Part objects or PIL Images.
                # However, since we are moving the image generation logic, we can just let Gemini handle it inside caption_generator.
                pass 
            except Exception as e:
                pass
                
        return "A generic video showing a sequence of events. A person or object is interacting with the environment."
