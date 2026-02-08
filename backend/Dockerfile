# PRALAYA-NET Production Dockerfile - Python 3.13
# Fixed for setuptools.build_meta compatibility

# Use Python 3.13 with slim image for faster builds
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables for Python 3.13 compatibility
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel FIRST (critical for Python 3.13)
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first (for better caching)
COPY pyproject.toml .
COPY requirements_simple.txt .

# Install Python dependencies with modern build system
RUN pip install --no-cache-dir -r requirements_simple.txt

# Copy application code
COPY main.py .
COPY app.py .

# Create data directories
RUN mkdir -p data/disaster_history data/predictions

# Expose port
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:10000/health')" || exit 1

# Run the application
CMD ["python", "main.py"]

