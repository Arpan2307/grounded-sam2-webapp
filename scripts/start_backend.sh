#!/bin/bash

# Navigate to the backend directory
cd backend

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install the required Python packages
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads outputs temp_frames tracking_results checkpoints

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the backend application
echo "Starting backend server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload