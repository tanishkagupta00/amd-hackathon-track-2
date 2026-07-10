from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class VideoUploadResponse(BaseModel):
    video_id: str
    status: str
    filename: str

class CaptionGenerationRequest(BaseModel):
    video_id: str
    styles: List[str] = Field(default=["formal", "sarcastic", "humorous-tech", "humorous-non-tech"])

class CaptionsSchema(BaseModel):
    formal: str
    sarcastic: str
    humorous_tech: str = Field(alias="humorous-tech")
    humorous_non_tech: str = Field(alias="humorous-non-tech")

    class Config:
        populate_by_name = True

class TaskCaptionResult(BaseModel):
    task_id: str
    captions: CaptionsSchema

class SubmissionSchema(BaseModel):
    tasks: List[TaskCaptionResult]

class EvaluationRequest(BaseModel):
    caption: str
    style: str
    entities: List[str]

class EvaluationResponse(BaseModel):
    caption: str
    accuracy_score: float
    style_score: float
    hallucination_detected: bool
    hallucinated_words: List[str]
