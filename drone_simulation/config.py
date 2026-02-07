"""
Configuration for Drone Simulation System
Centralized management of backend connectivity and frame upload settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# ==========================================
# BACKEND CONFIGURATION
# ==========================================

# Backend host and port - supports environment override
BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8001"))  # Default to 8001 (our running port)
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"

# ==========================================
# FRAME UPLOAD CONFIGURATION
# ==========================================

# Frame encoding
FRAME_ENCODING_FORMAT = ".jpg"  # Use JPEG for bandwidth efficiency
FRAME_JPEG_QUALITY = 85  # JPEG quality (0-100)
FRAME_RESIZE_WIDTH = 320
FRAME_RESIZE_HEIGHT = 240

# Request configuration
FRAME_UPLOAD_FPS = 10  # Frames per second to sync
FRAME_UPLOAD_TIMEOUT = 2.0  # Seconds
TELEMETRY_UPLOAD_TIMEOUT = 2.0  # Seconds

# Retry configuration
RETRY_CONNECT_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 0.5
HTTP_POOL_CONNECTIONS = 20
HTTP_POOL_MAXSIZE = 20

# ==========================================
# CAMERA CONFIGURATION
# ==========================================

NUM_DRONES = 12
CAMERA_FALLBACK_TO_SYNTHETIC = True  # Use synthetic frames if camera unavailable

# ==========================================
# LOGGING CONFIGURATION
# ==========================================

LOG_FRAME_ERRORS = True
LOG_FRAME_SUCCESS = False  # Set to True for verbose logging
LOG_TELEMETRY_ERRORS = True

# ==========================================
# VALIDATION
# ==========================================

def validate_backend_url():
    """Validate backend URL configuration"""
    print(f"🔗 Backend Configuration:")
    print(f"   Host: {BACKEND_HOST}")
    print(f"   Port: {BACKEND_PORT}")
    print(f"   URL: {BACKEND_URL}")
    
    if BACKEND_PORT != 8001:
        print(f"   ⚠️  WARNING: Non-standard port {BACKEND_PORT} (expected 8001)")
    
    return BACKEND_URL

if __name__ == "__main__":
    validate_backend_url()
