"""
API endpoints for Multi-Agent Negotiation Protocol
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.services.multi_agent_negotiation import multi_agent_negotiation

router = APIRouter(prefix="/negotiation", tags=["multi_agent_negotiation"])

class TaskCreateRequest(BaseModel):
    task_type: str
    priority: int
    location: Dict[str, float]
    requirements: Dict[str, Any]
    estimated_duration_minutes: int
    deadline: str

class TaskCreateResponse(BaseModel):
    task_id: str
    status: str
    message: str
    created_at: str

class AgentStatusResponse(BaseModel):
    agent_id: str
    agent_type: str
    capabilities: List[str]
    current_location: Dict[str, float]
    energy_level: float
    availability: float
    current_task: Optional[str]

class CoalitionResponse(BaseModel):
    coalition_id: str
    task_id: str
    member_agents: List[str]
    lead_agent: str
    formation_time: str
    status: str
    success_probability: float

class SystemMetricsResponse(BaseModel):
    total_agents: int
    available_agents: int
    active_coalitions: int
    average_agent_performance: float
    total_negotiations: int
    success_rate: float
    timestamp: str

@router.post("/create-task", response_model=TaskCreateResponse)
async def create_task(request: TaskCreateRequest):
    """Create new task for agent negotiation"""
    try:
        task_data = request.dict()
        task_data["deadline"] = datetime.fromisoformat(task_data["deadline"])
        
        task_id = await multi_agent_negotiation.create_task(task_data)
        
        return TaskCreateResponse(
            task_id=task_id,
            status="created",
            message="Task created and negotiation initiated",
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Task creation failed: {str(e)}")

@router.get("/agents/status", response_model=List[AgentStatusResponse])
async def get_agent_status():
    """Get current agent status"""
    try:
        agents = multi_agent_negotiation.get_agent_status()
        return [AgentStatusResponse(**agent) for agent in agents]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent status retrieval failed: {str(e)}")

@router.get("/agents/available")
async def get_available_agents():
    """Get available agents for task assignment"""
    try:
        all_agents = multi_agent_negotiation.get_agent_status()
        available_agents = [
            agent for agent in all_agents 
            if agent["availability"] > 0.5 and not agent["current_task"]
        ]
        
        return {
            "available_agents": available_agents,
            "total_count": len(available_agents),
            "capability_distribution": {
                capability: len([a for a in available_agents if capability in a["capabilities"]])
                for capability in ["surveillance", "search_rescue", "medical_response", "infrastructure_repair", "transport", "communication", "logistics"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Available agents retrieval failed: {str(e)}")

@router.get("/coalitions/active", response_model=List[CoalitionResponse])
async def get_active_coalitions():
    """Get active agent coalitions"""
    try:
        coalitions = multi_agent_negotiation.get_active_coalitions()
        return [CoalitionResponse(**coalition) for coalition in coalitions]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Active coalitions retrieval failed: {str(e)}")

@router.get("/coalition/{coalition_id}", response_model=CoalitionResponse)
async def get_coalition(coalition_id: str):
    """Get specific coalition details"""
    try:
        coalitions = multi_agent_negotiation.get_active_coalitions()
        
        for coalition in coalitions:
            if coalition["coalition_id"] == coalition_id:
                return CoalitionResponse(**coalition)
        
        raise HTTPException(status_code=404, detail="Coalition not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Coalition retrieval failed: {str(e)}")

@router.get("/task/{task_id}/bids")
async def get_task_bids(task_id: str):
    """Get bids for specific task"""
    try:
        # Get bids from negotiation system
        if task_id in multi_agent_negotiation.active_bids:
            bids = multi_agent_negotiation.active_bids[task_id]
            return {
                "task_id": task_id,
                "total_bids": len(bids),
                "bids": [
                    {
                        "bid_id": bid.bid_id,
                        "agent_id": bid.agent_id,
                        "bid_amount": bid.bid_amount,
                        "capability_match_score": bid.capability_match_score,
                        "proximity_score": bid.proximity_score,
                        "energy_cost": bid.energy_cost,
                        "time_to_complete": bid.time_to_complete,
                        "confidence": bid.confidence,
                        "timestamp": bid.timestamp.isoformat()
                    }
                    for bid in bids
                ],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "task_id": task_id,
                "total_bids": 0,
                "bids": [],
                "message": "No bids found for this task",
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task bids retrieval failed: {str(e)}")

@router.get("/negotiation-history")
async def get_negotiation_history(limit: int = 50):
    """Get negotiation history"""
    try:
        history = multi_agent_negotiation.get_negotiation_history(limit)
        return {
            "negotiation_history": history,
            "total_entries": len(history),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Negotiation history retrieval failed: {str(e)}")

@router.get("/system-metrics", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """Get negotiation system metrics"""
    try:
        metrics = multi_agent_negotiation.get_system_metrics()
        return SystemMetricsResponse(**metrics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System metrics retrieval failed: {str(e)}")

@router.get("/agent/{agent_id}/performance")
async def get_agent_performance(agent_id: str):
    """Get agent performance history"""
    try:
        if agent_id in multi_agent_negotiation.agent_performance_history:
            performance = multi_agent_negotiation.agent_performance_history[agent_id]
            
            return {
                "agent_id": agent_id,
                "total_tasks": len(performance),
                "average_performance": sum(performance) / len(performance) if performance else 0,
                "recent_performance": performance[-10:] if len(performance) >= 10 else performance,
                "performance_trend": "improving" if len(performance) >= 20 and sum(performance[-10:]) > sum(performance[-20:-10]) else "stable",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent performance retrieval failed: {str(e)}")

@router.get("/capabilities/distribution")
async def get_capability_distribution():
    """Get capability distribution across agents"""
    try:
        agents = multi_agent_negotiation.get_agent_status()
        
        capability_counts = {}
        for agent in agents:
            for capability in agent["capabilities"]:
                capability_counts[capability] = capability_counts.get(capability, 0) + 1
        
        return {
            "capability_distribution": capability_counts,
            "total_capabilities": sum(capability_counts.values()),
            "unique_capabilities": len(capability_counts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Capability distribution retrieval failed: {str(e)}")

@router.get("/health")
async def get_negotiation_health():
    """Get negotiation system health"""
    try:
        metrics = multi_agent_negotiation.get_system_metrics()
        agents = multi_agent_negotiation.get_agent_status()
        coalitions = multi_agent_negotiation.get_active_coalitions()
        
        return {
            "system_status": "healthy",
            "total_agents": metrics["total_agents"],
            "available_agents": metrics["available_agents"],
            "active_coalitions": metrics["active_coalitions"],
            "success_rate": metrics["success_rate"],
            "average_performance": metrics["average_agent_performance"],
            "last_update": datetime.now().isoformat(),
            "components": {
                "agent_management": "operational",
                "task_bidding": "operational",
                "coalition_formation": "operational",
                "performance_tracking": "operational"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
