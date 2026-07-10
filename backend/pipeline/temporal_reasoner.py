from typing import List, Dict, Any

class TemporalReasoner:
    def build_timeline(self, scene_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Builds a chronological narrative and sequence of events across all scenes.
        """
        if not scene_analyses:
            return {"timeline": [], "full_description": "No scenes analyzed."}

        timeline = []
        all_descriptions = []
        all_entities = set()

        for idx, analysis in enumerate(scene_analyses):
            start = analysis["timestamp"]["start"]
            end = analysis["timestamp"]["end"]
            
            # Record timeline entry
            timeline.append({
                "time_range": f"{start:.1f}s - {end:.1f}s",
                "location": analysis["location"],
                "actions": analysis["actions"],
                "entities": analysis["objects"]
            })
            
            all_descriptions.append(analysis["description"])
            all_entities.update(analysis["objects"])

        # Join descriptions logically into a full visual summary
        full_description = " ".join(all_descriptions)

        return {
            "timeline": timeline,
            "entities": list(all_entities),
            "full_description": full_description
        }
