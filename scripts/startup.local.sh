#!/bin/bash

# =============================================================================
# Beer Near Here - Local Startup Script
# =============================================================================

set -e  # Exit immediately if a command exits with a non-zero status

echo "================================================"
echo "[BEER NEAR HERE] Local Environment Setup"
echo "================================================"

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo "[!] ERROR: Docker or Docker Compose not found!"
    echo "Please install Docker Desktop or Docker Engine first."
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "[!] ERROR: Git not found!"
    echo "Please install Git first."
    exit 1
fi

echo "[*] Checking prerequisites..."
echo "[*] Git version:"
git --version
echo "[*] Docker version:"
docker --version

# Clone the repository if it doesn't exist locally
REPO_URL="https://github.com/brothersd/BeerNearHere.git"
PROJECT_NAME="BeerNearHere"

if [ ! -d "$PROJECT_NAME" ]; then
    echo "[*] Cloning repository from $REPO_URL..."
    git clone "$REPO_URL" "$PROJECT_NAME"
else
    echo "[*] Repository already exists, pulling latest changes..."
    cd "$PROJECT_NAME"
    git pull origin main
    cd ..
fi

# Change to project directory
cd "$PROJECT_NAME"

echo "[*] Checking for .env file..."

# Check if .env file exists in the cloned repository
if [ ! -f ".env" ]; then
    echo "[!] WARNING: .env file not found!"
    echo "[*] Copy the .env file into the root folder of the app & re-run this script..."
    exit 1
else
    echo "[*] .env file already exists"
fi

echo "[*] Checking for Walmart private key..."

# Check if Walmart private key exists in certs directory
if [ ! -f "./certs/WM_IO_private_key.pem" ]; then
    echo "[!] WARNING: Walmart private key not found!"
    echo "[*] Copy the WM_IO_private_key.pem file into the ./certs folder..."
    exit 1
else
    echo "[*] Walmart private key exists"
fi

echo ""
echo "================================================"
echo "[BUILDING & STARTING SERVICES]"
echo "================================================"

# Build and start services using Docker Compose
echo "[*] Building and starting all services..."
docker compose up --build -d

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "[SUCCESS] Local environment started successfully!"
    echo "================================================"
    echo ""
    echo "Your application is now running:"
    echo "- Backend: http://localhost:8000 (Django API)"
    echo "- Frontend: http://localhost:3000 (React App)" 
    echo ""
    echo "To view logs:"
    echo "  docker compose logs -f"
    echo ""
    echo "To stop the services:"
    echo "  docker compose down"
    echo ""
else
    echo "[!] ERROR: Failed to start services"
    exit 1
fi

echo "================================================"
echo "[READY] Setup complete!"
echo "================================================"
