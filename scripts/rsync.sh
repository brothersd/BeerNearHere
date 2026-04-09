#!/bin/bash

# --- Configuration ---
# REMOVED trailing slash from SOURCE to ensure the directory is created
SOURCE="/home/na/Desktop/CodePlatoon/BeerNearHere"
DEST_USER="root"
DEST_IP="192.168.2.108"
# Target the PARENT directory so that BeerNearHere is created inside /home/ubuntu/
DEST_PATH="/home/ubuntu"

# --- Script Logic ---

if ! ping -c 1 -W 1 "$DEST_IP" > /dev/null; then
    echo "Error: Cannot reach $DEST_IP."
    exit 1
fi

echo "Syncing as ROOT to $DEST_IP..."

# -a: archive mode
# -v: verbose (Changed to -v for better debugging output)
# -z: compress
# -P: progress
# --delete: remove files on dest that don't exist on source
rsync -avzP --delete \
    --exclude 'node_modules' \
    --exclude '.git' \
    --exclude 'venv' \
    --exclude '__pycache__' \
    "$SOURCE" "$DEST_USER@$DEST_IP:$DEST_PATH"

if [ $? -eq 0 ]; then
    echo "Sync Complete!"
else
    echo "Sync failed. Check permissions or SSH access."
fi