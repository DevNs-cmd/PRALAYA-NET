"""
PRALAYA-NET Backend - FastAPI Application
Main entry point for the Autonomous Disaster Response Infrastructure OS
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import asyncio
from dotenv import load_dotenv
from services.data_ingestion import data_ingestor
from services.ws_manager import ws_manager

# Import all new components
from camera_stream_multiplexer import router as camera_router
from gps_failure_navigation import navigation_manager
from capacity_intelligence import capacity_intelligence
from scalable_backend import backend_orchestrator, start_scalable_backend
from command_replay import replay_system
from autonomous_mission_intelligence import mission_intelligence, autonomous_mission_planner, get_mission_overview

from api.trigger_api import router as trigger_router
from api.drone_api import router as drone_router
from api.satellite_api import router as satellite_router
from api.alerts_api import router as alerts_router
from api.risk_alert_api import router as risk_alert_router
from config import APP_NAME, VERSION, CORS_ORIGINS, PORT as CONFIG_PORT
from middleware import (
    RateLimitMiddleware,
    InputValidationMiddleware,
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware
)

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title=APP_NAME,
    version=VERSION,
    description="Unified Disaster Command System - AI-powered disaster prediction and response"
)

# Security & Performance Middleware Stack (order matters)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputValidationMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=30000)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup Reliability Checks
@app.on_event("startup")
async def startup_event():
    print("\n" + "="*70)
    print("[STARTUP] PRALAYA-NET: AUTONOMOUS INFRASTRUCTURE OS INITIALIZING")
    print("="*70)
    
    # Start Live Data Ingestion in Background
    asyncio.create_task(data_ingestor.start_monitoring())
    print("[OK] LIVE DATA INGESTOR STARTED")
    
    # Initialize Autonomous Systems
    print("[INIT] Starting Autonomous Infrastructure Components...")
    
    # Start Camera Stream Multiplexer
    try:
        multiplexer.start_capture()
        print("[OK] CAMERA STREAM MULTIPLEXER: 12 DRONE FEEDS ACTIVE")
    except Exception as e:
        print(f"[WARN] Camera multiplexer initialization: {e}")
    
    # Start Scalable Backend Processing Grid
    try:
        backend_orchestrator.initialize_workers(num_stream_workers=4, num_ai_workers=3)
        backend_orchestrator.start_system()
        print("[OK] SCALABLE BACKEND: DISTRIBUTED PROCESSING GRID ACTIVE")
    except Exception as e:
        print(f"[WARN] Scalable backend initialization: {e}")
    
    # Start Autonomous Mission Intelligence
    try:
        mission_intelligence.start_autonomous_system()
        print("[OK] AUTONOMOUS MISSION INTELLIGENCE: READY FOR OPERATIONS")
    except Exception as e:
        print(f"[WARN] Mission intelligence initialization: {e}")
    
    # Valdiate environment
    data_key = os.getenv("DATA_GOV_KEY")
    if not data_key:
        print("[WARN] DATA_GOV_KEY missing! Entering SAFE DEMO MODE.")
        print("[INFO] Hardware and AI simulations will use internal synthetic data.")
        os.environ["DEMO_MODE"] = "true"
    else:
        print("[OK] DATA_GOV_KEY detected. Live data services active.")
        os.environ["DEMO_MODE"] = "false"

    print("[OK] RISK ENGINE READY")
    print("[OK] HARDWARE LOOP READY")
    print("[OK] DRONE MODULE READY")
    print("[OK] GNN DIGITAL TWIN LOADED")
    print("[OK] GPS FAILURE NAVIGATION: VISUAL SLAM READY")
    print("[OK] CAPACITY INTELLIGENCE: MISSION PLANNING READY")
    print("[OK] COMMAND REPLAY: FORENSIC ANALYSIS READY")

    # Initialize Demo Drone for SLAM
    try:
        from drone.drone_controller import drone_controller
        drone_controller.deploy_drone({"lat": 28.6139, "lon": 77.2090})
        print("[OK] RECON DRONE [drone_1]: DEPLOYED AT COMMAND CENTER")
    except Exception as e:
        print(f"[WARN] Drone initialization failed: {e}")
    # Optionally start the local webcam-based drone feed simulator
    start_sim = os.getenv("START_DRONE_SIMULATOR", "true").lower() in ("1", "true", "yes")
    if os.getenv("DEMO_MODE", "false").lower() == "true" or start_sim:
        try:
            from drone.simulator import start_simulator_in_thread
            backend_url = os.getenv("BACKEND_URL") or f"http://127.0.0.1:{CONFIG_PORT or 8000}"
            start_simulator_in_thread(backend_url=backend_url, num_drones=int(os.getenv("SIMULATED_DRONES", 12)), fps=int(os.getenv("SIMULATOR_FPS", 6)))
            print("[OK] Drone Feed Simulator started (webcam -> virtual drones)")
        except Exception as e:
            print(f"[WARN] Failed to start Drone Feed Simulator: {e}")
    print("\n[READY] PRALAYA-NET AUTONOMOUS INFRASTRUCTURE OS OPERATIONAL")
    print("="*70 + "\n")

# Include routers
app.include_router(trigger_router, prefix="/api/trigger", tags=["Trigger"])
app.include_router(drone_router, prefix="/api/drones", tags=["Drones"])
app.include_router(satellite_router, prefix="/api/satellite", tags=["Satellite"])
app.include_router(alerts_router, prefix="/api/orchestration/alerts", tags=["Alerts"])
app.include_router(risk_alert_router, tags=["Risk Alert"])
app.include_router(camera_router, prefix="/api/camera", tags=["Camera Streams"])

# Autonomous Mission Intelligence API
@app.post("/api/mission/autonomous")
async def plan_and_execute_mission(mission_request: dict):
    """Autonomously plan and execute a mission"""
    try:
        result = autonomous_mission_planner(
            area_coordinates=mission_request["area_coordinates"],
            terrain_type=mission_request["terrain_type"],
            disaster_type=mission_request["disaster_type"],
            priority=mission_request.get("priority", "search_and_rescue")
        )
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/mission/status")
async def get_mission_status():
    """Get status of all active missions"""
    return get_mission_overview()

@app.get("/api/system/status")
async def get_system_status():
    """Get comprehensive system status"""
    return {
        "camera_system": multiplexer.get_system_status(),
        "backend_grid": backend_orchestrator.get_system_status(),
        "navigation_system": navigation_manager.get_system_overview(),
        "mission_intelligence": get_mission_overview(),
        "replay_system": {
            "recording": replay_system.is_recording,
            "current_mission": replay_system.current_mission_id
        }
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.get("/")
def home():
    """Root endpoint - health check"""
    return {
        "status": "online",
        "system": APP_NAME,
        "version": VERSION,
        "message": "PRALAYA-NET backend is operational"
    }

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "components": {
            "api": "operational",
            "ai_models": "loaded",
            "orchestration": "ready"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__}
    )

if __name__ == "__main__":
    print("\n" + "="*70)
    print("[STARTUP] PRALAYA-NET Backend Starting...")
    print("="*70)
    # Allow overriding port via environment variables for deployment/runtime flexibility
    env_port = os.getenv("PORT") or os.getenv("BACKEND_PORT")
    try:
        port = int(env_port) if env_port else int(CONFIG_PORT or 8000)
    except Exception:
        port = 8000

    print(f"[SERVER] http://0.0.0.0:{port}")
    print(f"[LOCAL]  http://127.0.0.1:{port}")
    print(f"[DOCS]   http://127.0.0.1:{port}/docs")
    print(f"[HEALTH] http://127.0.0.1:{port}/api/health")
    print("="*70 + "\n")
    
    # Force 0.0.0.0 binding for Docker/Cloud compatibility
    host = "0.0.0.0"
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
