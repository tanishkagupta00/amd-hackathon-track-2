# Frontend Architecture

**Project:** CaptionForge AI  
**Document:** 16_Frontend_Architecture.md  
**Version:** 1.0 (Production Blueprint)

---

## 1. Executive Summary
This document specifies the frontend engineering architecture for **CaptionForge AI**, the modular client dashboard developed for Track 2 (Video Captioning Agent) of the AMD Developer Hackathon. The frontend provides a high-performance web interface designed to manage video ingestion uploads, track real-time visual analysis execution states, preview keyframe scene samplings, and showcase evaluation rankings across the four mandatory caption styles: **Formal, Sarcastic, Humorous-Tech, and Humorous-Non-Tech**.

## 2. Technology Stack & Core Layout
The platform's user interface is built as a single-page application (SPA) optimized for low latency and high accessibility.

*   **Core Framework:** React 18.3+ (TypeScript Strict Mode enabled)
*   **Build System:** Vite 5.x (ESBuild compiler configuration)
*   **Styling Engine:** Tailwind CSS 3.4+ & Headless UI components
*   **State Containers:** Zustand 4.5+ (Stateless atomic slices with persistent local storage hydration)
*   **Networking Client:** Axios 1.6+ (Configured with automated retry loops and interceptors)
*   **Iconography:** Lucide React

