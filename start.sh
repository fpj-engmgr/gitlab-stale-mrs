#!/bin/bash
# Start the GitLab Stale MRs Tracker

# Load PORT from .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep PORT | xargs)
fi

# Get port from environment or default to 8001
PORT=${PORT:-8001}

echo "Starting GitLab Stale MRs Tracker on http://localhost:$PORT"

# Activate virtual environment
source venv/bin/activate

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port $PORT
