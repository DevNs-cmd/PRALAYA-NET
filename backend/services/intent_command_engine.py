"""
Intent-Driven Command Engine
Machine-enforceable Response Intent Objects for autonomous disaster response
"""

import asyncio
import hashlib
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

class IntentType(Enum):
    EVACUATION = "evacuation"
    INFRASTRUCTURE_STABILIZATION = "infrastructure_stabilization"
    SEARCH_RESCUE = "search_rescue"
    MEDICAL_RESPONSE = "medical_response"
    SUPPLY_DEPLOYMENT = "supply_deployment"
    COMMUNICATION_RESTORE = "communication_restore"
    INFRASTRUCTURE_REPAIR = "infrastructure_repair"

class AuthorityLevel(Enum):
    NATIONAL = "national"      # Prime Minister, Cabinet
    STATE = "state"            # Chief Minister, State Agencies
    DISTRICT = "district"        # District Collector, Local Authorities
    MUNICIPAL = "municipal"      # Mayor, Municipal Corporation
    AUTONOMOUS = "autonomous"    # System-initiated emergency response

class RiskTolerance(Enum):
    ZERO_TOLERANCE = "zero_tolerance"      # No acceptable risk
    LOW_TOLERANCE = "low_tolerance"        # Minimal acceptable risk
    MODERATE_TOLERANCE = "moderate_tolerance"  # Balanced risk approach
    HIGH_TOLERANCE = "high_tolerance"        # High-risk acceptable for life-saving
    CRITICAL_TOLERANCE = "critical_tolerance"  # Maximum risk tolerance

class IntentStatus(Enum):
    PENDING = "pending"          # Created, awaiting validation
    VALIDATED = "validated"        # Validated and ready for execution
    EXECUTING = "executing"        # Currently being executed
    COMPLETED = "completed"        # Successfully completed
    FAILED = "failed"              # Execution failed
    EXPIRED = "expired"            # Intent expired without execution
    CANCELLED = "cancelled"        # Explicitly cancelled

@dataclass
class ResourcePermission:
    resource_type: str
    quantity: int
    authority_required: AuthorityLevel
    cost_estimate_usd: float
    availability_status: str

@dataclass
class EvidenceRequirement:
    evidence_type: str
    required_confidence: float
    verification_method: str
    collection_deadline: datetime
    current_status: str = "pending"

@dataclass
class ResponseIntent:
    intent_id: str
    intent_type: IntentType
    target_outcome: str
    risk_tolerance: RiskTolerance
    authority_level: AuthorityLevel
    evidence_requirements: List[EvidenceRequirement]
    resource_permissions: List[ResourcePermission]
    expiration_deadline: datetime
    created_at: datetime
    created_by: str
    status: IntentStatus = IntentStatus.PENDING
    execution_log: List[Dict] = field(default_factory=list)
    immutable_hash: str = ""
    
    def __post_init__(self):
        # Generate immutable hash for audit trail
        self.immutable_hash = self._generate_immutable_hash()
    
    def _generate_immutable_hash(self) -> str:
        """Generate immutable hash for forensic audit trail"""
        intent_data = {
            "intent_id": self.intent_id,
            "intent_type": self.intent_type.value,
            "target_outcome": self.target_outcome,
            "risk_tolerance": self.risk_tolerance.value,
            "authority_level": self.authority_level.value,
            "expiration_deadline": self.expiration_deadline.isoformat(),
            "created_at": self.created_at.isoformat()
        }
        intent_str = json.dumps(intent_data, sort_keys=True)
        return hashlib.sha256(intent_str.encode()).hexdigest()