```text
frontend/
├── public/
├── src/
│   ├── assets/             # Global static media and brand imagery
│   ├── components/         # Shared stateless design-system atomics
│   │   ├── ui/             # Buttons, Inputs, Modals, Dropdowns, Skeletons
│   │   └── common/         # Layout wraps, Error Boundaries, SEO Meta
│   ├── config/             # Environment configurations and endpoint mappings
│   ├── features/           # Domain-driven decoupled business features
│   │   ├── dashboard/      # Overview grids, metric layouts, historical evaluations
│   │   ├── upload/         # Drag-&-Drop zones, chunk validation, upload states
│   │   ├── processor/      # Active pipeline visualizers, weblog streaming panels
│   │   └── results/        # Quad-card caption comparison panels, criticism scores
│   ├── hooks/              # Reusable global hooks
│   ├── services/           # Hardened API Clients and WebSocket drivers
│   ├── store/              # Centralized Zustand atomic global slices
│   ├── styles/             # Tailwind layer modifications and baseline CSS
│   ├── types/              # Unified TypeScript strict type declarations
│   ├── utils/              # Math formatters, timing math, and string parsers
│   ├── App.tsx             # Application initialization layer
│   └── main.tsx            # DOM node injection mount point
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 3. Component Architecture
The interface adheres to an atomic design hierarchy grouped cleanly by bounded context. Components are strictly divided into reusable, presentation-only UI wrappers (`src/components/ui`) and contextual business wrappers (`src/features`).

### 3.1. Standard Core Viewports
1.  **Dashboard Shell:** Hosts global diagnostic status cards, aggregate execution counts, and historical processing run tables.
2.  **Upload Workspace:** Centered around an asynchronous file processing drag-and-drop boundary providing instantaneous local size/type file sanitization.
3.  **Pipeline Progress Screen:** Displays a live, synchronized sequence stepper mapped directly to the active AI backend execution layers.
4.  **Multi-Style Result Matrix:** Renders four modular cards comparing the style target generation matches concurrently alongside their respective semantic validation scores.

## 4. Feature Module Architecture
To maximize decoupling, each primary business domain operates as an isolated package inside `src/features/`. Modules are self-contained, encapsulating their own subset of presentation components, specialized business logic sub-hooks, and analytical widgets.

### 4.1. Ingestion & Upload Module (`src/features/upload`)
*   **Responsibilities:** Enforces strict local validation gatekeeping (Max file length: 120 seconds, format validations: `.mp4`, `.mov`, `.avi`). Orchestrates progressive multi-part upload streaming to `/api/v1/videos`.
*   **Components:** `DragDropZone.tsx`, `UploadProgressTracker.tsx`, `FileValidationBadge.tsx`.

### 4.2. Live Pipeline Monitor (`src/features/processor`)
*   **Responsibilities:** Establish a long-polling or Server-Sent Events (SSE) tracking hook tied to `/api/v1/videos/{id}` status changes. Updates structural states as the backend moves through Preprocessing, Frame Sampling, Scene Segmentation, Temporal Reasoning, and Generation.
*   **Components:** `PipelineStepper.tsx`, `LiveTerminalLog.tsx`, `FramePreviewStrip.tsx`.

### 4.3. Multi-Style Caption Presenter (`src/features/results`)
*   **Responsibilities:** Maps the payload from `/api/v1/captions/{id}` into a comparative split view. Highlights differences in stylistic vocabulary choices across the four required profiles.
*   **Components:** `CaptionDisplayCard.tsx`, `CriticMetricGauge.tsx`, `ClipboardExportButton.tsx`.

## 5. API Client Layer & Networking Protocol
The HTTP client layer built via Axios features default structural setups tuned specifically for high-volume video processing workloads.

```typescript
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status >= 500 && originalRequest.method === 'get' && !originalRequest._retryCount) {
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

## 6. State Management Patterns
Global states are minimized using Zustand to prevent unnecessary context re-renders. Component-specific presentation layouts rely strictly on native local React hooks.

```typescript
import { create } from 'zustand';

interface VideoProcessState {
  currentVideoId: string | null;
  processingStage: 'idle' | 'preprocessor' | 'sampling' | 'reasoning' | 'generating' | 'completed' | 'failed';
  currentLogs: string[];
  captions: Record<string, string> | null;
  setVideoId: (id: string) => void;
  updateStage: (stage: VideoProcessState['processingStage']) => void;
  appendLog: (log: string) => void;
  setCaptions: (captions: Record<string, string>) => void;
  resetProcessor: () => void;
}

export const useCaptionStore = create<VideoProcessState>((set) => ({
  currentVideoId: null,
  processingStage: 'idle',
  currentLogs: [],
  captions: null,
  setVideoId: (id) => set({ currentVideoId: id, processingStage: 'preprocessor', currentLogs: [] }),
  updateStage: (stage) => set({ processingStage: stage }),
  appendLog: (log) => set((state) => ({ currentLogs: [...state.currentLogs, log] })),
  setCaptions: (captions) => set({ captions, processingStage: 'completed' }),
  resetProcessor: () => set({ currentVideoId: null, processingStage: 'idle', currentLogs: [], captions: null }),
}));
```

## 7. Design System & Component Token Matrix
The visual wrapper leverages Tailwind CSS configured via design tokens matching WCAG 2.1 AA accessibility guidelines.

### 7.1. Color Palette Variable Tokens
*   **Brand Primary (Executive Slate):** `#1E293B` (`bg-slate-800`)
*   **Brand Accent (AMD Orange Highlight):** `#EA580C` (`text-orange-600`)
*   **Interface Baseline Background:** `#F8FAFC` (`bg-slate-50`)
*   **Container Card Background:** `#FFFFFF` (`bg-white`)
*   **Status Indicators - Success State:** `#16A34A` (`text-green-600`)
*   **Status Indicators - Error Alert State:** `#DC2626` (`text-red-600`)

### 7.2. Typography Guidelines
*   **Primary System Typography Stack:** Inter, system-ui, sans-serif.
*   **Header Type Weighting:** Bold (`font-bold`, `tracking-tight`), slate color text matching the primary brand layer.
*   **Code Terminals / System Outputs:** Source Code Pro / Fira Code (`font-mono`), light-grey text variants on pure pitch-black base rows.

## 8. Performance Optimization Framework
1.  **Asset Segmentation & Code Splitting:** Large feature layout modules are loaded asynchronously using standard dynamic routing strategies.
2.  **Virtualized Execution Logging Viewports:** Terminal log tracking arrays use windowing optimizations to ensure that systems pushing thousands of debug items only render visible screen slices.
3.  **Active Asset Ingestion Throttling:** Button export arrays and upload triggers implement aggressive debouncing and lock conditions.

## 9. Accessibility & Error Hardening (Resilience Blueprint)
### 9.1. Global Component Exception Interception
A root-level **Error Boundary** encapsulates the routing wrapper. If an unexpected runtime exception breaks a component, the user's workflow is preserved via a fall-back diagnostic state layout rather than crashing the browser.

```typescript
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props { children: ReactNode; }
interface State { hasError: boolean; error: Error | null; }

export class ErrorBoundary extends Component<Props, State> {
  public state: State = { hasError: false, error: null };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Unhandled UI Exception Intercepted:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="p-8 max-w-lg mx-auto mt-20 bg-red-50 border border-red-200 rounded-xl text-center">
          <h2 className="text-xl font-bold text-red-800 mb-2">Something went wrong in the interface.</h2>
          <p className="text-sm text-red-600 mb-4">{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()} className="px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition">
            Reload Application Interface
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

### 9.2. Loading & Skeleton UI Strategy
Blank spaces during data fetching are systematically avoided. Every primary dashboard view features matching CSS **Skeleton Layouts** to maintain structural consistency and reduce layout shifts.

## 10. Forms, Validation & Controls Blueprint
System input components leverage **React Hook Form** combined with lightweight custom type schemas.
*   **Video Ingestion Form:** Validates string URL patterns or intercept file handles directly from drag-and-drop triggers.
*   **Style Filtering Checklist:** Enforces strict array-bound configurations before pushing data generation requests, ensuring at least one required style is checked.

## 11. Testing & Verification Matrix
*   **Unit Component Verification:** Executed using **Vitest** + **React Testing Library** to validate standalone utility functions and design component state changes.
*   **Feature Integration Suites:** Validates complex states.
*   **Mock Verification Clients:** Rest endpoints are tracked using a mock environment layer (**MSW - Mock Service Worker**) to simplify UI development during offline testing.

## 12. Security & Scale Engineering
*   **Sanitization Filters:** All text fields, file strings, and live server logs are fully escaped before rendering to prevent Cross-Site Scripting (XSS) injections.
*   **Environment Enforcements:** Global build outputs automatically prune detailed logging arrays, assertion blocks, and source-map structures.
*   **Cross-Origin Protections (CORS):** The client connection pool blocks mixed protocol exceptions, handling API routing through secure HTTPS gateways.

## 13. Final Sign-off
*   **Status:** APPROVED
*   **Implementation Target:** Production Build Release Phase