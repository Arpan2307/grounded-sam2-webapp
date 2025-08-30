#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Set up the same paths as our application
project_root = Path(__file__).parent.parent  # Get to grounded-sam2-webapp root
grounded_sam2_path = str(project_root / "Grounded-SAM-2")
segment_anything_2_path = str(project_root / "segment-anything-2")
grounding_dino_path = str(project_root / "Grounded-SAM-2" / "grounding_dino")

# Add to Python path in correct order
for path in [grounded_sam2_path, segment_anything_2_path, grounding_dino_path]:
    if path not in sys.path:
        sys.path.insert(0, path)  # Insert at beginning for priority

print("=== SAM2 Debug Test ===")
print("Python path entries:")
for i, path in enumerate(sys.path[:5]):
    print(f"  {i}: {path}")

print("\n=== Testing SAM2 Import ===")
try:
    import sam2
    print("✅ sam2 imported successfully")
    print(f"sam2 location: {sam2.__file__}")
    print(f"sam2 _C attribute: {getattr(sam2, '_C', 'NOT_FOUND')}")
    
    # Test the function that uses _C
    from sam2.utils.misc import get_connected_components
    print("✅ get_connected_components imported")
    
    import torch
    print("✅ torch imported")
    
    # Test with a simple mask
    test_mask = torch.zeros(1, 1, 4, 4)
    test_mask[0, 0, 1:3, 1:3] = 1
    
    print("Testing get_connected_components with test mask...")
    labels, counts = get_connected_components(test_mask)
    print(f"✅ Success! Labels shape: {labels.shape}, Counts shape: {counts.shape}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Testing SAM2 Model Building ===")
try:
    from sam2.build_sam import build_sam2_video_predictor
    print("✅ build_sam2_video_predictor imported")
    
    # Try to build predictor (this might fail due to missing checkpoints, but should not have _C errors)
    config_path = str(project_root / "Grounded-SAM-2" / "configs" / "sam2.1" / "sam2.1_hiera_l.yaml")
    checkpoint_path = str(project_root / "backend" / "checkpoints" / "sam2.1_hiera_large.pt")
    
    print(f"Config path exists: {os.path.exists(config_path)}")
    print(f"Checkpoint path exists: {os.path.exists(checkpoint_path)}")
    
    if os.path.exists(config_path) and os.path.exists(checkpoint_path):
        predictor = build_sam2_video_predictor(config_path, checkpoint_path)
        print("✅ SAM2 video predictor built successfully")
    else:
        print("⚠️ Skipping predictor build (missing files)")
        
except Exception as e:
    print(f"❌ Model building error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Debug Complete ===")
