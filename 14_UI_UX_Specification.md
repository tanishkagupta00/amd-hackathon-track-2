
# UI/UX Specification

**Project:** CaptionForge AI  
**Document:** 14_UI_UX_Specification.md  
**Version:** 2.0 (Implementation Aligned)

---

# 1. Executive Summary

CaptionForge AI provides a modern, responsive web interface built with React and TypeScript. The UI enables users to upload videos, track processing progress in real-time, and view generated captions in four distinct styles.

**Technology Stack:**
- React 18.3+ with TypeScript
- Vite 5.x build system
- Tailwind CSS 3.4+ for styling
- Zustand for state management
- Axios for HTTP requests

---

# 2. Design Goals

- ✅ Minimal learning curve
- ✅ Fast, intuitive video upload
- ✅ Clear AI processing feedback
- ✅ Professional dashboard aesthetic
- ✅ Responsive across devices
- ✅ Accessible components (WCAG 2.1 AA)

---

# 3. Target Users

- **AMD Hackathon Judges** - Evaluate system capabilities
- **Developers** - Test API integration
- **Content Creators** - Generate styled captions
- **Researchers** - Analyze AI behavior

---

# 4. Application Structure

## 4.1 Route Structure

```typescript
// frontend/src/App.tsx
<Routes>
  <Route path="/" element={<Home />} />
  <Route path="/app" element={<Workspace />} />
</Routes>
```

## 4.2 Page Components

| Page | Route | Purpose |
|------|-------|---------|
| Home | `/` | Landing page with hero, features, CTA |
| Workspace | `/app` | Main video upload and caption viewing |

---

# 5. User Flow

```
Landing Page (Home)
    ↓ [Click "Get Started"]
Workspace (/app)
    ↓ [Drag & Drop Video]
Upload Processing
    ↓ [API: POST /videos or /videos/url]
Caption Generation
    ↓ [API: POST /captions/generate]
Results Display
    ↓ [View 4 styled captions]
Copy/Export
```

---

# 6. Component Architecture

## 6.1 Home Page

**Location:** `frontend/src/pages/Home.tsx`

**Sections:**
- Hero section with animated particle orb
- Feature highlights
- Call-to-action buttons
- Footer

**Key Features:**
- Animated CaptionOrbDemo component
- Smooth scroll to workspace
- Responsive hero layout

---

## 6.2 Workspace Page

**Location:** `frontend/src/pages/Workspace.tsx`

**Sections:**
- Header with branding
- Drag & drop upload zone
- Processing status indicator
- Four-card caption display
- Copy/export buttons

**Key Features:**
- Real-time progress tracking
- Visual feedback during processing
- Styled caption comparison cards

---

## 6.3 Drag & Drop Component

**Location:** `frontend/src/components/DragDrop.tsx`

**Functionality:**
- Accepts video files (MP4, MOV, AVI)
- Validates file size and format
- Shows upload progress
- Emits file for parent processing

**Implementation:**
```typescript
const handleDrop = useCallback((e: React.DragEvent) => {
  e.preventDefault();
  const file = e.dataTransfer.files[0];
  // Validate and emit
}, []);
```

---

## 6.4 Caption Orb Demo

**Location:** `frontend/src/components/CaptionOrbDemo.jsx`

**Purpose:** Animated particle visualization on landing page

**Features:**
- Canvas-based particle system
- Mouse interaction
- Smooth animations
- Performance optimized

---

# 7. API Integration

## 7.1 API Configuration

**Location:** `frontend/src/apiConfig.ts`

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL 
  || 'http://localhost:8000/api/v1';

export const uploadVideo = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_BASE_URL}/videos`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};
```

## 7.2 Caption Generation Flow

```typescript
// 1. Upload video to tmpfiles.org (or directly to backend)
const videoId = await uploadVideo(file);

// 2. Request caption generation
const result = await axios.post(`${API_BASE_URL}/captions/generate`, {
  video_id: videoId,
  video_url: videoUrl,  // For serverless mode
  styles: ['formal', 'sarcastic', 'humorous-tech', 'humorous-non-tech']
});

// 3. Display results
setCaptions(result.data.captions);
setEvaluations(result.data.evaluations);
```

---

# 8. State Management

## 8.1 Zustand Store (Recommended)

