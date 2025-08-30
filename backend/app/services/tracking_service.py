import os
import sys
import cv2
import torch
import numpy as np
import supervision as sv
from pathlib import Path
from PIL import Image
from tqdm import tqdm
from torchvision.ops import box_convert
from typing import Dict, List, Tuple, Optional
import redis
import json
import logging
from celery import Celery

# Add SAM2 and Grounding DINO to Python path
grounded_sam2_path = "/home/arpan/CourseWork/RoboProject/Grounded-SAM-2"
grounding_dino_path = "/home/arpan/CourseWork/RoboProject/Grounded-SAM-2/grounding_dino"

if grounded_sam2_path not in sys.path:
    sys.path.append(grounded_sam2_path)
if grounding_dino_path not in sys.path:
    sys.path.append(grounding_dino_path)

from app.config import Config
from app.models.schemas import TaskStatus, TrackingTask, DetectionResult
from app.services.file_handler import FileHandler

# Import SAM2 and Grounding DINO components
try:
    from sam2.build_sam import build_sam2_video_predictor, build_sam2
    from sam2.sam2_image_predictor import SAM2ImagePredictor 
    from grounding_dino.groundingdino.util.inference import load_model, load_image, predict
    from app.utils.track_utils import sample_points_from_masks
    from app.utils.video_utils import create_video_from_images
    imports_successful = True
except ImportError as e:
    logging.error(f"Failed to import required dependencies: {e}")
    imports_successful = False

