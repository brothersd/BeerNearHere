#!/bin/bash
# Production startup script for Beer Near Here

set -e

echo "================================================"
echo "[BEER NEAR HERE] Production Environment Setup"
echo "================================================"

# Verify .env file exists
if [ ! -f ".env" ]; then
    echo "[!] ERROR: .env file not found!"
    exit 1
fi

echo "[*] Environment variables loaded from .env"

# Build and start services in production mode (using Docker Compose v2 syntax)
echo "================================================"
echo "[BUILDING & STARTING SERVICES]"
echo "================================================"

docker compose up --build -d

echo ""
echo "================================================"
echo "[SUCCESS] Production environment started!"
echo "================================================"
echo ""
echo "Access your application at: http://localhost"
echo ""
echo "To view logs:"
echo "  docker compose logs -f"
echo ""
echo "To stop the services:"
echo "  docker compose down"
echo ""
