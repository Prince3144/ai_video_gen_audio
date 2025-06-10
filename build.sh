#!/usr/bin/env bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y espeak-ng

# Install Python dependencies
pip install -r requirements.txt