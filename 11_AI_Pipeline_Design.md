
# AI Pipeline Design

**Project:** CaptionForge AI  
**Document:** 11_AI_Pipeline_Design.md  
**Version:** 2.0 (Implementation Aligned)

---

# Table of Contents

1. Executive Summary
2. AI Objectives
3. AI Design Principles
4. Pipeline Overview
5. Pipeline Architecture
6. Data Contracts
7. Stage Specifications
8. Technology Choices
9. Error Handling & Fallbacks

---

# 1. Executive Summary

CaptionForge AI uses a modular, multi-stage multimodal reasoning pipeline. Instead of a single monolithic Vision-Language Model prompt, the system employs a decoupled **Extract-Reason-Style** architecture where each stage has a single responsibility and communicates through structured data contracts.

**Current Implementation:**
- **Audio Extraction:** imageio-ffmpeg (CPU, runs on Vercel)
- **Transcription:** Whisper-v3 (Fireworks AI on AMD MI300X)
- **Vision Analysis:** Kimi-k2p6 (Fireworks AI on AMD MI300X)
- **Style Generation:** DeepSeek-v4-pro (Fireworks AI on AMD MI300X)
- **Evaluation:** CaptionCritic (local rules-based)

---

# 2. AI Objectives

- ✅ Maximize caption accuracy through structured extraction
- ✅ Generate four required styles (Formal, Sarcastic, Humorous-Tech, Humorous-Non-Tech)
- ✅ Minimize hallucinations via critic validation
- ✅ Preserve temporal context via multi-frame analysis
- ✅ Enable modular model replacement (Fireworks API)
- ✅ Support serverless deployment (no local GPU required)

---

# 3. AI Design Principles

1. **Extract before generating** - Understand the video first
2. **Separate reasoning from styling** - Base caption → Style transformation
3. **Preserve factual consistency** - Critic validates accuracy
4. **Evaluate before returning** - Quality scores included in output
5. **Prefer modular agents** - CaptionGenerator, StyleTransformer, CaptionCritic
6. **Use cloud GPUs** - Fireworks AI on AMD MI300X for compute-heavy tasks

---

# 4. Pipeline Overview

```
Video Input
    ↓
[CaptionGenerator]
    ├─ Extract Audio (FFmpeg)
    ├─ Transcribe (Whisper-v3)
    ├─ Extract Frames (imageio)
    └─ Generate Base Caption (Kimi-k2p6)
    ↓
Base Caption (Factual)
    ↓
[StyleTransformer] (Parallel execution)
    ├─ Formal Style (DeepSeek-v4-pro)
    ├─ Sarcastic Style (DeepSeek-v4-pro)
    ├─ Humorous-Tech Style (DeepSeek-v4-pro)
    └─ Humorous-Non-Tech Style (DeepSeek-v4-pro)
    ↓
[CaptionCritic]
    ├─ Hallucination Detection
    ├─ Style Adherence Scoring
    └─ Accuracy Scoring
    ↓
Final Output (4 styled captions + evaluations)
```

---

# 5. Pipeline Architecture

| Stage | Module | Model/API | Responsibility | Output |
|---|---|---|---|---|
| Audio Extraction | `caption_generator.py` | imageio-ffmpeg | Extract audio track | MP3 file |
| Transcription | `caption_generator.py` | Whisper-v3 (Fireworks) | Speech to text | Transcript string |
| Frame Extraction | `caption_generator.py` | imageio + Pillow | Extract keyframes | 6 base64 JPEGs |
| Vision Analysis | `caption_generator.py` | Kimi-k2p6 (Fireworks) | Understand video | Base caption |
| Style Transformation | `style_transformer.py` | DeepSeek-v4-pro (Fireworks) | Rewrite in styles | 4 styled captions |
| Quality Evaluation | `caption_critic.py` | Local rules engine | Score quality | Evaluation metrics |

---

# 6. Data Contracts

## Input Contract (CaptionGenerationRequest)

```json
{
  "video_id": "uuid-string",
  "video_url": "https://tmpfiles.org/...",
  "styles": ["formal", "sarcastic", "humorous-tech", "humorous-non-tech"]
}
```

## Intermediate Contract (Base Caption)

```json
{
  "base_caption": "A detailed factual description of the video...",
  "transcript": "Speech transcription if audio present..."
}
```

## Output Contract (CaptionResult)

