"""
Autonomous Infrastructure Stabilization Engine
Self-healing infrastructure intelligence for proactive cascade prevention
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

from services.national_digital_twin import national_digital_twin, DisasterType, InfrastructureType

class StabilizationActionType(Enum):
    LOAD_REDISTRIBUTION = "load_redistribution"
    EMERGENCY_REROUTING = "emergency_rerouting"
    REDUNDANCY_ACTIVATION = "redundancy_activation"
    HOSPITAL_LOAD_BALANCING = "hospital_load_balancing"
    TELECOM_BACKUP_SWITCH = "telecom_backup_switch"
    POWER_GRID_ISOLATION = "power_grid_isolation"
    WATER_FLOW_REROUTING = "water_flow_rerouting"
    TRANSPORT_CORRIDOR_OPENING = "transport_corridor_opening"

class StabilizationPriority(Enum):
    CRITICAL = "critical"  # Execute immediately
    HIGH = "high"         # Execute within 5 minutes
    MEDIUM = "medium"     # Execute within 15 minutes
    LOW = "low"          # Execute within 30 minutes

@dataclass
class StabilizationAction:
    action_id: str
    action_type: StabilizationActionType
    target_node: str
    source_nodes: List[str]
    description: str
    expected_risk_reduction: float  # 0-1
    execution_time_minutes: int
    priority: StabilizationPriority
    resource_requirements: Dict[str, int]
    confidence_score: float
    side_effects: List[str]

@dataclass
class StabilizationPlan:
    plan_id: str
    cascade_probability: float
    affected_nodes: List[str]
    stabilization_actions: List[StabilizationAction]
    expected_risk_reduction_percent: float
    total_execution_time_minutes: int
    resource_requirements: Dict[str, int]
    confidence_score: float
    generated_at: datetime
    execution_sequence: List[str]

class InfrastructureStabilizationEngine:
    def __init__(self):
        self.active_plans: Dict[str, StabilizationPlan] = {}
        self.execution_history: List[Dict] = []
        self.stabilization_threshold = 0.3  # Trigger stabilization at 30% cascade probability
        
        # Stabilization effectiveness factors
        self.action_effectiveness = {
            StabilizationActionType.LOAD_REDISTRIBUTION: 0.25,
            StabilizationActionType.EMERGENCY_REROUTING: 0.20,
            StabilizationActionType.REDUNDANCY_ACTIVATION: 0.35,
            StabilizationActionType.HOSPITAL_LOAD_BALANCING: 0.30,
            StabilizationActionType.TELECOM_BACKUP_SWITCH: 0.40,
            StabilizationActionType.POWER_GRID_ISOLATION: 0.45,
            StabilizationActionType.WATER_FLOW_REROUTING: 0.25,
            StabilizationActionType.TRANSPORT_CORRIDOR_OPENING: 0.20
        }
    
    async def generate_stabilization_plan(self, 
                                       disaster_type: DisasterType,
                                       epicenter_lat: float,
                                       epicenter_lon: float,
                                       severity: float) -> StabilizationPlan:
        """
        Generate autonomous stabilization plan when cascade risk rises
        """
        try:
            # Run cascade simulation to assess risk
            simulation = await national_digital_twin.simulate_cascade(
                disaster_type, epicenter_lat, epicenter_lon, severity
            )
            
            if simulation.cascading_failure_probability < self.stabilization_threshold:
                raise ValueError("Cascade probability below stabilization threshold")
            
            plan_id = f"stab_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(epicenter_lat)) % 10000:04d}"
            
            # Generate stabilization actions
            actions = await self._generate_stabilization_actions(simulation)
            
            # Calculate execution sequence
            execution_sequence = self._calculate_execution_sequence(actions)
            
            # Calculate total resource requirements
            total_resources = self._calculate_total_resources(actions)
            
            # Create stabilization plan
            plan = StabilizationPlan(
                plan_id=plan_id,
                cascade_probability=simulation.cascading_failure_probability,
                affected_nodes=simulation.affected_nodes,
                stabilization_actions=actions,
                expected_risk_reduction_percent=sum(action.expected_risk_reduction for action in actions) / len(actions) * 100 if actions else 0,
                total_execution_time_minutes=max([action.execution_time_minutes for action in actions]) if actions else 0,
                resource_requirements=total_resources,
                confidence_score=min(0.9, simulation.cascading_failure_probability + 0.2),
                generated_at=datetime.now(),
                execution_sequence=execution_sequence
            )
            
            self.active_plans[plan_id] = plan
            
            return plan
            
        except Exception as e:
            raise Exception(f"Stabilization plan generation failed: {str(e)}")
    
    async def _generate_stabilization_actions(self, simulation) -> List[StabilizationAction]:
        """Generate specific stabilization actions based on cascade simulation"""
        actions = []
        
        for node_id in simulation.affected_nodes:
            node = national_digital_twin.nodes[node_id]
            
            # Generate actions based on node type and risk level
            if node.type == InfrastructureType.POWER_SUBSTATION:
                actions.extend(await self._generate_power_stabilization(node_id, node))
            elif node.type == InfrastructureType.HOSPITAL:
                actions.extend(await self._generate_hospital_stabilization(node_id, node))
            elif node.type == InfrastructureType.TELECOM_TOWER:
                actions.extend(await self._generate_telecom_stabilization(node_id, node))
            elif node.type == InfrastructureType.WATER_PLANT:
                actions.extend(await self._generate_water_stabilization(node_id, node))
            elif node.type == InfrastructureType.TRANSPORT_HUB:
                actions.extend(await self._generate_transport_stabilization(node_id, node))
        
        return actions
    
    async def _generate_power_stabilization(self, node_id: str, node) -> List[StabilizationAction]:
        """Generate power grid stabilization actions"""
        actions = []
        
        # Load redistribution
        if node.current_load > node.capacity * 0.8:
            # Find alternative power sources
            alternative_sources = [
                nid for nid in national_digital_twin.nodes.keys()
                if (national_digital_twin.nodes[nid].type == InfrastructureType.POWER_SUBSTATION and
                    nid != node_id and
                    national_digital_twin.nodes[nid].health_score > 0.7)
            ]
            
            if alternative_sources:
                action = StabilizationAction(
                    action_id=f"load_redist_{node_id}",
                    action_type=StabilizationActionType.LOAD_REDISTRIBUTION,
                    target_node=node_id,
                    source_nodes=alternative_sources[:2],
                    description=f"Redistribute {node.current_load:.0f}MW load from {node.name} to backup substations",
                    expected_risk_reduction=self.action_effectiveness[StabilizationActionType.LOAD_REDISTRIBUTION],
                    execution_time_minutes=5,
                    priority=StabilizationPriority.CRITICAL,
                    resource_requirements={"engineers": 2, "equipment": 1},
                    confidence_score=0.85,
                    side_effects=["Temporary voltage fluctuation", "Coordinated grid switching required"]
                )
                actions.append(action)
        
        # Grid isolation if critical
        if node.health_score < 0.3:
            action = StabilizationAction(
                action_id=f"grid_isolate_{node_id}",
                action_type=StabilizationActionType.POWER_GRID_ISOLATION,
                target_node=node_id,
                source_nodes=[],
                description=f"Isolate failing {node.name} to prevent cascade propagation",
                expected_risk_reduction=self.action_effectiveness[StabilizationActionType.POWER_GRID_ISOLATION],
                execution_time_minutes=2,
                priority=StabilizationPriority.CRITICAL,
                resource_requirements={"operators": 1, "automation": 1},
                confidence_score=0.95,
                side_effects=["Local power outage", "Downstream load shedding"]
            )
            actions.append(action)
        
        return actions
    
    async def _generate_hospital_stabilization(self, node_id: str, node) -> List[StabilizationAction]:
        """Generate hospital load balancing actions"""
        actions = []
        
        # Check hospital capacity
        if node.current_load > node.capacity * 0.9:
            # Find nearby hospitals with capacity
            nearby_hospitals = [
                nid for nid in national_digital_twin.nodes.keys()
                if (national_digital_twin.nodes[nid].type == InfrastructureType.HOSPITAL and
                    nid != node_id and
                    national_digital_twin.nodes[nid].current_load < national_digital_twin.nodes[nid].capacity * 0.7)
            ]
            
            if nearby_hospitals:
                action = StabilizationAction(
                    action_id=f"hospital_balance_{node_id}",
                    action_type=StabilizationActionType.HOSPITAL_LOAD_BALANCING,
                    target_node=node_id,
                    source_nodes=nearby_hospitals[:2],
                    description=f"Transfer patients from overloaded {node.name} to nearby facilities",
                    expected_risk_reduction=self.action_effectiveness[StabilizationActionType.HOSPITAL_LOAD_BALANCING],
                    execution_time_minutes=15,
                    priority=StabilizationPriority.HIGH,
                    resource_requirements={"ambulances": 5, "medical_staff": 10},
                    confidence_score=0.80,
                    side_effects=["Patient transport logistics", "Temporary bed shortages"]
                )
                actions.append(action)
        
        return actions
    
    async def _generate_telecom_stabilization(self, node_id: str, node) -> List[StabilizationAction]:
        """Generate telecom stabilization actions"""
        actions = []
        
        # Backup telecom activation
        if node.health_score < 0.5:
            action = StabilizationAction(
                action_id=f"telecom_backup_{node_id}",
                action_type=StabilizationActionType.TELECOM_BACKUP_SWITCH,
                target_node=node_id,
                source_nodes=[],
                description=f"Activate backup communication systems for {node.name}",
                expected_risk_reduction=self.action_effectiveness[StabilizationActionType.TELECOM_BACKUP_SWITCH],
                execution_time_minutes=3,
                priority=StabilizationPriority.HIGH,
                resource_requirements={"technicians": 2, "backup_systems": 1},
                confidence_score=0.90,
                side_effects=["Temporary service interruption", "Bandwidth reduction"]
            )
            actions.append(action)
        
        return actions
    
    async def _generate_water_stabilization(self, node_id: str, node) -> List[StabilizationAction]:
        """Generate water system stabilization actions"""
        actions = []
        
        # Water flow rerouting
        if node.health_score < 0.6:
            action = StabilizationAction(
                action_id=f"water_reroute_{node_id}",
                action_type=StabilizationActionType.WATER_FLOW_REROUTING,
                target_node=node_id,
                source_nodes=[],
                description=f"Reroute water flow around compromised {node.name}",
                expected_risk_reduction=self.action_effectiveness[StabilizationActionType.WATER_FLOW_REROUTING],
                execution_time_minutes=10,
                priority=StabilizationPriority.MEDIUM,
                resource_requirements={"operators": 3, "valves": 5},
                confidence_score=0.75,
                side_effects=["Pressure fluctuations", "Temporary supply reduction"]
            )
            actions.append(action)
        
        return actions
    
    async def _generate_transport_stabilization(self, node_id: str, node) -> List[StabilizationAction]:
        """Generate transport stabilization actions"""
        actions = []
        
        # Emergency corridor opening
        if node.health_score < 0.5:
            action = StabilizationAction(
                action_id=f"transport_corridor_{node_id}",
                action_type=StabilizationActionType.TRANSPORT_CORRIDOR_OPENING,
                target_node=node_id,
                source_nodes=[],
                description=f"Open emergency transport corridor bypassing {node.name}",
                expected_risk_reduction=self.action_effectiveness[StabilizationActionType.TRANSPORT_CORRIDOR_OPENING],
                execution_time_minutes=20,
                priority=StabilizationPriority.MEDIUM,
                resource_requirements={"traffic_control": 4, "signage": 10},
                confidence_score=0.70,
                side_effects=["Traffic congestion", "Route confusion"]
            )
            actions.append(action)
        
        return actions
    
    def _calculate_execution_sequence(self, actions: List[StabilizationAction]) -> List[str]:
        """Calculate optimal execution sequence based on priorities and dependencies"""
        # Sort by priority and execution time
        priority_order = {
            StabilizationPriority.CRITICAL: 0,
            StabilizationPriority.HIGH: 1,
            StabilizationPriority.MEDIUM: 2,
            StabilizationPriority.LOW: 3
        }
        
        sorted_actions = sorted(
            actions,
            key=lambda a: (priority_order[a.priority], a.execution_time_minutes)
        )
        
        return [action.action_id for action in sorted_actions]
    
    def _calculate_total_resources(self, actions: List[StabilizationAction]) -> Dict[str, int]:
        """Calculate total resource requirements for all actions"""
        total_resources = {}
        
        for action in actions:
            for resource, quantity in action.resource_requirements.items():
                total_resources[resource] = total_resources.get(resource, 0) + quantity
        
        return total_resources
    
    def get_active_stabilization_plans(self) -> List[Dict]:
        """Get all active stabilization plans"""
        return [
            {
                "plan_id": plan.plan_id,
                "cascade_probability": plan.cascade_probability,
                "affected_nodes_count": len(plan.affected_nodes),
                "actions_count": len(plan.stabilization_actions),
                "expected_risk_reduction": plan.expected_risk_reduction_percent,
                "total_execution_time": plan.total_execution_time_minutes,
                "confidence_score": plan.confidence_score,
                "generated_at": plan.generated_at.isoformat(),
                "status": "active"
            }
            for plan in self.active_plans.values()
            if (datetime.now() - plan.generated_at).total_seconds() < 3600  # Active for 1 hour
        ]
    
    async def execute_stabilization_action(self, action_id: str) -> Dict:
        """Execute a specific stabilization action (simulation)"""
        # Find the action
        action = None
        for plan in self.active_plans.values():
            for stab_action in plan.stabilization_actions:
                if stab_action.action_id == action_id:
                    action = stab_action
                    break
            if action:
                break
        
        if not action:
            raise ValueError(f"Action {action_id} not found")
        
        # Simulate execution
        execution_result = {
            "action_id": action_id,
            "status": "executed",
            "execution_time_seconds": action.execution_time_minutes * 60,
            "actual_risk_reduction": action.expected_risk_reduction * np.random.uniform(0.8, 1.2),
            "side_effects_observed": action.side_effects[:np.random.randint(0, len(action.side_effects) + 1)],
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in execution history
        self.execution_history.append(execution_result)
        
        return execution_result

# Global instance
infrastructure_stabilization_engine = InfrastructureStabilizationEngine()
