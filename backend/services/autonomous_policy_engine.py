"""
Autonomous Response Policy Engine
Policy-driven autonomous decision engine that generates executable response policies
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib

class PolicyTriggerType(Enum):
    RISK_THRESHOLD = "risk_threshold"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    CASCADE_DETECTION = "cascade_detection"
    SENSOR_ANOMALY = "sensor_anomaly"
    TIME_BASED = "time_based"
    MANUAL_OVERRIDE = "manual_override"

class ExecutionScope(Enum):
    LOCAL = "local"
    DISTRICT = "district"
    REGIONAL = "regional"
    NATIONAL = "national"

class PolicyStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXECUTING = "executing"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

@dataclass
class PolicyCondition:
    """Policy trigger condition"""
    condition_type: PolicyTriggerType
    threshold_value: float
    metric_name: str
    operator: str  # >, <, >=, <=, ==
    time_window_minutes: Optional[int] = None
    location_filter: Optional[Dict[str, Any]] = None
    
    def evaluate(self, current_metrics: Dict[str, Any]) -> bool:
        """Evaluate if condition is met"""
        if self.metric_name not in current_metrics:
            return False
        
        current_value = current_metrics[self.metric_name]
        
        if self.operator == ">":
            return current_value > self.threshold_value
        elif self.operator == "<":
            return current_value < self.threshold_value
        elif self.operator == ">=":
            return current_value >= self.threshold_value
        elif self.operator == "<=":
            return current_value <= self.threshold_value
        elif self.operator == "==":
            return current_value == self.threshold_value
        
        return False

@dataclass
class ResourceRequirement:
    """Resource reservation requirement"""
    resource_type: str
    quantity: int
    priority: int  # 1-10, 1 is highest
    reservation_window_minutes: int
    alternative_resources: List[str] = field(default_factory=list)

@dataclass
class StabilizationMetric:
    """Expected stabilization metric"""
    metric_name: str
    target_value: float
    measurement_window_minutes: int
    success_threshold: float  # percentage of target that constitutes success

@dataclass
class VerificationRequirement:
    """Verification requirement for policy execution"""
    verification_type: str
    required_confidence: float
    evidence_sources: List[str]
    verification_deadline_minutes: int
    automated_verification: bool = True

@dataclass
class AutonomousResponsePolicy:
    """Autonomous response policy definition"""
    policy_id: str
    name: str
    description: str
    version: int
    status: PolicyStatus
    
    # Policy definition
    trigger_conditions: List[PolicyCondition]
    execution_scope: ExecutionScope
    resource_requirements: List[ResourceRequirement]
    expiration_deadline: datetime
    stabilization_metrics: List[StabilizationMetric]
    verification_requirements: List[VerificationRequirement]
    
    # Policy metadata
    created_at: datetime
    created_by: str
    last_modified: datetime
    authorized_by: str
    priority: int  # 1-10, 1 is highest
    
    # Execution tracking
    execution_count: int = 0
    success_count: int = 0
    last_execution: Optional[datetime] = None
    effectiveness_score: float = 0.0
    
    def __post_init__(self):
        if not self.policy_id:
            self.policy_id = f"policy_{uuid.uuid4().hex[:12]}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert policy to dictionary"""
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "status": self.status.value,
            "trigger_conditions": [
                {
                    "condition_type": cond.condition_type.value,
                    "threshold_value": cond.threshold_value,
                    "metric_name": cond.metric_name,
                    "operator": cond.operator,
                    "time_window_minutes": cond.time_window_minutes,
                    "location_filter": cond.location_filter
                }
                for cond in self.trigger_conditions
            ],
            "execution_scope": self.execution_scope.value,
            "resource_requirements": [
                {
                    "resource_type": req.resource_type,
                    "quantity": req.quantity,
                    "priority": req.priority,
                    "reservation_window_minutes": req.reservation_window_minutes,
                    "alternative_resources": req.alternative_resources
                }
                for req in self.resource_requirements
            ],
            "expiration_deadline": self.expiration_deadline.isoformat(),
            "stabilization_metrics": [
                {
                    "metric_name": metric.metric_name,
                    "target_value": metric.target_value,
                    "measurement_window_minutes": metric.measurement_window_minutes,
                    "success_threshold": metric.success_threshold
                }
                for metric in self.stabilization_metrics
            ],
            "verification_requirements": [
                {
                    "verification_type": req.verification_type,
                    "required_confidence": req.required_confidence,
                    "evidence_sources": req.evidence_sources,
                    "verification_deadline_minutes": req.verification_deadline_minutes,
                    "automated_verification": req.automated_verification
                }
                for req in self.verification_requirements
            ],
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "last_modified": self.last_modified.isoformat(),
            "authorized_by": self.authorized_by,
            "priority": self.priority,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "effectiveness_score": self.effectiveness_score
        }

