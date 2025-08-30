#!/bin/bash

echo "🚀 Starting Grounded SAM-2 Web Application..."
echo "============================================="

# Check if we're in the correct directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    echo "   cd /path/to/grounded-sam2-webapp/backend"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not detected. Activating..."
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ Virtual environment not found. Please create one:"
        echo "   python3 -m venv venv"
        echo "   source venv/bin/activate"
        exit 1
    fi
fi

# Check if models are downloaded
echo "🔍 Checking model files..."
if [ ! -f "checkpoints/sam2.1_hiera_large.pt" ]; then
    echo "❌ SAM-2 model not found. Please run: ./download_models.sh"
    exit 1
else
    echo "✅ SAM-2 model found"
fi

if [ ! -f "gdino_checkpoints/groundingdino_swint_ogc.pth" ]; then
    echo "❌ Grounding DINO model not found. Please run: ./download_models.sh"
    exit 1
else
    echo "✅ Grounding DINO model found"
fi

# Install/update dependencies
echo "📦 Checking Python dependencies..."
pip install -r requirements-minimal.txt --quiet
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️  Some dependencies failed to install, trying minimal setup..."
    pip install fastapi uvicorn python-multipart aiofiles redis python-dotenv --quiet
fi

# Check if Redis is running (optional)
echo "🔧 Checking Redis connection..."
python3 -c "
import redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=1)
    r.ping()
    print('✅ Redis is running')
except:
    print('⚠️  Redis not running - background tasks will be disabled')
" 2>/dev/null

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads outputs temp_frames tracking_results
echo "✅ Directories created"

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo ""
echo "🎉 Starting the application..."
echo "📱 Frontend: http://localhost:3000/simple.html"
echo "📱 Alternative frontend: http://localhost:5000/static/simple.html"
echo "🔧 API Documentation: http://localhost:5000/api/docs"
echo "🌐 Backend API: http://localhost:5000/"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Start frontend server in background
if [ -d "../frontend/public" ]; then
    echo "🌐 Starting frontend server..."
    cd ../frontend/public
    python3 -m http.server 3000 > /dev/null 2>&1 &
    FRONTEND_PID=$!
    cd ../../backend
    echo "✅ Frontend server started on port 3000"
    sleep 1  # Give frontend time to start
else
    echo "⚠️  Frontend directory not found. Using static serving from backend."
fi

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend server stopped"
    fi
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
