import cv2
import os
import logging
from pathlib import Path
from typing import List, Optional

def read_video_frames(video_path: str) -> List:
    """
    Read all frames from a video file
    
    Args:
        video_path: Path to the video file
    
    Returns:
        List of video frames
    """
    frames = []
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
    finally:
        cap.release()
    
    return frames

def get_video_info(video_path: str) -> dict:
    """
    Get video information (fps, frame count, resolution)
    
    Args:
        video_path: Path to the video file
    
    Returns:
        Dictionary with video information
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        return {
            "fps": fps,
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "duration": frame_count / fps if fps > 0 else 0
        }
    finally:
        cap.release()

def save_video(frames: List, output_path: str, fps: float = 30):
    """
    Save frames as a video file
    
    Args:
        frames: List of video frames
        output_path: Output video file path
        fps: Frames per second for output video
    """
    if not frames:
        raise ValueError("No frames to save")
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    height, width = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    try:
        for frame in frames:
            out.write(frame)
        logging.info(f"Video saved to: {output_path}")
    finally:
        out.release()

def create_video_from_images(image_dir: str, output_path: str, fps: float = 30):
    """
    Create a video from a directory of images
    
    Args:
        image_dir: Directory containing images
        output_path: Output video file path
        fps: Frames per second for output video
    """
    # Get all image files and sort them
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
    images = []
    
    for file_path in Path(image_dir).iterdir():
        if file_path.suffix.lower() in image_extensions:
            images.append(file_path.name)
    
    if not images:
        raise ValueError(f"No images found in directory: {image_dir}")
    
    # Sort images by filename (assuming they are numbered)
    try:
        images.sort(key=lambda x: int(Path(x).stem.split('_')[-1]))
    except ValueError:
        # Fallback to alphabetical sort if numeric sort fails
        images.sort()
    
    frames = []
    for image in images:
        img_path = os.path.join(image_dir, image)
        frame = cv2.imread(img_path)
        if frame is not None:
            frames.append(frame)
        else:
            logging.warning(f"Could not read image: {img_path}")
    
    if not frames:
        raise ValueError("No valid frames could be loaded from images")
    
    save_video(frames, output_path, fps)

def resize_frame(frame, target_width: Optional[int] = None, target_height: Optional[int] = None, 
                 maintain_aspect: bool = True):
    """
    Resize a video frame
    
    Args:
        frame: Input frame
        target_width: Target width (optional)
        target_height: Target height (optional)
        maintain_aspect: Whether to maintain aspect ratio
    
    Returns:
        Resized frame
    """
    if target_width is None and target_height is None:
        return frame
    
    h, w = frame.shape[:2]
    
    if maintain_aspect:
        if target_width is not None and target_height is None:
            # Calculate height based on width
            aspect_ratio = h / w
            target_height = int(target_width * aspect_ratio)
        elif target_height is not None and target_width is None:
            # Calculate width based on height
            aspect_ratio = w / h
            target_width = int(target_height * aspect_ratio)
        elif target_width is not None and target_height is not None:
            # Use the dimension that results in smaller scaling
            scale_w = target_width / w
            scale_h = target_height / h
            scale = min(scale_w, scale_h)
            target_width = int(w * scale)
            target_height = int(h * scale)
    
    return cv2.resize(frame, (target_width, target_height))