from fastapi import APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect
from typing import List, Optional
import os
import uuid
import json
import logging
from pathlib import Path

from app.models.schemas import (
    TrackingRequest, TrackingResponse, TrackingTask, TaskStatus, 
    UploadResponse, PromptType
)
from app.services.tracking_service import TrackingService
from app.services.file_handler import FileHandler

router = APIRouter(prefix="/api", tags=["tracking"])

# Initialize services
tracking_service = TrackingService()
file_handler = FileHandler()

@router.post("/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """
    Upload a video file for processing
    """
    try:
        file_id, file_path = await file_handler.save_upload_file(file)
        
        return UploadResponse(
            success=True,
            message="File uploaded successfully",
            file_id=file_id,
            filename=file.filename
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/track", response_model=TrackingResponse)
async def start_tracking(
    background_tasks: BackgroundTasks,
    file_id: str = Form(...),
    text_prompt: str = Form(...),
    prompt_type: PromptType = Form(PromptType.BOX),
    box_threshold: Optional[float] = Form(0.35),
    text_threshold: Optional[float] = Form(0.25)
):
    """
    Start video tracking task
    """
    try:
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Get video file path
        video_files = list(Path(file_handler.config.UPLOAD_FOLDER).glob(f"{file_id}.*"))
        if not video_files:
            raise HTTPException(status_code=404, detail="Video file not found")
        
        video_path = str(video_files[0])
        
        # Start tracking task in background
        background_tasks.add_task(
            tracking_service.start_tracking,
            task_id=task_id,
            video_path=video_path,
            text_prompt=text_prompt,
            box_threshold=box_threshold,
            text_threshold=text_threshold
        )
        
        # Initialize task status
        tracking_service.update_task_status(
            task_id, TaskStatus.PENDING, progress=0, 
            message="Task queued for processing"
        )
        
        return TrackingResponse(
            task_id=task_id,
            status=TaskStatus.PENDING
        )
    
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Tracking error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start tracking: {str(e)}")

@router.get("/status/{task_id}", response_model=TrackingTask)
async def get_task_status(task_id: str):
    """
    Get the status of a tracking task
    """
    task = tracking_service.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@router.get("/download/{task_id}")
async def download_result(task_id: str):
    """
    Download the processed video result
    """
    task = tracking_service.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Task not completed")
    
    video_path = file_handler.get_output_video_path(task_id)
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Result video not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"tracked_video_{task_id}.mp4"
    )

@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time task status updates
    """
    await websocket.accept()
    
    try:
        while True:
            task = tracking_service.get_task_status(task_id)
            if task:
                await websocket.send_text(task.json())
                
                # Close connection if task is completed or failed
                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    break
            
            # Wait before next update
            import asyncio
            await asyncio.sleep(1)
    
    except WebSocketDisconnect:
        logging.info(f"WebSocket disconnected for task {task_id}")
    except Exception as e:
        logging.error(f"WebSocket error for task {task_id}: {e}")
    finally:
        await websocket.close()

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "models_loaded": tracking_service.models_loaded}

@router.delete("/cleanup/{task_id}")
async def cleanup_task(task_id: str):
    """
    Clean up temporary files for a task
    """
    try:
        file_handler.cleanup_temp_files(task_id)
        return {"message": f"Cleanup completed for task {task_id}"}
    except Exception as e:
        logging.error(f"Cleanup error for task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")