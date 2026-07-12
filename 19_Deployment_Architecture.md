
# Deployment Architecture

**Project:** CaptionForge AI  
**Document:** 19_Deployment_Architecture.md  
**Version:** 2.0 (Implementation Aligned)

---

## 1. Executive Summary

CaptionForge AI supports two deployment modes:
1. **Serverless (Vercel)** - Primary mode for hackathon evaluation
2. **Docker Container** - Alternative mode for local/GPU execution

Both modes use **Fireworks AI on AMD MI300X GPUs** for inference, enabling deployment without local GPU hardware.

---

## 2. Deployment Modes

### 2.1 Serverless (Vercel) - Primary

```
┌─────────────────┐
│   Vercel Edge   │
│                 │
│  ┌───────────┐  │
│  │ Frontend  │  │  React + Vite build
│  │ (Static)  │  │  Served from /dist
│  └───────────┘  │
│                 │
│  ┌───────────┐  │
│  │ Backend   │  │  FastAPI on Vercel Functions
│  │ (Serverless)│ │  api/index.py → backend/main.py
│  └─────┬─────┘  │
└────────┼─────────┘
         │
         ▼
┌─────────────────┐
│  Fireworks AI   │
│  (AMD MI300X)   │
│                 │
│  - Whisper-v3   │
│  - Kimi-k2p6    │
│  - DeepSeek-v4  │
└─────────────────┘
```

**Advantages:**
- Zero infrastructure management
- Auto-scaling
- Global CDN for frontend
- Free tier available

**Limitations:**
- 10-second function timeout (can be increased)
- Ephemeral storage
- No persistent database

### 2.2 Docker Container - Alternative

```
┌──────────────────────────────────┐
│       Docker Container            │
│                                   │
│  ┌─────────────────────────────┐ │
│  │ Python Application          │ │
│  │ - FastAPI backend           │ │
│  │ - SQLite database           │ │
│  │ - File storage              │ │
│  └─────────────────────────────┘ │
│                                   │
│  ┌─────────────────────────────┐ │
│  │ Input/Output Mounts         │ │
│  │ - /input/tasks.json         │ │
│  │ - /output/results.json      │ │
│  └─────────────────────────────┘ │
└───────────────────────────────────┘
```

**Advantages:**
- Full control over environment
- Persistent storage
- Can run on GPU hardware (optional)

**Limitations:**
- Requires container orchestration
- Manual scaling

---

## 3. Serverless Deployment (Vercel)

### 3.1 Project Structure

```
project-root/
├── api/
│   ├── index.py        # Vercel entry point
│   └── requirements.txt
├── backend/
│   ├── main.py         # FastAPI app
│   ├── database.py
│   ├── pipeline/
│   └── ...
├── frontend/
│   ├── dist/           # Build output
│   └── ...
└── vercel.json
```

### 3.2 Vercel Entry Point

```python
# api/index.py
import sys
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add backend to path
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend")
sys.path.insert(0, backend_path)

# Import FastAPI app
from main import app
```

### 3.3 Environment Variables

Set in Vercel dashboard:

| Variable | Value | Required |
|----------|-------|----------|
| `FIREWORKS_API_KEY` | Your Fireworks API key | ✅ Yes |
| `TEMP` | Temp directory path | No (auto) |

### 3.4 Vercel Configuration

```json
{
  "builds": [
    { "src": "api/index.py", "use": "@vercel/python" },
    { "src": "frontend/dist", "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "api/index.py" },
    { "src": "/(.*)", "dest": "frontend/dist/$1" }
  ]
}
```

### 3.5 Deployment Commands

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

---

## 4. Docker Deployment

### 4.1 Dockerfile

```dockerfile
# Multi-stage build
FROM python:3.11-slim AS builder

WORKDIR /build
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsm6 libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY backend/ /app/

# Create directories
RUN mkdir -p /input /output /tmp/captionforge_storage

# Environment
ENV PYTHONUNBUFFERED=1
ENV FIREWORKS_API_KEY=""

# Entrypoint
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
```

### 4.2 Entrypoint Script

