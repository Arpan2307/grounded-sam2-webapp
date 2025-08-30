FROM nvidia/cuda:11.8-devel-ubuntu20.04

# Prevent interactive installations
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    wget \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set Python alias
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set the working directory
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PyTorch with CUDA support
RUN pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cu118

# Create necessary directories
RUN mkdir -p /app/uploads /app/outputs /app/temp_frames /app/tracking_results /app/checkpoints

# Copy the application code
COPY app ./app
COPY .env .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose the port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Command to run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]