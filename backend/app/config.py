import os
import torch
from pathlib import Path

class Config:
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Model Configuration - Use environment variables or auto-detect paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    GROUNDED_SAM2_PATH = PROJECT_ROOT / "Grounded-SAM-2"
    
    # Try to find the correct Grounding DINO config path
    grounding_config_candidates = [
        os.getenv("GROUNDING_DINO_CONFIG"),  # Explicit environment variable
        str(GROUNDED_SAM2_PATH / "grounding_dino" / "groundingdino" / "config" / "GroundingDINO_SwinT_OGC.py"),
        os.path.join(os.getcwd(), "grounding_dino", "groundingdino", "config", "GroundingDINO_SwinT_OGC.py"),  # Relative to current dir
        str(PROJECT_ROOT / "Grounded-SAM-2" / "grounding_dino" / "groundingdino" / "config" / "GroundingDINO_SwinT_OGC.py")  # Fallback to our project
    ]
    
    GROUNDING_DINO_CONFIG = None
    for candidate in grounding_config_candidates:
        if candidate and os.path.exists(candidate):
            GROUNDING_DINO_CONFIG = candidate
            break
    
    if not GROUNDING_DINO_CONFIG:
        GROUNDING_DINO_CONFIG = grounding_config_candidates[-1]  # Use fallback
    
    GROUNDING_DINO_CHECKPOINT = os.getenv("GROUNDING_DINO_CHECKPOINT", "gdino_checkpoints/groundingdino_swint_ogc.pth")
    BOX_THRESHOLD = float(os.getenv("BOX_THRESHOLD", 0.35))
    TEXT_THRESHOLD = float(os.getenv("TEXT_THRESHOLD", 0.25))
    # Allow CUDA if available, but our patches will handle _C fallbacks
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    SAM2_CHECKPOINT = os.getenv("SAM2_CHECKPOINT", "./checkpoints/sam2.1_hiera_large.pt")
    MODEL_CFG = os.getenv("MODEL_CFG", "configs/sam2.1/sam2.1_hiera_l.yaml")
    
    # File Processing Configuration
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "./uploads")
    OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "./outputs")
    TEMP_FRAMES_DIR = os.getenv("TEMP_FRAMES_DIR", "./temp_frames")
    TRACKING_RESULTS_DIR = os.getenv("TRACKING_RESULTS_DIR", "./tracking_results")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 100 * 1024 * 1024))  # 100MB
    ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "webm"}
    
    # Video Processing Configuration
    PROMPT_TYPE_FOR_VIDEO = os.getenv("PROMPT_TYPE_FOR_VIDEO", "box")  # ["point", "box", "mask"]
    
    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [cls.UPLOAD_FOLDER, cls.OUTPUT_FOLDER, cls.TEMP_FRAMES_DIR, cls.TRACKING_RESULTS_DIR]:
            Path(directory).mkdir(parents=True, exist_ok=True)