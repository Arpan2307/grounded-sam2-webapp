# Model Checkpoints Download Guide

## Required Model Files

You need to download the following model checkpoints to run the Grounded SAM-2 application:

## 1. SAM-2 (Segment Anything Model 2)

### Download SAM-2 Checkpoint
```bash
# Create checkpoints directory
mkdir -p checkpoints

# Download SAM-2 Large model (recommended)
wget -P checkpoints/ https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt

# Alternative: SAM-2 Base model (smaller, faster)
# wget -P checkpoints/ https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt

# Alternative: SAM-2 Small model (fastest)
# wget -P checkpoints/ https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_small.pt
```

### SAM-2 Configuration Files
```bash
# Clone SAM-2 repository for config files
git clone https://github.com/facebookresearch/segment-anything-2.git sam2_repo
cp -r sam2_repo/sam2/configs ./configs
rm -rf sam2_repo
```

## 2. Grounding DINO

### Download Grounding DINO Checkpoint
```bash
# Create grounding dino directory
mkdir -p gdino_checkpoints

# Download GroundingDINO checkpoint
wget -P gdino_checkpoints/ https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth
```

### Grounding DINO Configuration
```bash
# Clone GroundingDINO repository
git clone https://github.com/IDEA-Research/GroundingDINO.git grounding_dino_repo

# Copy config files
mkdir -p grounding_dino
cp -r grounding_dino_repo/groundingdino ./grounding_dino/

# Install GroundingDINO
cd grounding_dino_repo
pip install -e .
cd ..
```

## 3. Complete Setup Script

Create a `download_models.sh` script:

```bash
#!/bin/bash

echo "🤖 Downloading AI Model Checkpoints..."
echo "======================================"

# Create directories
mkdir -p checkpoints
mkdir -p gdino_checkpoints
mkdir -p configs
mkdir -p grounding_dino

echo "📥 Downloading SAM-2 checkpoint..."
if [ ! -f "checkpoints/sam2.1_hiera_large.pt" ]; then
    wget -P checkpoints/ https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt
    if [ $? -eq 0 ]; then
        echo "✅ SAM-2 checkpoint downloaded successfully!"
    else
        echo "❌ Failed to download SAM-2 checkpoint"
        exit 1
    fi
else
    echo "✅ SAM-2 checkpoint already exists"
fi

echo "📥 Downloading GroundingDINO checkpoint..."
if [ ! -f "gdino_checkpoints/groundingdino_swint_ogc.pth" ]; then
    wget -P gdino_checkpoints/ https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth
    if [ $? -eq 0 ]; then
        echo "✅ GroundingDINO checkpoint downloaded successfully!"
    else
        echo "❌ Failed to download GroundingDINO checkpoint"
        exit 1
    fi
else
    echo "✅ GroundingDINO checkpoint already exists"
fi

echo "📥 Setting up configuration files..."

# Setup SAM-2 configs
if [ ! -d "configs/sam2.1" ]; then
    echo "Downloading SAM-2 config files..."
    git clone --depth 1 https://github.com/facebookresearch/segment-anything-2.git temp_sam2
    cp -r temp_sam2/sam2/configs/* ./configs/
    rm -rf temp_sam2
    echo "✅ SAM-2 configs installed"
fi

# Setup GroundingDINO
if [ ! -d "grounding_dino/groundingdino" ]; then
    echo "Setting up GroundingDINO..."
    git clone --depth 1 https://github.com/IDEA-Research/GroundingDINO.git temp_gdino
    cp -r temp_gdino/groundingdino ./grounding_dino/
    
    # Install GroundingDINO
    cd temp_gdino
    pip install -e . --quiet
    cd ..
    rm -rf temp_gdino
    echo "✅ GroundingDINO installed"
fi

echo ""
echo "🎉 All models downloaded and configured successfully!"
echo ""
echo "📊 Model Summary:"
echo "  SAM-2: checkpoints/sam2.1_hiera_large.pt"
echo "  GroundingDINO: gdino_checkpoints/groundingdino_swint_ogc.pth"
echo "  Configs: configs/ and grounding_dino/"
echo ""
echo "💾 Total download size: ~2.5GB"
echo "📁 Make sure you have enough disk space!"
```

## 4. File Structure After Download

After running the download script, your directory should look like:

```
backend/
├── checkpoints/
│   └── sam2.1_hiera_large.pt          # ~2.3GB
├── gdino_checkpoints/
│   └── groundingdino_swint_ogc.pth     # ~694MB
├── configs/
│   └── sam2.1/
│       └── sam2.1_hiera_l.yaml
└── grounding_dino/
    └── groundingdino/
        └── config/
            └── GroundingDINO_SwinT_OGC.py
```

## 5. Environment Variables

Update your `.env` file with the correct paths:

```bash
# Model Paths
SAM2_CHECKPOINT=./checkpoints/sam2.1_hiera_large.pt
MODEL_CFG=configs/sam2.1/sam2.1_hiera_l.yaml
GROUNDING_DINO_CONFIG=grounding_dino/groundingdino/config/GroundingDINO_SwinT_OGC.py
GROUNDING_DINO_CHECKPOINT=gdino_checkpoints/groundingdino_swint_ogc.pth
```

## 6. Alternative: Hugging Face Models

You can also use Hugging Face versions (easier setup):

```bash
# Install transformers
pip install transformers

# Models will be downloaded automatically when first used
# No manual download required!
```

## 7. Quick Test

Test if models are accessible:

```python
import os

# Check SAM-2
sam2_path = "checkpoints/sam2.1_hiera_large.pt"
print(f"SAM-2 exists: {os.path.exists(sam2_path)}")
print(f"SAM-2 size: {os.path.getsize(sam2_path) / (1024**3):.1f}GB" if os.path.exists(sam2_path) else "Not found")

# Check GroundingDINO
gdino_path = "gdino_checkpoints/groundingdino_swint_ogc.pth"
print(f"GroundingDINO exists: {os.path.exists(gdino_path)}")
print(f"GroundingDINO size: {os.path.getsize(gdino_path) / (1024**2):.0f}MB" if os.path.exists(gdino_path) else "Not found")
```

## 8. Troubleshooting

### Download Issues:
- **Slow download**: Use `wget -c` to resume interrupted downloads
- **Network issues**: Try using curl instead: `curl -L -o filename URL`
- **Permission denied**: Make sure you have write permissions

### Alternative Download Sources:
- **SAM-2**: https://github.com/facebookresearch/segment-anything-2
- **GroundingDINO**: https://github.com/IDEA-Research/GroundingDINO

### Storage Requirements:
- **SAM-2 Large**: ~2.3GB
- **GroundingDINO**: ~694MB  
- **Total**: ~3GB minimum free space required

Run this command to create and execute the download script:

```bash
# Make the script executable and run it
chmod +x download_models.sh
./download_models.sh
```
