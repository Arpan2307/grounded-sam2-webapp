#!/usr/bin/env python3
import os
import sys
import subprocess
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_python_path():
    """Add required paths to Python path"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Get to grounded-sam2-webapp root
    grounded_sam2_path = os.path.join(project_root, "Grounded-SAM-2")
    segment_anything_2_path = os.path.join(project_root, "segment-anything-2")
    grounding_dino_path = os.path.join(project_root, "Grounded-SAM-2", "grounding_dino")
    
    paths_to_add = [grounded_sam2_path, segment_anything_2_path, grounding_dino_path]
    
    for path in paths_to_add:
        if os.path.exists(path) and path not in sys.path:
            sys.path.insert(0, path)  # Insert at beginning for priority
            logger.info(f"Added {path} to Python path")
    
    # Also set environment variable
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    new_paths = ":".join(paths_to_add)
    if current_pythonpath:
        os.environ['PYTHONPATH'] = f"{new_paths}:{current_pythonpath}"
    else:
        os.environ['PYTHONPATH'] = new_paths

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import torch
        logger.info(f"PyTorch version: {torch.__version__}")
        
        # Try importing SAM2
        from sam2.build_sam import build_sam2
        logger.info("SAM2 import successful")
        
        # Try importing Grounding DINO
        from grounding_dino.groundingdino.util.inference import load_model
        logger.info("Grounding DINO import successful")
        
        return True
    except ImportError as e:
        logger.error(f"Dependency check failed: {e}")
        return False

def start_server():
    """Start the FastAPI server"""
    try:
        # Set up environment
        setup_python_path()
        
        # Check dependencies
        if not check_dependencies():
            logger.error("Dependency check failed, but continuing anyway...")
        
        # Start the server
        logger.info("Starting FastAPI server...")
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "5000", 
            "--reload"
        ]
        
        subprocess.run(cmd)
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
