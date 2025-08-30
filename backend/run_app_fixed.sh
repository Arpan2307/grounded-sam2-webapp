#!/bin/bash

# Grounded SAM-2 Web Application Startup Script
# This script sets up the environment and starts both backend and frontend servers

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

cd "$BACKEND_DIR"

echo "🚀 Starting Grounded SAM-2 Web Application..."
echo "============================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to activate virtual environment
activate_venv() {
    if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
        echo "✅ Virtual environment found"
        
        # Check if pip exists and is executable
        if [ ! -x "venv/bin/pip" ] && [ ! -x "venv/bin/pip3" ]; then
            echo "⚠️  Virtual environment appears corrupted (no pip). Recreating..."
            rm -rf venv
        else
            source venv/bin/activate
            
            # Verify activation and set commands
            if [[ "$VIRTUAL_ENV" != "" ]]; then
                echo "✅ Virtual environment activated ($VIRTUAL_ENV/bin/python)"
                PYTHON_CMD="$VIRTUAL_ENV/bin/python"
                # Check for pip or pip3
                if [ -x "$VIRTUAL_ENV/bin/pip" ]; then
                    PIP_CMD="$VIRTUAL_ENV/bin/pip"
                elif [ -x "$VIRTUAL_ENV/bin/pip3" ]; then
                    PIP_CMD="$VIRTUAL_ENV/bin/pip3"
                else
                    echo "⚠️  Virtual environment pip not found. Will use fallback."
                    PIP_CMD="pip3"
                fi
            else
                echo "⚠️  Virtual environment activation failed. Using system Python."
                PYTHON_CMD="python3"
                PIP_CMD="pip3"
            fi
        fi
    fi
    
    # Create venv if it doesn't exist or was removed
    if [ ! -d "venv" ]; then
        echo "⚠️  Creating new virtual environment..."
        if python3 -m venv venv; then
            echo "✅ Virtual environment created"
            
            if [ -f "venv/bin/activate" ]; then
                source venv/bin/activate
                
                # Upgrade pip first
                echo "   Upgrading pip..."
                python3 -m pip install --upgrade pip
                
                PYTHON_CMD="$VIRTUAL_ENV/bin/python"
                if [ -x "$VIRTUAL_ENV/bin/pip" ]; then
                    PIP_CMD="$VIRTUAL_ENV/bin/pip"
                else
                    PIP_CMD="python3 -m pip"
                fi
                echo "✅ Virtual environment activated ($VIRTUAL_ENV/bin/python)"
            else
                echo "⚠️  Failed to create virtual environment. Using system Python."
                PYTHON_CMD="python3"
                PIP_CMD="pip3"
            fi
        else
            echo "⚠️  Failed to create virtual environment. Using system Python."
            PYTHON_CMD="python3"
            PIP_CMD="pip3"
        fi
    fi
    
    echo "🔍 Using Python: $PYTHON_CMD"
    echo "🔍 Using pip: $PIP_CMD"
}

# Function to install dependencies with fallback
safe_pip_install() {
    # First try the configured pip command
    if [ -x "$PIP_CMD" ]; then
        if $PIP_CMD install "$@" 2>/dev/null; then
            return 0
        else
            echo "   ⚠️  Virtual environment pip failed, trying system pip..."
        fi
    else
        echo "   ⚠️  Virtual environment pip not executable, trying system pip..."
    fi
    
    # Fallback to system pip3
    if command_exists pip3; then
        if pip3 install "$@"; then
            return 0
        else
            echo "   ⚠️  System pip3 also failed for: $@"
        fi
    fi
    
    # Final fallback to python -m pip
    if command_exists python3; then
        if python3 -m pip install "$@"; then
            return 0
        else
            echo "   ⚠️  python3 -m pip also failed for: $@"
        fi
    fi
    
    echo "   ❌ All pip installation methods failed for: $@"
    return 1
}

# Function to check model files
check_model_files() {
    echo "🔍 Checking model files..."
    
    # Check SAM-2 checkpoint
    if [ -f "checkpoints/sam2_hiera_large.pt" ] || [ -f "checkpoints/sam2.1_hiera_large.pt" ]; then
        echo "✅ SAM-2 model found"
    else
        echo "⚠️  SAM-2 model not found. Please download it to checkpoints/"
    fi
    
    # Check Grounding DINO checkpoint
    if [ -f "gdino_checkpoints/groundingdino_swint_ogc.pth" ] || [ -f "checkpoints/groundingdino_swint_ogc.pth" ]; then
        echo "✅ Grounding DINO model found"
    else
        echo "⚠️  Grounding DINO model not found. Please download it to gdino_checkpoints/"
    fi
}

