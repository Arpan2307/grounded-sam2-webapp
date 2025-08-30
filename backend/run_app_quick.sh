#!/bin/bash

# Grounded SAM-2 Web Application - Quick Start
# Use this for daily startup after initial setup

echo "🚀 Quick Starting Grounded SAM-2 Web Application..."
echo "================================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

cd "$BACKEND_DIR"

# Quick activation of existing venv
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Using existing virtual environment"
    PYTHON_CMD="$VIRTUAL_ENV/bin/python"
else
    echo "❌ Virtual environment not found. Run full setup first:"
    echo "   ./run_app.sh"
    exit 1
fi

# Quick check for critical dependencies
if ! $PYTHON_CMD -c "import torch, fastapi, uvicorn" 2>/dev/null; then
    echo "❌ Missing dependencies. Run full setup first:"
    echo "   ./run_app.sh"
    exit 1
fi

# Quick model check
if [ ! -f "checkpoints/sam2_hiera_large.pt" ] && [ ! -f "checkpoints/sam2.1_hiera_large.pt" ]; then
    echo "⚠️  SAM-2 model not found in checkpoints/"
    echo "   App will work but you may need to download models for full functionality"
fi

# Apply quick patches only if needed
echo "🔧 Checking patches..."

# Function to apply quick SAM2 patch
quick_patch_sam2() {
    local repo_dir="$1"
    local repo_name="$2"
    
    if [ ! -d "$repo_dir" ]; then
        return
    fi
    
    local misc_file="$repo_dir/sam2/utils/misc.py"
    local init_file="$repo_dir/sam2/__init__.py"
    
    # Check if patches are needed
    local needs_misc_patch=false
    local needs_init_patch=false
    
    if [ -f "$misc_file" ] && ! grep -q "if _C is not None:" "$misc_file"; then
        needs_misc_patch=true
    fi
    
    if [ -f "$init_file" ] && ! grep -q "_C = None" "$init_file"; then
        needs_init_patch=true
    fi
    
    if [ "$needs_misc_patch" = true ] || [ "$needs_init_patch" = true ]; then
        echo "   Patching $repo_name..."
        $PYTHON_CMD -c "
import re
import os

repo_dir = '$repo_dir'
misc_file = os.path.join(repo_dir, 'sam2/utils/misc.py')
init_file = os.path.join(repo_dir, 'sam2/__init__.py')
needs_misc_patch = $needs_misc_patch
needs_init_patch = $needs_init_patch

# Patch misc.py if needed
if needs_misc_patch and os.path.exists(misc_file):
    with open(misc_file, 'r') as f:
        content = f.read()
    
    # Update the _C usage to check for None
    pattern = r'(\s+)from sam2 import _C\s*return _C\.get_connected_componnets\(mask\.to\(torch\.uint8\)\.contiguous\(\)\)'
    replacement = r'\1from sam2 import _C\n\1if _C is not None:\n\1    return _C.get_connected_componnets(mask.to(torch.uint8).contiguous())\n\1else:\n\1    raise ImportError(\"_C module is None\")'
    
    if re.search(r'from sam2 import _C\s*return _C\.get_connected_componnets', content):
        content = re.sub(pattern, replacement, content)
        
        with open(misc_file, 'w') as f:
            f.write(content)
        print('     ✅ Applied _C None check to misc.py')
    else:
        print('     Already patched misc.py')

# Patch __init__.py if needed
if needs_init_patch and os.path.exists(init_file):
    with open(init_file, 'r') as f:
        content = f.read()
    
    # Add _C import fallback
    init_patch = '''

# Try to import the compiled CUDA extension, but don't fail if it's not available
try:
    from . import _C
except (ImportError, ModuleNotFoundError) as e:
    import warnings
    warnings.warn(f\"SAM2 CUDA extension not available: {e}. Using CPU fallback where needed.\", UserWarning)
    _C = None'''
    
    content += init_patch
    
    with open(init_file, 'w') as f:
        f.write(content)
    print('     ✅ Applied _C import fallback to __init__.py')
"
    else
        echo "   $repo_name already patched"
    fi
}

