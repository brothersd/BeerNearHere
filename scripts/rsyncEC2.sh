#!/bin/bash

# --- Configuration ---
SOURCE="/home/na/Desktop/CodePlatoon/BeerNearHere/"
DEST_USER="ubuntu"
DEST_IP="18.216.65.155"
DEST_PATH="/home/ubuntu/BeerNearHere"
# Since you're running this from the scripts folder, 
# we'll point to the key in the Downloads folder
KEY_PATH="$HOME/Downloads/Beer1.pem"

# --- Script Logic ---

if [ ! -f "$KEY_PATH" ]; then
    echo "Error: Key file not found at $KEY_PATH"
    exit 1
fi

echo "Syncing to $DEST_IP as $DEST_USER..."

# --rsync-path="sudo rsync" allows rsync to modify files 
# even if they were created by Docker/root on the server.
rsync -avzP --delete \
    -e "ssh -i $KEY_PATH -o StrictHostKeyChecking=no" \
    --rsync-path="sudo rsync" \
    --exclude 'node_modules' \
    --exclude '.git' \
    --exclude 'venv' \
    --exclude '__pycache__' \
    "$SOURCE" "$DEST_USER@$DEST_IP:$DEST_PATH"

if [ $? -eq 0 ]; then
    echo "------------------------------"
    echo "Sync Complete!"
else
    echo "------------------------------"
    echo "Sync failed. Check if the server is up or if the IP changed."
fi