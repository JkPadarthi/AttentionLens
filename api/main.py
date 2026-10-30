"""FastAPI main app for AttentionLens."""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes import models, analyze, intervene

app = FastAPI(
    title="AttentionLens API",
    description="Interactive explainability and debugging framework for vision models",
    version="0.2.0",
)

# CORS for local dev (Vite runs on :5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(models.router, prefix="/api", tags=["models"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(intervene.router, prefix="/api", tags=["intervene"])


# Serve React build in production
FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "dist"

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        """Serve React SPA for any non-API route."""
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("ATTENTIONLENS_HOST", "0.0.0.0")
    port = int(os.environ.get("ATTENTIONLENS_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
