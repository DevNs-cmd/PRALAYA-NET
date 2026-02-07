"""
Autonomous Infrastructure Stabilization API
POST /stabilization/generate-plan
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from services.infrastructure_stabilization import (
    infrastructure_stabilization_engine,
    StabilizationActionType,
    StabilizationPriority
)
from services.national_digital_twin import DisasterType

router = APIRouter(prefix="/stabilization", tags=["infrastructure-stabilization"])

class StabilizationRequest(BaseModel):
    disaster_type: str = Field(..., description="Type of disaster")
    epicenter_lat: float = Field(..., ge=-90, le=90, description="Epicenter latitude")
    epicenter_lon: float = Field(..., ge=-180, le=180, description="Epicenter longitude")
    severity: float = Field(..., ge=0, le=1, description="Disaster severity (0-1)")
    auto_execute: bool = Field(default=False, description="Auto-execute critical actions")

class StabilizationActionResponse(BaseModel):
    action_id: str
    action_type: str
    target_node: str
    source_nodes: List[str]
    description: str
    expected_risk_reduction: float
    execution_time_minutes: int
    priority: str
    resource_requirements: Dict[str, int]
    confidence_score: float
    side_effects: List[str]

class StabilizationPlanResponse(BaseModel):
    plan_id: str
    cascade_probability: float
    affected_nodes: List[str]
    stabilization_actions: List[StabilizationActionResponse]
    expected_risk_reduction_percent: float
    total_execution_time_minutes: int
    resource_requirements: Dict[str, int]
    confidence_score: float
    generated_at: str
    execution_sequence: List[str]

@router.post("/generate-plan", response_model=StabilizationPlanResponse)
async def generate_stabilization_plan(request: StabilizationRequest, background_tasks: BackgroundTasks):
    """
    Generate autonomous infrastructure stabilization plan
    
    This endpoint transforms PRALAYA-NET from predictive to proactive
    by generating self-healing infrastructure actions.
    """
    try:
        # Validate disaster type
        try:
            disaster_type = DisasterType(request.disaster_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid disaster type. Must be one of: {[dt.value for dt in DisasterType]}"
            )
        
        # Generate stabilization plan
        plan = await infrastructure_stabilization_engine.generate_stabilization_plan(
            disaster_type=disaster_type,
            epicenter_lat=request.epicenter_lat,
            epicenter_lon=request.epicenter_lon,
            severity=request.severity
        )
        
        # Auto-execute critical actions if requested
        if request.auto_execute:
            critical_actions = [
                action for action in plan.stabilization_actions
                if action.priority == StabilizationPriority.CRITICAL
            ]
            
            for action in critical_actions:
                background_tasks.add_task(
                    infrastructure_stabilization_engine.execute_stabilization_action,
                    action.action_id
                )
        
        # Convert to response format
        actions_response = [
            StabilizationActionResponse(
                action_id=action.action_id,
                action_type=action.action_type.value,
                target_node=action.target_node,
                source_nodes=action.source_nodes,
                description=action.description,
                expected_risk_reduction=action.expected_risk_reduction,
                execution_time_minutes=action.execution_time_minutes,
                priority=action.priority.value,
                resource_requirements=action.resource_requirements,
                confidence_score=action.confidence_score,
                side_effects=action.side_effects
            )
            for action in plan.stabilization_actions
        ]
        
        return StabilizationPlanResponse(
            plan_id=plan.plan_id,
            cascade_probability=plan.cascade_probability,
            affected_nodes=plan.affected_nodes,
            stabilization_actions=actions_response,
            expected_risk_reduction_percent=plan.expected_risk_reduction_percent,
            total_execution_time_minutes=plan.total_execution_time_minutes,
            resource_requirements=plan.resource_requirements,
            confidence_score=plan.confidence_score,
            generated_at=plan.generated_at.isoformat(),
            execution_sequence=plan.execution_sequence
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stabilization plan generation failed: {str(e)}")

@router.post("/execute-action/{action_id}")
async def execute_stabilization_action(action_id: str):
    """
    Execute a specific stabilization action
    """
    try:
        result = await infrastructure_stabilization_engine.execute_stabilization_action(action_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action execution failed: {str(e)}")

@router.get("/active-plans")
async def get_active_stabilization_plans():
    """Get all active stabilization plans"""
    try:
        plans = infrastructure_stabilization_engine.get_active_stabilization_plans()
        return {
            "active_plans": plans,
            "total_active": len(plans),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active plans: {str(e)}")

@router.get("/execution-history")
async def get_execution_history():
    """Get stabilization action execution history"""
    try:
        history = infrastructure_stabilization_engine.execution_history
        return {
            "execution_history": history,
            "total_executed": len(history),
            "average_risk_reduction": sum(h["actual_risk_reduction"] for h in history) / len(history) if history else 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get execution history: {str(e)}")

@router.get("/action-types")
async def get_stabilization_action_types():
    """Get supported stabilization action types"""
    return {
        "action_types": [action_type.value for action_type in StabilizationActionType],
        "action_descriptions": {
            "load_redistribution": "Redistribute power load to prevent grid overload",
            "emergency_rerouting": "Reroute critical services around affected areas",
            "redundancy_activation": "Activate backup systems and redundancy",
            "hospital_load_balancing": "Transfer patients between medical facilities",
            "telecom_backup_switch": "Switch to backup communication systems",
            "power_grid_isolation": "Isolate failing grid sections to prevent cascade",
            "water_flow_rerouting": "Reroute water supply around compromised infrastructure",
            "transport_corridor_opening": "Open emergency transport corridors"
        },
        "priorities": [priority.value for priority in StabilizationPriority],
        "effectiveness_ratings": {
            "load_redistribution": 0.25,
            "emergency_rerouting": 0.20,
            "redundancy_activation": 0.35,
            "hospital_load_balancing": 0.30,
            "telecom_backup_switch": 0.40,
            "power_grid_isolation": 0.45,
            "water_flow_rerouting": 0.25,
            "transport_corridor_opening": 0.20
        }
    }

@router.get("/threshold-status")
async def get_stabilization_threshold_status():
    """Get current cascade risk vs stabilization threshold"""
    try:
        # Get current system-wide cascade risk (simplified)
        current_risk = 0.35  # This would be calculated from real-time data
        threshold = infrastructure_stabilization_engine.stabilization_threshold
        
        return {
            "current_cascade_risk": current_risk,
            "stabilization_threshold": threshold,
            "stabilization_required": current_risk >= threshold,
            "risk_margin": current_risk - threshold,
            "recommended_action": "IMMEDIATE_STABILIZATION" if current_risk >= threshold else "MONITOR",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threshold status: {str(e)}")
