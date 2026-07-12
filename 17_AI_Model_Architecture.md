
# AI Model Architecture

**Project:** CaptionForge AI  
**Document:** 17_AI_Model_Architecture.md  
**Version:** 2.0 (Implementation Aligned)

---

## 1. Executive Summary

CaptionForge AI uses a decoupled **Extract-Reason-Style** multi-model architecture. Instead of a monolithic end-to-end approach, the system separates:
1. **Extraction** - Audio transcription and visual analysis
2. **Reasoning** - Factual base caption generation
3. **Styling** - Multi-head style transformation

This architecture runs on **AMD MI300X GPUs** via Fireworks AI, enabling serverless deployment on Vercel without local GPU requirements.

---

## 2. Model Selection Matrix

| Component | Model | Provider | Purpose |
|-----------|-------|----------|---------|
| Speech-to-Text | **Whisper-v3** | Fireworks AI | Audio transcription |
| Vision-Language | **Kimi-k2p6** | Fireworks AI | Video understanding |
| Style Generation | **DeepSeek-v4-pro** | Fireworks AI | Caption rewriting |
| Fallback 1 | Kimi-k2p6 | Fireworks AI | Alternative LLM |
| Fallback 2 | GPT-OSS-120B | Fireworks AI | Backup LLM |

---

## 3. Architecture Overview

```
Video Input
    ↓
┌──────────────────────────────────────────────────────────────┐
│                    EXTRACTION LAYER                           │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐   │
│  │ Audio       │  │ Frame        │  │ OpenCV           │   │
│  │ Extraction  │  │ Sampling     │  │ (optional)       │   │
│  │ (FFmpeg)    │  │ (imageio)    │  │                  │   │
│  └──────┬──────┘  └──────┬───────┘  └───────────────────┘   │
│         │                │                                    │
│         ▼                ▼                                    │
│  ┌─────────────┐  ┌──────────────┐                          │
│  │ Whisper-v3  │  │ Base64       │                          │
│  │ (Fireworks) │  │ JPEG Frames  │                          │
│  └──────┬──────┘  └──────┬───────┘                          │
└─────────┼────────────────┼────────────────────────────────────┘
          │                │
          ▼                ▼
┌──────────────────────────────────────────────────────────────┐
│                    REASONING LAYER                            │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ Kimi-k2p6 (Fireworks AI on AMD MI300X)                │   │
│  │                                                        │   │
│  │ Input:                                                │   │
│  │ - 6 keyframes (base64 JPEG)                          │   │
│  │ - Audio transcript (if available)                     │   │
│  │ - Structured prompt for factual description           │   │
│  │                                                        │   │
│  │ Output:                                               │   │
│  │ - Factual base caption (3-4 sentences)               │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                    STYLING LAYER                              │
│                                                               │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────────────┐ │
│  │ Formal    │ │ Sarcastic │ │ Humorous  │ │ Humorous     │ │
│  │ Prompt    │ │ Prompt    │ │ -Tech     │ │ -Non-Tech    │ │
│  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └──────┬───────┘ │
│        │             │             │              │          │
│        └─────────────┴─────────────┴──────────────┘          │
│                            │                                  │
│                            ▼                                  │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ DeepSeek-v4-pro (Fireworks AI)                        │   │
│  │ - 4 parallel calls (one per style)                   │   │
│  │ - Fallback to Kimi-k2p6 if rate-limited              │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                    EVALUATION LAYER                           │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ CaptionCritic (Local Rules Engine)                    │   │
│  │                                                        │   │
│  │ Checks:                                               │   │
│  │ - Hallucination detection                             │   │
│  │ - Style adherence scoring                             │   │
│  │ - Accuracy scoring                                    │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Model Details

### 4.1 Whisper-v3 (Speech-to-Text)

**Purpose:** Transcribe audio from video

**Specifications:**
- **Provider:** Fireworks AI
- **Model:** `whisper-v3`
- **Audio Format:** MP3 at 16kHz
- **Languages:** Multi-language support
- **Latency:** ~1-3 seconds for typical audio

**Usage:**
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=FIREWORKS_API_KEY
)

with open(audio_path, "rb") as af:
    transcription = client.audio.transcriptions.create(
        model="whisper-v3",
        file=af
    )
```

---

### 4.2 Kimi-k2p6 (Vision-Language Model)

**Purpose:** Understand video frames and generate factual description

**Specifications:**
- **Provider:** Fireworks AI
- **Model:** `accounts/fireworks/models/kimi-k2p6`
- **Input:** Up to 6 frames (base64 JPEG) + text prompt
- **Max Tokens:** 10,000
- **Temperature:** 0.2 (low for factual accuracy)
- **Latency:** ~5-15 seconds

**Prompt Structure:**
```
System: You are a precise, factual video analysis assistant.
Output ONLY the final description. No reasoning or headers.

User: Watch this sequence of frames from a video carefully.
Also consider this audio transcript: "{transcript}"

Write a detailed, factual description:
- WHO is in the video
- WHAT specific actions occur
- WHERE it takes place
- HOW events unfold over time

Write 3-4 rich, concrete sentences.
Output ONLY the factual description.
```