```bash
#!/bin/bash

# Verify input exists
if [ ! -f /input/tasks.json ]; then
    echo "ERROR: /input/tasks.json not found"
    exit 1
fi

# Verify API key
if [ -z "$FIREWORKS_API_KEY" ]; then
    echo "ERROR: FIREWORKS_API_KEY not set"
    exit 1
fi

# Run the pipeline
python runner.py

# Verify output
if [ ! -f /output/results.json ]; then
    echo "ERROR: Output not generated"
    exit 1
fi

echo "Pipeline completed successfully"
exit 0
```

### 4.3 Build & Run

```bash
# Build image
docker build -t captionforge-ai .

# Run container
docker run \
    -v /path/to/input:/input \
    -v /path/to/output:/output \
    -e FIREWORKS_API_KEY=your_key \
    captionforge-ai
```

---

## 5. Input/Output Specifications

### 5.1 Input Format (`/input/tasks.json`)

```json
[
    {
        "task_id": "v_test_01",
        "video_path": "https://example.com/video1.mp4"
    },
    {
        "task_id": "v_test_02",
        "video_path": "/videos/sample.mp4"
    }
]
```

### 5.2 Output Format (`/output/results.json`)

```json
{
    "tasks": [
        {
            "task_id": "v_test_01",
            "captions": {
                "formal": "The subject demonstrates...",
                "sarcastic": "Behold, in a moment...",
                "humorous-tech": "The user initiated...",
                "humorous-non-tech": "Ah yes, the timeless..."
            }
        }
    ]
}
```

---

## 6. CI/CD Pipeline

### 6.1 GitHub Actions

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install Frontend Dependencies
        working-directory: frontend
        run: npm ci
      
      - name: Build Frontend
        working-directory: frontend
        run: npm run build
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

### 6.2 Docker Build

```yaml
name: Build Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Build and Push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64
          push: true
          tags: ghcr.io/${{ github.repository }}/captionforge:latest
```

---

## 7. Monitoring & Health Checks

### 7.1 Health Endpoint

```python
@router.get("/health")
def health_check():
    return {"status": "healthy", "version": settings.VERSION}
```

### 7.2 Container Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1
```

### 7.3 Logging

All logs are written to stdout/stderr:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
```

---

## 8. Security Considerations

### 8.1 API Key Protection

```python
# Never log API keys
logger.info(f"Using API key: {API_KEY[:8]}...")

# Use environment variables
FIREWORKS_API_KEY = os.environ.get("FIREWORKS_API_KEY")
if not FIREWORKS_API_KEY:
    raise Exception("FIREWORKS_API_KEY not set")
```

### 8.2 Input Validation

```python
# Validate video file size
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB

if file_size > MAX_VIDEO_SIZE:
    raise HTTPException(400, "Video file too large")
```

### 8.3 CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 9. Scalability

### 9.1 Serverless Scaling

Vercel automatically scales based on demand:
- Auto-scaling to handle traffic spikes
- Global CDN for frontend assets
- Regional compute for API functions

### 9.2 Container Scaling

For Docker deployment:
- Use Kubernetes for orchestration
- Horizontal Pod Autoscaler for scaling
- Load balancer for distribution

---

## 10. Cost Estimation

### 10.1 Vercel Costs

| Tier | Cost | Limits |
|------|------|--------|
| Free | $0 | 100GB bandwidth, 100 functions |
| Pro | $20/mo | 1TB bandwidth, unlimited functions |

### 10.2 Fireworks AI Costs

| Model | Cost per 1M tokens |
|-------|-------------------|
| Whisper-v3 | $0.006/min audio |
| Kimi-k2p6 | $0.20 input, $0.60 output |
| DeepSeek-v4-pro | $0.75 input, $2.10 output |

**Estimated cost per video:** ~$0.05-0.15

---

## 11. Final Sign-off

**Status:** ✅ IMPLEMENTATION ALIGNED

This document reflects the current dual-mode deployment architecture (Vercel serverless + Docker container).

---

## Next Iteration (Production)

- Add rate limiting
- Implement authentication
- Set up monitoring (DataDog/New Relic)
- Add automated backups
- Configure custom domain
- Set up staging environment

