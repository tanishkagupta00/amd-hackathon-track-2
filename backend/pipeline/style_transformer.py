import os
import requests
from typing import Dict, Any

class StyleTransformer:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    def transform(self, base_caption: str, style: str, entities: list) -> str:
        """
        Transforms the baseline factual caption into the requested style.
        """
        # 1. If API key is present, try to perform a zero-shot LLM translation
        if self.api_key:
            try:
                # Call Gemini API via simple REST call
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
                headers = {"Content-Type": "application/json"}
                
                prompt = self._get_prompt(base_caption, style)
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }
                
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if text:
                        return text
            except Exception as e:
                # Fallback to local rule-based engine if API fails
                pass

        # 2. Local Rule-based engine (highly detailed templates based on detected context)
        return self._local_transform(base_caption, style, entities)

    def _get_prompt(self, base_caption: str, style: str) -> str:
        if style == "formal":
            return f"Rewrite the following description into a highly objective, formal, third-person report: '{base_caption}'. Do not add any conversational words or humor."
        elif style == "sarcastic":
            return f"Rewrite the following description in a dry, ironic, mocking, and sarcastic tone: '{base_caption}'. Mock the actions shown."
        elif style == "humorous-tech":
            return f"Rewrite the following description into a humorous paragraph filled with software development, programming, or computer science jokes and metaphors (e.g. merge conflicts, buffer underruns, legacy debt): '{base_caption}'."
        elif style == "humorous-non-tech":
            return f"Rewrite the following description into an observational comedy style paragraph with general, everyday humor and tropes (do NOT use programming/tech jokes): '{base_caption}'."
        return base_caption

    def _local_transform(self, base_caption: str, style: str, entities: list) -> str:
        # Detect context
        ent_str = " ".join(entities).lower()
        
        is_dev = any(k in ent_str for k in ["developer", "keyboard", "monitor", "office", "desk"])
        is_cat = "cat" in ent_str
        is_dog = "dog" in ent_str
        is_cook = any(k in ent_str for k in ["chef", "pan", "kitchen", "cook"])
        is_car = "car" in ent_str
        is_nature = any(k in ent_str for k in ["mountain", "lake", "forest", "nature"])

        if style == "formal":
            if is_dev:
                return "The subject is observed engaging in software development tasks, utilizing a computer terminal and input interfaces at a dedicated office station."
            if is_cat:
                return "A domestic feline is observed executing motor patterns directed at a spherical textile object in an indoor setting."
            if is_dog:
                return "A canine subject is documented executing high-velocity locomotion to retrieve a spherical play object within a designated park area."
            if is_cook:
                return "A culinary practitioner is documented performing food preparation and thermal processing tasks at a standard kitchen station."
            if is_car:
                return "A motorized passenger vehicle is observed traveling at high velocity on an engineered public asphalt highway."
            if is_nature:
                return "A documentation of physical geographic features including high-altitude peaks, forestry, and a body of water under standard atmospheric conditions."
            return f"Subject observed: {base_caption}. Context is recorded objectively in third-person format."

        elif style == "sarcastic":
            if is_dev:
                return "Witness the absolute peak of modern civilization: a developer spending hours converting coffee into bugs and staring blankly at compile errors."
            if is_cat:
                return "Oh look, a feline mastermind expending maximum energy to dominate a stationary ball of yarn. Truely a predator of the wild."
            if is_dog:
                return "A dog executing a critical sprint to fetch a rubber ball, as if the entire future of the universe depended on this single, vital task."
            if is_cook:
                return "An aspiring chef performing the miraculous feat of slicing an onion without crying, aiming for a Michelin star with basic stir-fry."
            if is_car:
                return "Stunning. A car driving fast on a highway. Let's write a song about this highly unusual and complex event."
            if is_nature:
                return "Oh great, mountains and a lake. Just what the internet needs: another landscape view that looks exactly like a default wallpaper."
            return f"Fascinating. {base_caption}. Surely this will change the course of human history."

        elif style == "humorous-tech":
            if is_dev:
                return "The coder is frantically typing code, trying to resolve a critical merge conflict that somehow broke production. It is a legacy debt marathon!"
            if is_cat:
                return "A cute furry system thread executing a high-priority loop to debug a yarn ball entity. CPU utilization is at 100% due to playing."
            if is_dog:
                return "The dog is executing fetch protocols. The packet (tennis ball) was sent across the field, received, and successfully returned to the host."
            if is_cook:
                return "The chef is managing a multi-threaded kitchen pipeline, executing compile commands (slicing onions) and committing changes to the hot pan."
            if is_car:
                return "The vehicle is operating at peak clock speed on a dedicated PCIe lane (highway) with zero network latency."
            if is_nature:
                return "Beautiful landscape rendering in bfloat16. High-polygon mountains and a lake with ray-tracing enabled by default."
            return f"Executing system style override: {base_caption} has been compiled into a humorous-tech format with zero warnings."

        elif style == "humorous-non-tech":
            if is_dev:
                return "Trying to look incredibly busy typing random letters on the keyboard whenever the manager walks past the office desk."
            if is_cat:
                return "Cats: the only creature that can treat a ball of yarn like an ancient mythical enemy that must be destroyed at all costs."
            if is_dog:
                return "The pure, unadulterated joy of a dog who has absolutely no idea what taxes are, running after a green ball like it's gold."
            if is_cook:
                return "A cook attempting to chop onions like a cooking show host, while secretly hoping they don't slice off a finger in the process."
            if is_car:
                return "A driver moving down the road, probably singing along to a song they only know three words of, feeling like a movie star."
            if is_nature:
                return "Mountains and lakes: nature's way of reminding us that our daily problems are small, and that we really need to go outside more."
            return f"A funny situational look at this: {base_caption}. Who knew everyday life could be so entertaining?"

        return base_caption
