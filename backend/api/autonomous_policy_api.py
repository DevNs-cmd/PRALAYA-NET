"""
API endpoints for Autonomous Response Policy Engine
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio

from backend.services.autonomous_policy_engine import autonomous_policy_engine

router = APIRouter(prefix="/policy", tags=["autonomous_policy"])

class PolicyCreateRequest(BaseModel):
    name: str
    description: str
    trigger_conditions: List[Dict[str, Any]]
    execution_scope: str
    resource_requirements: List[Dict[str, Any]]
    expiration_deadline: str
    stabilization_metrics: List[Dict[str, Any]]
    verification_requirements: List[Dict[str, Any]]
    created_by: str
    authorized_by: str
    priority: int

class PolicyCreateResponse(BaseModel):
    policy_id: str
    status: str
    message: str
    created_at: str

class PolicyResponse(BaseModel):
    policy_id: str
    name: str
    description: str
    status: str
    created_at: str
    execution_count: int
    success_count: int
    effectiveness_score: float

class SystemMetricsResponse(BaseModel):
    total_policies: int
    active_policies: int
    total_executions: int
    success_rate: float
    current_metrics_count: int
    execution_history_size: int
    timestamp: str

@router.post("/create", response_model=PolicyCreateResponse)
async def create_policy(request: PolicyCreateRequest):
    """Create new autonomous response policy"""
    try:
        policy_data = request.dict()
        
        # Convert deadline string to datetime
        policy_data["expiration_deadline"] = datetime.fromisoformat(policy_data["expiration_deadline"])
        
        policy_id = autonomous_policy_engine.create_policy(policy_data)
        
        return PolicyCreateResponse(
            policy_id=policy_id,
            status="created",
            message="Policy created successfully",
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Policy creation failed: {str(e)}")

@router.post("/{policy_id}/activate")
async def activate_policy(policy_id: str):
    """Activate a policy"""
    try:
        success = autonomous_policy_engine.activate_policy(policy_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        return {
            "policy_id": policy_id,
            "status": "activated",
            "message": "Policy activated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy activation failed: {str(e)}")

@router.post("/{policy_id}/deactivate")
async def deactivate_policy(policy_id: str):
    """Deactivate a policy"""
    try:
        success = autonomous_policy_engine.deactivate_policy(policy_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        return {
            "policy_id": policy_id,
            "status": "deactivated",
            "message": "Policy deactivated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy deactivation failed: {str(e)}")

@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(policy_id: str):
    """Get policy by ID"""
    try:
        policy = autonomous_policy_engine.get_policy(policy_id)
        
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        return PolicyResponse(**policy)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy retrieval failed: {str(e)}")

@router.get("/all", response_model=List[PolicyResponse])
async def get_all_policies():
    """Get all policies"""
    try:
        policies = autonomous_policy_engine.get_all_policies()
        return [PolicyResponse(**policy) for policy in policies]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policies retrieval failed: {str(e)}")

@router.get("/active", response_model=List[PolicyResponse])
async def get_active_policies():
    """Get active policies"""
    try:
        policies = autonomous_policy_engine.get_active_policies()
        return [PolicyResponse(**policy) for policy in policies]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Active policies retrieval failed: {str(e)}")

@router.get("/execution-history")
async def get_execution_history(limit: int = 100):
    """Get policy execution history"""
    try:
        history = autonomous_policy_engine.get_execution_history(limit)
        return {
            "execution_history": history,
            "total_entries": len(history),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution history retrieval failed: {str(e)}")

@router.get("/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """Get policy engine system metrics"""
    try:
        metrics = autonomous_policy_engine.get_system_metrics()
        return SystemMetricsResponse(**metrics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {str(e)}")

@router.post("/update-metrics")
async def update_metrics(metrics: Dict[str, Any]):
    """Update system metrics for policy evaluation"""
    try:
        await autonomous_policy_engine.update_metrics(metrics)
        
        return {
            "status": "updated",
            "message": "Metrics updated successfully",
            "metrics_count": len(metrics),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics update failed: {str(e)}")