class TrackingService:
    def __init__(self):
        self.config = Config()
        self.file_handler = FileHandler()
        self.redis_client = redis.Redis(
            host=self.config.REDIS_HOST, 
            port=self.config.REDIS_PORT, 
            db=self.config.REDIS_DB,
            decode_responses=True
        )
        self.models_loaded = False
        self._load_models()
    
    def _load_models(self):
        """Load Grounding DINO and SAM2 models"""
        if not imports_successful:
            logging.error("Cannot load models due to failed imports")
            return
            
        try:
            # Load Grounding DINO model
            self.grounding_model = load_model(
                model_config_path=self.config.GROUNDING_DINO_CONFIG,
                model_checkpoint_path=self.config.GROUNDING_DINO_CHECKPOINT,
                device=self.config.DEVICE
            )
            
            # Load SAM2 models with CPU fallback for missing CUDA extensions
            try:
                self.video_predictor = build_sam2_video_predictor(
                    self.config.MODEL_CFG, 
                    self.config.SAM2_CHECKPOINT
                )
                self.sam2_image_model = build_sam2(
                    self.config.MODEL_CFG, 
                    self.config.SAM2_CHECKPOINT
                )
                self.image_predictor = SAM2ImagePredictor(self.sam2_image_model)
            except Exception as e:
                logging.warning(f"Failed to load SAM2 with default settings: {e}")
                logging.info("Attempting to load SAM2 with CPU-only mode...")
                
                # Force CPU mode and disable optimizations
                original_device = self.config.DEVICE
                self.config.DEVICE = "cpu"
                
                # Disable CUDA extensions that cause _C errors
                os.environ['CUDA_VISIBLE_DEVICES'] = ''
                
                self.video_predictor = build_sam2_video_predictor(
                    self.config.MODEL_CFG, 
                    self.config.SAM2_CHECKPOINT,
                    device="cpu"
                )
                self.sam2_image_model = build_sam2(
                    self.config.MODEL_CFG, 
                    self.config.SAM2_CHECKPOINT,
                    device="cpu"  
                )
                self.image_predictor = SAM2ImagePredictor(self.sam2_image_model)
                
                logging.info(f"SAM2 loaded successfully in CPU mode")
                
                # Reset device for other components
                self.config.DEVICE = original_device
            
            # Enable optimizations for newer GPUs
            if torch.cuda.is_available() and torch.cuda.get_device_properties(0).major >= 8:
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
            
            self.models_loaded = True
            logging.info("Models loaded successfully")
            
        except Exception as e:
            logging.error(f"Failed to load models: {e}")
            self.models_loaded = False
    
    def get_task_status(self, task_id: str) -> Optional[TrackingTask]:
        """Get task status from Redis"""
        try:
            task_data = self.redis_client.get(f"task:{task_id}")
            if task_data:
                return TrackingTask.parse_raw(task_data)
            return None
        except Exception as e:
            logging.error(f"Failed to get task status: {e}")
            return None
    
    def update_task_status(self, task_id: str, status: TaskStatus, progress: Optional[float] = None, 
                          message: Optional[str] = None, result_video_url: Optional[str] = None, 
                          error: Optional[str] = None):
        """Update task status in Redis"""
        try:
            task = TrackingTask(
                task_id=task_id,
                status=status,
                progress=progress,
                message=message,
                result_video_url=result_video_url,
                error=error
            )
            self.redis_client.set(f"task:{task_id}", task.json(), ex=3600)  # Expire after 1 hour
            logging.info(f"Updated task {task_id} status to {status}")
        except Exception as e:
            logging.error(f"Failed to update task status: {e}")
    
    async def start_tracking(self, task_id: str, video_path: str, text_prompt: str, 
                           box_threshold: float = 0.35, text_threshold: float = 0.25) -> str:
        """Start video tracking task"""
        if not self.models_loaded:
            self.update_task_status(task_id, TaskStatus.FAILED, error="Models not loaded")
            return task_id
        
        self.update_task_status(task_id, TaskStatus.PROCESSING, progress=0, 
                              message="Starting video processing...")
        
        try:
            # Process video in background
            await self._process_video_async(task_id, video_path, text_prompt, 
                                          box_threshold, text_threshold)
        except Exception as e:
            logging.error(f"Error in tracking task {task_id}: {e}")
            self.update_task_status(task_id, TaskStatus.FAILED, error=str(e))
        
        return task_id
    
    async def _process_video_async(self, task_id: str, video_path: str, text_prompt: str,
                                 box_threshold: float, text_threshold: float):
        """Process video tracking asynchronously"""
        try:
            # Step 1: Extract frames from video
            self.update_task_status(task_id, TaskStatus.PROCESSING, progress=10, 
                                  message="Extracting video frames...")
            
            frames_dir = self.file_handler.get_temp_frames_dir(task_id)
            frame_names = self._extract_video_frames(video_path, frames_dir)
            
            # Step 2: Initialize video predictor
            self.update_task_status(task_id, TaskStatus.PROCESSING, progress=20, 
                                  message="Initializing video predictor...")
            
            inference_state = self.video_predictor.init_state(video_path=frames_dir)
            
            # Step 3: Process first frame for object detection
            self.update_task_status(task_id, TaskStatus.PROCESSING, progress=30, 
                                  message="Detecting objects in first frame...")
            
            detections = self._detect_objects_in_frame(
                frames_dir, frame_names[0], text_prompt, box_threshold, text_threshold
            )
            
            if not detections:
                raise Exception(f"No objects detected with prompt: {text_prompt}")
            
            # Step 4: Set up tracking for detected objects
            self.update_task_status(task_id, TaskStatus.PROCESSING, progress=40, 
                                  message="Setting up object tracking...")
            
            self._setup_video_tracking(inference_state, detections, 0)
            
            # Step 5: Propagate tracking across all frames
            self.update_task_status(task_id, TaskStatus.PROCESSING, progress=50, 
                                  message="Tracking objects across video...")
            
            video_segments = self._propagate_tracking(inference_state)
            
            # Step 6: Create annotated video
            self.update_task_status(task_id, TaskStatus.PROCESSING, progress=70, 
                                  message="Creating annotated video...")
            
            output_video_path = self._create_annotated_video(
                task_id, frames_dir, frame_names, video_segments, detections
            )
            
            # Step 7: Complete task
            self.update_task_status(task_id, TaskStatus.COMPLETED, progress=100, 
                                  message="Video processing completed successfully!",
                                  result_video_url=f"/api/download/{task_id}")
            
            # Cleanup temporary files
            # self.file_handler.cleanup_temp_files(task_id)
            
        except Exception as e:
            logging.error(f"Error processing video for task {task_id}: {e}")
            self.update_task_status(task_id, TaskStatus.FAILED, error=str(e))
    
    def _extract_video_frames(self, video_path: str, frames_dir: str) -> List[str]:
        """Extract frames from video file"""
        video_info = sv.VideoInfo.from_video_path(video_path)
        frame_generator = sv.get_video_frames_generator(video_path, stride=1, start=0, end=None)
        
        with sv.ImageSink(
            target_dir_path=frames_dir, 
            overwrite=True, 
            image_name_pattern="{:05d}.jpg"
        ) as sink:
            for frame in tqdm(frame_generator, desc="Extracting frames"):
                sink.save_image(frame)
        
        # Get sorted frame names
        frame_names = [
            p for p in os.listdir(frames_dir)
            if os.path.splitext(p)[-1].lower() in [".jpg", ".jpeg"]
        ]
        frame_names.sort(key=lambda p: int(os.path.splitext(p)[0]))
        
        return frame_names
    
    def _detect_objects_in_frame(self, frames_dir: str, frame_name: str, text_prompt: str,
                               box_threshold: float, text_threshold: float) -> List[DetectionResult]:
        """Detect objects in the first frame using Grounding DINO"""
        img_path = os.path.join(frames_dir, frame_name)
        image_source, image = load_image(img_path)
        
        boxes, confidences, labels = predict(
            model=self.grounding_model,
            image=image,
            caption=text_prompt,
            box_threshold=box_threshold,
            text_threshold=text_threshold,
        )
        
        # Process detected boxes
        h, w, _ = image_source.shape
        boxes = boxes * torch.Tensor([w, h, w, h])
        input_boxes = box_convert(boxes=boxes, in_fmt="cxcywh", out_fmt="xyxy").numpy()
        
        # Create detection results
        detections = []
        for i, (box, confidence, label) in enumerate(zip(input_boxes, confidences, labels)):
            detections.append(DetectionResult(
                object_id=i + 1,
                label=label,
                confidence=float(confidence),
                bbox=box.tolist()
            ))
        
        # Get masks for the detected objects
        self.image_predictor.set_image(image_source)
        masks, scores, logits = self.image_predictor.predict(
            point_coords=None,
            point_labels=None,
            box=input_boxes,
            multimask_output=False,
        )
        
        if masks.ndim == 4:
            masks = masks.squeeze(1)
        
        # Store masks for tracking setup
        self._current_masks = masks
        self._current_boxes = input_boxes
        self._current_labels = labels
        
        return detections
    
    def _setup_video_tracking(self, inference_state, detections: List[DetectionResult], frame_idx: int):
        """Set up SAM2 video tracking for detected objects"""
        prompt_type = self.config.PROMPT_TYPE_FOR_VIDEO
        
        if prompt_type == "point":
            all_sample_points = sample_points_from_masks(masks=self._current_masks, num_points=10)
            for object_id, points in enumerate(all_sample_points, start=1):
                labels = np.ones((points.shape[0]), dtype=np.int32)
                self.video_predictor.add_new_points_or_box(
                    inference_state=inference_state,
                    frame_idx=frame_idx,
                    obj_id=object_id,
                    points=points,
                    labels=labels,
                )
        
        elif prompt_type == "box":
            for object_id, box in enumerate(self._current_boxes, start=1):
                self.video_predictor.add_new_points_or_box(
                    inference_state=inference_state,
                    frame_idx=frame_idx,
                    obj_id=object_id,
                    box=box,
                )
        
        elif prompt_type == "mask":
            for object_id, mask in enumerate(self._current_masks, start=1):
                self.video_predictor.add_new_mask(
                    inference_state=inference_state,
                    frame_idx=frame_idx,
                    obj_id=object_id,
                    mask=mask
                )
    
    def _propagate_tracking(self, inference_state) -> Dict:
        """Propagate tracking across all video frames"""
        video_segments = {}
        for out_frame_idx, out_obj_ids, out_mask_logits in self.video_predictor.propagate_in_video(inference_state):
            video_segments[out_frame_idx] = {
                out_obj_id: (out_mask_logits[i] > 0.0).cpu().numpy()
                for i, out_obj_id in enumerate(out_obj_ids)
            }
        return video_segments
    
    def _create_annotated_video(self, task_id: str, frames_dir: str, frame_names: List[str],
                              video_segments: Dict, detections: List[DetectionResult]) -> str:
        """Create annotated video with tracking results"""
        tracking_results_dir = self.file_handler.get_tracking_results_dir(task_id)
        
        # Create object ID to label mapping
        id_to_objects = {det.object_id: det.label for det in detections}
        
        # Annotate each frame
        for frame_idx, segments in video_segments.items():
            img = cv2.imread(os.path.join(frames_dir, frame_names[frame_idx]))
            
            if segments:
                object_ids = list(segments.keys())
                masks = list(segments.values())
                masks = np.concatenate(masks, axis=0)
                
                detections_sv = sv.Detections(
                    xyxy=sv.mask_to_xyxy(masks),
                    mask=masks,
                    class_id=np.array(object_ids, dtype=np.int32),
                )
                
                # Apply annotations
                box_annotator = sv.BoxAnnotator()
                annotated_frame = box_annotator.annotate(scene=img.copy(), detections=detections_sv)
                
                label_annotator = sv.LabelAnnotator()
                labels = [id_to_objects.get(i, f"Object_{i}") for i in object_ids]
                annotated_frame = label_annotator.annotate(annotated_frame, detections=detections_sv, labels=labels)
                
                mask_annotator = sv.MaskAnnotator()
                annotated_frame = mask_annotator.annotate(scene=annotated_frame, detections=detections_sv)
            else:
                annotated_frame = img
            
            cv2.imwrite(
                os.path.join(tracking_results_dir, f"annotated_frame_{frame_idx:05d}.jpg"), 
                annotated_frame
            )
        
        # Create output video
        output_video_path = self.file_handler.get_output_video_path(task_id)
        create_video_from_images(tracking_results_dir, output_video_path)
        
        return output_video_path