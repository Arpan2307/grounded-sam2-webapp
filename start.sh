#!/bin/bash

# Grounded SAM-2 Web Application Startup Script

echo "🚀 Starting Grounded SAM-2 Web Application..."
echo "================================================"

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✅ Docker found"
    echo "Starting with Docker Compose..."
    echo ""
    
    # Check if docker-compose.yml exists
    if [ -f "docker-compose.yml" ]; then
        echo "📦 Building and starting containers..."
        docker-compose up --build -d
        
        echo ""
        echo "🌟 Application is starting up!"
        echo "📱 Frontend: http://localhost:3000"
        echo "🔧 Backend API: http://localhost:5000"
        echo "📚 API Docs: http://localhost:5000/api/docs"
        echo ""
        echo "⏳ Please wait a few moments for all services to be ready..."
        echo "📋 View logs with: docker-compose logs -f"
        echo "🛑 Stop services with: docker-compose down"
    else
        echo "❌ docker-compose.yml not found!"
        exit 1
    fi
else
    echo "⚠️  Docker not found. Starting manually..."
    echo ""
    
    # Start backend
    echo "🔧 Starting backend..."
    if [ -f "scripts/start_backend.sh" ]; then
        chmod +x scripts/start_backend.sh
        ./scripts/start_backend.sh &
        BACKEND_PID=$!
        echo "✅ Backend started (PID: $BACKEND_PID)"
    else
        echo "❌ Backend startup script not found!"
        exit 1
    fi
    
    # Wait a moment for backend to start
    sleep 3
    
    # Start frontend
    echo "📱 Starting frontend..."
    if [ -f "scripts/start_frontend.sh" ]; then
        chmod +x scripts/start_frontend.sh
        ./scripts/start_frontend.sh &
        FRONTEND_PID=$!
        echo "✅ Frontend started (PID: $FRONTEND_PID)"
    else
        echo "❌ Frontend startup script not found!"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    echo ""
    echo "🌟 Application is running!"
    echo "📱 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:5000"
    echo "📚 API Docs: http://localhost:5000/api/docs"
    echo ""
    echo "🛑 To stop the application, press Ctrl+C"
    
    # Wait for both processes
    wait $BACKEND_PID $FRONTEND_PID
fi
