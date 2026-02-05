"""
Run helper for PRALAYA-NET backend.
Reads `PORT` or `BACKEND_PORT` from environment with sensible fallback.
Usage: `python run.py` or `BACKEND_PORT=8000 python run.py`
"""
import os
import uvicorn

from app import app
from config import PORT as CONFIG_PORT


def get_port():
    env_port = os.getenv("PORT") or os.getenv("BACKEND_PORT")
    try:
        return int(env_port) if env_port else int(CONFIG_PORT or 8000)
    except Exception:
        return 8000


if __name__ == "__main__":
    port = get_port()
    print(f"Starting PRALAYA-NET backend on http://0.0.0.0:{port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True, log_level="info")
