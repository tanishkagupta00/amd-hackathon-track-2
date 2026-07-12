
# API Specification

**Project:** CaptionForge AI  
**Document:** 13_API_Specification.md  
**Version:** 2.0 (Implementation Aligned)

---

# Executive Summary

CaptionForge AI exposes a RESTful API built with FastAPI for video upload, caption generation, evaluation, and system monitoring. The API is versioned at `/api/v1` and returns JSON responses.

**Base URLs:**
- **Development:** `http://localhost:8000/api/v1`
- **Production (Vercel):** `https://your-app.vercel.app/api/v1`

**OpenAPI Documentation:**
- Swagger UI: `/docs`
- ReDoc: `/redoc`

---

# Authentication

**Competition Mode:** No authentication required

**Production Mode:** JWT Bearer Tokens (future enhancement)

---

# Endpoints Overview

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/videos` | Upload video file |
| POST | `/videos/url` | Upload video from URL |
| GET | `/videos/{id}` | Get video status |
| POST | `/captions/generate` | Generate captions |
| GET | `/captions/{id}` | Retrieve captions |
| POST | `/evaluations` | Evaluate caption quality |
| GET | `/health` | Health check |
| GET | `/config` | Runtime configuration |

---

# 1. Video Upload

## 1.1 Upload Video File

**POST** `/api/v1/videos`

Uploads a video file directly to the server.

### Request
- **Content-Type:** `multipart/form-data`
- **Body:** `file` (required) - Video file

### Response (200 OK)
```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "uploaded",
  "filename": "sample.mp4"
}
```

### Error Responses
- **500:** Failed to save uploaded file

---

## 1.2 Upload Video from URL

**POST** `/api/v1/videos/url`

Downloads a video from a URL and stores it locally.

### Request
```json
{
  "url": "https://tmpfiles.org/12345/video.mp4",
  "filename": "sample.mp4"
}
```

### Response (200 OK)
```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "uploaded",
  "filename": "sample.mp4"
}
```

### Error Responses
- **500:** Failed to download video after 3 attempts

### Implementation Notes
- Retries up to 3 times for flaky hosts
- Validates Content-Type is not HTML (handles tmpfiles.org expired links)
- Rejects files smaller than 10KB (likely error pages)

---

# 2. Video Status

## 2.1 Get Video Status

**GET** `/api/v1/videos/{id}`

Retrieves the processing status and logs for a video.

### Response (200 OK)
```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "sample.mp4",
  "status": "completed",
  "logs": [
    "Video uploaded successfully",
    "Started video processing task",
    "Base caption generated: '...'",
    "Captioning pipeline finished successfully"
  ],
  "created_at": "2024-01-15T10:30:00"
}
```

### Error Responses
- **404:** Video record not found

---

# 3. Caption Generation

## 3.1 Generate Captions

**POST** `/api/v1/captions/generate`

Runs the full AI pipeline to generate styled captions for a video.

### Request (Self-Contained Mode)
```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "video_url": "https://tmpfiles.org/12345/video.mp4",
  "styles": ["formal", "sarcastic", "humorous-tech", "humorous-non-tech"]
}
```

### Response (200 OK)
```json
{
  "status": "completed",
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "base_caption": "A person is demonstrating the use of a new software tool...",
  "captions": {
    "formal": {
      "style": "formal",
      "caption": "The subject demonstrates the designated functionality..."
    },
    "sarcastic": {
      "style": "sarcastic",
      "caption": "Behold — in a moment that will surely be studied..."
    },
    "humorous-tech": {
      "style": "humorous-tech",
      "caption": "The user initiated a production deploy..."
    },
    "humorous-non-tech": {
      "style": "humorous-non-tech",
      "caption": "Ah yes, the timeless ritual..."
    }
  },
  "evaluations": {
    "formal": {
      "accuracy_score": 0.95,
      "style_score": 0.90,
      "hallucination_detected": false,
      "hallucinated_words": []
    }
  }
}
```

### Error Responses
- **400:** Video URL returned an HTML page (expired link)
- **404:** Video record not found (legacy mode only)
- **500:** Pipeline execution failed

### Implementation Notes

**Two Modes:**

1. **Self-Contained Mode (Vercel):**
   - Frontend uploads to tmpfiles.org, gets a URL
   - API downloads video fresh from URL
   - No DB lookup needed
   - Returns captions directly

2. **Legacy Mode (Local/Railway):**
   - Frontend called `/videos/url` first
   - API finds record by video_id
   - Runs pipeline on saved file

---

# 4. Caption Retrieval

## 4.1 Get Captions

**GET** `/api/v1/captions/{id}`

Retrieves previously generated captions for a video.

### Response (200 OK)
```json
{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "captions": {
    "formal": "The subject demonstrates...",
    "sarcastic": "Behold — in a moment...",
    "humorous-tech": "The user initiated...",
    "humorous-non-tech": "Ah yes, the timeless..."
  },
  "evaluations": {
    "formal": { ... }
  }
}
```

### Error Responses
- **404:** Video record not found
- **400:** Captions are not ready (status not "completed")

---

# 5. Caption Evaluation

## 5.1 Evaluate Caption

**POST** `/api/v1/evaluations`

Evaluates a caption's quality (hallucination detection, style adherence).

### Request
```json
{
  "caption": "The user initiated a production deploy of their morning routine...",
  "style": "humorous-tech",
  "entities": ["person", "computer", "keyboard"]
}
```

### Response (200 OK)
```json
{
  "caption": "The user initiated a production deploy of their morning routine...",
  "accuracy_score": 0.95,
  "style_score": 0.90,
  "hallucination_detected": false,
  "hallucinated_words": []
}
```

---

# 6. Health Check

## 6.1 Health Check

**GET** `/api/v1/health`

Returns the service health status.

### Response (200 OK)
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

# 7. Configuration

## 7.1 Get Configuration

**GET** `/api/v1/config`

Returns runtime configuration details.

### Response (200 OK)
```json
{
  "project_name": "CaptionForge AI",
  "storage_dir": "/tmp/captionforge_storage",
  "database": "SQLite",
  "primary_vlm": "Qwen2.5-VL (Mock/API)",
  "stylist_model": "Llama-3.3 (Mock/API)"
}
```

---

# Request/Response Schemas

## VideoUploadResponse
```python
class VideoUploadResponse(BaseModel):
    video_id: str
    status: str
    filename: str
