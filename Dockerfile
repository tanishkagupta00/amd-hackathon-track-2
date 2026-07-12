# ─────────────────────────────────────────────────────────────────────────────
# CaptionForge AI — Full-Stack Docker Image (Backend + Frontend)
#
# Design decisions:
#   - Stage 1: Build frontend with Node.js 20 (outputs to frontend/dist/)
#   - Stage 2: Install Python deps
#   - Stage 3: Runtime image with backend + frontend static files
#   - Dual-mode operation:
#       a) Headless CLI: reads /input/tasks.json → writes /output/results.json
#       b) Web server: serves API at /api/v1 and UI at /
#   - All AI compute happens on AMD MI300X via Fireworks AI (no local GPU needed)
#
# Build:
#   docker build -t captionforge-ai:latest .
#
# Run (Headless mode for hackathon evaluation):
#   docker run --rm \
#     -v /path/to/input:/input:ro \
#     -v /path/to/output:/output \
#     -e FIREWORKS_API_KEY=<key> \
#     captionforge-ai:latest
#
# Run (Web server mode for manual demo):
#   docker run -p 8000:8000 \
#     -e FIREWORKS_API_KEY=<key> \
#     captionforge-ai:latest web
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Build Frontend ──────────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /build

# Install dependencies first (cached layer)
COPY frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY frontend/ ./
RUN npm run build
# Output: /build/dist/


# ── Stage 2: Install Python Dependencies ─────────────────────────────────────
FROM python:3.11-slim AS backend-builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc g++ libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# ── Stage 3: Lean Runtime Image ──────────────────────────────────────────────
FROM python:3.11-slim

# ffmpeg required for audio/frame extraction
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages
COPY --from=backend-builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

WORKDIR /app

# Copy backend code
COPY backend/ /app/backend/

# Copy frontend build from Stage 1
COPY --from=frontend-builder /build/dist /app/frontend/dist

# Copy entrypoint
COPY entrypoint.sh /app/entrypoint.sh

# Pre-create I/O directories
RUN mkdir -p /input /output /tmp/captionforge_storage

ENV PYTHONUNBUFFERED=1
ENV FIREWORKS_API_KEY=""

RUN chmod +x /app/entrypoint.sh

# Expose port 8000 for web mode
EXPOSE 8000

# Default: headless CLI mode (for hackathon evaluation)
# Override with "web" argument to start web server
ENTRYPOINT ["/app/entrypoint.sh"]
CMD []
