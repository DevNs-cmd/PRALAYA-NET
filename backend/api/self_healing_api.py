"""
Self-Healing Infrastructure Simulation API
Real-time infrastructure modeling with reinforcement learning stabilization strategies
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from services.self_healing_simulation import (
    self_healing_simulation,
    InfrastructureType,
    InfrastructureStatus,
    FailureMode
)

router = APIRouter(prefix="/infrastructure", tags=["self-healing"])

class CascadeSimulationRequest(BaseModel):
    initial_failure_node: str = Field(..., description="Initial failing node ID")
    failure_mode: str = Field(..., description="Type of failure")
    severity: float = Field(..., ge=0, le=1, description="Failure severity 0-1")

class CascadeSimulationResponse(BaseModel):
    initial_failure: str
    failure_mode: str
    severity: float
    failed_nodes: List[str]
    total_affected: int
    cascade_log: List[Dict]

class StabilizationRequest(BaseModel):
    failed_nodes: List[str] = Field(..., description="List of failed node IDs")

class StabilizationResponse(BaseModel):
    stabilization_results: Dict[str, Dict]
    total_actions: int
    average_reward: float
    execution_time: str

class InfrastructureHealthResponse(BaseModel):
    total_nodes: int
    status_distribution: Dict[str, int]
    average_health_score: float
    average_load_percentage: float
    critical_nodes: int
    at_risk_nodes: int
    timestamp: str

class RecommendationResponse(BaseModel):
    node_id: str
    node_name: str
    node_type: str
    current_status: str
    recommended_action: str
    action_description: str
    expected_effectiveness: float
    estimated_cost: float
    q_value: float
    confidence: float

@router.post("/simulate-cascade", response_model=CascadeSimulationResponse)
async def simulate_cascade_failure(request: CascadeSimulationRequest, background_tasks: BackgroundTasks):
    """
    Simulate cascading infrastructure failure
    
    This endpoint models realistic infrastructure dependencies and failure propagation
    """
    try:
        # Validate failure mode
        try:
            failure_mode = FailureMode(request.failure_mode.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid failure mode. Must be one of: {[fm.value for fm in FailureMode]}"
            )
        
        # Validate node exists
        if request.initial_failure_node not in self_healing_simulation.nodes:
            raise HTTPException(
                status_code=404,
                detail=f"Node {request.initial_failure_node} not found"
            )
        
        # Simulate cascade failure
        result = await self_healing_simulation.simulate_cascade_failure(
            initial_failure_node=request.initial_failure_node,
            failure_mode=failure_mode,
            severity=request.severity
        )
        
        return CascadeSimulationResponse(
            initial_failure=result["initial_failure"],
            failure_mode=result["failure_mode"],
            severity=result["severity"],
            failed_nodes=result["failed_nodes"],
            total_affected=result["total_affected"],
            cascade_log=result["cascade_log"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cascade simulation failed: {str(e)}")

@router.post("/run-stabilization", response_model=StabilizationResponse)
async def run_stabilization(request: StabilizationRequest, background_tasks: BackgroundTasks):
    """
    Run reinforcement learning stabilization strategies
    
    This endpoint uses Q-learning to find optimal stabilization actions
    """
    try:
        # Validate nodes exist
        for node_id in request.failed_nodes:
            if node_id not in self_healing_simulation.nodes:
                raise HTTPException(
                    status_code=404,
                    detail=f"Node {node_id} not found"
                )
        
        # Run reinforcement learning stabilization
        result = await self_healing_simulation.run_reinforcement_learning_stabilization(
            failed_nodes=request.failed_nodes
        )
        
        total_actions = len(result)
        average_reward = sum(r.get("reward", 0) for r in result.values()) / total_actions if total_actions > 0 else 0
        
        return StabilizationResponse(
            stabilization_results=result,
            total_actions=total_actions,
            average_reward=average_reward,
            execution_time=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stabilization failed: {str(e)}")

@router.get("/health", response_model=InfrastructureHealthResponse)
async def get_infrastructure_health():
    """Get current infrastructure health metrics"""
    try:
        health = self_healing_simulation.get_infrastructure_health()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_stabilization_recommendations():
    """Get RL-based stabilization recommendations"""
    try:
        recommendations = self_healing_simulation.get_stabilization_recommendations()
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")

@router.get("/nodes")
async def get_infrastructure_nodes():
    """Get all infrastructure nodes"""
    try:
        nodes = {}
        for node_id, node in self_healing_simulation.nodes.items():
            nodes[node_id] = {
                "node_id": node_id,
                "name": node.name,
                "type": node.type.value,
                "location": node.location,
                "status": node.status.value,
                "health_score": node.health_score,
                "load_percentage": node.load_percentage,
                "redundancy_level": node.redundancy_level,
                "dependencies": node.dependencies,
                "dependents": node.dependents,
                "failure_probability": node.failure_probability,
                "current_failure_mode": node.current_failure_mode.value if node.current_failure_mode else None,
                "stabilization_actions": node.stabilization_actions
            }
        return nodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Node retrieval failed: {str(e)}")

@router.get("/simulation-metrics")
async def get_simulation_metrics():
    """Get simulation and training metrics"""
    try:
        metrics = self_healing_simulation.get_simulation_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")

@router.get("/node/{node_id}/status")
async def get_node_status(node_id: str):
    """Get detailed status of a specific node"""
    try:
        if node_id not in self_healing_simulation.nodes:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
        
        node = self_healing_simulation.nodes[node_id]
        
        return {
            "node_id": node_id,
            "name": node.name,
            "type": node.type.value,
            "location": node.location,
            "status": node.status.value,
            "health_score": node.health_score,
            "load_percentage": node.load_percentage,
            "redundancy_level": node.redundancy_level,
            "dependencies": node.dependencies,
            "dependents": node.dependents,
            "repair_time_hours": node.repair_time_hours,
            "last_maintenance": node.last_maintenance.isoformat(),
            "failure_probability": node.failure_probability,
            "current_failure_mode": node.current_failure_mode.value if node.current_failure_mode else None,
            "stabilization_actions": node.stabilization_actions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Node status retrieval failed: {str(e)}")

@router.get("/infrastructure-types")
async def get_infrastructure_types():
    """Get available infrastructure types"""
    return {
        "infrastructure_types": [it.value for it in InfrastructureType],
        "type_descriptions": {
            "power_grid": "Electrical power generation and distribution systems",
            "telecom_tower": "Telecommunication towers and network infrastructure",
            "water_system": "Water treatment and distribution systems",
            "transport_bridge": "Transportation bridges and critical infrastructure",
            "hospital": "Medical facilities and hospitals",
            "school": "Educational institutions and schools",
            "communication_center": "Communication and data centers"
        }
    }

@router.get("/failure-modes")
async def get_failure_modes():
    """Get available failure modes"""
    return {
        "failure_modes": [fm.value for fm in FailureMode],
        "mode_descriptions": {
            "overload": "System overload due to excessive load",
            "weather_damage": "Damage caused by severe weather conditions",
            "structural_damage": "Physical structural damage to infrastructure",
            "equipment_failure": "Failure of critical equipment or components",
            "power_outage": "Loss of electrical power supply",
            "connectivity_loss": "Loss of network connectivity"
        }
    }

@router.get("/stabilization-actions")
async def get_stabilization_actions():
    """Get available stabilization actions"""
    actions = []
    for action in self_healing_simulation.stabilization_actions.values():
        actions.append({
            "action_id": action.action_id,
            "action_type": action.action_type,
            "description": action.description,
            "effectiveness": action.effectiveness,
            "cost_estimate": action.cost_estimate,
            "execution_time_minutes": action.execution_time_minutes,
            "resource_requirements": action.resource_requirements
        })
    
    return {
        "stabilization_actions": actions,
        "total_actions": len(actions)
    }
