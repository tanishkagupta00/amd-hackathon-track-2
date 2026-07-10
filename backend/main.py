import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from core.config import settings
from api.routes import router as api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production configure origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import HTMLResponse

# Include APIs
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve frontend build folder if it exists
frontend_dist_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "../frontend/dist"))
print(f"DEBUG CAPTIONFORGE: frontend_dist_path={frontend_dist_path}, exists={os.path.exists(frontend_dist_path)}")

if os.path.exists(frontend_dist_path):
    app.mount("/", StaticFiles(directory=frontend_dist_path, html=True), name="frontend")
else:
    @app.get("/", response_class=HTMLResponse)
    def root():
        template_path = os.path.join(os.path.dirname(__file__), "templates/index.html")
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        return """
        <html>
            <body style="font-family: sans-serif; padding: 50px; text-align: center; background: #f8fafc;">
                <h1>Welcome to CaptionForge AI API Gateway</h1>
                <p>Swagger docs: <a href="/docs">/docs</a></p>
            </body>
        </html>
        """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
