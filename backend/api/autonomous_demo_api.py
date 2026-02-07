"""
API endpoints for Autonomous Demo Scenario
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.services.autonomous_demo_scenario import autonomous_demo_scenario

router = APIRouter(prefix="/demo", tags=["autonomous_demo"])

class DemoStatusResponse(BaseModel):
    demo_active: bool
    current_phase: str
    demo_start_time: Optional[str]
    disaster_risk: float
    infrastructure_risk: float
    agent_coordination_active: bool
    stabilization_actions_count: int
    evidence_artifacts_count: int
    events_count: int
    components_ready: Dict[str, bool]

class DemoEventResponse(BaseModel):
    event_type: str
    timestamp: str
    phase: str
    data: Dict[str, Any]

class DemoSummaryResponse(BaseModel):
    demo_completed: bool
    total_events: int
    phases_executed: int
    final_risk_level: float
    risk_reduction_achieved: float
    stabilization_success: bool
    forensic_proof_generated: bool

@router.post("/start")
async def start_autonomous_demo(background_tasks: BackgroundTasks):
    """Start the autonomous demo scenario"""
    try:
        # Start demo in background
        background_tasks.add_task(autonomous_demo_scenario.start_autonomous_demo)
        
        return {
            "status": "demo_started",
            "message": "Autonomous demo scenario started in background",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo start failed: {str(e)}")

@router.get("/status", response_model=DemoStatusResponse)
async def get_demo_status():
    """Get current demo status"""
    try:
        status = autonomous_demo_scenario.get_demo_status()
        return DemoStatusResponse(**status)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo status retrieval failed: {str(e)}")

@router.get("/events", response_model=List[DemoEventResponse])
async def get_demo_events(limit: int = 50):
    """Get demo events"""
    try:
        events = autonomous_demo_scenario.get_demo_events(limit)
        return [DemoEventResponse(**event) for event in events]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo events retrieval failed: {str(e)}")

@router.get("/summary", response_model=DemoSummaryResponse)
async def get_demo_summary():
    """Get demo summary"""
    try:
        summary = autonomous_demo_scenario.get_demo_summary()
        return DemoSummaryResponse(**summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo summary retrieval failed: {str(e)}")

@router.post("/reset")
async def reset_demo():
    """Reset demo scenario"""
    try:
        # Reset demo state
        autonomous_demo_scenario.demo_active = False
        autonomous_demo_scenario.demo_start_time = None
        autonomous_demo_scenario.current_phase = "idle"
        autonomous_demo_scenario.disaster_risk = 0.0
        autonomous_demo_scenario.infrastructure_risk = 0.0
        autonomous_demo_scenario.agent_coordination_active = False
        autonomous_demo_scenario.stabilization_actions = []
        autonomous_demo_scenario.evidence_artifacts = []
        autonomous_demo_scenario.demo_events = []
        
        return {
            "status": "demo_reset",
            "message": "Demo scenario reset successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo reset failed: {str(e)}")

@router.get("/phases")
async def get_demo_phases():
    """Get demo phases information"""
    try:
        phases = [
            {
                "phase": "risk_appearance",
                "name": "Disaster Risk Appearance",
                "description": "Simulating disaster risk appearance",
                "duration_seconds": 30
            },
            {
                "phase": "intent_generation",
                "name": "Autonomous Intent Generation",
                "description": "System autonomously generates response intents",
                "duration_seconds": 15
            },
            {
                "phase": "agent_coordination",
                "name": "Multi-Agent Coordination",
                "description": "Agents coordinate through negotiation protocol",
                "duration_seconds": 20
            },
            {
                "phase": "infrastructure_stabilization",
                "name": "Infrastructure Stabilization",
                "description": "System executes autonomous stabilization actions",
                "duration_seconds": 25
            },
            {
                "phase": "risk_visualization",
                "name": "Risk Reduction Visualization",
                "description": "Visualizing risk reduction on dashboard",
                "duration_seconds": 10
            },
            {
                "phase": "execution_proof",
                "name": "Execution Proof Recording",
                "description": "Recording execution proof in forensic ledger",
                "duration_seconds": 15
            }
        ]
        
        return {
            "phases": phases,
            "total_phases": len(phases),
            "estimated_total_duration": sum(p["duration_seconds"] for p in phases),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo phases retrieval failed: {str(e)}")

@router.get("/components")
async def get_demo_components():
    """Get demo components status"""
    try:
        components_ready = autonomous_demo_scenario._check_components_ready()
        
        return {
            "components": components_ready,
            "all_ready": all(components_ready.values()),
            "total_components": len(components_ready),
            "ready_components": sum(1 for ready in components_ready.values() if ready),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo components retrieval failed: {str(e)}")

@router.get("/timeline")
async def get_demo_timeline():
    """Get demo timeline with risk progression"""
    try:
        events = autonomous_demo_scenario.get_demo_events(100)
        
        timeline = []
        for event in events:
            if "disaster_risk" in event["data"]:
                timeline.append({
                    "timestamp": event["timestamp"],
                    "phase": event["phase"],
                    "disaster_risk": event["data"]["disaster_risk"],
                    "infrastructure_risk": event["data"].get("infrastructure_risk", 0),
                    "event": event["event_type"]
                })
        
        return {
            "timeline": timeline,
            "total_events": len(timeline),
            "initial_risk": timeline[0]["disaster_risk"] if timeline else 0,
            "final_risk": timeline[-1]["disaster_risk"] if timeline else 0,
            "risk_reduction": (timeline[0]["disaster_risk"] - timeline[-1]["disaster_risk"]) if timeline else 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo timeline retrieval failed: {str(e)}")

@router.get("/stabilization-actions")
async def get_stabilization_actions():
    """Get stabilization actions from demo"""
    try:
        actions = autonomous_demo_scenario.stabilization_actions
        
        return {
            "stabilization_actions": actions,
            "total_actions": len(actions),
            "actions_by_type": {
                action["action_type"]: len([a for a in actions if a["action_type"] == action["action_type"]])
                for action in actions
            },
            "total_expected_risk_reduction": sum(a["expected_risk_reduction"] for a in actions),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stabilization actions retrieval failed: {str(e)}")

@router.get("/evidence-artifacts")
async def get_evidence_artifacts():
    """Get evidence artifacts from demo"""
    try:
        artifacts = autonomous_demo_scenario.evidence_artifacts
        
        return {
            "evidence_artifacts": artifacts,
            "total_artifacts": len(artifacts),
            "artifact_types": {
                artifact["evidence_type"]: len([a for a in artifacts if a["evidence_type"] == artifact["evidence_type"]])
                for artifact in artifacts
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evidence artifacts retrieval failed: {str(e)}")

@router.get("/health")
async def get_demo_health():
    """Get demo system health"""
    try:
        status = autonomous_demo_scenario.get_demo_status()
        components = autonomous_demo_scenario._check_components_ready()
        
        return {
            "system_status": "healthy",
            "demo_active": status["demo_active"],
            "current_phase": status["current_phase"],
            "components_ready": components,
            "all_components_ready": all(components.values()),
            "last_update": datetime.now().isoformat(),
            "components": {
                "policy_engine": "operational" if components["policy_engine"] else "error",
                "stabilization_system": "operational" if components["stabilization_system"] else "error",
                "cascade_engine": "operational" if components["cascade_engine"] else "error",
                "agent_system": "operational" if components["agent_system"] else "error",
                "verification_system": "operational" if components["verification_system"] else "error",
                "reliability_system": "operational" if components["reliability_system"] else "error"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
