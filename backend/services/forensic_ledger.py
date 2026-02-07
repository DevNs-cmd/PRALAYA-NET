"""
Forensic Execution Ledger
Immutable audit trails for all decisions, predictions, and actions with replayable simulation states
"""

import asyncio
import hashlib
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

class EventType(Enum):
    INTENT_CREATED = "intent_created"
    INTENT_EXECUTED = "intent_executed"
    PREDICTION_MADE = "prediction_made"
    ACTION_TAKEN = "action_taken"
    AGENT_ALLOCATED = "agent_allocated"
    TASK_COMPLETED = "task_completed"
    INFRASTRUCTURE_STABILIZED = "infrastructure_stabilized"
    SENSOR_DATA_RECEIVED = "sensor_data_received"
    DATA_FUSED = "data_fused"
    CASCADE_DETECTED = "cascade_detected"
    EMERGENCY_BROADCAST = "emergency_broadcast"

class EvidenceType(Enum):
    SENSOR_DATA = "sensor_data"
    CAMERA_FEED = "camera_feed"
    PREDICTION_MODEL = "prediction_model"
    HUMAN_DECISION = "human_decision"
    SYSTEM_LOG = "system_log"
    EXTERNAL_API = "external_api"
    COMMUNICATION_LOG = "communication_log"