class AutonomousResponsePolicyEngine:
    """Policy-driven autonomous decision engine"""
    
    def __init__(self):
        self.policies: Dict[str, AutonomousResponsePolicy] = {}
        self.active_policies: Set[str] = set()
        self.policy_templates: Dict[str, Dict] = {}
        self.current_metrics: Dict[str, Any] = {}
        self.execution_history: List[Dict] = []
        self.policy_effectiveness_cache: Dict[str, float] = {}
        
        # Initialize with default policies
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize default autonomous response policies"""
        
        # High-risk infrastructure stabilization policy
        high_risk_policy = AutonomousResponsePolicy(
            policy_id="policy_high_risk_stabilization",
            name="High-Risk Infrastructure Stabilization",
            description="Automatically stabilize infrastructure when cascade risk exceeds threshold",
            version=1,
            status=PolicyStatus.ACTIVE,
            trigger_conditions=[
                PolicyCondition(
                    condition_type=PolicyTriggerType.RISK_THRESHOLD,
                    threshold_value=0.75,
                    metric_name="cascade_probability",
                    operator=">=",
                    time_window_minutes=5
                )
            ],
            execution_scope=ExecutionScope.REGIONAL,
            resource_requirements=[
                ResourceRequirement(
                    resource_type="infrastructure_control",
                    quantity=5,
                    priority=1,
                    reservation_window_minutes=30
                ),
                ResourceRequirement(
                    resource_type="emergency_power",
                    quantity=3,
                    priority=2,
                    reservation_window_minutes=45
                )
            ],
            expiration_deadline=datetime.now() + timedelta(hours=24),
            stabilization_metrics=[
                StabilizationMetric(
                    metric_name="cascade_probability",
                    target_value=0.3,
                    measurement_window_minutes=60,
                    success_threshold=0.8
                )
            ],
            verification_requirements=[
                VerificationRequirement(
                    verification_type="infrastructure_status",
                    required_confidence=0.9,
                    evidence_sources=["sensor_fusion", "infrastructure_monitoring"],
                    verification_deadline_minutes=15,
                    automated_verification=True
                )
            ],
            created_at=datetime.now(),
            created_by="system",
            last_modified=datetime.now(),
            authorized_by="autonomous_system",
            priority=1
        )
        
        # Critical infrastructure failure policy
        critical_failure_policy = AutonomousResponsePolicy(
            policy_id="policy_critical_failure_response",
            name="Critical Infrastructure Failure Response",
            description="Immediate autonomous response to critical infrastructure failures",
            version=1,
            status=PolicyStatus.ACTIVE,
            trigger_conditions=[
                PolicyCondition(
                    condition_type=PolicyTriggerType.INFRASTRUCTURE_FAILURE,
                    threshold_value=0.5,
                    metric_name="critical_nodes_failed",
                    operator=">=",
                    time_window_minutes=2
                )
            ],
            execution_scope=ExecutionScope.LOCAL,
            resource_requirements=[
                ResourceRequirement(
                    resource_type="repair_teams",
                    quantity=2,
                    priority=1,
                    reservation_window_minutes=15
                ),
                ResourceRequirement(
                    resource_type="backup_systems",
                    quantity=1,
                    priority=1,
                    reservation_window_minutes=10
                )
            ],
            expiration_deadline=datetime.now() + timedelta(hours=12),
            stabilization_metrics=[
                StabilizationMetric(
                    metric_name="infrastructure_availability",
                    target_value=0.95,
                    measurement_window_minutes=30,
                    success_threshold=0.9
                )
            ],
            verification_requirements=[
                VerificationRequirement(
                    verification_type="infrastructure_integrity",
                    required_confidence=0.95,
                    evidence_sources=["infrastructure_monitoring", "sensor_data"],
                    verification_deadline_minutes=10,
                    automated_verification=True
                )
            ],
            created_at=datetime.now(),
            created_by="system",
            last_modified=datetime.now(),
            authorized_by="autonomous_system",
            priority=1
        )
        
        # Add policies to engine
        self.policies[high_risk_policy.policy_id] = high_risk_policy
        self.policies[critical_failure_policy.policy_id] = critical_failure_policy
        self.active_policies.add(high_risk_policy.policy_id)
        self.active_policies.add(critical_failure_policy.policy_id)
    
    async def update_metrics(self, metrics: Dict[str, Any]):
        """Update current system metrics"""
        self.current_metrics.update(metrics)
        
        # Check for policy triggers
        await self._evaluate_policy_triggers()
    
    async def _evaluate_policy_triggers(self):
        """Evaluate all active policies for trigger conditions"""
        triggered_policies = []
        
        for policy_id in self.active_policies:
            policy = self.policies[policy_id]
            
            # Check if policy is expired
            if datetime.now() > policy.expiration_deadline:
                policy.status = PolicyStatus.EXPIRED
                self.active_policies.discard(policy_id)
                continue
            
            # Evaluate trigger conditions
            conditions_met = 0
            for condition in policy.trigger_conditions:
                if condition.evaluate(self.current_metrics):
                    conditions_met += 1
            
            # If all conditions are met, trigger policy
            if conditions_met == len(policy.trigger_conditions):
                triggered_policies.append(policy)
        
        # Execute triggered policies
        for policy in triggered_policies:
            await self._execute_policy(policy)
    
    async def _execute_policy(self, policy: AutonomousResponsePolicy):
        """Execute autonomous response policy"""
        try:
            policy.status = PolicyStatus.EXECUTING
            policy.last_execution = datetime.now()
            policy.execution_count += 1
            
            # Generate machine-enforceable execution intent
            execution_intent = await self._generate_execution_intent(policy)
            
            # Record execution
            execution_record = {
                "policy_id": policy.policy_id,
                "execution_id": f"exec_{uuid.uuid4().hex[:12]}",
                "timestamp": datetime.now().isoformat(),
                "trigger_conditions_met": [
                    {
                        "condition_type": cond.condition_type.value,
                        "metric_name": cond.metric_name,
                        "threshold_value": cond.threshold_value,
                        "actual_value": self.current_metrics.get(cond.metric_name)
                    }
                    for cond in policy.trigger_conditions
                ],
                "execution_intent": execution_intent,
                "resource_allocations": [
                    {
                        "resource_type": req.resource_type,
                        "quantity": req.quantity,
                        "priority": req.priority
                    }
                    for req in policy.resource_requirements
                ],
                "stabilization_targets": [
                    {
                        "metric_name": metric.metric_name,
                        "target_value": metric.target_value,
                        "success_threshold": metric.success_threshold
                    }
                    for metric in policy.stabilization_metrics
                ]
            }
            
            self.execution_history.append(execution_record)
            
            # Update policy status
            policy.status = PolicyStatus.COMPLETED
            
            # Calculate effectiveness (placeholder - would be updated based on actual results)
            policy.effectiveness_score = 0.85  # Default effectiveness
            
            print(f"✅ Policy executed: {policy.name}")
            print(f"   Execution ID: {execution_record['execution_id']}")
            print(f"   Resources allocated: {len(policy.resource_requirements)}")
            print(f"   Stabilization targets: {len(policy.stabilization_metrics)}")
            
        except Exception as e:
            policy.status = PolicyStatus.CANCELLED
            print(f"❌ Policy execution failed: {policy.name} - {str(e)}")
    
    async def _generate_execution_intent(self, policy: AutonomousResponsePolicy) -> Dict[str, Any]:
        """Generate machine-enforceable execution intent"""
        intent_id = f"intent_{uuid.uuid4().hex[:12]}"
        
        execution_intent = {
            "intent_id": intent_id,
            "policy_id": policy.policy_id,
            "intent_type": "autonomous_stabilization",
            "target_outcome": policy.description,
            "risk_tolerance": "high_tolerance",
            "authority_level": "autonomous",
            "evidence_requirements": [
                {
                    "evidence_type": req.verification_type,
                    "required_confidence": req.required_confidence,
                    "verification_method": "automated" if req.automated_verification else "manual",
                    "collection_deadline": (datetime.now() + timedelta(minutes=req.verification_deadline_minutes)).isoformat(),
                    "evidence_sources": req.evidence_sources
                }
                for req in policy.verification_requirements
            ],
            "resource_permissions": [
                {
                    "resource_type": req.resource_type,
                    "quantity": req.quantity,
                    "authority_required": "autonomous",
                    "cost_estimate": 0,
                    "availability_status": "reserved"
                }
                for req in policy.resource_requirements
            ],
            "expiration_deadline": policy.expiration_deadline.isoformat(),
            "stabilization_metrics": [
                {
                    "metric_name": metric.metric_name,
                    "target_value": metric.target_value,
                    "measurement_window": metric.measurement_window_minutes,
                    "success_threshold": metric.success_threshold
                }
                for metric in policy.stabilization_metrics
            ],
            "execution_scope": policy.execution_scope.value,
            "priority": policy.priority,
            "created_at": datetime.now().isoformat(),
            "immutable_hash": ""
        }
        
        # Generate immutable hash
        intent_str = json.dumps(execution_intent, sort_keys=True, default=str)
        execution_intent["immutable_hash"] = hashlib.sha256(intent_str.encode()).hexdigest()
        
        return execution_intent
    
    def create_policy(self, policy_data: Dict[str, Any]) -> str:
        """Create new autonomous response policy"""
        try:
            policy = AutonomousResponsePolicy(
                policy_id=policy_data.get("policy_id", ""),
                name=policy_data["name"],
                description=policy_data["description"],
                version=policy_data.get("version", 1),
                status=PolicyStatus.DRAFT,
                trigger_conditions=[
                    PolicyCondition(
                        condition_type=PolicyTriggerType(cond["condition_type"]),
                        threshold_value=cond["threshold_value"],
                        metric_name=cond["metric_name"],
                        operator=cond["operator"],
                        time_window_minutes=cond.get("time_window_minutes"),
                        location_filter=cond.get("location_filter")
                    )
                    for cond in policy_data["trigger_conditions"]
                ],
                execution_scope=ExecutionScope(policy_data["execution_scope"]),
                resource_requirements=[
                    ResourceRequirement(
                        resource_type=req["resource_type"],
                        quantity=req["quantity"],
                        priority=req["priority"],
                        reservation_window_minutes=req["reservation_window_minutes"],
                        alternative_resources=req.get("alternative_resources", [])
                    )
                    for req in policy_data["resource_requirements"]
                ],
                expiration_deadline=datetime.fromisoformat(policy_data["expiration_deadline"]),
                stabilization_metrics=[
                    StabilizationMetric(
                        metric_name=metric["metric_name"],
                        target_value=metric["target_value"],
                        measurement_window_minutes=metric["measurement_window_minutes"],
                        success_threshold=metric["success_threshold"]
                    )
                    for metric in policy_data["stabilization_metrics"]
                ],
                verification_requirements=[
                    VerificationRequirement(
                        verification_type=req["verification_type"],
                        required_confidence=req["required_confidence"],
                        evidence_sources=req["evidence_sources"],
                        verification_deadline_minutes=req["verification_deadline_minutes"],
                        automated_verification=req.get("automated_verification", True)
                    )
                    for req in policy_data["verification_requirements"]
                ],
                created_at=datetime.now(),
                created_by=policy_data["created_by"],
                last_modified=datetime.now(),
                authorized_by=policy_data["authorized_by"],
                priority=policy_data["priority"]
            )
            
            self.policies[policy.policy_id] = policy
            return policy.policy_id
            
        except Exception as e:
            raise ValueError(f"Policy creation failed: {str(e)}")
    
    def activate_policy(self, policy_id: str) -> bool:
        """Activate a policy"""
        if policy_id in self.policies:
            policy = self.policies[policy_id]
            policy.status = PolicyStatus.ACTIVE
            self.active_policies.add(policy_id)
            return True
        return False
    
    def deactivate_policy(self, policy_id: str) -> bool:
        """Deactivate a policy"""
        if policy_id in self.policies:
            policy = self.policies[policy_id]
            policy.status = PolicyStatus.CANCELLED
            self.active_policies.discard(policy_id)
            return True
        return False
    
    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get policy by ID"""
        if policy_id in self.policies:
            return self.policies[policy_id].to_dict()
        return None
    
    def get_all_policies(self) -> List[Dict[str, Any]]:
        """Get all policies"""
        return [policy.to_dict() for policy in self.policies.values()]
    
    def get_active_policies(self) -> List[Dict[str, Any]]:
        """Get active policies"""
        return [self.policies[policy_id].to_dict() for policy_id in self.active_policies]
    
    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get policy execution history"""
        return self.execution_history[-limit:] if self.execution_history else []
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get policy engine system metrics"""
        total_policies = len(self.policies)
        active_policies = len(self.active_policies)
        total_executions = sum(p.execution_count for p in self.policies.values())
        success_rate = sum(p.success_count for p in self.policies.values()) / max(total_executions, 1)
        
        return {
            "total_policies": total_policies,
            "active_policies": active_policies,
            "total_executions": total_executions,
            "success_rate": success_rate,
            "current_metrics_count": len(self.current_metrics),
            "execution_history_size": len(self.execution_history),
            "timestamp": datetime.now().isoformat()
        }

# Global policy engine instance
autonomous_policy_engine = AutonomousResponsePolicyEngine()
