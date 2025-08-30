#!/bin/bash

# Navigate to the frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
else
    echo "Dependencies already installed, checking for updates..."
    npm update
fi

# Set environment variables
export REACT_APP_API_BASE_URL=http://localhost:5000

# Start the frontend development server
echo "Starting frontend development server..."
npm start