```

## VideoUrlUploadRequest
```python
class VideoUrlUploadRequest(BaseModel):
    url: str
    filename: str
```

## CaptionGenerationRequest
```python
class CaptionGenerationRequest(BaseModel):
    video_id: str
    video_url: Optional[str] = None
    styles: List[str] = Field(
        default=["formal", "sarcastic", "humorous-tech", "humorous-non-tech"]
    )
```

## StyleItem
```python
class StyleItem(BaseModel):
    style: str
    caption: Optional[str] = None
    error: Optional[str] = None
```

## CaptionResult
```python
class CaptionResult(BaseModel):
    status: str
    video_id: str
    base_caption: Optional[str] = None
    captions: Dict[str, StyleItem] = {}
    evaluations: Dict[str, Any] = {}
```

## EvaluationRequest
```python
class EvaluationRequest(BaseModel):
    caption: str
    style: str
    entities: List[str]
```

## EvaluationResponse
```python
class EvaluationResponse(BaseModel):
    caption: str
    accuracy_score: float
    style_score: float
    hallucination_detected: bool
    hallucinated_words: List[str]
```

---

# HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid input, expired link |
| 404 | Not Found | Video/caption not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Pipeline failure |
| 503 | Service Unavailable | Model API unavailable |

---

# Error Handling

## Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Common Errors

### Expired tmpfiles.org Link
```json
{
  "detail": "The video URL returned an HTML page — the tmpfiles.org link likely expired. Please re-upload the video."
}
```

### Video Not Found
```json
{
  "detail": "Video record not found and no video_url was provided. The frontend must include video_url in the request body."
}
```

### Pipeline Failure
```json
{
  "detail": "Vision model caption generation failed: API timeout"
}
```

---

# CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

# Rate Limiting

**Competition Mode:** No rate limiting

**Production Mode:** Recommended limits:
- Upload: 20/min
- Generate: 10/min
- Evaluate: 30/min

---

# Final Sign-off

**Status:** ✅ IMPLEMENTATION ALIGNED

This document accurately reflects the current FastAPI implementation in `backend/api_v1/routes.py`.

