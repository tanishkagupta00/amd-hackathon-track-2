import re
from typing import Dict, Any, List


class CaptionCritic:
    """
    Evaluates styled captions for:
    1. Style adherence  — does the caption actually match the requested tone?
    2. Cross-style leakage — does a non-tech caption accidentally use tech-ONLY
       jargon that makes no sense outside a developer context?

    What this critic does NOT do:
    - It does NOT flag real-world object words (keyboard, monitor, screen, phone)
      as hallucinations. Those are genuine video content — appearing in any style
      caption is fine and expected.
    - Only flags multi-word dev-specific phrases (e.g. "merge conflict", "stack
      overflow", "null pointer exception") that have no place in casual humor.
    """

    # ── Phrases that are ONLY meaningful in a developer/tech context ──────────
    # Single words like "keyboard", "monitor", "code", "bug" are everyday words
    # and must NOT be flagged — they appear in the video itself.
    # Only flag unmistakably developer-only compound phrases.
    TECH_ONLY_PHRASES = [
        "merge conflict", "null pointer", "stack overflow", "segmentation fault",
        "runtime error", "deployment pipeline", "ci/cd", "pull request",
        "git commit", "git push", "git merge", "docker container",
        "kubernetes", "buffer overflow", "stack trace", "heap allocation",
        "garbage collector", "async await", "dependency injection",
        "microservice", "api endpoint", "rest api", "graphql",
        "machine learning model", "neural network", "gradient descent",
    ]

    # ── Style-specific positive markers ───────────────────────────────────────
    SARCASTIC_MARKERS = [
        "oh", "behold", "wow", "revolutionary", "groundbreaking", "stunning",
        "riveting", "fascinating", "truly", "surely", "undoubtedly", "clearly",
        "obviously", "incredible", "remarkable", "breathtaking", "miraculous",
        "historic", "peak", "bold", "daring", "cosmic", "galaxy-brain",
        "never been done", "wait for it",
    ]

    TECH_HUMOR_MARKERS = [
        "merge", "conflict", "compile", "bug", "code", "loop", "thread",
        "cpu", "git", "deploy", "server", "database", "function", "variable",
        "error", "exception", "null", "undefined", "stack", "heap", "cache",
        "runtime", "algorithm", "framework", "library", "syntax", "binary",
        "debug", "refactor", "pipeline", "container", "api", "endpoint",
        "async", "callback", "pointer", "memory", "kernel", "process",
    ]

    def evaluate_caption(
        self,
        caption: str,
        style: str,
        entities: List[str] = None,
    ) -> Dict[str, Any]:

        cap_lower = caption.lower()
        hallucination_detected = False
        hallucinated_phrases: List[str] = []

        # ── Cross-style leakage check ─────────────────────────────────────────
        # Only flag unmistakably dev-only compound phrases that have no place
        # in formal, sarcastic, or humorous-non-tech captions.
        if style in ("formal", "sarcastic", "humorous-non-tech"):
            for phrase in self.TECH_ONLY_PHRASES:
                if phrase in cap_lower:
                    hallucination_detected = True
                    hallucinated_phrases.append(phrase)

        # ── Accuracy score ────────────────────────────────────────────────────
        accuracy_score = 1.0
        if hallucination_detected:
            # Each leaked phrase costs 0.1, floored at 0.5 (still a decent caption)
            accuracy_score = max(0.5, 1.0 - 0.1 * len(hallucinated_phrases))
        accuracy_score = round(accuracy_score, 2)

        # ── Style adherence score ─────────────────────────────────────────────
        style_score = 1.0
        reasons: List[str] = []

        if style == "formal":
            if "!" in caption:
                style_score -= 0.15
                reasons.append("Exclamation marks weaken formal tone")
            # Only flag first-person pronouns as standalone words (not "your", "you're")
            first_person = {"i", "we", "my", "our"}
            words = set(re.findall(r"\b\w+\b", cap_lower))
            overlap = first_person & words
            if overlap:
                style_score -= 0.15
                reasons.append(f"Personal pronouns present: {', '.join(sorted(overlap))}")

        elif style == "sarcastic":
            if not any(m in cap_lower for m in self.SARCASTIC_MARKERS):
                style_score -= 0.2
                reasons.append("Missing sarcastic irony markers")
            if "!" not in caption and "..." not in caption:
                style_score -= 0.05
                reasons.append("Sarcasm reads flat without emphasis punctuation")

        elif style == "humorous-tech":
            hits = [m for m in self.TECH_HUMOR_MARKERS if m in cap_lower]
            if not hits:
                style_score -= 0.3
                reasons.append("No computing/developer references found")
            elif len(hits) < 2:
                style_score -= 0.1
                reasons.append("Light on tech references — needs more jargon density")

        elif style == "humorous-non-tech":
            # Only penalise unmistakably developer compound phrases
            leaked = [p for p in self.TECH_ONLY_PHRASES if p in cap_lower]
            if leaked:
                style_score -= 0.2
                reasons.append(f"Developer jargon leaked into everyday humor: {leaked[0]}")

        style_score = max(0.1, round(style_score, 2))

        # ── Clean leaked phrases from caption ─────────────────────────────────
        cleaned_caption = caption
        if hallucination_detected:
            for phrase in hallucinated_phrases:
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                cleaned_caption = pattern.sub("something", cleaned_caption)

        return {
            "caption": cleaned_caption,
            "original_caption": caption,
            "accuracy_score": accuracy_score,
            "style_score": style_score,
            "hallucination_detected": hallucination_detected,
            "hallucinated_words": hallucinated_phrases,
            "style_reasons": reasons,
        }
