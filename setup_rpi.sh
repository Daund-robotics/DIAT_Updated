#!/bin/bash
# Raspberry Pi 4 deployment script for Aerial Surveillance System (Python 3.13 ready)

echo "============================================================"
echo "    Setting up Drone Detection System on Raspberry Pi 4B    "
echo "============================================================"

# Update and upgrade system packages
echo "Updating system..."
sudo apt-get update && sudo apt-get upgrade -y

# Install standard dependencies required for OpenCV, building, and running python
echo "Installing dependencies..."
sudo apt-get install -y python3-pip python3-venv python3-dev \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libgtk2.0-dev libjpeg-dev libpng-dev

# Set up Python virtual environment (Required on modern Pi OS like Bookworm/Ubuntu or for Python 3.13)
# If python3 doesn't point to 3.13 on your Pi yet, you can replace python3 with python3.13
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install PyTorch for CPU (Raspberry Pi is ARM/CPU based)
echo "Installing PyTorch..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install OpenCV and other required libraries
echo "Installing OpenCV, Flask, Pillow, and YOLOv5 requirements..."
# OpenCV headless is heavily recommended on RPi to avoid X11 graphical library issues over SSH
pip install "opencv-python-headless<=4.8.1.78" numpy Pillow flask requests pandas pyyaml tqdm matplotlib seaborn

echo "============================================================"
echo " Setup complete!                                              "
echo " To run the application on your Raspberry Pi:                 "
echo " 1. Activate the environment: source venv/bin/activate        "
echo " 2. Run the main file:        python mainpi.py                "
echo "============================================================"
