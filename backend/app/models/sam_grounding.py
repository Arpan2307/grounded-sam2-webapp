"""
SAM Grounding Model Integration and Pydantic Models

This module provides both Pydantic models for API requests/responses
and integration classes for Grounding DINO and SAM-2 models.
"""

import torch
import numpy as np
from typing import List, Optional, Dict, Tuple
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

# Pydantic Models for API

class Box(BaseModel):
    x_min: float = Field(..., description="Left coordinate of bounding box")
    y_min: float = Field(..., description="Top coordinate of bounding box")
    x_max: float = Field(..., description="Right coordinate of bounding box")
    y_max: float = Field(..., description="Bottom coordinate of bounding box")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence score")
    label: str = Field(..., description="Object class label")

class DetectionResult(BaseModel):
    boxes: List[Box] = Field(default=[], description="List of detected bounding boxes")
    masks: Optional[List[List[float]]] = Field(None, description="List of segmentation masks")
    class_names: List[str] = Field(default=[], description="List of detected class names")
    frame_index: Optional[int] = Field(None, description="Frame index for video processing")

class VideoProcessingRequest(BaseModel):
    video_path: str = Field(..., description="Path to input video file")
    text_prompt: str = Field(..., description="Text description of objects to detect")
    prompt_type: str = Field("box", regex="^(point|box|mask)$", description="Type of prompt for SAM-2")
    box_threshold: float = Field(0.35, ge=0, le=1, description="Detection confidence threshold")
    text_threshold: float = Field(0.25, ge=0, le=1, description="Text matching threshold")

class VideoProcessingResponse(BaseModel):
    output_video_path: str = Field(..., description="Path to processed output video")
    detection_results: DetectionResult = Field(..., description="Detection and tracking results")
    processing_stats: Optional[Dict] = Field(None, description="Processing statistics")

# Integration Classes

class SAMGroundingModel:
    """
    Integrated model class that combines Grounding DINO and SAM-2 
    for text-prompted object detection and segmentation.
    """
    
    def __init__(self, grounding_model, sam_model, device: str = "cuda"):
        self.grounding_model = grounding_model
        self.sam_model = sam_model
        self.device = device
        
    def detect_and_segment(self, 
                          image: np.ndarray,
                          text_prompt: str,
                          box_threshold: float = 0.35,
                          text_threshold: float = 0.25) -> Dict:
        """
        Detect objects using Grounding DINO and segment them using SAM-2
        
        Args:
            image: Input image array
            text_prompt: Text description of objects to detect
            box_threshold: Detection confidence threshold
            text_threshold: Text matching threshold
            
        Returns:
            Dictionary containing detection results with boxes, masks, and labels
        """
        try:
            # Import here to avoid circular imports
            from grounding_dino.groundingdino.util.inference import predict
            from torchvision.ops import box_convert
            
            # Get detections from Grounding DINO
            boxes, confidences, labels = predict(
                model=self.grounding_model,
                image=image,
                caption=text_prompt,
                box_threshold=box_threshold,
                text_threshold=text_threshold,
            )
            
            if len(boxes) == 0:
                return {
                    "boxes": [],
                    "masks": [],
                    "labels": [],
                    "confidences": []
                }
            
            # Convert boxes to correct format
            h, w = image.shape[:2]
            boxes = boxes * torch.Tensor([w, h, w, h])
            input_boxes = box_convert(boxes=boxes, in_fmt="cxcywh", out_fmt="xyxy").numpy()
            
            # Get masks from SAM-2
            from sam2.sam2_image_predictor import SAM2ImagePredictor
            image_predictor = SAM2ImagePredictor(self.sam_model)
            image_predictor.set_image(image)
            
            masks, scores, logits = image_predictor.predict(
                point_coords=None,
                point_labels=None,
                box=input_boxes,
                multimask_output=False,
            )
            
            if masks.ndim == 4:
                masks = masks.squeeze(1)
            
            return {
                "boxes": input_boxes,
                "masks": masks,
                "labels": labels,
                "confidences": confidences.numpy()
            }
            
        except Exception as e:
            logger.error(f"Error in detect_and_segment: {e}")
            return {
                "boxes": [],
                "masks": [],
                "labels": [],
                "confidences": []
            }
    
    def prepare_for_tracking(self, detection_results: Dict, frame_idx: int = 0) -> Dict:
        """
        Prepare detection results for video tracking with SAM-2
        
        Args:
            detection_results: Results from detect_and_segment
            frame_idx: Frame index for tracking initialization
            
        Returns:
            Dictionary with tracking-ready data
        """
        return {
            "frame_idx": frame_idx,
            "boxes": detection_results["boxes"],
            "masks": detection_results["masks"],
            "labels": detection_results["labels"],
            "confidences": detection_results["confidences"]
        }

def create_sam_grounding_model(grounding_model, sam_model, device: str = "cuda") -> SAMGroundingModel:
    """
    Factory function to create SAMGroundingModel instance
    
    Args:
        grounding_model: Loaded Grounding DINO model
        sam_model: Loaded SAM-2 model
        device: Device to run models on
        
    Returns:
        SAMGroundingModel instance
    """
    return SAMGroundingModel(grounding_model, sam_model, device)

def validate_detection_results(results: Dict) -> bool:
    """
    Validate detection results structure
    
    Args:
        results: Detection results dictionary
        
    Returns:
        True if results are valid, False otherwise
    """
    required_keys = ["boxes", "masks", "labels", "confidences"]
    
    if not all(key in results for key in required_keys):
        return False
    
    # Check that all arrays have consistent lengths
    if len(results["boxes"]) > 0:
        box_count = len(results["boxes"])
        return (len(results["masks"]) == box_count and
                len(results["labels"]) == box_count and
                len(results["confidences"]) == box_count)
    
    return True