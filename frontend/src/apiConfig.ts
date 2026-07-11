/// <reference types="vite/client" />

// Central API base URL — set VITE_API_BASE_URL in Vercel environment variables
// to point at your backend (e.g. https://your-backend.railway.app).
// Leave empty when frontend and backend share the same Vercel deployment.
const API_BASE_URL: string = (import.meta as any).env?.VITE_API_BASE_URL ?? '';

export default API_BASE_URL;
