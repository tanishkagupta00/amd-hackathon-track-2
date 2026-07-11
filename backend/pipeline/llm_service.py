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
        Generates text using Fireworks AI first, falls back to Gemini.
        Returns the generated text.
        Sets self.last_provider = 'fireworks' | 'gemini' so callers can
        decide whether to throttle subsequent calls.
        """
        self.last_provider = None
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
                    # deepseek-v4-pro — confirmed working with this Fireworks API key
                    model="accounts/fireworks/models/deepseek-v4-pro",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=800,
                    temperature=0.75
                )
                text = response.choices[0].message.content.strip()
                if text:
                    logger.info("Generated text via Fireworks AI (deepseek-v4-pro).")
                    self.last_provider = "fireworks"
                    return text
            except Exception as e:
                logger.warning(f"Fireworks AI call failed: {e}. Falling back to Gemini...")

        # Fallback to Gemini
        if gemini_api_key:
            gemini_client = genai.Client(api_key=gemini_api_key)
            # gemini-2.0-flash: 15 RPM free tier (vs 5 RPM for 2.5-flash)
            # Retry up to 3 times with backoff on 429 RESOURCE_EXHAUSTED
            last_err = None
            for attempt in range(3):
                try:
                    response = gemini_client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=0.75,
                            max_output_tokens=800
                        )
                    )
                    if response.text:
                        logger.info(f"Generated text via Gemini (attempt {attempt + 1}).")
                        self.last_provider = "gemini"
                        return response.text.strip()
                except Exception as e:
                    last_err = e
                    err_str = str(e)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        # Parse retry delay from error if available, default to 30s
                        import re, time
                        delay_match = re.search(r'retryDelay.*?(\d+)s', err_str)
                        wait = int(delay_match.group(1)) + 2 if delay_match else 32
                        logger.warning(f"Gemini 429 on attempt {attempt + 1}. Waiting {wait}s...")
                        time.sleep(wait)
                    else:
                        # Non-rate-limit error — don't retry
                        logger.error(f"Gemini text generation failed: {e}")
                        raise Exception(f"Both Fireworks and Gemini failed. Last error: {e}")
            raise Exception(f"Gemini rate limit exceeded after 3 retries. Last error: {last_err}")

        raise Exception(
            "No valid API keys configured. "
            "Please set GEMINI_API_KEY in your Vercel environment variables and redeploy."
        )
