"""
Self-Healing Infrastructure Simulation
Real-time infrastructure modeling with reinforcement learning stabilization strategies
"""

import asyncio
import numpy as np
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import random
from collections import defaultdict, deque

class InfrastructureType(Enum):
    POWER_GRID = "power_grid"
    TELECOMM_TOWER = "telecom_tower"
    WATER_SYSTEM = "water_system"
    TRANSPORT_BRIDGE = "transport_bridge"
    HOSPITAL = "hospital"
    SCHOOL = "school"
    COMMUNICATION_CENTER = "communication_center"

class InfrastructureStatus(Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNDER_REPAIR = "under_repair"
    MAINTENANCE = "maintenance"

class FailureMode(Enum):
    OVERLOAD = "overload"
    WEATHER_DAMAGE = "weather_damage"
    STRUCTURAL_DAMAGE = "structural_damage"
    EQUIPMENT_FAILURE = "equipment_failure"
    POWER_OUTAGE = "power_outage"
    CONNECTIVITY_LOSS = "connectivity_loss"

@dataclass
class InfrastructureNode:
    node_id: str
    name: str
    type: InfrastructureType
    location: Dict  # lat, lon
    status: InfrastructureStatus
    health_score: float  # 0-1
    load_percentage: float  # 0-1
    redundancy_level: int  # 1-5
    dependencies: List[str]  # Node IDs it depends on
    dependents: List[str]  # Nodes that depend on it
    repair_time_hours: float
    last_maintenance: datetime
    failure_probability: float = 0.0
    current_failure_mode: Optional[FailureMode] = None
    stabilization_actions: List[str] = field(default_factory=list)

@dataclass
class StabilizationAction:
    action_id: str
    action_type: str
    target_node: str
    description: str
    effectiveness: float  # 0-1
    cost_estimate: float
    execution_time_minutes: int
    resource_requirements: Dict[str, int]

class ReinforcementLearningAgent:
    """Q-learning agent for infrastructure stabilization"""
    
    def __init__(self, learning_rate=0.1, discount_factor=0.95, exploration_rate=0.1):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.training_history = []
        
    def get_state_key(self, node_status: str, load_level: str, dependencies_status: str) -> str:
        """Convert state to Q-table key"""
        return f"{node_status}_{load_level}_{dependencies_status}"
    
    def get_action_key(self, action: str) -> str:
        """Convert action to Q-table key"""
        return action
    
    def choose_action(self, state_key: str, available_actions: List[str]) -> str:
        """Choose action using epsilon-greedy policy"""
        if random.random() < self.exploration_rate:
            return random.choice(available_actions)
        
        q_values = {action: self.q_table[state_key][action] for action in available_actions}
        return max(q_values, key=q_values.get)
    
    def update_q_value(self, state_key: str, action_key: str, reward: float, next_state_key: str):
        """Update Q-value using Q-learning formula"""
        current_q = self.q_table[state_key][action_key]
        max_next_q = max(self.q_table[next_state_key].values()) if self.q_table[next_state_key] else 0
        
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state_key][action_key] = new_q
        
        self.training_history.append({
            "timestamp": datetime.now().isoformat(),
            "state": state_key,
            "action": action_key,
            "reward": reward,
            "new_q": new_q
        })

