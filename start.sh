#!/bin/bash
# Start the GitLab Stale MRs Tracker

# Activate virtual environment
source venv/bin/activate

# Start the server
# Port is configurable via PORT env var, defaults to 8001 (set in .env)
uvicorn app.main:app --reload --host 0.0.0.0 --port ${PORT:-8001}
