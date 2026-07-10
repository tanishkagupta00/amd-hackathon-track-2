import re
from typing import Dict, Any, List

class CaptionCritic:
    def evaluate_caption(self, caption: str, style: str, entities: List[str] = None) -> Dict[str, Any]:
        """
        Evaluates a caption on factual accuracy, style adherence, and checks for hallucinations.
        """
        cap_lower = caption.lower()
        hallucination_detected = False
        hallucinated_words = []
        
        # Simplified Hallucination Check
        # Check if they hallucinate technical jargon in a non-tech style
        tech_keywords = ["developer", "keyboard", "monitor", "code", "compile", "git", "merge conflict", "bug"]
        
        if style != "humorous-tech":
            for k in tech_keywords:
                if k in cap_lower:
                    hallucination_detected = True
                    hallucinated_words.append(k)

        # 2. Accuracy Score calculation
        # Base accuracy starts at 1.0, drops for hallucinations
        accuracy_score = 1.0
        if hallucination_detected:
            accuracy_score -= 0.15 * len(hallucinated_words)
            accuracy_score = max(0.2, accuracy_score)

        # 3. Style Adherence Score calculation
        style_score = 1.0
        reasons = []

        if style == "formal":
            # Formal check: no exclamation marks, no personal pronouns (I, you, we)
            if "!" in caption:
                style_score -= 0.2
                reasons.append("Contains exclamation mark in formal text")
            if any(p in cap_lower.split() for p in ["i", "you", "we", "my", "our"]):
                style_score -= 0.2
                reasons.append("Contains personal pronouns")
        elif style == "sarcastic":
            # Sarcastic check: search for sarcastic markers
            markers = ["oh", "look", "fascinating", "stunning", "surely", "miraculous", "peak", "witness"]
            if not any(m in cap_lower for m in markers):
                style_score -= 0.2
                reasons.append("Lacks sarcastic irony markers")
        elif style == "humorous-tech":
            # Tech humor check: must contain technical jargon
            tech_markers = ["merge", "conflict", "compile", "bug", "code", "loop", "packet", "thread", "cpu", "system", "git"]
            if not any(m in cap_lower for m in tech_markers):
                style_score -= 0.3
                reasons.append("Lacks computing/developer jargon")
        elif style == "humorous-non-tech":
            # Non-tech check: must NOT contain technical jargon
            tech_markers = ["merge conflict", "compile", "git", "stack overflow", "vram", "rocm"]
            if any(m in cap_lower for m in tech_markers):
                style_score -= 0.3
                reasons.append("Contains technical jargon in non-tech humor")

        style_score = max(0.1, round(style_score, 2))

        # 4. Automated Regeneration Loop
        # If hallucination is severe, we clean the caption
        cleaned_caption = caption
        if hallucination_detected:
            for word in hallucinated_words:
                # Replace the hallucinated word with a generic one or remove it
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                cleaned_caption = pattern.sub("item", cleaned_caption)

        return {
            "caption": cleaned_caption,
            "original_caption": caption,
            "accuracy_score": accuracy_score,
            "style_score": style_score,
            "hallucination_detected": hallucination_detected,
            "hallucinated_words": hallucinated_words,
            "style_reasons": reasons
        }
Class_Name = "CaptionCritic"
