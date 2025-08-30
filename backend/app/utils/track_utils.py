import numpy as np

def sample_points_from_masks(masks, num_points=10):
    """
    Sample positive points from object masks for SAM2 tracking
    
    Args:
        masks: numpy array of shape (N, H, W) where N is number of objects
        num_points: number of points to sample per mask
    
    Returns:
        List of sampled points for each mask
    """
    points = []
    for mask in masks:
        # Get the indices of the mask where the value is True/1 (object is present)
        indices = np.argwhere(mask > 0.5)
        if len(indices) > 0:
            # Randomly sample points from the indices
            sampled_indices = np.random.choice(
                len(indices), 
                size=min(num_points, len(indices)), 
                replace=False
            )
            sampled_points = indices[sampled_indices]
            # Convert from (y, x) to (x, y) format for SAM2
            sampled_points = sampled_points[:, [1, 0]]
            points.append(sampled_points)
        else:
            # No points to sample from if mask is empty
            points.append(np.array([]).reshape(0, 2))
    return points

def filter_detections_by_confidence(boxes, confidences, labels, threshold=0.5):
    """
    Filter detections based on confidence threshold
    
    Args:
        boxes: detection boxes
        confidences: confidence scores
        labels: object labels
        threshold: minimum confidence threshold
    
    Returns:
        Filtered boxes, confidences, and labels
    """
    mask = confidences >= threshold
    return boxes[mask], confidences[mask], [labels[i] for i, m in enumerate(mask) if m]

def compute_mask_area(mask):
    """Compute the area of a binary mask"""
    return np.sum(mask > 0.5)

def compute_mask_centroid(mask):
    """Compute the centroid of a binary mask"""
    y_indices, x_indices = np.where(mask > 0.5)
    if len(y_indices) > 0:
        centroid_x = np.mean(x_indices)
        centroid_y = np.mean(y_indices)
        return np.array([centroid_x, centroid_y])
    else:
        return np.array([0.0, 0.0])