class IntentCommandEngine:
    def __init__(self):
        self.active_intents: Dict[str, ResponseIntent] = {}
        self.intent_history: List[ResponseIntent] = []
        self.execution_queue: List[str] = []
        self.authority_matrix = self._build_authority_matrix()
        
    def _build_authority_matrix(self) -> Dict[AuthorityLevel, Dict[str, Any]]:
        """Build authority level permissions matrix"""
        return {
            AuthorityLevel.NATIONAL: {
                "max_risk_tolerance": RiskTolerance.CRITICAL_TOLERANCE,
                "max_cost_usd": 1000000000,  # $1B
                "can_override": [AuthorityLevel.STATE, AuthorityLevel.DISTRICT, AuthorityLevel.MUNICIPAL],
                "requires_approval": False
            },
            AuthorityLevel.STATE: {
                "max_risk_tolerance": RiskTolerance.HIGH_TOLERANCE,
                "max_cost_usd": 100000000,   # $100M
                "can_override": [AuthorityLevel.DISTRICT, AuthorityLevel.MUNICIPAL],
                "requires_approval": False
            },
            AuthorityLevel.DISTRICT: {
                "max_risk_tolerance": RiskTolerance.MODERATE_TOLERANCE,
                "max_cost_usd": 10000000,    # $10M
                "can_override": [AuthorityLevel.MUNICIPAL],
                "requires_approval": True
            },
            AuthorityLevel.MUNICIPAL: {
                "max_risk_tolerance": RiskTolerance.LOW_TOLERANCE,
                "max_cost_usd": 1000000,     # $1M
                "can_override": [],
                "requires_approval": True
            },
            AuthorityLevel.AUTONOMOUS: {
                "max_risk_tolerance": RiskTolerance.MODERATE_TOLERANCE,
                "max_cost_usd": 5000000,      # $5M for life-saving
                "can_override": [AuthorityLevel.MUNICIPAL],
                "requires_approval": False
            }
        }
    
    async def create_intent(self,
                          intent_type: IntentType,
                          target_outcome: str,
                          risk_tolerance: RiskTolerance,
                          authority_level: AuthorityLevel,
                          evidence_requirements: List[EvidenceRequirement],
                          resource_permissions: List[ResourcePermission],
                          expiration_hours: int = 24,
                          created_by: str = "system") -> str:
        """Create a new Response Intent with validation"""
        
        intent_id = f"intent_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        # Validate authority and risk tolerance
        validation_result = await self._validate_intent_authority(
            authority_level, risk_tolerance, resource_permissions
        )
        
        if not validation_result["valid"]:
            raise ValueError(f"Intent validation failed: {validation_result['reason']}")
        
        intent = ResponseIntent(
            intent_id=intent_id,
            intent_type=intent_type,
            target_outcome=target_outcome,
            risk_tolerance=risk_tolerance,
            authority_level=authority_level,
            evidence_requirements=evidence_requirements,
            resource_permissions=resource_permissions,
            expiration_deadline=datetime.now() + timedelta(hours=expiration_hours),
            created_at=datetime.now(),
            created_by=created_by
        )
        
        # Store intent
        self.active_intents[intent_id] = intent
        
        # Add to execution queue if auto-executable
        if authority_level == AuthorityLevel.AUTONOMOUS:
            await self._queue_for_execution(intent_id)
        
        return intent_id
    
    async def _validate_intent_authority(self,
                                      authority_level: AuthorityLevel,
                                      risk_tolerance: RiskTolerance,
                                      resource_permissions: List[ResourcePermission]) -> Dict[str, Any]:
        """Validate intent against authority matrix"""
        
        authority_perms = self.authority_matrix[authority_level]
        
        # Check risk tolerance
        risk_hierarchy = {
            RiskTolerance.ZERO_TOLERANCE: 0,
            RiskTolerance.LOW_TOLERANCE: 1,
            RiskTolerance.MODERATE_TOLERANCE: 2,
            RiskTolerance.HIGH_TOLERANCE: 3,
            RiskTolerance.CRITICAL_TOLERANCE: 4
        }
        
        if risk_hierarchy[risk_tolerance] > risk_hierarchy[authority_perms["max_risk_tolerance"]]:
            return {
                "valid": False,
                "reason": f"Risk tolerance {risk_tolerance.value} exceeds authority level {authority_level.value} limit"
            }
        
        # Check cost
        total_cost = sum(rp.cost_estimate_usd for rp in resource_permissions)
        if total_cost > authority_perms["max_cost_usd"]:
            return {
                "valid": False,
                "reason": f"Total cost ${total_cost:,.0f} exceeds authority level {authority_level.value} limit of ${authority_perms['max_cost_usd']:,.0f}"
            }
        
        return {"valid": True}
    
    async def _queue_for_execution(self, intent_id: str):
        """Queue intent for autonomous execution"""
        if intent_id not in self.active_intents:
            raise ValueError(f"Intent {intent_id} not found")
        
        self.execution_queue.append(intent_id)
        self.execution_queue.sort(key=lambda x: self._calculate_priority(x))
    
    def _calculate_priority(self, intent_id: str) -> int:
        """Calculate execution priority for intent"""
        intent = self.active_intents[intent_id]
        
        # Priority factors
        urgency = 5 if intent.risk_tolerance == RiskTolerance.CRITICAL_TOLERANCE else \
                 4 if intent.risk_tolerance == RiskTolerance.HIGH_TOLERANCE else \
                 3 if intent.risk_tolerance == RiskTolerance.MODERATE_TOLERANCE else \
                 2 if intent.risk_tolerance == RiskTolerance.LOW_TOLERANCE else 1
        
        authority_priority = {
            AuthorityLevel.NATIONAL: 5,
            AuthorityLevel.STATE: 4,
            AuthorityLevel.DISTRICT: 3,
            AuthorityLevel.MUNICIPAL: 2,
            AuthorityLevel.AUTONOMOUS: 5  # High priority for life-saving
        }
        
        time_remaining = (intent.expiration_deadline - datetime.now()).total_seconds()
        time_priority = max(1, int(time_remaining / 3600))  # Hours remaining
        
        return urgency * authority_priority[authority_level] * time_priority
    
    async def execute_intent(self, intent_id: str, executor_id: str) -> Dict[str, Any]:
        """Execute a Response Intent with full audit trail"""
        
        if intent_id not in self.active_intents:
            raise ValueError(f"Intent {intent_id} not found")
        
        intent = self.active_intents[intent_id]
        
        # Check if intent is expired
        if datetime.now() > intent.expiration_deadline:
            intent.status = IntentStatus.EXPIRED
            self._move_to_history(intent_id)
            return {
                "status": "expired",
                "reason": "Intent expired before execution",
                "intent_id": intent_id
            }
        
        # Update status
        intent.status = IntentStatus.EXECUTING
        
        # Log execution start
        execution_log = {
            "timestamp": datetime.now().isoformat(),
            "action": "execution_started",
            "executor_id": executor_id,
            "immutable_hash": intent.immutable_hash
        }
        intent.execution_log.append(execution_log)
        
        # Simulate execution (in production, this would trigger actual response)
        execution_result = await self._simulate_intent_execution(intent)
        
        # Update status based on result
        if execution_result["success"]:
            intent.status = IntentStatus.COMPLETED
        else:
            intent.status = IntentStatus.FAILED
        
        # Log execution completion
        completion_log = {
            "timestamp": datetime.now().isoformat(),
            "action": "execution_completed",
            "result": execution_result,
            "executor_id": executor_id
        }
        intent.execution_log.append(completion_log)
        
        # Move to history
        self._move_to_history(intent_id)
        
        return execution_result
    
    async def _simulate_intent_execution(self, intent: ResponseIntent) -> Dict[str, Any]:
        """Simulate intent execution (replace with actual execution in production)"""
        
        # Simulate execution based on intent type
        execution_results = {
            IntentType.EVACUATION: {
                "success": True,
                "people_evacuated": 5000,
                "time_taken_minutes": 45,
                "resources_used": ["buses", "emergency_services"],
                "outcome": "Evacuation completed successfully"
            },
            IntentType.INFRASTRUCTURE_STABILIZATION: {
                "success": True,
                "infrastructure_stabilized": ["power_grid", "telecom_tower"],
                "time_taken_minutes": 30,
                "resources_used": ["engineering_teams", "backup_systems"],
                "outcome": "Infrastructure stabilized successfully"
            },
            IntentType.SEARCH_RESCUE: {
                "success": True,
                "people_rescued": 150,
                "time_taken_minutes": 120,
                "resources_used": ["rescue_teams", "helicopters", "medical_teams"],
                "outcome": "Search and rescue completed successfully"
            },
            IntentType.MEDICAL_RESPONSE: {
                "success": True,
                "patients_treated": 200,
                "time_taken_minutes": 60,
                "resources_used": ["medical_teams", "ambulances", "supplies"],
                "outcome": "Medical response completed successfully"
            },
            IntentType.SUPPLY_DEPLOYMENT: {
                "success": True,
                "supplies_delivered": 1000,
                "time_taken_minutes": 90,
                "resources_used": ["trucks", "distribution_centers"],
                "outcome": "Supply deployment completed successfully"
            },
            IntentType.COMMUNICATION_RESTORE: {
                "success": True,
                "services_restored": ["cell_towers", "internet"],
                "time_taken_minutes": 180,
                "resources_used": ["tech_teams", "backup_equipment"],
                "outcome": "Communication restored successfully"
            },
            IntentType.INFRASTRUCTURE_REPAIR: {
                "success": True,
                "infrastructure_repaired": ["bridge", "power_lines"],
                "time_taken_minutes": 240,
                "resources_used": ["repair_crews", "materials", "equipment"],
                "outcome": "Infrastructure repair completed successfully"
            }
        }
        
        return execution_results.get(intent.intent_type, {
            "success": False,
            "error": "Unknown intent type",
            "outcome": "Execution failed"
        })
    
    def _move_to_history(self, intent_id: str):
        """Move intent to history and remove from active"""
        if intent_id in self.active_intents:
            intent = self.active_intents.pop(intent_id)
            self.intent_history.append(intent)
            
            # Keep only last 1000 intents in history
            if len(self.intent_history) > 1000:
                self.intent_history = self.intent_history[-1000:]
    
    async def get_intent_status(self, intent_id: str) -> Dict[str, Any]:
        """Get current status of an intent"""
        
        # Check active intents
        if intent_id in self.active_intents:
            intent = self.active_intents[intent_id]
            return {
                "intent_id": intent_id,
                "status": intent.status.value,
                "intent_type": intent.intent_type.value,
                "target_outcome": intent.target_outcome,
                "authority_level": intent.authority_level.value,
                "created_at": intent.created_at.isoformat(),
                "expiration_deadline": intent.expiration_deadline.isoformat(),
                "execution_log": intent.execution_log,
                "immutable_hash": intent.immutable_hash
            }
        
        # Check history
        for intent in self.intent_history:
            if intent.intent_id == intent_id:
                return {
                    "intent_id": intent_id,
                    "status": intent.status.value,
                    "intent_type": intent.intent_type.value,
                    "target_outcome": intent.target_outcome,
                    "authority_level": intent.authority_level.value,
                    "created_at": intent.created_at.isoformat(),
                    "expiration_deadline": intent.expiration_deadline.isoformat(),
                    "execution_log": intent.execution_log,
                    "immutable_hash": intent.immutable_hash
                }
        
        return {"error": f"Intent {intent_id} not found"}
    
    def get_execution_queue(self) -> List[Dict[str, Any]]:
        """Get current execution queue"""
        queue_intents = []
        
        for intent_id in self.execution_queue:
            if intent_id in self.active_intents:
                intent = self.active_intents[intent_id]
                queue_intents.append({
                    "intent_id": intent_id,
                    "intent_type": intent.intent_type.value,
                    "target_outcome": intent.target_outcome,
                    "priority": self._calculate_priority(intent_id),
                    "authority_level": intent.authority_level.value,
                    "created_at": intent.created_at.isoformat(),
                    "expires_in_hours": (intent.expiration_deadline - datetime.now()).total_seconds() / 3600
                })
        
        return sorted(queue_intents, key=lambda x: x["priority"], reverse=True)
    
    def get_forensic_ledger(self, limit: int = 100) -> Dict[str, Any]:
        """Get forensic execution ledger for audit"""
        all_intents = self.intent_history + list(self.active_intents.values())
        
        # Sort by creation time
        all_intents.sort(key=lambda x: x.created_at, reverse=True)
        
        ledger_entries = []
        for intent in all_intents[:limit]:
            entry = {
                "intent_id": intent.intent_id,
                "intent_type": intent.intent_type.value,
                "target_outcome": intent.target_outcome,
                "authority_level": intent.authority_level.value,
                "risk_tolerance": intent.risk_tolerance.value,
                "status": intent.status.value,
                "created_at": intent.created_at.isoformat(),
                "expiration_deadline": intent.expiration_deadline.isoformat(),
                "created_by": intent.created_by,
                "immutable_hash": intent.immutable_hash,
                "execution_log": intent.execution_log,
                "resource_permissions": [
                    {
                        "resource_type": rp.resource_type,
                        "quantity": rp.quantity,
                        "cost_estimate_usd": rp.cost_estimate_usd
                    }
                    for rp in intent.resource_permissions
                ]
            }
            ledger_entries.append(entry)
        
        return {
            "total_entries": len(ledger_entries),
            "ledger": ledger_entries,
            "generated_at": datetime.now().isoformat()
        }

# Global instance
intent_command_engine = IntentCommandEngine()