# Function to install Python dependencies
install_dependencies() {
    echo "📦 Installing Python dependencies..."
    
    echo "   Installing basic dependencies..."
    safe_pip_install fastapi uvicorn redis python-multipart pillow opencv-python
    safe_pip_install aiofiles jinja2 python-jose cryptography
    
    echo "   Installing PyTorch with CUDA support..."
    safe_pip_install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    
    echo "   Installing computer vision dependencies..."
    safe_pip_install transformers timm supervision
    
    # Install from requirements if exists
    if [ -f "requirements.txt" ]; then
        echo "   Installing from requirements.txt..."
        safe_pip_install -r requirements.txt
    fi
    
    echo "   Installing additional packages..."
    safe_pip_install numpy scipy matplotlib seaborn tqdm
    safe_pip_install gradio spaces huggingface-hub
    
    echo "✅ Dependencies installation completed"
}

# Function to verify critical dependencies
verify_dependencies() {
    echo "🔍 Verifying critical dependencies..."
    
    if $PYTHON_CMD -c "import fastapi, uvicorn" 2>/dev/null; then
        echo "✅ FastAPI and Uvicorn are available"
    else
        echo "❌ FastAPI or Uvicorn not found. Installing..."
        safe_pip_install fastapi uvicorn
    fi
}

# Function to setup required repositories
setup_repositories() {
    echo "🔄 Setting up required repositories..."
    
    cd "$PROJECT_ROOT"
    
    # Clone Grounded-SAM-2 if not exists
    if [ ! -d "Grounded-SAM-2" ]; then
        echo "   Cloning Grounded-SAM-2..."
        git clone https://github.com/IDEA-Research/Grounded-Segment-Anything-2.git Grounded-SAM-2
    else
        echo "   ✅ Grounded-SAM-2 already exists"
    fi
    
    # Clone segment-anything-2 if not exists
    if [ ! -d "segment-anything-2" ]; then
        echo "   Cloning Segment-Anything-2..."
        git clone https://github.com/facebookresearch/segment-anything-2.git segment-anything-2
    else
        echo "   ✅ SAM-2 already exists"
    fi
    
    # Install SAM-2 package
    if [ -d "segment-anything-2" ]; then
        echo "   Installing SAM-2 package..."
        cd segment-anything-2
        safe_pip_install -e .
        cd "$PROJECT_ROOT"
        echo "   ✅ SAM-2 package installed"
    fi
    
    # Install GroundingDINO dependencies
    if [ -d "Grounded-SAM-2" ]; then
        echo "   Installing GroundingDINO dependencies..."
        cd "Grounded-SAM-2"
        safe_pip_install -e .
        cd "$PROJECT_ROOT"
        echo "   ✅ GroundingDINO installed"
    fi
    
    echo "✅ Repository setup completed"
}