**Reasoning Cleanup:**
Some models prepend chain-of-thought reasoning. The `clean_kimi_reasoning()` function removes:
- "The user wants..."
- "Let me analyze..."
- "First frame:", "Second frame:", etc.
- Markdown headers

---

### 4.3 DeepSeek-v4-pro (Style Transformer)

**Purpose:** Rewrite factual caption in required styles

**Specifications:**
- **Provider:** Fireworks AI
- **Model:** `accounts/fireworks/models/deepseek-v4-pro`
- **Max Tokens:** 10,000
- **Temperature:** 0.75 (higher for creative styles)
- **Latency:** ~2-5 seconds per style

**Fallback Chain:**
```python
models_to_try = [
    "accounts/fireworks/models/deepseek-v4-pro",   # Primary
    "accounts/fireworks/models/kimi-k2p6",          # Fallback 1
    "accounts/fireworks/models/gpt-oss-120b",       # Fallback 2
]
```

**Style Prompts:**

| Style | Key Instructions |
|-------|-----------------|
| **Formal** | Objective, third-person, passive voice, no humor |
| **Sarcastic** | Dry irony, mock reverence, dramatic overstatement |
| **Humorous-Tech** | Programming metaphors, DevOps jargon |
| **Humorous-Non-Tech** | Everyday comedy, no tech references |

---

## 5. API Integration

### 5.1 Fireworks AI Client

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=os.environ.get("FIREWORKS_API_KEY")
)
```

### 5.2 Vision Call (Multi-Frame)

```python
messages = [
    {"role": "system", "content": "You are a precise video analysis assistant..."},
    {"role": "user", "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame1}"}},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{frame2}"}},
        # ... up to 6 frames
    ]}
]

response = client.chat.completions.create(
    model="accounts/fireworks/models/kimi-k2p6",
    messages=messages,
    max_tokens=10000,
    temperature=0.2
)
```

### 5.3 Style Generation Call

```python
response = client.chat.completions.create(
    model="accounts/fireworks/models/deepseek-v4-pro",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    max_tokens=10000,
    temperature=0.75
)
```

---

## 6. CaptionCritic (Local Evaluation)

### 6.1 Purpose

Evaluate generated captions for:
1. **Hallucination Detection** - Flag non-existent objects
2. **Style Adherence** - Score how well the style matches
3. **Accuracy Scoring** - Overall quality metric

### 6.2 Hallucination Detection

**Tech-Only Phrases (Flag in non-tech styles):**
```python
TECH_ONLY_PHRASES = [
    "merge conflict", "null pointer", "stack overflow",
    "segmentation fault", "deployment pipeline", "pull request",
    "docker container", "kubernetes", "api endpoint", ...
]
```

**Note:** Everyday words like "keyboard", "monitor", "screen" are NOT flagged.

### 6.3 Style Scoring

| Style | Scoring Criteria |
|-------|-----------------|
| **Formal** | -0.15 for exclamation marks, -0.15 for first-person pronouns |
| **Sarcastic** | -0.2 for missing irony markers (behold, wow, truly) |
| **Humorous-Tech** | -0.3 for no tech references, -0.1 for light references |
| **Humorous-Non-Tech** | -0.2 for tech-only phrases |

---

## 7. Why Fireworks AI?

| Factor | Fireworks AI (AMD MI300X) | Local GPU |
|--------|---------------------------|-----------|
| Hardware | AMD MI300X (cloud) | Requires AMD ROCm |
| Deployment | Serverless-ready | Docker + GPU runtime |
| Cost | Pay-per-token | Free (if hardware available) |
| Latency | Low (optimized inference) | Depends on hardware |
| Availability | Always available | Limited by local resources |

---

## 8. Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Audio extraction | ~1s | Local CPU (FFmpeg) |
| Frame extraction | ~2s | Local CPU (imageio) |
| Whisper transcription | ~1-3s | Fireworks AI |
| Vision analysis | ~5-15s | Fireworks AI (Kimi) |
| Style generation | ~2-5s per style | Fireworks AI (DeepSeek) |
| **Total pipeline** | ~30-45s | End-to-end |

---

## 9. Error Handling

### 9.1 Model Fallback

```python
for model in models_to_try:
    try:
        response = client.chat.completions.create(model=model, ...)
        return response
    except Exception as e:
        if "429" in str(e):  # Rate limit
            continue  # Try next model
        raise  # Non-transient error
```

### 9.2 Graceful Degradation

- **No audio:** Skip transcription, proceed with vision
- **Rate limit:** Fall back to next model
- **API timeout:** Return error with actionable message

---

## 10. Final Sign-off

**Status:** ✅ IMPLEMENTATION ALIGNED

This document accurately reflects the current Fireworks AI integration with Whisper-v3, Kimi-k2p6, and DeepSeek-v4-pro.

---

## Next Iteration (Future)

- Fine-tune style prompts based on evaluation feedback
- Add model versioning support
- Implement caching for repeated requests
- Add A/B testing for prompt variations

