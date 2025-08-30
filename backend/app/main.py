from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import os
from pathlib import Path

from app.config import Config
from app.api.tracking import router as tracking_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize configuration and create directories
config = Config()
config.create_directories()

# Create FastAPI app
app = FastAPI(
    title="Grounded SAM-2 Video Tracking API",
    description="API for object detection and tracking in videos using Grounded DINO and SAM-2",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount static files for serving output videos
if Path(config.OUTPUT_FOLDER).exists():
    app.mount("/static/outputs", StaticFiles(directory=config.OUTPUT_FOLDER), name="outputs")

# Mount frontend static files if available
frontend_path = Path(__file__).parent.parent.parent / "frontend" / "public"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="frontend")

# Include API routers
app.include_router(tracking_router)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    frontend_available = (Path(__file__).parent.parent.parent / "frontend" / "public").exists()
    
    return {
        "message": "Grounded SAM-2 Video Tracking API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "track": "/api/track",
            "status": "/api/status/{task_id}",
            "download": "/api/download/{task_id}",
            "docs": "/api/docs"
        },
        "frontend": {
            "available": frontend_available,
            "url": "/static/simple.html" if frontend_available else None,
            "external_url": "http://localhost:3000/simple.html"
        }
    }

@app.get("/api/info")
async def get_api_info():
    """Get API information and system status"""
    return {
        "api_version": "1.0.0",
        "device": config.DEVICE,
        "max_file_size_mb": config.MAX_FILE_SIZE / (1024 * 1024),
        "supported_formats": list(config.ALLOWED_EXTENSIONS),
        "model_config": {
            "sam2_checkpoint": config.SAM2_CHECKPOINT,
            "grounding_dino_config": config.GROUNDING_DINO_CONFIG,
            "box_threshold": config.BOX_THRESHOLD,
            "text_threshold": config.TEXT_THRESHOLD
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG
    )