# Function to apply patches to SAM2 misc.py files
apply_sam2_patches() {
    echo "🔧 Applying patches to SAM2 repositories..."
    
    # Function to patch a single misc.py file
    patch_misc_file() {
        local misc_file="$1"
        local repo_name="$2"
        
        if [ ! -f "$misc_file" ]; then
            echo "   ⚠️  File not found: $misc_file"
            return
        fi
        
        echo "   Patching $repo_name misc.py..."
        
        # Create backup
        if [ ! -f "${misc_file}.original" ]; then
            cp "$misc_file" "${misc_file}.original"
            echo "     Created backup"
        fi
        
        # Check if already patched
        if grep -q "Failed to use compiled CUDA extension" "$misc_file"; then
            echo "     Already patched"
            return
        fi
        
        # Apply patch using Python
        $PYTHON_CMD -c "
import re

misc_file = '$misc_file'

with open(misc_file, 'r') as f:
    content = f.read()

# Patch 1: get_connected_components function
old_pattern = r'def get_connected_components\(mask\):.*?from sam2 import _C.*?return _C\.get_connected_componnets\(mask\.to\(torch\.uint8\)\.contiguous\(\)\)'

new_implementation = '''def get_connected_components(mask):
    \"\"\"
    Get the connected components (8-connectivity) of binary masks of shape (N, 1, H, W).

    Inputs:
    - mask: A binary mask tensor of shape (N, 1, H, W), where 1 is foreground and 0 is
            background.

    Outputs:
    - labels: A tensor of shape (N, 1, H, W) containing the connected component labels
              for foreground pixels and 0 for background pixels.
    - counts: A tensor of shape (N, 1, H, W) containing the area of the connected
              components for foreground pixels and 0 for background pixels.
    \"\"\"
    try:
        from sam2 import _C
        return _C.get_connected_componnets(mask.to(torch.uint8).contiguous())
    except (ImportError, AttributeError, NameError) as e:
        import warnings
        warnings.warn(f\"Failed to use compiled CUDA extension for connected components: {e}. Using CPU fallback.\", UserWarning)
        # CPU fallback using cv2
        try:
            import cv2
            import numpy as np
            
            # Convert to numpy for processing
            masks_np = mask.cpu().numpy().astype(np.uint8)
            N, _, H, W = masks_np.shape
            
            labels = np.zeros_like(masks_np, dtype=np.int32)
            counts = np.zeros_like(masks_np, dtype=np.int32)
            
            for i in range(N):
                # Get connected components using OpenCV
                num_labels, label_img = cv2.connectedComponents(masks_np[i, 0])
                labels[i, 0] = label_img
                
                # Calculate component areas
                unique_labels, label_counts = np.unique(label_img, return_counts=True)
                count_map = np.zeros_like(label_img)
                for label_id, count in zip(unique_labels, label_counts):
                    if label_id > 0:  # Skip background
                        count_map[label_img == label_id] = count
                counts[i, 0] = count_map
            
            return torch.from_numpy(labels).to(mask.device), torch.from_numpy(counts).to(mask.device)
            
        except ImportError:
            # Final fallback - just return the mask as labels with count 1
            warnings.warn(\"OpenCV not available. Using basic fallback for connected components.\", UserWarning)
            labels = mask.to(torch.int32)
            counts = mask.to(torch.int32)
            return labels, counts'''

# Apply the patch
if re.search(old_pattern, content, re.DOTALL):
    content = re.sub(old_pattern, new_implementation, content, flags=re.DOTALL)
    print('     Applied connected components patch')
    patched = True
else:
    print('     Connected components already patched or pattern not found')
    patched = False

# Patch 2: get_sdpa_settings function for CUDA error handling
sdpa_pattern = r'def get_sdpa_settings\(\):.*?return old_gpu, use_flash_attn, math_kernel_on'

if re.search(sdpa_pattern, content, re.DOTALL) and 'device_count = torch.cuda.device_count()' not in content:
    sdpa_replacement = '''def get_sdpa_settings():
    if torch.cuda.is_available():
        try:
            # Try to access CUDA device properties, handle potential errors
            device_count = torch.cuda.device_count()
            if device_count == 0:
                # CUDA available but no devices
                old_gpu = True
                use_flash_attn = False
                math_kernel_on = True
            else:
                old_gpu = torch.cuda.get_device_properties(0).major < 7
                # only use Flash Attention on Ampere (8.0) or newer GPUs
                use_flash_attn = torch.cuda.get_device_properties(0).major >= 8
                if not use_flash_attn:
                    warnings.warn(
                        \"Flash Attention is disabled as it requires a GPU with Ampere (8.0) CUDA capability.\",
                        category=UserWarning,
                        stacklevel=2,
                    )
                # keep math kernel for PyTorch versions before 2.2 (Flash Attention v2 is only
                # available on PyTorch 2.2+, while Flash Attention v1 cannot handle all cases)
                pytorch_version = tuple(int(v) for v in torch.__version__.split(\".\")[:2])
                if pytorch_version < (2, 2):
                    warnings.warn(
                        f\"You are using PyTorch {torch.__version__} without Flash Attention v2 support. \"
                        \"Consider upgrading to PyTorch 2.2+ for Flash Attention v2 (which could be faster).\",
                        category=UserWarning,
                        stacklevel=2,
                    )
                math_kernel_on = pytorch_version < (2, 2) or not use_flash_attn
        except (RuntimeError, AssertionError) as e:
            # Handle CUDA device errors gracefully
            import warnings
            warnings.warn(f\"CUDA device error: {e}. Falling back to CPU settings.\", UserWarning)
            old_gpu = True
            use_flash_attn = False
            math_kernel_on = True
    else:
        old_gpu = True
        use_flash_attn = False
        math_kernel_on = True

    return old_gpu, use_flash_attn, math_kernel_on'''
    
    content = re.sub(sdpa_pattern, sdpa_replacement, content, flags=re.DOTALL)
    print('     Applied SDPA settings patch')
    patched = True

if patched:
    with open(misc_file, 'w') as f:
        f.write(content)
    print('     ✅ Patches applied successfully')
else:
    print('     ℹ️  No patches applied')
"
    }
    
    # Apply patches to both repositories
    if [ -d "$PROJECT_ROOT/Grounded-SAM-2/sam2/utils" ]; then
        patch_misc_file "$PROJECT_ROOT/Grounded-SAM-2/sam2/utils/misc.py" "Grounded-SAM-2"
    fi
    
    if [ -d "$PROJECT_ROOT/segment-anything-2/sam2/utils" ]; then
        patch_misc_file "$PROJECT_ROOT/segment-anything-2/sam2/utils/misc.py" "segment-anything-2"
    fi
    
    echo "✅ SAM2 patches applied"
}

