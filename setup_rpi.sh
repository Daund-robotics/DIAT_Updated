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
    python3-opencv python3-numpy \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libgtk2.0-dev libjpeg-dev libpng-dev

# Set up Python virtual environment (Required on modern Pi OS like Bookworm/Ubuntu or for Python 3.13)
# Creating the virtual environment with system-site-packages ensures it can access the apt-installed OpenCV/NumPy
echo "Creating Python virtual environment..."
python3 -m venv --system-site-packages venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install PyTorch for Raspberry Pi (ARM architecture)
# We remove the --index-url since the default PyPi now has proper aarch64 wheels for PyTorch 2.x
# The previous --index-url (download.pytorch.org) often serves x86-optimised wheels causing Illegal Instructions
echo "Installing PyTorch..."
pip install setuptools wheel
pip install torch torchvision torchaudio

# Install tracking, web, and YOLOv5 requirements
# We install numpy<2 explicitly because OpenCV 4.x wheels/apt packages crash with numpy 2.x
echo "Installing Flask, Pillow, and YOLOv5 requirements..."
pip install "numpy<2"
pip install Pillow flask requests pandas pyyaml tqdm matplotlib seaborn

echo "============================================================"
echo " Setup complete!                                              "
echo " To run the application on your Raspberry Pi:                 "
echo " 1. Activate the environment: source venv/bin/activate        "
echo " 2. Run the main file:        python mainpi.py                "
echo "============================================================"
