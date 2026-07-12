# AMD GPU Worker

This is a lightweight FastAPI microservice that runs on your **AMD GPU Cloud instance** (provided by the AMD Hackathon credits).

It handles all the GPU/compute-heavy video processing that cannot run on Vercel serverless functions.

## What it does

1. Receives a video file from the Vercel backend.
2. Extracts audio using `ffmpeg` (locally on AMD cloud).
3. Extracts keyframes using `OpenCV` (locally on AMD cloud).
4. Calls **Fireworks AI `whisper-v3`** for multilingual audio transcription.
5. Calls **Fireworks AI `kimi-k2p6`** (vision model) with the frames + transcript to generate a detailed, factual base caption.
6. Returns the caption to the Vercel backend.

## Setup on AMD Cloud GPU Instance

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set environment variable

```bash
export FIREWORKS_API_KEY=your_fireworks_api_key_here
```

Or create a `.env` file:

```
FIREWORKS_API_KEY=your_fireworks_api_key_here
```

### 3. Start the worker server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://<your-amd-instance-ip>:8000`.

## Connect to Vercel Backend

Set the `AMD_WORKER_URL` environment variable in your **Vercel project settings**:

```
AMD_WORKER_URL=http://<your-amd-instance-ip>:8000/generate_base_caption
```

> **Note:** Make sure port 8000 is open in your AMD Cloud instance's firewall/security group settings.

## API

### `POST /generate_base_caption`

**Request:** multipart/form-data with a `video` file field.

**Response:**
```json
{
  "caption": "A detailed factual description of the video content..."
}
```
