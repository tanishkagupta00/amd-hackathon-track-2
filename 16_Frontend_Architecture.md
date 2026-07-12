
# Frontend Architecture

**Project:** CaptionForge AI  
**Document:** 16_Frontend_Architecture.md  
**Version:** 2.0 (Implementation Aligned)

---

## 1. Executive Summary

CaptionForge AI provides a modern web interface built with React 18 and TypeScript. The frontend enables users to upload videos, track processing progress, and view generated captions across four distinct styles.

**Current Implementation:**
- **Framework:** React 18.3+ with TypeScript (strict mode)
- **Build Tool:** Vite 5.x
- **Styling:** Tailwind CSS 3.4+
- **State Management:** Component state (Zustand recommended for production)
- **HTTP Client:** Axios

---

## 2. Technology Stack

| Category | Technology | Version |
|----------|-----------|---------|
| Framework | React | 18.3+ |
| Language | TypeScript | Strict mode |
| Build System | Vite | 5.x |
| Styling | Tailwind CSS | 3.4+ |
| Routing | React Router | 6.x |
| HTTP Client | Axios | 1.6+ |
| Icons | Lucide React | Latest |

---

## 3. Project Structure

```
frontend/
├── public/
│   └── favicon.svg            # App icon
│
├── src/
│   ├── App.tsx                # Main routing component
│   ├── main.tsx               # DOM entry point
│   ├── apiConfig.ts           # API base URL configuration
│   │
│   ├── pages/
│   │   ├── Home.tsx           # Landing page
│   │   └── Workspace.tsx      # Main workspace
│   │
│   └── components/
│       ├── DragDrop.tsx       # File upload component
│       └── CaptionOrbDemo.jsx  # Animated particle system
│
├── index.html                 # HTML template
├── package.json               # Dependencies
├── tsconfig.json              # TypeScript config
├── vite.config.ts             # Vite config
├── postcss.config.js          # PostCSS config
└── tailwind.config.js         # Tailwind config
```

---

## 4. Component Architecture

### 4.1 App Component (`App.tsx`)

```tsx
import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Workspace from './pages/Workspace';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/app" element={<Workspace />} />
    </Routes>
  );
}
```

### 4.2 Page Components

| Component | Path | Purpose |
|-----------|------|---------|
| `Home` | `/` | Landing page with hero, features, CTA |
| `Workspace` | `/app` | Upload, process, view captions |

---

## 5. Core Components

### 5.1 DragDrop Component

**Location:** `src/components/DragDrop.tsx`

**Purpose:** Handle video file upload via drag & drop

**Features:**
- Drag & drop zone with visual feedback
- File validation (format, size)
- Upload progress indication
- Emits file to parent component

**Implementation:**
```tsx
interface DragDropProps {
  onFileSelect: (file: File) => void;
  acceptedFormats?: string[];
  maxSize?: number;
}

const DragDrop: React.FC<DragDropProps> = ({ 
  onFileSelect,
  acceptedFormats = ['.mp4', '.mov', '.avi'],
  maxSize = 500 * 1024 * 1024  // 500MB
}) => {
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    
    // Validate format and size
    if (validateFile(file, acceptedFormats, maxSize)) {
      onFileSelect(file);
    }
  }, [onFileSelect]);
  
  return (
    <div 
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      className="border-2 border-dashed border-slate-300 rounded-xl p-12"
    >
      <UploadIcon className="w-16 h-16 mx-auto text-slate-400" />
      <p className="text-center mt-4">Drag & drop your video here</p>
    </div>
  );
};
```

---

### 5.2 CaptionOrbDemo Component

**Location:** `src/components/CaptionOrbDemo.jsx`

**Purpose:** Animated particle system for landing page hero

**Features:**
- Canvas-based particle animation
- Mouse interaction
- Smooth transitions
- Performance optimized

---

## 6. API Integration

### 6.1 API Configuration (`apiConfig.ts`)

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL 
  || 'http://localhost:8000/api/v1';

export default API_BASE_URL;
```

### 6.2 API Client Setup

```typescript
import axios from 'axios';
import API_BASE_URL from './apiConfig';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,  // 2 minutes for video processing
  headers: {
    'Content-Type': 'application/json',
  }
});

// Retry logic for serverless cold starts
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status >= 500 && !originalRequest._retryCount) {
      originalRequest._retryCount = originalRequest._retryCount || 0;
      if (originalRequest._retryCount < 3) {
        originalRequest._retryCount++;
        return apiClient(originalRequest);
      }
    }
    return Promise.reject(error);
  }
);
```

### 6.3 API Functions

```typescript
// Upload video file
export const uploadVideo = async (file: File): Promise<VideoUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/videos', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

// Upload from URL
export const uploadVideoFromUrl = async (url: string, filename: string) => {
  const response = await apiClient.post('/videos/url', { url, filename });
  return response.data;
};

