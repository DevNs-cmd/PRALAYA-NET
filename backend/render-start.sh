#!/bin/bash
# Production start script for Render - Python 3.13 optimized
set -e

echo "🚀 Starting PRALAYA-NET Backend in Production Mode (Python 3.13)"

# Ensure we are in the backend directory
cd "$(dirname "$0")"

echo "📦 Python version: $(python --version)"
echo "📦 pip version: $(pip --version)"

# Upgrade pip, setuptools, and wheel if needed
echo "🔧 Ensuring build tools are up-to-date..."
pip install --upgrade pip setuptools wheel --quiet

# Check if pyproject.toml exists and install dependencies
if [ -f "pyproject.toml" ]; then
    echo "📦 Found pyproject.toml, installing dependencies..."
    pip install --no-cache-dir -e . --quiet || {
        echo "⚠️  pip install -e . failed, trying requirements.txt..."
        pip install --no-cache-dir -r requirements_simple.txt
    }
fi

# Start uvicorn without reload for production stability
echo "🌐 Starting server..."
uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000} --log-level info --workers 1

