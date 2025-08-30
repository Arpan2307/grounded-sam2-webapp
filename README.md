# Grounded SAM-2 Video Tracking Web Application

## Overview

This web application provides an intuitive interface for object detection and tracking in videos using state-of-the-art AI models: **Grounding DINO** for object detection and **SAM-2** (Segment Anything Model 2) for precise segmentation and tracking.

### Key Features

- 🎥 **Video Upload**: Support for multiple video formats (MP4, AVI, MOV, MKV, WEBM)
- 🎯 **Text-Based Detection**: Describe objects in natural language (e.g., "cat", "person walking", "red car")
- 🎨 **Real-time Processing**: Live progress updates during video processing
- 📊 **Visual Results**: Download annotated videos with bounding boxes, masks, and tracking paths
- 🌐 **Web Interface**: Clean, modern UI built with React
- 🐳 **Docker Support**: Easy deployment with Docker containers
- ⚡ **GPU Acceleration**: CUDA support for fast processing

## Quick Start (Git Users)

### First time setup:
```bash
# Clone and setup
git clone https://github.com/Arpan2307/grounding-sam2-webapp
cd grounded-sam2-webapp

# One-time setup (creates directories, checks dependencies)
bash setup.sh

# Create virtual environment 
cd backend
python3 -m venv venv
```

### Every time after:
```bash
cd backend
bash run_app.sh
```

### What gets auto-handled:
- ✅ Virtual environment activation
- ✅ Dependencies installation
- ✅ Model availability checks
- ✅ Required repositories cloning
- ✅ Server startup

### What you need to do once:
- ⚙️ Create virtual environment (`python3 -m venv venv`)
- 📥 Download model files (links provided in setup)

## Architecture

```
grounded-sam2-webapp/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Core business logic
│   │   ├── utils/          # Utility functions
│   │   ├── config.py       # Configuration
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Backend container
│   └── .env              # Environment variables
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API client
│   │   └── App.tsx        # Main application
│   ├── package.json       # Node dependencies
│   └── Dockerfile        # Frontend container
├── docker-compose.yml     # Multi-container setup
└── scripts/              # Helper scripts
    ├── start_backend.sh
    └── start_frontend.sh
```

## Prerequisites

### System Requirements
- **OS**: Linux (recommended), macOS, or Windows with WSL2
- **GPU**: NVIDIA GPU with CUDA 11.8+ (recommended for performance)
- **Memory**: 8GB RAM minimum, 16GB+ recommended
- **Storage**: 10GB free space for models and temporary files

### Software Dependencies
- **Python**: 3.8-3.11
- **Node.js**: 16+ and npm
- **Docker** (optional): For containerized deployment
- **Git**: For cloning repositories

### Model Files Required
You need to download the following model files:

1. **SAM-2 Checkpoints**:
   ```bash
   # Create checkpoints directory
   mkdir -p checkpoints
   
   # Download SAM-2 model (adjust URL based on official release)
   wget -O checkpoints/sam2.1_hiera_large.pt https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt
   ```

2. **Grounding DINO**:
   ```bash
   # Create grounding dino directory
   mkdir -p gdino_checkpoints
   
   # Download GroundingDINO checkpoint
   wget -O gdino_checkpoints/groundingdino_swint_ogc.pth https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth
   ```

## Installation & Setup

### Option 1: Quick Setup with Automated Script (Recommended)

**First Time Setup:**
```bash
# Clone the repository
git clone <repository-url>
cd grounded-sam2-webapp

# Create virtual environment (one-time only)
cd backend
python3 -m venv venv

# Run automated setup script
bash run_app.sh
```

**After First Time:**
```bash
cd backend
bash run_app.sh
```

**What the script handles automatically:**
- ✅ Virtual environment activation
- ✅ Python dependencies installation  
- ✅ Required repositories cloning (SAM-2, GroundingDINO)
- ✅ Model file availability checks
- ✅ Redis server connection
- ✅ Backend server startup

**What you need once:**
- ⚙️ Create virtual environment (`python3 -m venv venv`) 
- 📥 Download model files (see prerequisites section)

### Option 2: Docker Deployment

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd grounded-sam2-webapp
   ```

2. **Download model files** (see prerequisites section above)

3. **Start services**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

### Option 3: Manual Setup

#### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

5. **Start backend server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

#### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm start
   ```

## Usage Guide

### Step 1: Upload Video
- Click the upload area or drag and drop your video file
- Supported formats: MP4, AVI, MOV, MKV, WEBM
- Maximum file size: 100MB (configurable)

### Step 2: Set Detection Prompt
- Enter a text description of objects you want to track
- Examples:
  - `"cat"` - Track cats in the video
  - `"person walking"` - Track walking people
  - `"red car"` - Track red colored cars
  - `"dog playing with ball"` - Track dogs playing with balls

### Step 3: Process Video
- Click "Start Tracking" to begin processing
- Monitor real-time progress updates
- Processing time depends on video length and complexity

### Step 4: Download Results
- View the annotated video with tracking results
- Download the processed video file
- Start a new tracking session if needed

