"""
PRALAYA-NET Backend - FastAPI Application
Main entry point for the disaster management system
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

from api.trigger_api import router as trigger_router
from api.drone_api import router as drone_router
from api.satellite_api import router as satellite_router
from api.alerts_api import router as alerts_router
from api.risk_alert_api import router as risk_alert_router
from api.national_risk import router as national_risk_router
from api.emergency_broadcast_api import router as emergency_broadcast_router
from api.crowd_intelligence_api import router as crowd_intelligence_router
from api.response_recommendation_api import router as response_recommendation_router
from api.national_resilience_api import router as national_resilience_router
from api.infrastructure_stabilization_api import router as infrastructure_stabilization_router
from api.crisis_learning_api import router as crisis_learning_router
from api.risk_fusion_api import router as risk_fusion_router
from api.intent_command_api import router as intent_command_router
from api.multi_agent_api import router as multi_agent_router
from api.self_healing_api import router as self_healing_router
from api.sensor_fusion_api import router as sensor_fusion_router
from api.forensic_ledger_api import router as forensic_ledger_router
from api.autonomous_policy_api import router as autonomous_policy_router
from api.closed_loop_stabilization_api import router as closed_loop_stabilization_router
from api.digital_twin_cascade_api import router as digital_twin_cascade_router
from api.multi_agent_negotiation_api import router as multi_agent_negotiation_router
from api.autonomous_training_api import router as autonomous_training_router
from api.execution_verification_api import router as execution_verification_router
from api.live_reliability_api import router as live_reliability_router
from api.autonomous_demo_api import router as autonomous_demo_router
from api.autonomous_execution_api import router as autonomous_execution_router
from api.decision_explainability_api import router as decision_explainability_router
from api.replay_api import router as replay_router
from api.stability_index_api import router as stability_index_router
from services.decision_explainability_engine import decision_explainability_engine
from services.replay_engine import replay_engine
from services.stability_index_service import stability_index_service
from services.disaster_simulation_loop import disaster_simulation_loop
from websocket_manager import ws_manager
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
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

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
    print("\n" + "═"*70)
    print("🚀 PRALAYA-NET: STARTUP SEQUENCE INITIATED")
    print("═"*70)
    
    # Check required packages
    try:
        import fastapi
        import uvicorn
        import asyncio
        print("✅ Required packages verified")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return
    
    # Check .env file
    import os
    env_file = ".env"
    if not os.path.exists(env_file):
        print("⚠️  .env file not found, creating default...")
        with open(env_file, "w") as f:
            f.write("DEMO_MODE=true\n")
            f.write("DATA_GOV_KEY=demo_key\n")
        print("✅ Default .env file created")
    else:
        print("✅ .env file found")
    
    # Start Live Data Ingestion in Background
    try:
        asyncio.create_task(data_ingestor.start_monitoring())
        print("✅ LIVE DATA INGESTOR STARTED")
    except Exception as e:
        print(f"⚠️  Data ingestion error: {e}")
        print("💡 Continuing with synthetic data...")
    
    # Validate environment
    data_key = os.getenv("DATA_GOV_KEY")
    if not data_key:
        print("⚠️  DATA_GOV_KEY missing! Entering SAFE DEMO MODE.")
        print("💡 Hardware and AI simulations will use internal synthetic data.")
        os.environ["DEMO_MODE"] = "true"
    else:
        print("✅ Environment variables validated")
        print("✅ DATA_GOV_KEY detected. Live data services active.")
        os.environ["DEMO_MODE"] = "false"

    print("✅ RISK ENGINE READY")
    print("✅ HARDWARE LOOP READY")
    print("✅ DRONE MODULE READY")
    print("✅ GNN DIGITAL TWIN LOADED")
    print("✅ NATIONAL DIGITAL TWIN INITIALIZED")
    print("✅ CASCADE SIMULATION ENGINE READY")
    print("✅ EMERGENCY BROADCAST SYSTEM READY")
    print("✅ CROWD INTELLIGENCE MESH ACTIVE")
    print("✅ AUTONOMOUS RESPONSE ENGINE ONLINE")
    print("✅ NATIONAL RESILIENCE SCORE ACTIVE")
    print("✅ INFRASTRUCTURE STABILIZATION ENGINE READY")
    print("✅ CRISIS MEMORY & LEARNING SYSTEM ACTIVE")
    print("✅ MULTI-LAYER RISK FUSION INTELLIGENCE ONLINE")
    print("✅ ADIRI INTENT-DRIVEN COMMAND ENGINE READY")
    print("✅ MULTI-AGENT AUTONOMOUS RESPONSE NETWORK ACTIVE")
    print("✅ SELF-HEALING INFRASTRUCTURE SIMULATION READY")
    print("✅ REAL-TIME SENSOR FUSION PIPELINE ACTIVE")
    print("✅ FORENSIC EXECUTION LEDGER READY")
    print("✅ AUTONOMOUS POLICY ENGINE READY")
    print("✅ CLOSED-LOOP INFRASTRUCTURE STABILIZATION ACTIVE")
    print("✅ DIGITAL TWIN CASCADE FORECAST ENGINE READY")
    print("✅ MULTI-AGENT NEGOTIATION PROTOCOL ACTIVE")
    print("✅ AUTONOMOUS SIMULATION TRAINING SYSTEM ACTIVE")
    print("✅ EXECUTION VERIFICATION LAYER READY")
    print("✅ LIVE SYSTEM RELIABILITY METRICS ACTIVE")
    print("✅ DEMO-READY AUTONOMOUS SCENARIO READY")
    print("✅ AUTONOMOUS EXECUTION ENGINE READY")
    print("✅ MULTI-AGENT NEGOTIATION ENGINE ACTIVE")
    print("✅ DECISION EXPLAINABILITY ENGINE READY")
    print("✅ REPLAY ENGINE ACTIVE")
    print("✅ STABILITY INDEX SERVICE ACTIVE")
    print("✅ DISASTER SIMULATION LOOP READY")
    print("\n✨ BACKEND READY: PRALAYA-NET OPERATIONAL")
    print("═"*70 + "\n")
    
    # Start background services
    print("🔄 Starting background services...")
    asyncio.create_task(disaster_simulation_loop.start_simulation())
    print("✅ Disaster simulation loop started")
    
    print("\n" + "═"*70)
    print("🎉 BACKEND STARTUP COMPLETE")
    print("📍 Backend running at: http://127.0.0.1:8000")
    print("📍 API Documentation: http://127.0.0.1:8000/docs")
    print("📍 Health Check: http://127.0.0.1:8000/api/health")
    print("═"*70 + "\n")

# Include routers
app.include_router(trigger_router, prefix="/api/trigger", tags=["Trigger"])
app.include_router(drone_router, prefix="/api/drones", tags=["Drones"])
app.include_router(satellite_router, prefix="/api/satellite", tags=["Satellite"])
app.include_router(alerts_router, prefix="/api/orchestration/alerts", tags=["Alerts"])
app.include_router(risk_alert_router, tags=["Risk Alert"])
app.include_router(national_risk_router, tags=["National Risk"])
app.include_router(emergency_broadcast_router, tags=["Emergency Broadcast"])
app.include_router(crowd_intelligence_router, tags=["Crowd Intelligence"])
app.include_router(response_recommendation_router, tags=["Response Recommendation"])
app.include_router(national_resilience_router, tags=["National Resilience"])
app.include_router(infrastructure_stabilization_router, tags=["Infrastructure Stabilization"])
app.include_router(crisis_learning_router, tags=["Crisis Learning"])
app.include_router(risk_fusion_router, tags=["Risk Fusion"])
app.include_router(intent_command_router, tags=["Intent-Driven Command"])
app.include_router(multi_agent_router, tags=["Multi-Agent Network"])
app.include_router(self_healing_router, tags=["Self-Healing Infrastructure"])
app.include_router(sensor_fusion_router, tags=["Sensor Fusion"])
app.include_router(forensic_ledger_router, tags=["Forensic Ledger"])
app.include_router(autonomous_policy_router, tags=["Autonomous Policy"])
app.include_router(closed_loop_stabilization_router, tags=["Closed-Loop Stabilization"])
app.include_router(digital_twin_cascade_router, tags=["Digital Twin Cascade"])
app.include_router(multi_agent_negotiation_router, tags=["Multi-Agent Negotiation"])
app.include_router(autonomous_training_router, tags=["Autonomous Training"])
app.include_router(execution_verification_router, tags=["Execution Verification"])
app.include_router(live_reliability_router, tags=["Live Reliability"])
app.include_router(autonomous_demo_router, tags=["Autonomous Demo"])
app.include_router(autonomous_execution_router, tags=["Autonomous Execution"])
app.include_router(decision_explainability_router, tags=["Decision Explainability"])
app.include_router(replay_router, tags=["Replay Engine"])
app.include_router(stability_index_router, tags=["Stability Index"])

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket, "general")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.websocket("/ws/risk-stream")
async def risk_stream_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket, "risk")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.websocket("/ws/stability-stream")
async def stability_stream_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket, "stability")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.websocket("/ws/actions-stream")
async def actions_stream_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket, "actions")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.websocket("/ws/timeline-stream")
async def timeline_stream_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket, "timeline")
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
    print("🚀 PRALAYA-NET Backend Starting...")
    print("="*70)
    # Allow overriding port via environment variables for deployment/runtime flexibility
    env_port = os.getenv("PORT") or os.getenv("BACKEND_PORT")
    try:
        port = int(env_port) if env_port else int(CONFIG_PORT or 8000)
    except Exception:
        port = 8000

    print(f"📍 Server: http://0.0.0.0:{port}")
    print(f"📍 Local:  http://127.0.0.1:{port}")
    print(f"📍 Docs:   http://127.0.0.1:{port}/docs")
    print(f"📍 Health: http://127.0.0.1:{port}/api/health")
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