class SelfHealingSimulation:
    def __init__(self):
        self.nodes: Dict[str, InfrastructureNode] = {}
        self.stabilization_actions: Dict[str, StabilizationAction] = {}
        self.rl_agent = ReinforcementLearningAgent()
        self.simulation_time = datetime.now()
        self.cascade_events: List[Dict] = []
        self.stabilization_history: List[Dict] = []
        
        # Initialize infrastructure network
        self._initialize_infrastructure_network()
        
        # Initialize stabilization actions
        self._initialize_stabilization_actions()
    
    def _initialize_infrastructure_network(self):
        """Initialize realistic infrastructure network"""
        
        # Power grid nodes
        power_nodes = [
            ("power_main", "Main Power Station", InfrastructureType.POWER_GRID, (19.0760, 72.8777)),
            ("power_substation_1", "Power Substation 1", InfrastructureType.POWER_GRID, (19.0860, 72.8877)),
            ("power_substation_2", "Power Substation 2", InfrastructureType.POWER_GRID, (19.0660, 72.8677)),
            ("power_substation_3", "Power Substation 3", InfrastructureType.POWER_GRID, (19.0560, 72.8477))
        ]
        
        # Telecom towers
        telecom_nodes = [
            ("telecom_main", "Main Tower", InfrastructureType.TELECOMM_TOWER, (19.0760, 72.8777)),
            ("telecom_tower_1", "Tower 1", InfrastructureType.TELECOMM_TOWER, (19.0860, 72.8877)),
            ("telecom_tower_2", "Tower 2", InfrastructureType.TELECOMM_TOWER, (19.0660, 72.8677)),
            ("telecom_tower_3", "Tower 3", InfrastructureType.TELECOMM_TOWER, (19.0560, 72.8477))
        ]
        
        # Water system nodes
        water_nodes = [
            ("water_main", "Water Treatment Plant", InfrastructureType.WATER_SYSTEM, (19.0760, 72.8777)),
            ("water_pumping_1", "Pumping Station 1", InfrastructureType.WATER_SYSTEM, (19.0860, 72.8877)),
            ("water_pumping_2", "Pumping Station 2", InfrastructureType.WATER_SYSTEM, (19.0660, 72.8677))
        ]
        
        # Transport bridges
        bridge_nodes = [
            ("bridge_main", "Main Bridge", InfrastructureType.TRANSPORT_BRIDGE, (19.0760, 72.8777)),
            ("bridge_1", "Bridge 1", InfrastructureType.TRANSPORT_BRIDGE, (19.0860, 72.8877)),
            ("bridge_2", "Bridge 2", InfrastructureType.TRANSPORT_BRIDGE, (19.0660, 72.8677))
        ]
        
        # Hospitals
        hospital_nodes = [
            ("hospital_main", "Main Hospital", InfrastructureType.HOSPITAL, (19.0760, 72.8777)),
            ("hospital_1", "Hospital 1", InfrastructureType.HOSPITAL, (19.0860, 72.8877)),
            ("hospital_2", "Hospital 2", InfrastructureType.HOSPITAL, (19.0660, 72.8677))
        ]
        
        # Create nodes
        all_nodes = power_nodes + telecom_nodes + water_nodes + bridge_nodes + hospital_nodes
        
        for node_id, name, node_type, location in all_nodes:
            node = InfrastructureNode(
                node_id=node_id,
                name=name,
                type=node_type,
                location={"lat": location[0], "lon": location[1]},
                status=InfrastructureStatus.OPERATIONAL,
                health_score=np.random.uniform(0.7, 1.0),
                load_percentage=np.random.uniform(0.3, 0.8),
                redundancy_level=np.random.randint(1, 4),
                dependencies=[],
                dependents=[],
                repair_time_hours=np.random.uniform(4, 24),
                last_maintenance=datetime.now() - timedelta(days=np.random.randint(1, 30)),
                failure_probability=np.random.uniform(0.01, 0.1)
            )
            
            self.nodes[node_id] = node
        
        # Set up dependencies
        self._setup_dependencies()
    
    def _setup_dependencies(self):
        """Setup realistic infrastructure dependencies"""
        
        # Power dependencies
        self.nodes["power_substation_1"].dependencies = ["power_main"]
        self.nodes["power_substation_2"].dependencies = ["power_main"]
        self.nodes["power_substation_3"].dependencies = ["power_main"]
        
        self.nodes["power_main"].dependents = ["power_substation_1", "power_substation_2", "power_substation_3"]
        
        # Telecom dependencies
        self.nodes["telecom_tower_1"].dependencies = ["power_substation_1"]
        self.nodes["telecom_tower_2"].dependencies = ["power_substation_2"]
        self.nodes["telecom_tower_3"].dependencies = ["power_substation_3"]
        
        self.nodes["power_substation_1"].dependents.append("telecom_tower_1")
        self.nodes["power_substation_2"].dependents.append("telecom_tower_2")
        self.nodes["power_substation_3"].dependents.append("telecom_tower_3")
        
        # Water dependencies
        self.nodes["water_pumping_1"].dependencies = ["power_main"]
        self.nodes["water_pumping_2"].dependencies = ["power_substation_2"]
        
        self.nodes["power_main"].dependents.extend(["water_pumping_1", "water_pumping_2"])
        self.nodes["power_substation_2"].dependents.append("water_pumping_2")
        
        # Bridge dependencies
        self.nodes["bridge_1"].dependencies = ["power_substation_1"]
        self.nodes["bridge_2"].dependencies = ["power_substation_2"]
        
        # Hospital dependencies
        self.nodes["hospital_1"].dependencies = ["power_substation_1", "telecom_tower_1"]
        self.nodes["hospital_2"].dependencies = ["power_substation_2", "telecom_tower_2"]
        
        self.nodes["power_substation_1"].dependents.extend(["bridge_1", "hospital_1"])
        self.nodes["power_substation_2"].dependents.extend(["bridge_2", "hospital_2"])
        self.nodes["telecom_tower_1"].dependents.append("hospital_1")
        self.nodes["telecom_tower_2"].dependents.append("hospital_2")
        
        # Main node dependencies
        self.nodes["telecom_main"].dependencies = ["power_main"]
        self.nodes["water_main"].dependencies = ["power_main"]
        self.nodes["bridge_main"].dependencies = ["power_main"]
        self.nodes["hospital_main"].dependencies = ["power_main", "telecom_main"]
        
        self.nodes["power_main"].dependents.extend(["telecom_main", "water_main", "bridge_main", "hospital_main"])
    
    def _initialize_stabilization_actions(self):
        """Initialize available stabilization actions"""
        
        actions = [
            StabilizationAction(
                action_id="load_redistribution",
                action_type="load_redistribution",
                target_node="",
                description="Redistribute load to prevent overload",
                effectiveness=0.7,
                cost_estimate=5000,
                execution_time_minutes=15,
                resource_requirements={"engineers": 2, "equipment": 1}
            ),
            StabilizationAction(
                action_id="backup_activation",
                action_type="backup_activation",
                target_node="",
                description="Activate backup systems",
                effectiveness=0.8,
                cost_estimate=10000,
                execution_time_minutes=30,
                resource_requirements={"technicians": 3, "backup_systems": 1}
            ),
            StabilizationAction(
                action_id="emergency_repair",
                action_type="emergency_repair",
                target_node="",
                description="Emergency repair procedures",
                effectiveness=0.6,
                cost_estimate=15000,
                execution_time_minutes=60,
                resource_requirements={"repair_crew": 4, "materials": 1}
            ),
            StabilizationAction(
                action_id="isolation",
                action_type="isolation",
                target_node="",
                description="Isolate failing node to prevent cascade",
                effectiveness=0.9,
                cost_estimate=2000,
                execution_time_minutes=5,
                resource_requirements={"operators": 1}
            ),
            StabilizationAction(
                action_id="load_shedding",
                action_type="load_shedding",
                target_node="",
                description="Shed non-critical load",
                effectiveness=0.5,
                cost_estimate=1000,
                execution_time_minutes=10,
                resource_requirements={"operators": 1}
            )
        ]
        
        for action in actions:
            self.stabilization_actions[action.action_id] = action
    
    async def simulate_cascade_failure(self, initial_failure_node: str, failure_mode: FailureMode, severity: float) -> Dict[str, Any]:
        """Simulate cascading infrastructure failure"""
        
        cascade_log = []
        failed_nodes = [initial_failure_node]
        
        # Mark initial failure
        self.nodes[initial_failure_node].status = InfrastructureStatus.FAILED
        self.nodes[initial_failure_node].current_failure_mode = failure_mode
        self.nodes[initial_failure_node].health_score = 0.1
        
        cascade_log.append({
            "timestamp": datetime.now().isoformat(),
            "event": "initial_failure",
            "node_id": initial_failure_node,
            "failure_mode": failure_mode.value,
            "severity": severity
        })
        
        # Simulate cascade propagation
        max_iterations = 10
        for iteration in range(max_iterations):
            new_failures = []
            
            for node_id in failed_nodes:
                node = self.nodes[node_id]
                
                # Check dependents
                for dependent_id in node.dependents:
                    dependent = self.nodes[dependent_id]
                    
                    # Calculate failure probability based on dependency strength and severity
                    dependency_strength = len(dependent.dependencies) / 10.0
                    failure_prob = severity * dependency_strength * (1 - dependent.health_score)
                    
                    if np.random.random() < failure_prob:
                        dependent.status = InfrastructureStatus.FAILED
                        dependent.health_score = 0.1
                        dependent.current_failure_mode = failure_mode
                        
                        new_failures.append(dependent_id)
                        
                        cascade_log.append({
                            "timestamp": datetime.now().isoformat(),
                            "event": "cascade_failure",
                            "iteration": iteration + 1,
                            "failed_node": node_id,
                            "affected_node": dependent_id,
                            "failure_probability": failure_prob
                        })
            
            if not new_failures:
                break
            
            failed_nodes.extend(new_failures)
        
        self.cascade_events.append({
            "timestamp": datetime.now().isoformat(),
            "initial_failure": initial_failure_node,
            "failure_mode": failure_mode.value,
            "severity": severity,
            "total_failed_nodes": len(failed_nodes),
            "cascade_log": cascade_log
        })
        
        return {
            "initial_failure": initial_failure_node,
            "failure_mode": failure_mode.value,
            "severity": severity,
            "failed_nodes": failed_nodes,
            "cascade_log": cascade_log,
            "total_affected": len(failed_nodes)
        }
    
    async def run_reinforcement_learning_stabilization(self, failed_nodes: List[str]) -> Dict[str, Any]:
        """Run reinforcement learning to find optimal stabilization strategies"""
        
        stabilization_results = {}
        
        for node_id in failed_nodes:
            node = self.nodes[node_id]
            
            # Get current state
            state_key = self.rl_agent.get_state_key(
                node.status.value,
                f"load_{int(node.load_percentage * 100)}",
                f"deps_{len(node.dependencies)}"
            )
            
            # Get available actions
            available_actions = [
                action.action_id for action in self.stabilization_actions.values()
                if action.target_node == "" or action.target_node == node_id
            ]
            
            if not available_actions:
                continue
            
            # Choose action
            action_id = self.rl_agent.choose_action(state_key, available_actions)
            action = self.stabilization_actions[action_id]
            
            # Execute action
            action.target_node = node_id
            result = await self._execute_stabilization_action(action)
            
            # Get next state
            next_state_key = self.rl_agent.get_state_key(
                result["new_status"],
                f"load_{int(result['new_load'] * 100)}",
                f"deps_{len(result['new_dependencies'])}"
            )
            
            # Calculate reward
            reward = self._calculate_stabilization_reward(node, result)
            
            # Update Q-value
            self.rl_agent.update_q_value(state_key, action_id, reward, next_state_key)
            
            # Apply stabilization
            node.status = InfrastructureStatus(result["new_status"])
            node.load_percentage = result["new_load"]
            node.dependencies = result["new_dependencies"]
            node.stabilization_actions.append(action_id)
            
            stabilization_results[node_id] = {
                "action_id": action_id,
                "action_type": action.action_type,
                "reward": reward,
                "new_status": result["new_status"],
                "execution_time": result["execution_time"],
                "cost": result["cost"]
            }
        
        return stabilization_results
    
    async def _execute_stabilization_action(self, action: StabilizationAction) -> Dict[str, Any]:
        """Execute stabilization action and return result"""
        
        # Simulate action execution
        execution_time = action.execution_time_minutes
        
        # Simulate action effectiveness
        effectiveness = action.effectiveness * np.random.uniform(0.8, 1.0)
        
        # Apply action effects
        node = self.nodes[action.target_node]
        
        if action.action_type == "load_redistribution":
            new_load = max(0.1, node.load_percentage - 0.3)
            new_status = InfrastructureStatus.OPERATIONAL if new_load < 0.8 else InfrastructureStatus.DEGRADED
            
        elif action.action_type == "backup_activation":
            new_load = max(0.1, node.load_percentage * 0.5)
            new_status = InfrastructureStatus.OPERATIONAL
            node.redundancy_level = min(5, node.redundancy_level + 1)
            
        elif action.action_type == "emergency_repair":
            new_status = InfrastructureStatus.UNDER_REPAIR
            new_load = 0.0
            
        elif action.action_type == "isolation":
            new_status = InfrastructureStatus.FAILED
            new_load = 0.0
            # Remove dependencies temporarily
            original_dependencies = node.dependencies.copy()
            node.dependencies = []
            
        elif action.action_type == "load_shedding":
            new_load = max(0.1, node.load_percentage * 0.5)
            new_status = InfrastructureStatus.OPERATIONAL if new_load < 0.7 else InfrastructureStatus.DEGRADED
        
        else:
            new_status = node.status
            new_load = node.load_percentage
        
        return {
            "action_id": action.action_id,
            "action_type": action.action_type,
            "new_status": new_status,
            "new_load": new_load,
            "new_dependencies": node.dependencies,
            "execution_time": execution_time,
            "cost": action.cost_estimate,
            "effectiveness": effectiveness
        }
    
    def _calculate_stabilization_reward(self, node: InfrastructureNode, result: Dict[str, Any]) -> float:
        """Calculate reward for stabilization action"""
        
        # Base reward for improvement
        if result["new_status"] == InfrastructureStatus.OPERATIONAL:
            base_reward = 1.0
        elif result["new_status"] == InfrastructureStatus.DEGRADED:
            base_reward = 0.5
        elif result["new_status"] == InfrastructureStatus.UNDER_REPAIR:
            base_reward = 0.3
        else:  # FAILED
            base_reward = -0.5
        
        # Load improvement bonus
        load_improvement = max(0, (node.load_percentage - result["new_load"]))
        load_bonus = load_improvement * 0.5
        
        # Cost penalty
        cost_penalty = -result["cost"] / 10000  # Normalize by $10,000
        
        # Time penalty
        time_penalty = -result["execution_time"] / 60  # Normalize by 1 hour
        
        return base_reward + load_bonus + cost_penalty + time_penalty
    
    def get_infrastructure_health(self) -> Dict[str, Any]:
        """Get current infrastructure health metrics"""
        
        status_distribution = {}
        for status in InfrastructureStatus:
            status_distribution[status.value] = len([n for n in self.nodes.values() if n.status == status])
        
        health_scores = [node.health_score for node in self.nodes.values()]
        load_levels = [node.load_percentage for node in self.nodes.values()]
        
        return {
            "total_nodes": len(self.nodes),
            "status_distribution": status_distribution,
            "average_health_score": np.mean(health_scores),
            "average_load_percentage": np.mean(load_levels),
            "critical_nodes": len([n for n in self.nodes.values() if n.status == InfrastructureStatus.FAILED]),
            "at_risk_nodes": len([n for n in self.nodes.values() if n.health_score < 0.5]),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_stabilization_recommendations(self) -> List[Dict[str, Any]]:
        """Get RL-based stabilization recommendations"""
        
        recommendations = []
        
        for node_id, node in self.nodes.items():
            if node.status in [InfrastructureStatus.DEGRADED, InfrastructureStatus.FAILED]:
                # Get current state
                state_key = self.rl_agent.get_state_key(
                    node.status.value,
                    f"load_{int(node.load_percentage * 100)}",
                    f"deps_{len(node.dependencies)}"
                )
                
                # Get available actions
                available_actions = [
                    action.action_id for action in self.stabilization_actions.values()
                ]
                
                if available_actions:
                    # Get best action from Q-table
                    best_action = self.rl_agent.choose_action(state_key, available_actions)
                    action = self.stabilization_actions[best_action]
                    
                    recommendations.append({
                        "node_id": node_id,
                        "node_name": node.name,
                        "node_type": node.type.value,
                        "current_status": node.status.value,
                        "recommended_action": best_action,
                        "action_description": action.description,
                        "expected_effectiveness": action.effectiveness,
                        "estimated_cost": action.cost_estimate,
                        "q_value": self.rl_agent.q_table[state_key][best_action],
                        "confidence": min(1.0, len(self.rl_agent.training_history) / 100)
                    })
        
        # Sort by Q-value
        recommendations.sort(key=lambda x: x["q_value"], reverse=True)
        
        return recommendations
    
    def get_simulation_metrics(self) -> Dict[str, Any]:
        """Get simulation and training metrics"""
        
        return {
            "total_cascade_events": len(self.cascade_events),
            "total_stabilization_actions": len(self.stabilization_history),
            "q_table_size": len(self.rl_agent.q_table),
            "training_history_size": len(self.rl_agent.training_history),
            "average_reward": np.mean([h["reward"] for h in self.rl_agent.training_history]) if self.rl_agent.training_history else 0,
            "exploration_rate": self.rl_agent.exploration_rate,
            "timestamp": datetime.now().isoformat()
        }

# Global instance
self_healing_simulation = SelfHealingSimulation()
