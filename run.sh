#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    python -m venv .venv
    echo "Virtual environment created."
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run the application
uvicorn main:app --reload
