#!/bin/bash
# Simple script to run the GeoPulse Flask application

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the Flask application
python app.py