```json
{
  "status": "completed",
  "video_id": "uuid-string",
  "base_caption": "Factual description...",
  "captions": {
    "formal": { "style": "formal", "caption": "..." },
    "sarcastic": { "style": "sarcastic", "caption": "..." },
    "humorous-tech": { "style": "humorous-tech", "caption": "..." },
    "humorous-non-tech": { "style": "humorous-non-tech", "caption": "..." }
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

---

# 7. Stage Specifications

## 7.1 CaptionGenerator (`caption_generator.py`)

**Purpose:** Extract audio, frames, and generate the factual base caption

**Key Functions:**
- `extract_audio_lightweight()` - FFmpeg-based audio extraction
- `extract_keyframes_lightweight()` - imageio-based frame extraction
- `generate_base_caption()` - Orchestrate extraction + Fireworks AI calls
- `clean_kimi_reasoning()` - Strip leaked chain-of-thought from model output

**Audio Processing:**
```python
# Extract audio as MP3 at 16kHz (Whisper optimal)
ffmpeg -y -i video.mp4 -vn -acodec libmp3lame -ar 16000 -q:a 4 audio.mp3
```

**Frame Sampling:**
- Extracts 6 evenly-spaced keyframes
- Resizes to 512x512 to reduce bandwidth
- Encodes as base64 JPEG for API transmission

**Vision Model Call:**
```python
# Uses Kimi-k2p6 for advanced vision understanding
response = client.chat.completions.create(
    model="accounts/fireworks/models/kimi-k2p6",
    messages=[
        {"role": "system", "content": "You are a precise video analysis assistant..."},
        {"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
        ]}
    ],
    max_tokens=10000,
    temperature=0.2
)
```

---

## 7.2 StyleTransformer (`style_transformer.py`)

**Purpose:** Transform the factual base caption into four required styles

**Style Definitions:**

### Formal
```
Write in a formal, objective, third-person documentary register.
Use precise academic or corporate language with passive-voice constructions.
No humor, colloquialisms, slang, exclamation marks, or personal pronouns.
Example: "The subject proceeds to demonstrate the designated functionality..."
```

### Sarcastic
```
Write with biting, theatrical dry sarcasm.
Treat every mundane action as earth-shattering.
Use dramatic overstatement, mock reverence, and ironic understatement.
Example: "Behold — in a moment that will surely be studied by future generations..."
```

### Humorous-Tech
```
Write as a senior software engineer using programming metaphors.
Reference: stack traces, null pointers, merge conflicts, deployment failures, etc.
Example: "The user initiated a live production deploy of their morning routine..."
```

### Humorous-Non-Tech
```
Write warm, relatable, observational everyday comedy.
Reference everyday struggles, relatable tropes, slice-of-life irony.
NO tech or programming references.
Example: "Ah yes, the timeless ritual — doing that one thing we all do..."
```

**Model Selection:**
- Primary: DeepSeek-v4-pro
- Fallback 1: Kimi-k2p6
- Fallback 2: GPT-OSS-120B

---

## 7.3 CaptionCritic (`caption_critic.py`)

**Purpose:** Evaluate captions for hallucinations and style adherence

**Evaluation Dimensions:**

### 1. Hallucination Detection
- Flags tech-only phrases in non-tech styles
- Examples: "merge conflict", "null pointer", "stack overflow"
- **Does NOT flag** everyday tech words: "keyboard", "monitor", "screen"

### 2. Style Adherence Scoring
- **Formal:** Checks for exclamation marks, first-person pronouns
- **Sarcastic:** Looks for irony markers (behold, wow, truly, etc.)
- **Humorous-Tech:** Verifies computing jargon density
- **Humorous-Non-Tech:** Penalizes dev-only compound phrases

### 3. Accuracy Scoring
- Base score: 1.0
- Deduction: -0.1 per hallucinated phrase
- Floor: 0.5 (even poor captions stay above this)

**Example Evaluation:**
```python
{
    "caption": "The user initiated a production deploy...",
    "accuracy_score": 0.95,
    "style_score": 0.90,
    "hallucination_detected": false,
    "hallucinated_words": [],
    "style_reasons": []
}
```

---

## 7.4 LLMService (`llm_service.py`)

**Purpose:** Abstraction layer for LLM API calls with fallback chain

**Fallback Strategy:**
1. Try DeepSeek-v4-pro (primary)
2. If rate-limited (429) → Try Kimi-k2p6
3. If rate-limited → Try GPT-OSS-120B
4. If all fail → Raise exception with actionable message

**Error Handling:**
- Detects rate limits (429) and unavailable models (404)
- Skips to next model on transient errors
- Raises immediately on non-transient errors

---

# 8. Technology Choices

## Why Fireworks AI?

| Factor | Fireworks AI | Alternative (Local) |
|--------|--------------|---------------------|
| GPU Requirement | None (cloud) | AMD MI300X required |
| Deployment | Serverless-ready | Docker with ROCm |
| Latency | Low (AMD MI300X) | Depends on hardware |
| Cost | Pay-per-token | Free (if you have hardware) |

## Model Selection Rationale

| Model | Why Chosen |
|-------|------------|
| **Whisper-v3** | Best-in-class speech recognition, optimized for 16kHz audio |
| **Kimi-k2p6** | Advanced vision understanding, handles multiple frames |
| **DeepSeek-v4-pro** | Excellent style adherence, high vocabulary range |

---

# 9. Error Handling & Fallbacks

## Model Fallback Chain

```python
models_to_try = [
    "accounts/fireworks/models/deepseek-v4-pro",   # Primary
    "accounts/fireworks/models/kimi-k2p6",          # Fallback 1
    "accounts/fireworks/models/gpt-oss-120b",       # Fallback 2
]
```

## Graceful Degradation

- **No audio detected:** Skip transcription, proceed with vision only
- **Frame extraction fails:** Raise HTTPException with clear message
- **Vision model fails:** Raise exception with actionable guidance
- **Style generation fails:** Return error message in caption field

## Reasoning Cleanup

Models like Kimi and DeepSeek sometimes prepend chain-of-thought reasoning:
- `clean_kimi_reasoning()` strips leaked monologue
- `_strip_reasoning()` removes planning indicators
- Final output is always clean caption text

---

## Iteration Status

✅ Executive Summary - Updated with actual implementation  
✅ AI Objectives - Verified against code  
✅ Pipeline Architecture - Reflects actual stages  
✅ Data Contracts - Matches Pydantic schemas  
✅ Stage Specifications - Documents actual code  
✅ Technology Choices - Explains Fireworks AI usage  
✅ Error Handling - Documents fallback chain  

**Status:** ✅ IMPLEMENTATION ALIGNED

