from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class VideoUploadResponse(BaseModel):
    video_id: str
    status: str
    filename: str

class VideoUrlUploadRequest(BaseModel):
    url: str
    filename: str

class CaptionGenerationRequest(BaseModel):
    video_id: str
    # video_url is passed directly to make /captions/generate self-contained on Vercel.
    # Vercel runs each serverless function in an isolated container with an ephemeral /tmp,
    # so the DB record written during upload may not exist by the time generate runs.
    # When video_url is provided the route downloads the file fresh and skips the DB lookup.
    video_url: Optional[str] = None
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
