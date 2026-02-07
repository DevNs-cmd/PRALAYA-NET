"""
Intent-Driven Command API
Machine-enforceable Response Intent Objects for autonomous disaster response
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from services.intent_command_engine import (
    intent_command_engine,
    ResponseIntent,
    IntentType,
    AuthorityLevel,
    RiskTolerance,
    IntentStatus
)

router = APIRouter(prefix="/adir", tags=["intent-driven-command"])

class IntentCreationRequest(BaseModel):
    intent_type: str = Field(..., description="Type of intent")
    target_outcome: str = Field(..., description="Desired outcome")
    risk_tolerance: str = Field(..., description="Risk tolerance level")
    authority_level: str = Field(..., description="Authority level")
    evidence_requirements: List[Dict] = Field(default_factory=list, description="Evidence requirements")
    resource_permissions: List[Dict] = Field(default_factory=list, description="Resource permissions")
    expiration_hours: int = Field(default=24, description="Expiration time in hours")
    created_by: str = Field(default="system", description="Creator of intent")

class IntentCreationResponse(BaseModel):
    intent_id: str
    status: str
    message: str
    created_at: str
    immutable_hash: str

class IntentExecutionRequest(BaseModel):
    intent_id: str = Field(..., description="Intent ID to execute")
    executor_id: str = Field(..., description="Executor identifier")

class IntentStatusResponse(BaseModel):
    intent_id: str
    status: str
    intent_type: str
    target_outcome: str
    authority_level: str
    created_at: str
    expiration_deadline: str
    execution_log: List[Dict]
    immutable_hash: str

@router.post("/create-intent", response_model=IntentCreationResponse)
async def create_intent(request: IntentCreationRequest, background_tasks: BackgroundTasks):
    """
    Create a machine-enforceable Response Intent
    
    This endpoint creates intent objects that govern all disaster response actions
    """
    try:
        # Validate intent type
        try:
            intent_type = IntentType(request.intent_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid intent type. Must be one of: {[it.value for it in IntentType]}"
            )
        
        # Validate risk tolerance
        try:
            risk_tolerance = RiskTolerance(request.risk_tolerance.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid risk tolerance. Must be one of: {[rt.value for rt in RiskTolerance]}"
            )
        
        # Validate authority level
        try:
            authority_level = AuthorityLevel(request.authority_level.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid authority level. Must be one of {[al.value for al in AuthorityLevel]}"
            )
        
        # Convert evidence requirements
        evidence_requirements = []
        for req in request.evidence_requirements:
            evidence_requirements.append({
                "evidence_type": req.get("evidence_type"),
                "required_confidence": req.get("required_confidence", 0.7),
                "verification_method": req.get("verification_method", "automated"),
                "collection_deadline": datetime.now() + timedelta(hours=req.get("collection_deadline_hours", 24)),
                "current_status": "pending"
            })
        
        # Convert resource permissions
        resource_permissions = []
        for req in request.resource_permissions:
            resource_permissions.append({
                "resource_type": req.get("resource_type"),
                "quantity": req.get("quantity", 1),
                "authority_required": req.get("authority_required", "municipal"),
                "cost_estimate_usd": req.get("cost_estimate_usd", 0),
                "availability_status": req.get("availability_status", "available")
            })
        
        # Create intent
        intent_id = await intent_command_engine.create_intent(
            intent_type=intent_type,
            target_outcome=request.target_outcome,
            risk_tolerance=risk_tolerance,
            authority_level=authority_level,
            evidence_requirements=evidence_requirements,
            resource_permissions=resource_permissions,
            expiration_hours=request.expiration_hours,
            created_by=request.created_by
        )
        
        return IntentCreationResponse(
            intent_id=intent_id,
            status="created",
            message="Intent created successfully",
            created_at=datetime.now().isoformat(),
            immutable_hash=intent_command_engine.active_intents[intent_id].immutable_hash
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent creation failed: {str(e)}")

@router.post("/execute-intent", response_model=Dict)
async def execute_intent(request: IntentExecutionRequest):
    """
    Execute a Response Intent with full audit trail
    
    This endpoint enforces machine-enforceable commands with immutable logging
    """
    try:
        result = await intent_command_engine.execute_intent(
            intent_id=request.intent_id,
            executor_id=request.executor_id
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent execution failed: {str(e)}")

@router.get("/intent/{intent_id}/status", response_model=IntentStatusResponse)
async def get_intent_status(intent_id: str):
    """Get current status of an intent"""
    try:
        status = await intent_command_engine.get_intent_status(intent_id)
        return status
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.get("/execution-queue")
async def get_execution_queue():
    """Get current execution queue"""
    try:
        queue = intent_command_engine.get_execution_queue()
        return queue
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Queue retrieval failed: {str(e)}")

@router.get("/forensic-ledger")
async def get_forensic_ledger(limit: int = 100):
    """Get forensic execution ledger for audit trails"""
    try:
        ledger = intent_command_engine.get_forensic_ledger(limit)
        return ledger
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ledger retrieval failed: {str(e)}")

@router.get("/intent-types")
async def get_intent_types():
    """Get available intent types and their descriptions"""
    return {
        "intent_types": [it.value for it in IntentType],
        "intent_descriptions": {
            "evacuation": "Coordinate civilian evacuation operations",
            "infrastructure_stabilization": "Stabilize failing infrastructure to prevent cascades",
            "search_rescue": "Deploy search and rescue operations",
            "medical_response": "Coordinate medical response teams",
            "supply_deployment": "Deploy emergency supplies and resources",
            "communication_restore": "Restore critical communication infrastructure",
            "infrastructure_repair": "Repair damaged infrastructure"
        },
        "authority_levels": [al.value for al in AuthorityLevel],
        "authority_descriptions": {
            "national": "Prime Minister, Cabinet - National level authority",
            "state": "Chief Minister, State Agencies - State level authority",
            "district": "District Collector, Local Authorities - District level authority",
            "municipal": "Mayor, Municipal Corporation - Municipal level authority",
            "autonomous": "System-initiated emergency response - Autonomous authority for life-saving"
        },
        "risk_tolerances": [rt.value for rt in RiskTolerance],
        "risk_descriptions": {
            "zero_tolerance": "No acceptable risk - maximum safety protocols",
            "low_tolerance": "Minimal acceptable risk - conservative approach",
            "moderate_tolerance": "Balanced risk approach - standard protocols",
            "high_tolerance": "High-risk acceptable for life-saving operations",
            "critical_tolerance": "Maximum risk tolerance - emergency situations"
        }
    }

@router.get("/authority-matrix")
async def get_authority_matrix():
    """Get authority level permissions matrix"""
    return intent_command_engine.authority_matrix
