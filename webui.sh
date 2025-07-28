#!/bin/bash

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
  echo "'venv' not found. Creating virtual environment..."
  python3 -m venv venv || {
    echo "Failed to create virtual environment."
    exit 1
  }
fi

# Check if the Python binary inside venv works
if ! ./venv/bin/python3 --version &>/dev/null; then
  echo "'venv/bin/python3' is not working or not executable."
  exit 1
fi

# Install missing packages from requirements.txt if the file exists
if [ -f "requirements.txt" ]; then
  echo "Installing missing requirements from requirements.txt..."
  ./venv/bin/pip3 install --upgrade pip > /dev/null
  ./venv/bin/pip3 install -r requirements.txt
else
  echo "No requirenments.txt found. Skipping dependency installation."
fi

# Run the Gradio app
echo "Running app.py using venv..."
./venv/bin/python3 app.py

