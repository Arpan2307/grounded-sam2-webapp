#!/bin/bash

echo "🔧 First-time setup for Grounded SAM-2 Web Application"
echo "===================================================="

# Check if we're in the project root
if [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   (grounded-sam2-webapp/)"
    exit 1
fi

# Create backend virtual environment
echo "📦 Creating virtual environment..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p checkpoints gdino_checkpoints uploads outputs temp
echo "✅ Directories created"

# Check for model files
echo "🔍 Checking for model files..."

if [ ! -f "checkpoints/sam2.1_hiera_large.pt" ]; then
    echo "⚠️  SAM-2 model not found"
    echo "📥 Download it with:"
    echo "   wget -O backend/checkpoints/sam2.1_hiera_large.pt https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt"
else
    echo "✅ SAM-2 model found"
fi

if [ ! -f "gdino_checkpoints/groundingdino_swint_ogc.pth" ]; then
    echo "⚠️  Grounding DINO model not found"
    echo "📥 Download it with:"
    echo "   wget -O backend/gdino_checkpoints/groundingdino_swint_ogc.pth https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth"
else
    echo "✅ Grounding DINO model found"
fi

cd ..

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Download model files (if not already done)"
echo "   2. cd backend && bash run_app.sh"
echo ""
echo "🔗 Useful links:"
echo "   • SAM-2 model: https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt"
echo "   • Grounding DINO model: https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth"