# Function to check Redis
check_redis() {
    echo "🔧 Checking Redis connection..."
    
    if command_exists redis-cli; then
        if redis-cli ping > /dev/null 2>&1; then
            echo "✅ Redis is running"
            return 0
        fi
    fi
    
    echo "⚠️  Redis not running. Starting Redis server..."
    
    if command_exists redis-server; then
        redis-server --daemonize yes --port 6379
        sleep 2
        
        if redis-cli ping > /dev/null 2>&1; then
            echo "✅ Redis started successfully"
            return 0
        fi
    fi
    
    echo "❌ Redis not available. Please install and start Redis manually."
    return 1
}

# Function to create necessary directories
create_directories() {
    echo "📁 Creating directories..."
    
    mkdir -p uploads outputs temp_frames tracking_results checkpoints gdino_checkpoints
    
    echo "✅ Directories created"
}

# Function to setup environment variables and paths
setup_environment() {
    echo "🔧 Setting up Python paths and environment..."
    
    # Add current directory to Python path
    export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/Grounded-SAM-2:$PROJECT_ROOT/segment-anything-2:$PYTHONPATH"
    
    # Set Grounding DINO config path
    export GROUNDING_DINO_CONFIG_PATH="$PROJECT_ROOT/Grounded-SAM-2/grounding_dino/groundingdino/config"
    
    echo "✅ Grounding DINO config path set"
    echo "✅ Python paths and environment configured"
}

# Function to start frontend server
start_frontend() {
    echo "🌐 Starting frontend server..."
    
    FRONTEND_DIR="$PROJECT_ROOT/frontend"
    
    if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
        cd "$FRONTEND_DIR"
        
        # Check if npm is available
        if ! command_exists npm; then
            echo "⚠️  npm not found. Please install Node.js and npm to run the React frontend."
            echo "   For now, using FastAPI static file serving only."
            echo "   Frontend will be available at: http://localhost:8000/static/simple.html"
            cd "$BACKEND_DIR"
            return
        fi
        
        if [ ! -d "node_modules" ]; then
            echo "   Installing frontend dependencies..."
            if ! npm install; then
                echo "⚠️  npm install failed. Using FastAPI static file serving only."
                cd "$BACKEND_DIR"
                return
            fi
        fi
        
        # Start frontend server in background
        echo "   Starting React development server..."
        npm start > ../backend/frontend.log 2>&1 &
        FRONTEND_PID=$!
        
        # Wait a moment for startup
        sleep 3
        
        # Check if frontend is running
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo "✅ Frontend server started on port 3000"
            echo "   React frontend: http://localhost:3000/simple.html"
        else
            echo "⚠️  Frontend server failed to start. Check frontend.log for details."
            echo "   Using FastAPI static file serving as fallback."
        fi
        
        cd "$BACKEND_DIR"
    else
        echo "⚠️  Frontend directory not found. Serving via FastAPI static files only."
    fi
    
    # Always show the FastAPI static option as it's available regardless of npm
    echo "   Static frontend: http://localhost:8000/static/simple.html"
}

# Function to start FastAPI backend server
start_backend() {
    echo "🚀 Starting FastAPI server..."
    
    cd "$BACKEND_DIR"
    
    # Start the server with auto-reload
    $PYTHON_CMD -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Main execution flow
main() {
    # Setup steps
    activate_venv
    check_model_files
    install_dependencies
    verify_dependencies
    setup_repositories
    apply_sam2_patches
    check_redis
    create_directories
    setup_environment
    
    echo ""
    echo "🎉 Starting the application..."
    echo "📱 Frontend options:"
    echo "   - FastAPI Static: http://localhost:8000/static/simple.html (always available)"
    if command_exists npm; then
        echo "   - React Dev Server: http://localhost:3000/simple.html (if npm available)"
    else
        echo "   - React Dev Server: Not available (npm not installed)"
    fi
    echo "🔧 API Documentation: http://localhost:8000/api/docs"
    echo "🌐 Backend API: http://localhost:8000/"
    echo "🛑 Press Ctrl+C to stop"
    echo ""
    
    # Start services
    start_frontend
    start_backend
}

# Handle script termination
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    
    # Kill background processes
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    exit 0
}

trap cleanup SIGINT SIGTERM

# Run main function
main "$@"
