import os
import logging
from openai import OpenAI
from google import genai
from google.genai import types

logger = logging.getLogger("captionforge.llm_service")


class LLMService:
    def __init__(self):
        pass  # Keys always read fresh per-request for Vercel serverless compatibility

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates text using Fireworks AI (Llama 3.1 70B) first.
        Falls back to Gemini 2.5 Flash if Fireworks fails or key is missing.
        Raises an exception if both fail.
        """
        # Always read fresh from env — critical for Vercel serverless
        fireworks_api_key = os.environ.get("FIREWORKS_API_KEY")
        gemini_api_key = (
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GOOGLE_GEMINI_KEY")
        )

        # Try Fireworks first (only if key is set)
        if fireworks_api_key:
            try:
                fireworks_client = OpenAI(
                    base_url="https://api.fireworks.ai/inference/v1",
                    api_key=fireworks_api_key
                )
                response = fireworks_client.chat.completions.create(
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
                    logger.info("Generated text via Fireworks AI (Llama 3.1 70B).")
                    return text
            except Exception as e:
                logger.warning(f"Fireworks AI call failed: {e}. Falling back to Gemini...")

        # Fallback to Gemini
        if gemini_api_key:
            try:
                gemini_client = genai.Client(api_key=gemini_api_key)
                response = gemini_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.75,
                        max_output_tokens=800
                    )
                )
                if response.text:
                    logger.info("Generated text via Gemini (fallback).")
                    return response.text.strip()
            except Exception as e:
                logger.error(f"Gemini text generation also failed: {e}")
                raise Exception(f"Both Fireworks and Gemini failed. Last error: {e}")

        raise Exception(
            "No valid API keys configured. "
            "Please set GEMINI_API_KEY in your Vercel environment variables and redeploy."
        )
