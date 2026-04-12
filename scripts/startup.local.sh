#!/bin/bash

# =============================================================================
# Beer Near Here - Local Startup Script
# =============================================================================

set -e  # Exit immediately if a command exits with a non-zero status

docker compose down

echo ""
echo "================================================"
echo "[BUILDING & STARTING SERVICES]"
echo "================================================"

# Build and start services using Docker Compose
echo "[*] Building and starting all services..."
docker compose up --build -d

echo "Waiting for database to be ready..."
until docker compose exec web python manage.py showmigrations > /dev/null 2>&1; do
    echo "  DB not ready, retrying in 2 seconds..."
    sleep 2
done
echo "Database is ready!"

docker compose exec web python manage.py makemigrations stores
sleep 3
docker compose exec web python manage.py migrate
sleep 3
docker compose exec web python manage.py createsuperuser

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
