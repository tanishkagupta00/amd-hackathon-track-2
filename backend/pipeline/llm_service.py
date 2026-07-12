import os
import logging
from openai import OpenAI

logger = logging.getLogger("captionforge.llm_service")


class LLMService:
    def __init__(self):
        pass  # Keys always read fresh per-request for Vercel serverless compatibility

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates text using Fireworks AI exclusively (no Gemini fallback).
        Returns the generated text.
        Sets self.last_provider = 'fireworks' so callers can track usage.
        """
        self.last_provider = None
        # Always read fresh from env — critical for Vercel serverless
        fireworks_api_key = os.environ.get("FIREWORKS_API_KEY")

        if not fireworks_api_key:
            raise Exception(
                "No FIREWORKS_API_KEY found. Please set FIREWORKS_API_KEY "
                "in your Vercel environment variables and redeploy."
            )

        fireworks_client = OpenAI(
            base_url="https://api.fireworks.ai/inference/v1",
            api_key=fireworks_api_key
        )

        # Try primary model, then fallback models in order
        models_to_try = [
            "accounts/fireworks/models/deepseek-v4-pro",   # primary
            "accounts/fireworks/models/kimi-k2p6",          # fallback 1
            "accounts/fireworks/models/gpt-oss-120b",       # fallback 2
        ]

        last_error = None
        for model in models_to_try:
            try:
                response = fireworks_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=800,
                    temperature=0.75
                )
                text = response.choices[0].message.content.strip()
                if text:
                    logger.info(f"Generated text via Fireworks AI ({model}).")
                    self.last_provider = "fireworks"
                    return text
            except Exception as e:
                err_str = str(e)
                is_rate_limit = "429" in err_str or "RESOURCE_EXHAUSTED" in err_str
                is_unavailable = "404" in err_str or "NOT_FOUND" in err_str
                if is_rate_limit or is_unavailable:
                    logger.warning(f"Fireworks model {model} unavailable/rate-limited: {e}. Trying next...")
                    last_error = e
                    continue
                # Non-transient error — raise immediately
                raise Exception(f"Fireworks AI text generation failed: {e}")

        raise Exception(
            f"All Fireworks AI models exhausted. Last error: {last_error}. "
            "Please check your FIREWORKS_API_KEY and account credits."
        )
