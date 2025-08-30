import os
import uuid
import aiofiles
from pathlib import Path
from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException
from app.config import Config

class FileHandler:
    def __init__(self):
        self.config = Config()
        self.config.create_directories()
    
    async def save_upload_file(self, upload_file: UploadFile) -> Tuple[str, str]:
        """
        Save uploaded file and return file_id and file_path
        """
        # Validate file
        if not self._is_allowed_file(upload_file.filename):
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Supported formats: {', '.join(self.config.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        file_size = await self._get_file_size(upload_file)
        if file_size > self.config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File size too large. Maximum size: {self.config.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Generate unique file ID and path
        file_id = str(uuid.uuid4())
        file_extension = Path(upload_file.filename).suffix
        filename = f"{file_id}{file_extension}"
        file_path = os.path.join(self.config.UPLOAD_FOLDER, filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await upload_file.read()
            await f.write(content)
        
        return file_id, file_path
    
    def _is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        if not filename:
            return False
        return Path(filename).suffix.lower().lstrip('.') in self.config.ALLOWED_EXTENSIONS
    
    async def _get_file_size(self, upload_file: UploadFile) -> int:
        """Get file size without consuming the file stream"""
        # Read content to get size then reset stream
        content = await upload_file.read()
        await upload_file.seek(0)  # Reset stream position
        return len(content)
    
    def get_output_video_path(self, task_id: str) -> str:
        """Get output video file path for a task"""
        return os.path.join(self.config.OUTPUT_FOLDER, f"{task_id}_result.mp4")
    
    def get_temp_frames_dir(self, task_id: str) -> str:
        """Get temporary frames directory for a task"""
        temp_dir = os.path.join(self.config.TEMP_FRAMES_DIR, task_id)
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        return temp_dir
    
    def get_tracking_results_dir(self, task_id: str) -> str:
        """Get tracking results directory for a task"""
        results_dir = os.path.join(self.config.TRACKING_RESULTS_DIR, task_id)
        Path(results_dir).mkdir(parents=True, exist_ok=True)
        return results_dir
    
    def cleanup_temp_files(self, task_id: str):
        """Clean up temporary files for a task"""
        import shutil
        
        temp_frames_dir = os.path.join(self.config.TEMP_FRAMES_DIR, task_id)
        tracking_results_dir = os.path.join(self.config.TRACKING_RESULTS_DIR, task_id)
        
        for directory in [temp_frames_dir, tracking_results_dir]:
            if os.path.exists(directory):
                shutil.rmtree(directory)