## API Documentation

The backend provides a RESTful API with the following endpoints:

### Core Endpoints

- **POST /api/upload** - Upload video file
- **POST /api/track** - Start tracking task
- **GET /api/status/{task_id}** - Get task status
- **GET /api/download/{task_id}** - Download result video
- **WebSocket /api/ws/{task_id}** - Real-time status updates

### Example API Usage

```python
import requests

# Upload video
with open('video.mp4', 'rb') as f:
    response = requests.post('http://localhost:8000/api/upload', 
                           files={'file': f})
file_id = response.json()['file_id']

# Start tracking
data = {
    'file_id': file_id,
    'text_prompt': 'cat',
    'prompt_type': 'box',
    'box_threshold': 0.35,
    'text_threshold': 0.25
}
response = requests.post('http://localhost:8000/api/track', data=data)
task_id = response.json()['task_id']

# Check status
response = requests.get(f'http://localhost:8000/api/status/{task_id}')
print(response.json())
```

## Configuration

### Environment Variables (.env)

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Model Paths
GROUNDING_DINO_CONFIG=grounding_dino/groundingdino/config/GroundingDINO_SwinT_OGC.py
GROUNDING_DINO_CHECKPOINT=gdino_checkpoints/groundingdino_swint_ogc.pth
SAM2_CHECKPOINT=./checkpoints/sam2.1_hiera_large.pt
MODEL_CFG=configs/sam2.1/sam2.1_hiera_l.yaml

# Detection Thresholds
BOX_THRESHOLD=0.35
TEXT_THRESHOLD=0.25

# File Processing
MAX_FILE_SIZE=104857600  # 100MB
UPLOAD_FOLDER=./uploads
OUTPUT_FOLDER=./outputs

# Redis (for background tasks)
REDIS_HOST=redis
REDIS_PORT=6379
```

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**:
   - Reduce video resolution
   - Process shorter video segments
   - Use CPU-only mode (slower)

2. **Model Not Found**:
   - Ensure model files are downloaded to correct paths
   - Check file permissions

3. **Upload Fails**:
   - Check file size limits
   - Verify supported video formats
   - Check disk space

4. **Slow Processing**:
   - Verify GPU is being used
   - Check system resources
   - Consider using smaller video files for testing

### Logs and Debugging

- Backend logs: Check console output or container logs
- Frontend logs: Check browser developer console
- Enable debug mode in `.env` file

## Development

### Adding New Features

1. **Backend**: Add new endpoints in `app/api/`
2. **Frontend**: Add new components in `src/components/`
3. **Models**: Add new Pydantic models in `app/models/`

### Testing

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests  
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Meta AI**: SAM-2 (Segment Anything Model 2)
- **IDEA Research**: Grounding DINO
- **Facebook Research**: Original SAM model
- **Open Source Community**: Various supporting libraries

## Support

For questions, issues, or contributions:
- 📧 Create an issue on GitHub
- 📖 Check the documentation
- 💬 Join our community discussions

---

**Note**: This application requires significant computational resources for optimal performance. Consider using cloud GPUs for production deployments.

- **tsconfig.json**: TypeScript configuration file.

- **public/**: Contains static files.
  - **index.html**: Main HTML file for the frontend application.

- **src/**: Contains the React application source code.
  - **index.tsx**: Entry point for the React application.
  - **App.tsx**: Main App component managing the layout and state.
  - **components/**: Contains reusable components.
    - **UploadForm.tsx**: Component for uploading video files.
    - **PromptInput.tsx**: Component for inputting text prompts.
    - **VideoPlayer.tsx**: Component for displaying processed video output.
    - **ProgressBar.tsx**: Component for showing processing progress.

### Checkpoints
- **checkpoints/README.md**: Documentation related to model checkpoints.

### Scripts
- **scripts/start_backend.sh**: Script to start the backend server.

- **scripts/start_frontend.sh**: Script to start the frontend development server.

### Docker
- **docker-compose.yml**: Defines services and configurations for running the application using Docker Compose.

### Testing
- **tests/**: Contains unit tests for both backend and frontend components.
  - **backend/test_api.py**: Unit tests for backend API endpoints.
  - **frontend/App.test.tsx**: Unit tests for frontend App component.

## Setup Instructions
1. **Clone the Repository**
   ```
   git clone <repository-url>
   cd grounded-sam2-webapp
   ```

2. **Backend Setup**
   - Navigate to the `backend` directory.
   - Install dependencies:
     ```
     pip install -r requirements.txt
     ```
   - Configure environment variables in the `.env` file.
   - Start the backend server:
     ```
     ./scripts/start_backend.sh
     ```

3. **Frontend Setup**
   - Navigate to the `frontend` directory.
   - Install dependencies:
     ```
     npm install
     ```
   - Start the frontend development server:
     ```
     ./scripts/start_frontend.sh
     ```

4. **Access the Application**
   - Open your web browser and go to `http://localhost:3000` to access the application.

## Usage
- Upload a video file using the upload form.
- Input a text prompt for object detection.
- View the processed video output with detected objects annotated.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.