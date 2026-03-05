#!/bin/bash
#script for testing outside the docker container

# Exit on error
set -e

# 1. Update and install python3-venv if missing
if ! dpkg -s python3-venv >/dev/null 2>&1; then
    echo "[*] Installing python3-venv..."
    sudo apt update && sudo apt install -y python3-venv
fi

# 2. Create the virtual environment
# Using 'venv' as the folder name for standard conventions
if [ ! -d "venv" ]; then
    echo "[*] Creating virtual environment..."
    python3 -m venv venv
else
    echo "[*] Virtual environment already exists."
fi

# 3. Activate the environment
source venv/bin/activate

# 4. Upgrade pip and install requirements
echo "[*] Installing Python dependencies..."
pip install --upgrade pip

# Check if requirements.txt exists before installing
if [ -f "requirements.txt" ]; then
    pip install -r backend/requirements.txt
else
    echo "[!] No requirements.txt found. Installing pytest for stretch goal..."
    pip install pytest
fi

echo "------------------------------------------------"
echo "[SUCCESS] "
echo "To start, run: source venv/bin/activate && python main.py"
echo "------------------------------------------------"