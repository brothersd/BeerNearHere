#!/bin/bash
# deploy.sh - EC2 production deployment (SAFE)

echo "🚀 Deploying to EC2..."

# Pull latest code
git pull origin main

# Build only what changed (faster, preserves data)
docker compose build --no-cache web react

# Restart services (KEEP volumes/database)
docker compose up -d --remove-orphans

# Clean only dangling resources (safe)
docker image prune -f
docker builder prune -f

echo "✅ Deployment complete!"
echo "🌐 App: http://your-ec2-public-ip:8000"