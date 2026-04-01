#!/bin/bash
# deploy.sh - EC2 production deployment (SAFE)

echo "🚀 Deploying to EC2..."

# Pull latest code
git pull origin main

# Build only what changed (faster, preserves data)
docker compose -f docker-compose.prod.yml up -d --build

docker compose -f docker-compose.prod.yml ps

# Restart services (KEEP volumes/database)
docker compose -f docker-compose.prod.yml up -d --remove-orphans

# Clean only dangling resources (safe)
docker image prune -f
docker builder prune -f

echo "✅ Deployment complete!"
echo "🌐 App: http://18.218.53.191:8000"