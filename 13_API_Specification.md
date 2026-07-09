
# API Specification

**Project:** CaptionForge AI
**Document:** 13_API_Specification.md
**Version:** 1.0 (Iteration 1 + 2)

---

# Executive Summary

CaptionForge AI exposes a RESTful API built with FastAPI for video upload, caption generation, evaluation, and system monitoring.

## Design Principles

- RESTful
- Stateless
- Versioned (/api/v1)
- JSON-first
- OpenAPI compatible

## Base URLs

Development:
`http://localhost:8000/api/v1`

Production:
`https://api.captionforge.ai/v1`

---

# Authentication

Competition Mode:
- No authentication

Production Mode:
- JWT Bearer Tokens

---

# Request Lifecycle

Client → API → AI Pipeline → JSON Export → Client

---

# Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /videos | Upload video |
| GET | /videos/{id} | Video metadata |
| POST | /captions/generate | Generate captions |
| GET | /captions/{id} | Retrieve captions |
| POST | /evaluations | Evaluate captions |
| GET | /health | Health check |
| GET | /config | Runtime configuration |

---

# Video Upload

POST /api/v1/videos

Request

```json
{"filename":"sample.mp4"}
```

Response

```json
{"video_id":"uuid","status":"uploaded"}
```

---

# Caption Generation

POST /api/v1/captions/generate

```json
{
 "video_id":"uuid",
 "styles":["formal","sarcastic","humorous-tech","humorous-non-tech"]
}
```

---

# Evaluation API

POST /api/v1/evaluations

Returns quality metrics including accuracy, fluency, style and hallucination score.

---

# Health API

GET /api/v1/health

```json
{"status":"healthy","version":"1.0.0"}
```

---

# Configuration API

GET /api/v1/config

Returns active model, prompt version and runtime limits.

---

# Request Schemas

- VideoUploadRequest
- CaptionGenerationRequest
- EvaluationRequest

# Response Schemas

- CaptionResponse
- ErrorResponse

---

# HTTP Status Codes

200, 201, 202, 400, 401, 403, 404, 409, 422, 429, 500, 503

---

# Validation Rules

- Supported formats: MP4, MOV, AVI
- Max duration: 60 seconds
- Valid video_id required
- Supported styles only

---

# Rate Limiting

Competition:
- None

Production:
- Upload: 20/min
- Generate: 10/min
- Evaluate: 30/min

---

# Pagination

Future analytics endpoints:

GET /api/v1/videos?page=1&page_size=20

---

# OpenAPI

Automatic documentation:

- /docs
- /redoc

---

# Security

- HTTPS
- JWT
- CORS
- Input validation
- Sanitization

---

# Next Iteration

- Error catalog
- Idempotency
- Retry strategy
- Async jobs
- Webhooks
- OpenAPI YAML
- Final sign-off
