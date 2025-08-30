from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class PromptType(str, Enum):
    POINT = "point"
    BOX = "box"
    MASK = "mask"

class TrackingRequest(BaseModel):
    text_prompt: str = Field(..., description="Text description of the object to track")
    prompt_type: PromptType = Field(PromptType.BOX, description="Type of prompt for SAM-2")
    box_threshold: Optional[float] = Field(0.35, description="Box detection threshold")
    text_threshold: Optional[float] = Field(0.25, description="Text detection threshold")

class TrackingTask(BaseModel):
    task_id: str
    status: TaskStatus
    progress: Optional[float] = Field(None, description="Progress percentage (0-100)")
    message: Optional[str] = None
    result_video_url: Optional[str] = None
    error: Optional[str] = None

class DetectionResult(BaseModel):
    object_id: int
    label: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]

class TrackingResponse(BaseModel):
    task_id: str
    status: TaskStatus
    detections: Optional[List[DetectionResult]] = None
    video_url: Optional[str] = None
    error: Optional[str] = None

class UploadResponse(BaseModel):
    success: bool
    message: str
    file_id: Optional[str] = None
    filename: Optional[str] = None
