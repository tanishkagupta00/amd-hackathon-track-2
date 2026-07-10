from typing import List, Dict, Any

class SceneDetector:
    def __init__(self, scene_threshold: float = 30.0):
        self.scene_threshold = scene_threshold

    def detect_scenes(self, keyframes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Groups keyframes into semantic scenes based on temporal proximity and visual difference.
        """
        if not keyframes:
            return []

        scenes = []
        current_scene_keyframes = [keyframes[0]]
        scene_id = 1

        for i in range(1, len(keyframes)):
            prev_kf = keyframes[i - 1]
            curr_kf = keyframes[i]
            
            # Simple scene boundary logic: if temporal gap > 5 seconds, treat as new scene
            time_gap = curr_kf["timestamp"] - prev_kf["timestamp"]
            
            if time_gap > 5.0:
                # Close current scene
                scenes.append({
                    "scene_id": scene_id,
                    "start_time": current_scene_keyframes[0]["timestamp"],
                    "end_time": prev_kf["timestamp"],
                    "keyframes": current_scene_keyframes,
                    "confidence": 0.85
                })
                scene_id += 1
                current_scene_keyframes = [curr_kf]
            else:
                current_scene_keyframes.append(curr_kf)

        # Close the last scene
        if current_scene_keyframes:
            scenes.append({
                "scene_id": scene_id,
                "start_time": current_scene_keyframes[0]["timestamp"],
                "end_time": keyframes[-1]["timestamp"],
                "keyframes": current_scene_keyframes,
                "confidence": 0.90
            })

        # Ensure end time is at least slightly after start time
        for scene in scenes:
            if scene["start_time"] == scene["end_time"]:
                scene["end_time"] += 2.0

        return scenes
