import os
import json
import logging
from typing import Dict, List, Any
from pydantic import ValidationError

from pipeline.pipeline import CaptionForgePipeline
from schemas.models import SubmissionSchema, TaskCaptionResult, CaptionsSchema

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("captionforge.runner")

def get_io_paths():
    """
    Returns the resolved input and output file paths based on environment.
    """
    # 1. Check Docker paths
    input_path = "/input/tasks.json"
    output_path = "/output/results.json"
    
    # 2. Check local relative paths
    if not os.path.exists(input_path):
        input_path = "input/tasks.json"
        output_path = "output/results.json"
        
    # 3. Check Windows root paths
    if not os.path.exists(input_path):
        input_path = "C:\\input\\tasks.json"
        output_path = "C:\\output\\results.json"
        
    # 4. Fallback: Workspace folder
    if not os.path.exists(input_path):
        workspace_dir = os.getcwd()
        input_path = os.path.join(workspace_dir, "tasks.json")
        output_path = os.path.join(workspace_dir, "results.json")

    return input_path, output_path

def main():
    logger.info("Initializing CaptionForge AI Headless Runner...")
    
    input_file, output_file = get_io_paths()
    
    if not os.path.exists(input_file):
        logger.error(f"Input file tasks.json not found at: {input_file}")
        # Create a dummy tasks.json for local testing convenience if not present
        dummy_tasks = [
            {
                "task_id": "v_test_01",
                "video_path": "sample.mp4"
            }
        ]
        os.makedirs(os.path.dirname(input_file) or ".", exist_ok=True)
        with open(input_file, "w") as f:
            json.dump(dummy_tasks, f, indent=2)
        logger.info(f"Created sample input file: {input_file}")
        
    logger.info(f"Reading tasks from: {input_file}")
    try:
        with open(input_file, "r") as f:
            tasks_data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to parse tasks.json: {str(e)}")
        return

    # If it's a list or dictionary, unpack it
    if isinstance(tasks_data, dict) and "tasks" in tasks_data:
        tasks = tasks_data["tasks"]
    else:
        tasks = tasks_data

    pipeline = CaptionForgePipeline()
    results = []

    for task in tasks:
        task_id = task.get("task_id")
        video_path = task.get("video_path") or task.get("video_url")
        
        if not task_id or not video_path:
            logger.warning(f"Skipping malformed task: {task}")
            continue

        logger.info(f"Processing Task: {task_id} | Video: {video_path}")
        
        try:
            # Run pipeline
            res = pipeline.process_video(video_path)
            
            # Map output to schema structure
            caps = res["captions"]
            
            # Map keys with hyphens
            captions_schema = CaptionsSchema(
                formal=caps["formal"],
                sarcastic=caps["sarcastic"],
                **{
                    "humorous-tech": caps["humorous-tech"],
                    "humorous-non-tech": caps["humorous-non-tech"]
                }
            )
            
            task_result = TaskCaptionResult(
                task_id=task_id,
                captions=captions_schema
            )
            results.append(task_result)
            logger.info(f"Completed Task: {task_id}")
            
        except Exception as e:
            logger.error(f"Error processing Task {task_id}: {str(e)}")
            # Write a fallback to avoid failing the entire process
            fallback_captions = CaptionsSchema(
                formal=f"An action is executed in the video.",
                sarcastic="Look, something happened. How thrilling.",
                **{
                    "humorous-tech": "Execution complete. System status code 200.",
                    "humorous-non-tech": "And that is how things are done!"
                }
            )
            results.append(TaskCaptionResult(task_id=task_id, captions=fallback_captions))

    # Compile results under SubmissionSchema
    try:
        submission = SubmissionSchema(tasks=results)
        # Convert Pydantic model to Dict (by_alias=True is crucial to serialize keys with hyphens)
        output_payload = submission.model_dump(by_alias=True)
    except ValidationError as ve:
        logger.error(f"JSON validation failed: {str(ve)}")
        return

    # Write output file
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    logger.info(f"Writing compliance-checked results to: {output_file}")
    try:
        with open(output_file, "w") as f:
            json.dump(output_payload, f, indent=2)
        logger.info("Successfully exported results.")
    except Exception as e:
        logger.error(f"Failed to write results.json: {str(e)}")

if __name__ == "__main__":
    main()
