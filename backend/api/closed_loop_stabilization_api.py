"""
API endpoints for Closed-Loop Infrastructure Stabilization
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.services.closed_loop_stabilization import closed_loop_stabilization

router = APIRouter(prefix="/stabilization", tags=["closed_loop_stabilization"])

class StabilizationLoopResponse(BaseModel):
    loop_id: str
    start_time: str
    end_time: Optional[str]
    current_phase: str
    status: str
    risk_detection: Optional[Dict[str, Any]]
    stabilization_intent: Optional[Dict[str, Any]]
    agent_deployments: List[Dict[str, Any]]
    infrastructure_controls: List[Dict[str, Any]]
    effectiveness_metrics: Optional[Dict[str, Any]]

class SystemEffectivenessResponse(BaseModel):
    total_loops: int
    successful_loops: int
    success_rate: float
    average_effectiveness: float
    average_duration: float
    current_risk_thresholds: Dict[str, float]
    learning_weights: Dict[str, float]
    timestamp: str

class RealTimeMetricsResponse(BaseModel):
    active_loops: int
    current_phase_distribution: Dict[str, int]
    status_distribution: Dict[str, int]
    recent_effectiveness: List[Dict[str, Any]]
    system_health: Dict[str, Any]
    timestamp: str

@router.get("/active-loops", response_model=List[StabilizationLoopResponse])
async def get_active_loops():
    """Get active stabilization loops"""
    try:
        loops = closed_loop_stabilization.get_active_loops()
        return [StabilizationLoopResponse(**loop) for loop in loops]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Active loops retrieval failed: {str(e)}")

@router.get("/completed-loops")
async def get_completed_loops(limit: int = 50):
    """Get completed stabilization loops"""
    try:
        loops = closed_loop_stabilization.get_completed_loops(limit)
        return {
            "completed_loops": [StabilizationLoopResponse(**loop) for loop in loops],
            "total_count": len(loops),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Completed loops retrieval failed: {str(e)}")

@router.get("/system-effectiveness", response_model=SystemEffectivenessResponse)
async def get_system_effectiveness():
    """Get overall system effectiveness metrics"""
    try:
        effectiveness = closed_loop_stabilization.get_system_effectiveness()
        return SystemEffectivenessResponse(**effectiveness)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System effectiveness retrieval failed: {str(e)}")

@router.get("/real-time-metrics", response_model=RealTimeMetricsResponse)
async def get_real_time_metrics():
    """Get real-time stabilization metrics"""
    try:
        metrics = closed_loop_stabilization.get_real_time_metrics()
        return RealTimeMetricsResponse(**metrics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Real-time metrics retrieval failed: {str(e)}")

@router.get("/loop/{loop_id}", response_model=StabilizationLoopResponse)
async def get_stabilization_loop(loop_id: str):
    """Get specific stabilization loop"""
    try:
        # Get from active loops first
        active_loops = closed_loop_stabilization.get_active_loops()
        for loop in active_loops:
            if loop["loop_id"] == loop_id:
                return StabilizationLoopResponse(**loop)
        
        # Get from completed loops
        completed_loops = closed_loop_stabilization.get_completed_loops(1000)
        for loop in completed_loops:
            if loop["loop_id"] == loop_id:
                return StabilizationLoopResponse(**loop)
        
        raise HTTPException(status_code=404, detail="Stabilization loop not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Loop retrieval failed: {str(e)}")

@router.get("/health")
async def get_stabilization_health():
    """Get stabilization system health"""
    try:
        effectiveness = closed_loop_stabilization.get_system_effectiveness()
        real_time = closed_loop_stabilization.get_real_time_metrics()
        
        return {
            "system_status": "healthy" if effectiveness["success_rate"] > 0.7 else "degraded",
            "active_loops": real_time["active_loops"],
            "success_rate": effectiveness["success_rate"],
            "average_effectiveness": effectiveness["average_effectiveness"],
            "last_update": datetime.now().isoformat(),
            "components": {
                "risk_detection": "operational",
                "intent_generation": "operational",
                "agent_coordination": "operational",
                "infrastructure_control": "operational",
                "effectiveness_evaluation": "operational",
                "learning_update": "operational"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
