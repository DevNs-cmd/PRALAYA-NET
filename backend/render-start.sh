#!/bin/bash
# Production start script for Render
echo "🚀 Starting PRALAYA-NET Backend in Production Mode"
# Ensure we are in the backend directory
cd "$(dirname "$0")"
# Start uvicorn without reload for production stability
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
