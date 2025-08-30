# Development Setup Guide

## Quick Start

### Option 1: Simple HTML Frontend (Recommended for Testing)

1. **Start the backend server:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
   ```

2. **Open the simple frontend:**
   Open `frontend/public/simple.html` in your web browser, or serve it locally:
   ```bash
   cd frontend/public
   python -m http.server 3000
   # Then visit: http://localhost:3000/simple.html
   ```

### Option 2: React Development

1. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start both servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

### Option 3: Docker Compose

```bash
docker-compose up --build
```

## Model Setup

Before running the application, you need to download the required model files:

### 1. Create directories
```bash
mkdir -p checkpoints
mkdir -p gdino_checkpoints
```

### 2. Download SAM-2 checkpoint
```bash
# Option A: Download directly (if available)
wget -O checkpoints/sam2.1_hiera_large.pt https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt

# Option B: Use official SAM-2 repository
git clone https://github.com/facebookresearch/segment-anything-2.git
# Follow their download instructions
```

### 3. Download Grounding DINO checkpoint
```bash
wget -O gdino_checkpoints/groundingdino_swint_ogc.pth https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth
```

### 4. Setup Grounding DINO
```bash
git clone https://github.com/IDEA-Research/GroundingDINO.git
cd GroundingDINO
pip install -e .
```

## Testing the API

### Upload a video
```bash
curl -X POST "http://localhost:5000/api/upload" \
     -F "file=@test_video.mp4"
```

### Start tracking
```bash
curl -X POST "http://localhost:5000/api/track" \
     -F "file_id=YOUR_FILE_ID" \
     -F "text_prompt=cat" \
     -F "prompt_type=box"
```

### Check status
```bash
curl "http://localhost:5000/api/status/YOUR_TASK_ID"
```

### Download result
```bash
curl -o result.mp4 "http://localhost:5000/api/download/YOUR_TASK_ID"
```

## Troubleshooting

### Backend Issues

1. **Import errors**: Make sure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. **CUDA issues**: Check if CUDA is available:
   ```python
   import torch
   print(torch.cuda.is_available())
   ```

3. **Model not found**: Verify model files are in the correct locations

### Frontend Issues

1. **CORS errors**: Make sure backend is running on port 5000
2. **Upload fails**: Check file size and format
3. **React compilation errors**: Use the simple HTML version instead

## Development Tips

1. **Use simple.html for quick testing** - It doesn't require React compilation
2. **Check browser developer console** for frontend errors
3. **Monitor backend logs** for processing status
4. **Use small video files** for faster testing
5. **Enable debug mode** in .env file for detailed logs