@dataclass
class EvidenceArtifact:
    artifact_id: str
    evidence_type: EvidenceType
    timestamp: datetime
    content: Dict[str, Any]
    source: str
    hash_value: str
    verified: bool = False
    verification_timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        # Generate hash for integrity verification
        self.hash_value = self._generate_hash()
    
    def _generate_hash(self) -> str:
        """Generate SHA-256 hash for evidence integrity"""
        content_str = json.dumps(self.content, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()

@dataclass
class LedgerEntry:
    entry_id: str
    event_type: EventType
    timestamp: datetime
    actor_id: str
    actor_type: str
    action_description: str
    decision_context: Dict[str, Any]
    evidence_artifacts: List[EvidenceArtifact]
    outcome: Dict[str, Any]
    immutable_hash: str
    related_entries: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        # Generate immutable hash for audit trail
        self.immutable_hash = self._generate_immutable_hash()
    
    def _generate_immutable_hash(self) -> str:
        """Generate immutable hash for forensic audit"""
        ledger_data = {
            "entry_id": self.entry_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "actor_id": self.actor_id,
            "action_description": self.action_description,
            "outcome": self.outcome
        }
        ledger_str = json.dumps(ledger_data, sort_keys=True, default=str)
        return hashlib.sha256(ledger_str.encode()).hexdigest()

class SimulationState:
    """Replayable simulation state for post-incident analysis"""
    
    def __init__(self):
        self.state_id: str = ""
        self.timestamp: datetime = datetime.now()
        self.infrastructure_state: Dict[str, Any] = {}
        self.agent_states: Dict[str, Any] = {}
        self.sensor_data_snapshot: List[Dict] = {}
        self.active_intents: List[Dict] = {}
        self.risk_assessment: Dict[str, Any] = {}
        self.environmental_conditions: Dict[str, Any] = {}
        self.communication_logs: List[Dict] = []
    
    def capture_state(self, 
                     infrastructure_state: Dict[str, Any],
                     agent_states: Dict[str, Any],
                     sensor_data: List[Dict],
                     active_intents: List[Dict],
                     risk_assessment: Dict[str, Any],
                     environmental_conditions: Dict[str, Any],
                     communication_logs: List[Dict]):
        """Capture current system state"""
        self.state_id = f"state_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.timestamp = datetime.now()
        self.infrastructure_state = infrastructure_state.copy()
        self.agent_states = agent_states.copy()
        self.sensor_data_snapshot = sensor_data.copy()
        self.active_intents = active_intents.copy()
        self.risk_assessment = risk_assessment.copy()
        self.environmental_conditions = environmental_conditions.copy()
        self.communication_logs = communication_logs.copy()

class ForensicLedger:
    def __init__(self):
        self.ledger_entries: List[LedgerEntry] = []
        self.simulation_states: List[SimulationState] = []
        self.evidence_artifacts: Dict[str, EvidenceArtifact] = {}
        self.verification_chain: List[Dict] = []
        self.ledger_hash: str = ""
        
    async def create_entry(self,
                          event_type: EventType,
                          actor_id: str,
                          actor_type: str,
                          action_description: str,
                          decision_context: Dict[str, Any],
                          evidence_artifacts: List[EvidenceArtifact],
                          outcome: Dict[str, Any],
                          related_entries: List[str] = None) -> str:
        """Create a new ledger entry with full audit trail"""
        
        entry_id = f"ledger_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Store evidence artifacts
        for artifact in evidence_artifacts:
            self.evidence_artifacts[artifact.artifact_id] = artifact
        
        # Create ledger entry
        entry = LedgerEntry(
            entry_id=entry_id,
            event_type=event_type,
            timestamp=datetime.now(),
            actor_id=actor_id,
            actor_type=actor_type,
            action_description=action_description,
            decision_context=decision_context,
            evidence_artifacts=evidence_artifacts,
            outcome=outcome,
            immutable_hash="",
            related_entries=related_entries or []
        )
        
        # Add to ledger
        self.ledger_entries.append(entry)
        
        # Keep only recent entries (last 10000)
        if len(self.ledger_entries) > 10000:
            self.ledger_entries = self.ledger_entries[-10000:]
        
        # Update ledger hash
        self._update_ledger_hash()
        
        return entry_id
    
    def _update_ledger_hash(self):
        """Update overall ledger hash for integrity verification"""
        if not self.ledger_entries:
            self.ledger_hash = ""
            return
        
        # Create hash from all entry hashes
        entry_hashes = [entry.immutable_hash for entry in self.ledger_entries]
        ledger_str = json.dumps(entry_hashes, sort_keys=True)
        self.ledger_hash = hashlib.sha256(ledger_str.encode()).hexdigest()
    
    async def capture_simulation_state(self,
                                    infrastructure_state: Dict[str, Any],
                                    agent_states: Dict[str, Any],
                                    sensor_data: List[Dict],
                                    active_intents: List[Dict],
                                    risk_assessment: Dict[str, Any],
                                    environmental_conditions: Dict[str, Any],
                                    communication_logs: List[Dict]) -> str:
        """Capture simulation state for replayable analysis"""
        
        state = SimulationState()
        state.capture_state(
            infrastructure_state=infrastructure_state,
            agent_states=agent_states,
            sensor_data=sensor_data,
            active_intents=active_intents,
            risk_assessment=risk_assessment,
            environmental_conditions=environmental_conditions,
            communication_logs=communication_logs
        )
        
        self.simulation_states.append(state)
        
        # Keep only recent states (last 1000)
        if len(self.simulation_states) > 1000:
            self.simulation_states = self.simulation_states[-1000]
        
        return state.state_id
    
    async def verify_evidence_integrity(self, artifact_id: str) -> Dict[str, Any]:
        """Verify integrity of evidence artifact"""
        
        if artifact_id not in self.evidence_artifacts:
            return {"error": "Evidence artifact not found"}
        
        artifact = self.evidence_artifacts[artifact_id]
        
        # Recalculate hash
        content_str = json.dumps(artifact.content, sort_keys=True, default=str)
        current_hash = hashlib.sha256(content_str.encode()).hexdigest()
        
        # Verify integrity
        is_valid = current_hash == artifact.hash_value
        
        # Update verification status
        artifact.verified = is_valid
        artifact.verification_timestamp = datetime.now()
        
        # Add to verification chain
        self.verification_chain.append({
            "timestamp": datetime.now().isoformat(),
            "artifact_id": artifact_id,
            "original_hash": artifact.hash_value,
            "current_hash": current_hash,
            "is_valid": is_valid
        })
        
        return {
            "artifact_id": artifact_id,
            "is_valid": is_valid,
            "original_hash": artifact.hash_value,
            "current_hash": current_hash,
            "verification_timestamp": artifact.verification_timestamp.isoformat(),
            "evidence_type": artifact.evidence_type.value,
            "source": artifact.source
        }
    
    def get_entry_by_id(self, entry_id: str) -> Optional[LedgerEntry]:
        """Get ledger entry by ID"""
        for entry in self.ledger_entries:
            if entry.entry_id == entry_id:
                return entry
        return None
    
    def get_entries_by_event_type(self, event_type: EventType, limit: int = 100) -> List[LedgerEntry]:
        """Get ledger entries by event type"""
        entries = [entry for entry in self.ledger_entries if entry.event_type == event_type]
        return entries[-limit:] if entries else []
    
    def get_entries_by_actor(self, actor_id: str, limit: int = 100) -> List[LedgerEntry]:
        """Get ledger entries by actor"""
        entries = [entry for entry in self.ledger_entries if entry.actor_id == actor_id]
        return entries[-limit:] if entries else []
    
    def get_entries_by_timerange(self, start_time: datetime, end_time: datetime) -> List[LedgerEntry]:
        """Get ledger entries within time range"""
        entries = [
            entry for entry in self.ledger_entries
            if start_time <= entry.timestamp <= end_time
        ]
        return entries
    
    def replay_simulation_state(self, state_id: str) -> Optional[SimulationState]:
        """Get simulation state for replay"""
        for state in self.simulation_states:
            if state.state_id == state_id:
                return state
        return None
    
    def generate_incident_report(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate comprehensive incident report"""
        
        # Get relevant entries
        entries = self.get_entries_by_timerange(start_time, end_time)
        
        # Analyze events
        event_counts = {}
        for entry in entries:
            event_type = entry.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Analyze actors
        actor_counts = {}
        for entry in entries:
            actor_id = entry.actor_id
            actor_counts[actor_id] = actor_counts.get(actor_id, 0) + 1
        
        # Analyze outcomes
        successful_actions = 0
        failed_actions = 0
        for entry in entries:
            if entry.outcome.get("success"):
                successful_actions += 1
            elif entry.outcome.get("success") == False:
                failed_actions += 1
        
        # Get evidence summary
        evidence_summary = {}
        for entry in entries:
            for artifact in entry.evidence_artifacts:
                evidence_type = artifact.evidence_type.value
                evidence_summary[evidence_type] = evidence_summary.get(evidence_type, 0) + 1
        
        return {
            "incident_period": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_hours": (end_time - start_time).total_seconds() / 3600
            },
            "summary": {
                "total_entries": len(entries),
                "successful_actions": successful_actions,
                "failed_actions": failed_actions,
                "success_rate": successful_actions / (successful_actions + failed_actions) if (successful_actions + failed_actions) > 0 else 0
            },
            "event_analysis": event_counts,
            "actor_analysis": actor_counts,
            "evidence_analysis": evidence_summary,
            "ledger_integrity": {
                "ledger_hash": self.ledger_hash,
                "total_entries_in_ledger": len(self.ledger_entries),
                "verification_chain_entries": len(self.verification_chain)
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def get_ledger_statistics(self) -> Dict[str, Any]:
        """Get forensic ledger statistics"""
        
        if not self.ledger_entries:
            return {"message": "No ledger entries available"}
        
        # Calculate statistics
        total_entries = len(self.ledger_entries)
        event_distribution = {}
        for entry in self.ledger_entries:
            event_type = entry.event_type.value
            event_distribution[event_type] = event_distribution.get(event_type, 0) + 1
        
        # Evidence statistics
        evidence_distribution = {}
        for artifact in self.evidence_artifacts.values():
            evidence_type = artifact.evidence_type.value
            evidence_distribution[evidence_type] = evidence_distribution.get(evidence_type, 0) + 1
        
        # Time range
        timestamps = [entry.timestamp for entry in self.ledger_entries]
        time_range = {
            "earliest": min(timestamps).isoformat(),
            "latest": max(timestamps).isoformat()
        }
        
        return {
            "total_entries": total_entries,
            "event_distribution": event_distribution,
            "evidence_distribution": evidence_distribution,
            "total_evidence_artifacts": len(self.evidence_artifacts),
            "simulation_states": len(self.simulation_states),
            "verification_chain_entries": len(self.verification_chain),
            "time_range": time_range,
            "ledger_hash": self.ledger_hash,
            "generated_at": datetime.now().isoformat()
        }

# Global instance
forensic_ledger = ForensicLedger()
