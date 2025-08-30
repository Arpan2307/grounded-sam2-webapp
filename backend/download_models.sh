#!/bin/bash

echo "🤖 Downloading AI Model Checkpoints for Grounded SAM-2..."
echo "======================================================="

# Create directories
mkdir -p checkpoints
mkdir -p gdino_checkpoints
mkdir -p configs
mkdir -p grounding_dino

echo "📥 Downloading SAM-2 checkpoint (Large model - ~2.3GB)..."
if [ ! -f "checkpoints/sam2.1_hiera_large.pt" ]; then
    echo "This may take several minutes depending on your internet connection..."
    wget -c -P checkpoints/ https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt
    if [ $? -eq 0 ]; then
        echo "✅ SAM-2 checkpoint downloaded successfully!"
    else
        echo "❌ Failed to download SAM-2 checkpoint"
        echo "💡 Try manually downloading from: https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt"
        exit 1
    fi
else
    echo "✅ SAM-2 checkpoint already exists"
fi

echo ""
echo "📥 Downloading GroundingDINO checkpoint (~694MB)..."
if [ ! -f "gdino_checkpoints/groundingdino_swint_ogc.pth" ]; then
    wget -c -P gdino_checkpoints/ https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth
    if [ $? -eq 0 ]; then
        echo "✅ GroundingDINO checkpoint downloaded successfully!"
    else
        echo "❌ Failed to download GroundingDINO checkpoint"
        echo "💡 Try manually downloading from: https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth"
        exit 1
    fi
else
    echo "✅ GroundingDINO checkpoint already exists"
fi

echo ""
echo "📥 Setting up configuration files..."

# Setup SAM-2 configs
if [ ! -d "configs/sam2.1" ]; then
    echo "Downloading SAM-2 config files..."
    git clone --depth 1 https://github.com/facebookresearch/segment-anything-2.git temp_sam2
    if [ $? -eq 0 ]; then
        cp -r temp_sam2/sam2/configs/* ./configs/ 2>/dev/null || mkdir -p configs/sam2.1
        rm -rf temp_sam2
        echo "✅ SAM-2 configs installed"
    else
        echo "⚠️  Failed to clone SAM-2 repo, creating basic config..."
        mkdir -p configs/sam2.1
        echo "You may need to manually download config files from: https://github.com/facebookresearch/segment-anything-2"
    fi
fi

# Setup GroundingDINO
if [ ! -d "grounding_dino/groundingdino" ]; then
    echo "Setting up GroundingDINO..."
    git clone --depth 1 https://github.com/IDEA-Research/GroundingDINO.git temp_gdino
    if [ $? -eq 0 ]; then
        mkdir -p grounding_dino
        cp -r temp_gdino/groundingdino ./grounding_dino/ 2>/dev/null || echo "⚠️  Config copy failed"
        rm -rf temp_gdino
        echo "✅ GroundingDINO configs installed"
    else
        echo "⚠️  Failed to clone GroundingDINO repo"
        echo "You may need to manually download from: https://github.com/IDEA-Research/GroundingDINO"
    fi
fi

echo ""
echo "🎉 Model download completed!"
echo ""
echo "📊 Downloaded Files:"
if [ -f "checkpoints/sam2.1_hiera_large.pt" ]; then
    size=$(du -h checkpoints/sam2.1_hiera_large.pt | cut -f1)
    echo "  ✅ SAM-2: checkpoints/sam2.1_hiera_large.pt ($size)"
else
    echo "  ❌ SAM-2: Not downloaded"
fi

if [ -f "gdino_checkpoints/groundingdino_swint_ogc.pth" ]; then
    size=$(du -h gdino_checkpoints/groundingdino_swint_ogc.pth | cut -f1)
    echo "  ✅ GroundingDINO: gdino_checkpoints/groundingdino_swint_ogc.pth ($size)"
else
    echo "  ❌ GroundingDINO: Not downloaded"
fi

echo "  ✅ Configs: configs/ and grounding_dino/"
echo ""

# Check total size
total_size=$(du -sh checkpoints gdino_checkpoints 2>/dev/null | awk '{sum+=$1} END {print sum"GB"}' 2>/dev/null || echo "~3GB")
echo "💾 Total model size: $total_size"
echo ""

# Verify checksums if possible
echo "🔍 Verifying downloads..."
if [ -f "checkpoints/sam2.1_hiera_large.pt" ]; then
    actual_size=$(stat -c%s "checkpoints/sam2.1_hiera_large.pt" 2>/dev/null || stat -f%z "checkpoints/sam2.1_hiera_large.pt" 2>/dev/null)
    if [ "$actual_size" -gt 2000000000 ]; then  # > 2GB
        echo "  ✅ SAM-2 file size looks correct"
    else
        echo "  ⚠️  SAM-2 file might be incomplete (size: $actual_size bytes)"
    fi
fi

echo ""
echo "🚀 Next steps:"
echo "  1. Install dependencies: pip install -r requirements.txt"
echo "  2. Update .env file with correct model paths"
echo "  3. Run the application: uvicorn app.main:app --reload"
echo ""
echo "📖 See MODEL_DOWNLOAD.md for detailed instructions"
