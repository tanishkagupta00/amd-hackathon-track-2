// Central API base URL config.
// Set VITE_API_BASE_URL in Vercel env vars to point to your backend.
// e.g. https://abc123.ngrok-free.app  OR  https://your-backend.railway.app
// When running locally with the backend on the same server, leave it empty.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export default API_BASE_URL;
