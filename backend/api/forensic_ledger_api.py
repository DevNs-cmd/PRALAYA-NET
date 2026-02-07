"""
Forensic Execution Ledger API
Immutable audit trails for all decisions, predictions, and actions with replayable simulation states
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from services.forensic_ledger import (
    forensic_ledger,
    EventType,
    EvidenceType
)

router = APIRouter(prefix="/forensic", tags=["forensic-ledger"])

class LedgerEntryRequest(BaseModel):
    event_type: str = Field(..., description="Type of event")
    actor_id: str = Field(..., description="Actor identifier")
    actor_type: str = Field(..., description="Type of actor")
    action_description: str = Field(..., description="Description of action")
    decision_context: Dict = Field(default_factory=dict, description="Decision context")
    evidence_artifacts: List[Dict] = Field(default_factory=list, description="Evidence artifacts")
    outcome: Dict = Field(default_factory=dict, description="Action outcome")
    related_entries: List[str] = Field(default_factory=list, description="Related entry IDs")

class EvidenceArtifactRequest(BaseModel):
    artifact_id: str = Field(..., description="Evidence artifact ID")
    evidence_type: str = Field(..., description="Type of evidence")
    content: Dict = Field(..., description="Evidence content")
    source: str = Field(..., description="Evidence source")

class SimulationStateRequest(BaseModel):
    infrastructure_state: Dict = Field(default_factory=dict, description="Infrastructure state")
    agent_states: Dict = Field(default_factory=dict, description="Agent states")
    sensor_data: List[Dict] = Field(default_factory=list, description="Sensor data snapshot")
    active_intents: List[Dict] = Field(default_factory=list, description="Active intents")
    risk_assessment: Dict = Field(default_factory=dict, description="Risk assessment")
    environmental_conditions: Dict = Field(default_factory=dict, description="Environmental conditions")
    communication_logs: List[Dict] = Field(default_factory=list, description="Communication logs")

class IncidentReportRequest(BaseModel):
    start_time: datetime = Field(..., description="Incident start time")
    end_time: datetime = Field(..., description="Incident end time")

@router.post("/create-entry")
async def create_ledger_entry(request: LedgerEntryRequest, background_tasks: BackgroundTasks):
    """
    Create a new ledger entry with full audit trail
    
    This endpoint creates immutable audit trails for all system actions
    """
    try:
        # Validate event type
        try:
            event_type = EventType(request.event_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event type. Must be one of: {[et.value for et in EventType]}"
            )
        
        # Convert evidence artifacts
        from services.forensic_ledger import EvidenceArtifact
        evidence_artifacts = []
        
        for artifact_data in request.evidence_artifacts:
            try:
                evidence_type = EvidenceType(artifact_data["evidence_type"].lower())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid evidence type. Must be one of: {[et.value for et in EvidenceType]}"
                )
            
            artifact = EvidenceArtifact(
                artifact_id=artifact_data["artifact_id"],
                evidence_type=evidence_type,
                timestamp=datetime.now(),
                content=artifact_data["content"],
                source=artifact_data["source"],
                hash_value=""
            )
            
            evidence_artifacts.append(artifact)
        
        # Create ledger entry
        entry_id = await forensic_ledger.create_entry(
            event_type=event_type,
            actor_id=request.actor_id,
            actor_type=request.actor_type,
            action_description=request.action_description,
            decision_context=request.decision_context,
            evidence_artifacts=evidence_artifacts,
            outcome=request.outcome,
            related_entries=request.related_entries
        )
        
        return {
            "entry_id": entry_id,
            "status": "created",
            "message": "Ledger entry created successfully",
            "timestamp": datetime.now().isoformat(),
            "immutable_hash": forensic_ledger.get_entry_by_id(entry_id).immutable_hash
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ledger entry creation failed: {str(e)}")

@router.post("/capture-simulation-state")
async def capture_simulation_state(request: SimulationStateRequest):
    """
    Capture simulation state for replayable analysis
    
    This endpoint enables post-incident reconstruction and analysis
    """
    try:
        state_id = await forensic_ledger.capture_simulation_state(
            infrastructure_state=request.infrastructure_state,
            agent_states=request.agent_states,
            sensor_data=request.sensor_data,
            active_intents=request.active_intents,
            risk_assessment=request.risk_assessment,
            environmental_conditions=request.environmental_conditions,
            communication_logs=request.communication_logs
        )
        
        return {
            "state_id": state_id,
            "status": "captured",
            "message": "Simulation state captured successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"State capture failed: {str(e)}")

@router.get("/entry/{entry_id}")
async def get_ledger_entry(entry_id: str):
    """Get ledger entry by ID"""
    try:
        entry = forensic_ledger.get_entry_by_id(entry_id)
        
        if not entry:
            raise HTTPException(status_code=404, detail=f"Entry {entry_id} not found")
        
        return {
            "entry_id": entry.entry_id,
            "event_type": entry.event_type.value,
            "timestamp": entry.timestamp.isoformat(),
            "actor_id": entry.actor_id,
            "actor_type": entry.actor_type,
            "action_description": entry.action_description,
            "decision_context": entry.decision_context,
            "outcome": entry.outcome,
            "immutable_hash": entry.immutable_hash,
            "related_entries": entry.related_entries,
            "evidence_artifacts": [
                {
                    "artifact_id": artifact.artifact_id,
                    "evidence_type": artifact.evidence_type.value,
                    "timestamp": artifact.timestamp.isoformat(),
                    "source": artifact.source,
                    "hash_value": artifact.hash_value,
                    "verified": artifact.verified,
                    "verification_timestamp": artifact.verification_timestamp.isoformat() if artifact.verification_timestamp else None
                }
                for artifact in entry.evidence_artifacts
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Entry retrieval failed: {str(e)}")

@router.get("/verify-evidence/{artifact_id}")
async def verify_evidence_integrity(artifact_id: str):
    """Verify integrity of evidence artifact"""
    try:
        result = await forensic_ledger.verify_evidence_integrity(artifact_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evidence verification failed: {str(e)}")

@router.get("/replay-state/{state_id}")
async def replay_simulation_state(state_id: str):
    """Get simulation state for replay"""
    try:
        state = forensic_ledger.replay_simulation_state(state_id)
        
        if not state:
            raise HTTPException(status_code=404, detail=f"State {state_id} not found")
        
        return {
            "state_id": state.state_id,
            "timestamp": state.timestamp.isoformat(),
            "infrastructure_state": state.infrastructure_state,
            "agent_states": state.agent_states,
            "sensor_data_snapshot": state.sensor_data_snapshot,
            "active_intents": state.active_intents,
            "risk_assessment": state.risk_assessment,
            "environmental_conditions": state.environmental_conditions,
            "communication_logs": state.communication_logs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"State replay failed: {str(e)}")

@router.post("/incident-report")
async def generate_incident_report(request: IncidentReportRequest):
    """Generate comprehensive incident report"""
    try:
        report = forensic_ledger.generate_incident_report(request.start_time, request.end_time)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.get("/statistics")
async def get_ledger_statistics():
    """Get forensic ledger statistics"""
    try:
        stats = forensic_ledger.get_ledger_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")

@router.get("/events/{event_type}")
async def get_entries_by_event_type(event_type: str, limit: int = 100):
    """Get ledger entries by event type"""
    try:
        try:
            event_enum = EventType(event_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event type. Must be one of: {[et.value for et in EventType]}"
            )
        
        entries = forensic_ledger.get_entries_by_event_type(event_enum, limit)
        
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                "entry_id": entry.entry_id,
                "event_type": entry.event_type.value,
                "timestamp": entry.timestamp.isoformat(),
                "actor_id": entry.actor_id,
                "actor_type": entry.actor_type,
                "action_description": entry.action_description,
                "outcome": entry.outcome,
                "immutable_hash": entry.immutable_hash,
                "evidence_count": len(entry.evidence_artifacts)
            })
        
        return {
            "event_type": event_type,
            "entries": formatted_entries,
            "total_found": len(formatted_entries),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event type retrieval failed: {str(e)}")

@router.get("/actor/{actor_id}")
async def get_entries_by_actor(actor_id: str, limit: int = 100):
    """Get ledger entries by actor"""
    try:
        entries = forensic_ledger.get_entries_by_actor(actor_id, limit)
        
        formatted_entries = []
        for entry in entries:
            formatted_entries.append({
                "entry_id": entry.entry_id,
                "event_type": entry.event_type.value,
                "timestamp": entry.timestamp.isoformat(),
                "action_description": entry.action_description,
                "outcome": entry.outcome,
                "immutable_hash": entry.immutable_hash,
                "evidence_count": len(entry.evidence_artifacts)
            })
        
        return {
            "actor_id": actor_id,
            "entries": formatted_entries,
            "total_found": len(formatted_entries),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Actor entries retrieval failed: {str(e)}")

@router.get("/event-types")
async def get_event_types():
    """Get available event types"""
    return {
        "event_types": [et.value for et in EventType],
        "event_descriptions": {
            "intent_created": "Response intent created for disaster response",
            "intent_executed": "Response intent executed by system",
            "prediction_made": "Disaster prediction generated by AI models",
            "action_taken": "Autonomous action taken by system",
            "agent_allocated": "Multi-agent task allocation performed",
            "task_completed": "Agent task completed successfully",
            "infrastructure_stabilized": "Infrastructure stabilization action performed",
            "sensor_data_received": "Sensor data received from various sources",
            "data_fused": "Multi-source sensor data fusion completed",
            "cascade_detected": "Infrastructure cascade failure detected",
            "emergency_broadcast": "Emergency broadcast message sent"
        }
    }

@router.get("/evidence-types")
async def get_evidence_types():
    """Get available evidence types"""
    return {
        "evidence_types": [et.value for et in EvidenceType],
        "evidence_descriptions": {
            "sensor_data": "Data from IoT sensors and monitoring systems",
            "camera_feed": "Visual evidence from camera feeds and drones",
            "prediction_model": "AI/ML model predictions and outputs",
            "human_decision": "Human operator decisions and commands",
            "system_log": "System logs and automated processes",
            "external_api": "Data from external APIs and services",
            "communication_log": "Communication transcripts and logs"
        }
    }

@router.get("/ledger-integrity")
async def get_ledger_integrity():
    """Get ledger integrity information"""
    try:
        return {
            "ledger_hash": forensic_ledger.ledger_hash,
            "total_entries": len(forensic_ledger.ledger_entries),
            "total_evidence_artifacts": len(forensic_ledger.evidence_artifacts),
            "simulation_states": len(forensic_ledger.simulation_states),
            "verification_chain_entries": len(forensic_ledger.verification_chain),
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integrity check failed: {str(e)}")
