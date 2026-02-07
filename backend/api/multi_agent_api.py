"""
Multi-Agent Autonomous Response Network API
Distributed agents for drones, rescue teams, medical units, infrastructure nodes, and supply chains
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from services.multi_agent_network import (
    multi_agent_network,
    AgentType,
    AgentStatus,
    TaskType,
    TaskPriority
)

router = APIRouter(prefix="/agents", tags=["multi-agent-network"])

class TaskCreationRequest(BaseModel):
    task_type: str = Field(..., description="Type of task")
    priority: str = Field(..., description="Task priority")
    location: Dict = Field(..., description="Task location {lat, lon, altitude}")
    requirements: Dict = Field(default_factory=dict, description="Task requirements")
    estimated_duration_minutes: int = Field(..., ge=1, description="Estimated duration in minutes")
    risk_level: float = Field(default=0.5, ge=0, le=1, description="Risk level 0-1")
    deadline_hours: Optional[int] = Field(default=None, description="Deadline in hours")

class TaskCreationResponse(BaseModel):
    task_id: str
    status: str
    message: str
    created_at: str

class AgentStatusResponse(BaseModel):
    agent_id: str
    agent_type: str
    name: str
    location: Dict
    status: str
    battery_level: float
    current_task: Optional[str]
    capabilities: List[Dict]
    last_heartbeat: str

class TaskStatusResponse(BaseModel):
    task_id: str
    task_type: str
    priority: str
    location: Dict
    status: str
    risk_level: float
    assigned_agent_id: Optional[str]
    created_at: str
    deadline: Optional[str]
    estimated_duration_minutes: int

class NetworkMetricsResponse(BaseModel):
    total_agents: int
    active_agents: int
    idle_agents: int
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    success_rate: float
    agent_type_distribution: Dict[str, int]
    negotiation_history_count: int
    pending_tasks: int
    timestamp: str

@router.post("/create-task", response_model=TaskCreationResponse)
async def create_task(request: TaskCreationRequest, background_tasks: BackgroundTasks):
    """
    Create a task for multi-agent allocation
    
    This endpoint enables dynamic task allocation using risk-weighted priority arbitration
    """
    try:
        # Validate task type
        try:
            task_type = TaskType(request.task_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid task type. Must be one of: {[tt.value for tt in TaskType]}"
            )
        
        # Validate priority
        try:
            priority = TaskPriority(request.priority.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid priority. Must be one of {[tp.value for tp in TaskPriority]}"
            )
        
        # Create task
        task_id = await multi_agent_network.create_task(
            task_type=task_type,
            priority=priority,
            location=request.location,
            requirements=request.requirements,
            estimated_duration_minutes=request.estimated_duration_minutes,
            risk_level=request.risk_level,
            deadline_hours=request.deadline_hours
        )
        
        return TaskCreationResponse(
            task_id=task_id,
            status="created",
            message="Task created and queued for agent allocation",
            created_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task creation failed: {str(e)}")

@router.get("/agents/status", response_model=List[AgentStatusResponse])
async def get_agent_status():
    """Get current status of all agents"""
    try:
        status = multi_agent_network.get_agent_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent status retrieval failed: {str(e)}")

@router.get("/tasks/status", response_model=List[TaskStatusResponse])
async def get_task_status():
    """Get current status of all tasks"""
    try:
        status = multi_agent_network.get_task_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task status retrieval failed: {str(e)}")

@router.get("/network/metrics", response_model=NetworkMetricsResponse)
async def get_network_metrics():
    """Get network performance metrics"""
    try:
        metrics = multi_agent_network.get_network_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Network metrics retrieval failed: {str(e)}")

@router.post("/task/{task_id}/complete")
async def complete_task(task_id: str, agent_id: str, success: bool, outcome: Dict):
    """
    Mark task as completed and update agent status
    """
    try:
        result = await multi_agent_network.complete_task(task_id, agent_id, success, outcome)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task completion failed: {str(e)}")

@router.get("/agent/{agent_id}/heartbeat")
async def agent_heartbeat(agent_id: str):
    """Update agent heartbeat"""
    try:
        if agent_id in multi_agent_network.agents:
            multi_agent_network.agents[agent_id].last_heartbeat = datetime.now()
            return {"status": "heartbeat_updated", "agent_id": agent_id}
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heartbeat update failed: {str(e)}")

@router.get("/available-agents")
async def get_available_agents():
    """Get list of available agents for task allocation"""
    try:
        available_agents = [
            agent_id for agent in multi_agent_network.agents.values()
            if agent.status == AgentStatus.IDLE
        ]
        return {"available_agents": available_agents, "total_available": len(available_agents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Available agents retrieval failed: {str(e)}")

@router.get("/agent-types")
async def get_agent_types():
    """Get available agent types and their descriptions"""
    return {
        "agent_types": [at.value for at in AgentType],
        "agent_descriptions": {
            "drone": "Autonomous drone for surveillance and reconnaissance",
            "rescue_team": "Ground rescue and emergency response teams",
            "medical_unit": "Medical response units and hospitals",
            "infrastructure_node": "Infrastructure monitoring and control nodes",
            "supply_chain": "Logistics and supply chain management",
            "communication_node": "Communication network nodes"
        }
    }

@router.get("/task-types")
async def get_task_types():
    """Get available task types and their descriptions"""
    return {
        "task_types": [tt.value for tt in TaskType],
        "task_descriptions": {
            "search_rescue": "Search and rescue operations",
            "medical_response": "Medical emergency response coordination",
            "infrastructure_assessment": "Infrastructure damage assessment",
            "supply_delivery": "Emergency supply delivery",
            "evacuation_support": "Evacuation coordination and support",
            "communication_relay": "Communication relay establishment",
            "surveillance": "Area surveillance and monitoring"
        }
    }

@router.get("/task-priority")
async def get_task_priorities():
    """Get task priority levels and their meanings"""
    return {
        "task_priorities": [tp.value for tp in TaskPriority],
        "priority_descriptions": {
            "critical": "Life-threatening situations requiring immediate response",
            "high": "Infrastructure collapse or major service disruption",
            "medium": "Evacuation and rescue operations",
            "low": "Supply and support operations",
            "routine": "Maintenance and monitoring"
        }
    }