// Generate captions
export const generateCaptions = async (
  videoId: string, 
  videoUrl: string
): Promise<CaptionResult> => {
  const response = await apiClient.post('/captions/generate', {
    video_id: videoId,
    video_url: videoUrl,
    styles: ['formal', 'sarcastic', 'humorous-tech', 'humorous-non-tech']
  });
  return response.data;
};
```

---

## 7. State Management

### 7.1 Current Approach (Component State)

For the hackathon, state is managed within components:

```tsx
const Workspace: React.FC = () => {
  const [video, setVideo] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'processing' | 'completed'>('idle');
  const [captions, setCaptions] = useState<Captions | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const handleUpload = async (file: File) => {
    setStatus('uploading');
    // Upload and process...
  };
  
  return (
    <div>
      {/* Render based on status */}
    </div>
  );
};
```

### 7.2 Recommended Approach (Zustand)

For production, use Zustand for global state:

```typescript
// src/store/useCaptionStore.ts
import { create } from 'zustand';

interface CaptionState {
  currentVideoId: string | null;
  processingStage: ProcessingStage;
  captions: Record<string, string> | null;
  evaluations: Record<string, Evaluation> | null;
  error: string | null;
  
  setVideoId: (id: string) => void;
  updateStage: (stage: ProcessingStage) => void;
  setCaptions: (captions: Record<string, string>) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useCaptionStore = create<CaptionState>((set) => ({
  currentVideoId: null,
  processingStage: 'idle',
  captions: null,
  evaluations: null,
  error: null,
  
  setVideoId: (id) => set({ currentVideoId: id, processingStage: 'uploading' }),
  updateStage: (stage) => set({ processingStage: stage }),
  setCaptions: (captions) => set({ captions, processingStage: 'completed' }),
  setError: (error) => set({ error }),
  reset: () => set({ 
    currentVideoId: null, 
    processingStage: 'idle', 
    captions: null, 
    evaluations: null, 
    error: null 
  })
}));
```

---

## 8. Design System

### 8.1 Color Tokens

| Token | Tailwind Class | Color | Usage |
|-------|---------------|-------|-------|
| Primary | `bg-slate-800` | #1E293B | Primary background |
| Accent | `text-orange-600` | #EA580C | Highlights, buttons |
| Surface | `bg-white` | #FFFFFF | Cards, inputs |
| Background | `bg-slate-50` | #F8FAFC | Page background |
| Success | `text-green-600` | #16A34A | Success messages |
| Error | `text-red-600` | #DC2626 | Error messages |

### 8.2 Typography

| Element | Classes |
|---------|---------|
| H1 | `text-4xl font-bold tracking-tight text-slate-800` |
| H2 | `text-2xl font-semibold text-slate-700` |
| Body | `text-base text-slate-600` |
| Caption | `text-sm text-slate-500` |

### 8.3 Spacing Scale

| Size | Tailwind | Pixels |
|------|----------|--------|
| xs | `p-1` | 4px |
| sm | `p-2` | 8px |
| md | `p-4` | 16px |
| lg | `p-6` | 24px |
| xl | `p-8` | 32px |

---

## 9. Performance Optimization

### 9.1 Code Splitting

```tsx
import { lazy, Suspense } from 'react';

const Workspace = lazy(() => import('./pages/Workspace'));

export default function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/app" element={<Workspace />} />
      </Routes>
    </Suspense>
  );
}
```

### 9.2 Bundle Optimization

- Vite's automatic tree shaking
- Dynamic imports for large components
- Minimal third-party dependencies

---

## 10. Error Handling

### 10.1 Error Boundary

```tsx
import { Component, ErrorInfo, ReactNode } from 'react';

interface Props { children: ReactNode; }
interface State { hasError: boolean; error: Error | null; }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("UI Error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 max-w-lg mx-auto mt-20 bg-red-50 border border-red-200 rounded-xl text-center">
          <h2 className="text-xl font-bold text-red-800">Something went wrong</h2>
          <p className="text-sm text-red-600 mt-2">{this.state.error?.message}</p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg"
          >
            Reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

### 10.2 API Error Handling

```tsx
const handleGenerateCaptions = async () => {
  try {
    setStatus('processing');
    const result = await generateCaptions(videoId, videoUrl);
    setCaptions(result.captions);
    setStatus('completed');
  } catch (error) {
    if (axios.isAxiosError(error)) {
      setError(error.response?.data?.detail || 'An error occurred');
    } else {
      setError('An unexpected error occurred');
    }
    setStatus('error');
  }
};
```

---

## 11. Accessibility

### 11.1 ARIA Labels

```tsx
<button aria-label="Upload video file" onClick={handleUpload}>
  <UploadIcon />
</button>

<div role="status" aria-live="polite">
  {status === 'processing' && 'Generating captions...'}
</div>
```

### 11.2 Keyboard Navigation

- All interactive elements are focusable
- Focus indicators visible (`focus:ring-2`)
- Logical tab order

---

## 12. Build & Deployment

### 12.1 Development

```bash
npm run dev
# Starts Vite dev server at http://localhost:5173
```

### 12.2 Production Build

```bash
npm run build
# Outputs to dist/ folder
```

### 12.3 Deployment

Built assets are served by FastAPI backend:

```python
# backend/main.py
frontend_dist_path = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(frontend_dist_path):
    app.mount("/", StaticFiles(directory=frontend_dist_path, html=True))
```

---

## 13. Final Sign-off

**Status:** ✅ IMPLEMENTATION ALIGNED

This document reflects the current React + TypeScript + Vite implementation.

---

## Next Iteration (Future)

- Implement Zustand store
- Add dark mode toggle
- Add video preview playback
- Add caption editing
- Export captions as SRT/VTT
- Add user preferences persistence

