@echo off

REM This script builds the Docker images for the frontend and backend.

echo "Building backend image..."
docker build -t hackathon-backend:latest .\backend
if %errorlevel% neq 0 (
    echo "Failed to build backend image"
    exit /b %errorlevel%
)


echo "Building frontend image..."
docker build -t hackathon-frontend:latest .\frontend
if %errorlevel% neq 0 (
    echo "Failed to build frontend image"
    exit /b %errorlevel%
)

echo "Docker images built successfully!"