# Function to apply quick Grounding DINO patch
quick_patch_grounding_dino() {
    local repo_dir="$1"
    local repo_name="$2"
    
    if [ ! -d "$repo_dir" ]; then
        return
    fi
    
    local ms_deform_file="$repo_dir/grounding_dino/groundingdino/models/GroundingDINO/ms_deform_attn.py"
    
    if [ ! -f "$ms_deform_file" ]; then
        return
    fi
    
    # Check if patch is needed
    if grep -q "_C_available = True" "$ms_deform_file"; then
        echo "   $repo_name Grounding DINO already patched"
        return
    fi
    
    echo "   Patching $repo_name Grounding DINO..."
    
    $PYTHON_CMD -c "
import os
import re

ms_deform_file = '$ms_deform_file'

if os.path.exists(ms_deform_file):
    with open(ms_deform_file, 'r') as f:
        content = f.read()
    
    # Patch 1: Update _C import to track availability
    old_import = '''try:
    from grounding_dino.groundingdino import _C
except:
    warnings.warn(\"Failed to load custom C++ ops. Running on CPU mode Only!\")'''
    
    new_import = '''try:
    from grounding_dino.groundingdino import _C
    _C_available = True
except:
    _C = None
    _C_available = False
    warnings.warn(\"Failed to load custom C++ ops. Running on CPU mode Only!\")'''
    
    content = content.replace(old_import, new_import)
    
    # Patch 2: Update MultiScaleDeformableAttnFunction.forward to handle _C unavailable
    if 'if not _C_available:' not in content:
        old_forward_start = '''    @staticmethod
    def forward(
        ctx,
        value,
        value_spatial_shapes,
        value_level_start_index,
        sampling_locations,
        attention_weights,
        im2col_step,
    ):
        ctx.im2col_step = im2col_step
        output = _C.ms_deform_attn_forward('''
        
        new_forward_start = '''    @staticmethod
    def forward(
        ctx,
        value,
        value_spatial_shapes,
        value_level_start_index,
        sampling_locations,
        attention_weights,
        im2col_step,
    ):
        if not _C_available:
            # Fallback to PyTorch implementation when _C is not available
            return multi_scale_deformable_attn_pytorch(
                value, value_spatial_shapes, sampling_locations, attention_weights
            )
        
        ctx.im2col_step = im2col_step
        output = _C.ms_deform_attn_forward('''
        
        content = content.replace(old_forward_start, new_forward_start)
    
    # Patch 3: Update backward method
    if 'if not _C_available:' not in content.split('def backward(ctx, grad_output):')[1]:
        old_backward_start = '''    @staticmethod
    @once_differentiable
    def backward(ctx, grad_output):
        (
            value,
            value_spatial_shapes,
            value_level_start_index,
            sampling_locations,
            attention_weights,
        ) = ctx.saved_tensors
        grad_value, grad_sampling_loc, grad_attn_weight = _C.ms_deform_attn_backward('''
        
        new_backward_start = '''    @staticmethod
    @once_differentiable
    def backward(ctx, grad_output):
        if not _C_available:
            # Return zeros for gradients when _C is not available (fallback mode)
            return None, None, None, None, None, None
            
        (
            value,
            value_spatial_shapes,
            value_level_start_index,
            sampling_locations,
            attention_weights,
        ) = ctx.saved_tensors
        grad_value, grad_sampling_loc, grad_attn_weight = _C.ms_deform_attn_backward('''
        
        content = content.replace(old_backward_start, new_backward_start)
    
    # Patch 4: Update the condition in forward method of MultiScaleDeformableAttention
    old_condition = 'if torch.cuda.is_available() and value.is_cuda:'
    new_condition = 'if torch.cuda.is_available() and value.is_cuda and _C_available:'
    content = content.replace(old_condition, new_condition)
    
    with open(ms_deform_file, 'w') as f:
        f.write(content)
    
    print('     ✅ Applied _C fallback patches to ms_deform_attn.py')
"
}

# Quick patch both SAM2 repositories if they exist
if [ -d "$PROJECT_ROOT/Grounded-SAM-2/sam2/utils" ]; then
    quick_patch_sam2 "$PROJECT_ROOT/Grounded-SAM-2" "Grounded-SAM-2"
fi

if [ -d "$PROJECT_ROOT/segment-anything-2/sam2/utils" ]; then
    quick_patch_sam2 "$PROJECT_ROOT/segment-anything-2" "segment-anything-2"
fi

# Quick patch Grounding DINO if it exists
if [ -d "$PROJECT_ROOT/Grounded-SAM-2/grounding_dino" ]; then
    quick_patch_grounding_dino "$PROJECT_ROOT/Grounded-SAM-2" "Grounded-SAM-2"
fi

# Quick Redis check and start
echo "🔧 Starting Redis..."
if ! pgrep redis-server > /dev/null; then
    if command -v redis-server >/dev/null 2>&1; then
        redis-server --daemonize yes --port 6379 > /dev/null 2>&1
        echo "   ✅ Redis started"
    else
        echo "   ⚠️  Redis not available"
    fi
else
    echo "   ✅ Redis already running"
fi

# Kill any existing servers
echo "🛑 Stopping any existing servers..."
pkill -f "uvicorn.*app.main:app" > /dev/null 2>&1 || true
sleep 1

# Set up environment quickly - allow CUDA but with _C fallbacks
export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/Grounded-SAM-2:$PROJECT_ROOT/segment-anything-2:$PYTHONPATH"
export GROUNDING_DINO_CONFIG_PATH="$PROJECT_ROOT/Grounded-SAM-2/grounding_dino/groundingdino/config"

# Create directories if needed
mkdir -p uploads outputs temp_frames tracking_results checkpoints gdino_checkpoints

# Start backend quickly
echo "🚀 Starting FastAPI backend..."

cd "$BACKEND_DIR"

# Start the server in background for quick startup
$PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Give server a moment to start
sleep 3

# Check if server started successfully
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo ""
    echo "🎉 Application started quickly!"
    echo "📱 Web Interface: http://localhost:8000/static/simple.html"
    echo "🔧 API Documentation: http://localhost:8000/api/docs"
    echo "🌐 Backend API: http://localhost:8000/"
    echo "🛑 Press Ctrl+C to stop"
    echo ""
    echo "💡 If you need to install dependencies or models, use: ./run_app.sh"
    echo ""
else
    echo "❌ Backend failed to start. Try full setup: ./run_app.sh"
    exit 1
fi

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $BACKEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for the backend process
wait $BACKEND_PID
