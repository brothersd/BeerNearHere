#!/bin/bash

# --- Configuration ---
SOURCE="/home/na/Desktop/CodePlatoon/BeerNearHere/"
DEST_USER="root"
DEST_IP="192.168.2.108"
DEST_PATH="/home/ubuntu/BeerNearHere"

# --- Script Logic ---

if ! ping -c 1 -W 1 "$DEST_IP" > /dev/null; then
    echo "Error: Cannot reach $DEST_IP."
    exit 1
fi

echo "Syncing as ROOT to $DEST_IP..."

# -a: archive mode (preserves permissions/links)
# -v: verbose (shows progress)
# -z: compress for faster transfer
# -P: show progress bar
# --delete: removes files on destination that you deleted locally
# --exclude: skip node_modules and .git to save time/space
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