```typescript
// frontend/src/store/useCaptionStore.ts
import { create } from 'zustand';

interface CaptionState {
  currentVideoId: string | null;
  processingStage: 'idle' | 'uploading' | 'analyzing' | 'generating' | 'completed' | 'failed';
  captions: Record<string, string> | null;
  evaluations: Record<string, any> | null;
  
  setVideoId: (id: string) => void;
  updateStage: (stage: string) => void;
  setCaptions: (captions: Record<string, string>) => void;
  reset: () => void;
}

export const useCaptionStore = create<CaptionState>((set) => ({
  currentVideoId: null,
  processingStage: 'idle',
  captions: null,
  evaluations: null,
  
  setVideoId: (id) => set({ currentVideoId: id, processingStage: 'uploading' }),
  updateStage: (stage) => set({ processingStage: stage }),
  setCaptions: (captions) => set({ captions, processingStage: 'completed' }),
  reset: () => set({ currentVideoId: null, processingStage: 'idle', captions: null })
}));
```

---

# 9. Styling Guidelines

## 9.1 Color Palette

| Token | Color | Usage |
|-------|-------|-------|
| `bg-slate-800` | #1E293B | Primary background |
| `text-orange-600` | #EA580C | Accent color (AMD brand) |
| `bg-slate-50` | #F8FAFC | Interface baseline |
| `bg-white` | #FFFFFF | Card backgrounds |
| `text-green-600` | #16A34A | Success states |
| `text-red-600` | #DC2626 | Error states |

## 9.2 Typography

| Element | Style | Font |
|---------|-------|------|
| Headings | Bold, tracking-tight | Inter, sans-serif |
| Body | Regular | Inter, sans-serif |
| Code/Terminal | Monospace | Source Code Pro |

## 9.3 Spacing

- Standard padding: `p-4` (1rem)
- Card gaps: `gap-6` (1.5rem)
- Section margins: `my-12` (3rem)

---

# 10. Responsive Breakpoints

| Breakpoint | Width | Columns |
|------------|-------|---------|
| Mobile | <640px | 1 column |
| Tablet | 640-1024px | 2 columns |
| Desktop | >1024px | 4 columns (caption cards) |

---

# 11. Accessibility

## 11.1 WCAG 2.1 AA Compliance

- ✅ Keyboard navigation support
- ✅ Screen reader labels (aria-*)
- ✅ High contrast text (4.5:1 minimum)
- ✅ Focus indicators
- ✅ Semantic HTML structure

## 11.2 Implementation

```tsx
<button
  aria-label="Upload video file"
  className="focus:ring-2 focus:ring-orange-500"
>
  <UploadIcon />
</button>
```

---

# 12. Loading States

## 12.1 Skeleton UI

```tsx
// Placeholder during data loading
<div className="animate-pulse">
  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
</div>
```

## 12.2 Progress Indicators

- **Upload progress:** Linear progress bar
- **Processing:** Animated spinner with stage text
- **Generation:** Pulsing skeleton

---

# 13. Error Handling UI

## 13.1 Error Boundary

```tsx
export class ErrorBoundary extends Component<Props, State> {
  public static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 max-w-lg mx-auto mt-20 bg-red-50 border border-red-200 rounded-xl text-center">
          <h2 className="text-xl font-bold text-red-800 mb-2">Something went wrong</h2>
          <p className="text-sm text-red-600 mb-4">{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()} className="px-4 py-2 bg-red-600 text-white rounded-lg">
            Reload Application
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

## 13.2 Error Messages

| Scenario | User Message |
|----------|--------------|
| Upload failed | "Failed to upload video. Please try again." |
| Expired link | "Video link expired. Please re-upload." |
| Processing error | "Processing failed. Check file format and try again." |
| Network error | "Network error. Check your connection." |

---

# 14. Performance Optimization

## 14.1 Code Splitting

```typescript
// Lazy load workspace
const Workspace = lazy(() => import('./pages/Workspace'));
```

## 14.2 Image Optimization

- Use WebP format where supported
- Lazy load images below fold
- Compress uploaded video previews

## 14.3 Bundle Optimization

- Tree shaking via Vite
- Dynamic imports for large components
- Minimize third-party dependencies

---

# 15. Final Sign-off

**Status:** ✅ IMPLEMENTATION ALIGNED

This document reflects the current React + TypeScript + Vite implementation in the frontend directory.

---

## Next Iteration (Future)

- Add dark mode support
- Implement video preview playback
- Add caption editing capability
- Export captions as SRT/VTT
- User preference persistence

