from typing import Dict, Any

class CaptionGenerator:
    def generate_base_caption(self, temporal_graph: Dict[str, Any]) -> str:
        """
        Creates a factual, non-stylized base caption summarizing the video timeline.
        """
        desc = temporal_graph.get("full_description", "")
        entities = ", ".join(temporal_graph.get("entities", []))
        
        if not desc:
            return "No activities or entities detected in the video."

        # Simplify/clean the visual description to get a clear factual base
        base_caption = f"The video displays {entities}. Specifically, {desc}"
        
        # Clean double spaces or clean phrasing
        base_caption = base_caption.replace("  ", " ").strip()
        return base_caption
