import os
import sys

# Ensure backend module can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.pipeline.pipeline import CaptionForgePipeline

def main():
    print("CaptionForge Pipeline - Multimodal Grounding Test")
    print("Verifying that captions are dynamically generated from real visual/audio context.\n")
    
    if len(sys.argv) < 2:
        print("Usage: python test_grounding.py <video1.mp4> <video2.mp4> ...")
        return

    # Check for Fireworks API key
    if not os.environ.get("FIREWORKS_API_KEY"):
        print("\nWARNING: FIREWORKS_API_KEY not set. Multimodal generation will fail or return stubs.\n")

    pipeline = CaptionForgePipeline()
    
    for vid_path in sys.argv[1:]:
        print(f"\n" + "="*50)
        print(f" TESTING VIDEO: {vid_path}")
        print("="*50)
        
        if not os.path.exists(vid_path):
            print("File not found. Skipping.")
            continue
            
        def progress(stage, msg):
            if stage == "generating":
                print(f"[{stage.upper()}] {msg}")
                
        result = pipeline.process_video(vid_path, progress_callback=progress)
        
        print("\n=== FACTUAL BASE SCENE DESCRIPTION (Model Generated) ===")
        print(result["base_caption"])
        
        print("\n=== STYLED CAPTIONS (Model Rewrites) ===")
        for style, cap in result["captions"].items():
            print(f"\n--- {style.upper()} ---")
            print(cap)
            
if __name__ == "__main__":
    main()
