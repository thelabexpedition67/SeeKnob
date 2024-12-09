#!/bin/bash

# Run SeekKnob application with virtual environment check

# Set the virtual environment path
VENV_PATH="venv/bin/activate"

# Check if virtual environment exists
if [ -f "$VENV_PATH" ]; then
    echo "Activating virtual environment..."
    source "$VENV_PATH"
else
    echo "Virtual environment not found. Please create one using:"
    echo "  python3 -m venv venv"
    echo "Then install requirements:"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Run the application
echo "Starting SeekKnob..."
python3 main.py
