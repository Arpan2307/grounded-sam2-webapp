#!/bin/bash

echo "🔧 Setting up Grounded SAM-2 Backend Environment"
echo "================================================"

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install base dependencies first
echo "📚 Installing base dependencies..."
pip install -r requirements-base.txt

# Install PyTorch with CPU or CUDA support
echo "🔥 Installing PyTorch..."
if command -v nvidia-smi &> /dev/null && nvidia-smi > /dev/null 2>&1; then
    echo "🎮 CUDA detected - installing PyTorch with CUDA support..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
else
    echo "💻 No CUDA detected - installing CPU-only PyTorch..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Install additional ML dependencies
echo "🤖 Installing additional ML dependencies..."
pip install transformers>=4.20.0 timm>=0.6.0

# Try to install computer vision utilities
echo "👁️  Installing computer vision utilities..."
pip install supervision || echo "⚠️  Warning: Could not install supervision - will work without advanced CV utilities"

# Install Celery for background tasks
echo "⚙️  Installing task queue support..."
pip install celery || echo "⚠️  Warning: Could not install celery - background tasks may not work"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads outputs temp_frames tracking_results checkpoints

echo ""
echo "✅ Setup complete! Next steps:"
echo "   1. Download model checkpoints (see DEVELOPMENT.md)"
echo "   2. Set up Grounding DINO and SAM-2 repositories"
echo "   3. Run: uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload"
echo ""
echo "🔍 To verify installation:"
echo "   python3 -c \"import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')\""
