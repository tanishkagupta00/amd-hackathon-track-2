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
                    max_tokens=600,
                    temperature=0.7
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
                        max_output_tokens=600
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
