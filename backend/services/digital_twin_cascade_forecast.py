"""
Digital Twin Cascade Forecast Engine
Real dependency graph-based cascade prediction and pre-stabilization
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
from collections import defaultdict, deque

class NodeType(Enum):
    POWER_GRID = "power_grid"
    TELECOM_TOWER = "telecom_tower"
    WATER_SYSTEM = "water_system"
    TRANSPORT_BRIDGE = "transport_bridge"
    HOSPITAL = "hospital"
    SCHOOL = "school"
    COMMUNICATION_CENTER = "communication_center"

class FailureMode(Enum):
    OVERLOAD = "overload"
    WEATHER_DAMAGE = "weather_damage"
    STRUCTURAL_DAMAGE = "structural_damage"
    EQUIPMENT_FAILURE = "equipment_failure"
    POWER_OUTAGE = "power_outage"
    CONNECTIVITY_LOSS = "connectivity_loss"

class CascadeSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DependencyEdge:
    """Infrastructure dependency relationship"""
    source_node: str
    target_node: str
    dependency_type: str
    failure_propagation_weight: float  # 0-1, how likely failure propagates
    recovery_dependency: float  # 0-1, how much target depends on source for recovery
    distance_km: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_node": self.source_node,
            "target_node": self.target_node,
            "dependency_type": self.dependency_type,
            "failure_propagation_weight": self.failure_propagation_weight,
            "recovery_dependency": self.recovery_dependency,
            "distance_km": self.distance_km
        }

@dataclass
class InfrastructureNode:
    """Infrastructure node in dependency graph"""
    node_id: str
    name: str
    node_type: NodeType
    location: Dict[str, float]  # lat, lon
    capacity: float
    current_load: float
    health_score: float  # 0-1
    redundancy_level: int  # 0-5, number of backup systems
    repair_time_hours: float
    criticality_score: float  # 0-1, importance to overall system
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "node_type": self.node_type.value,
            "location": self.location,
            "capacity": self.capacity,
            "current_load": self.current_load,
            "health_score": self.health_score,
            "redundancy_level": self.redundancy_level,
            "repair_time_hours": self.repair_time_hours,
            "criticality_score": self.criticality_score,
            "dependencies": self.dependencies,
            "dependents": self.dependents
        }

@dataclass
class CascadePrediction:
    """Cascade failure prediction"""
    prediction_id: str
    timestamp: datetime
    initial_failure_node: str
    failure_mode: FailureMode
    cascade_probability: float
    predicted_radius_km: float
    affected_nodes: List[str]
    cascade_timeline: List[Dict[str, Any]]
    total_impact_score: float
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "timestamp": self.timestamp.isoformat(),
            "initial_failure_node": self.initial_failure_node,
            "failure_mode": self.failure_mode.value,
            "cascade_probability": self.cascade_probability,
            "predicted_radius_km": self.predicted_radius_km,
            "affected_nodes": self.affected_nodes,
            "cascade_timeline": self.cascade_timeline,
            "total_impact_score": self.total_impact_score,
            "confidence": self.confidence
        }

@dataclass
class PreStabilizationStrategy:
    """Pre-emptive stabilization strategy"""
    strategy_id: str
    target_nodes: List[str]
    stabilization_actions: List[Dict[str, Any]]
    expected_cascade_reduction: float
    implementation_cost: float
    implementation_time_minutes: int
    priority_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "target_nodes": self.target_nodes,
            "stabilization_actions": self.stabilization_actions,
            "expected_cascade_reduction": self.expected_cascade_reduction,
            "implementation_cost": self.implementation_cost,
            "implementation_time_minutes": self.implementation_time_minutes,
            "priority_score": self.priority_score
        }

@dataclass
class CriticalNodeAnalysis:
    """Critical node analysis for pre-stabilization"""
    node_id: str
    centrality_score: float
    cascade_contribution_score: float
    vulnerability_score: float
    stabilization_priority: float
    recommended_actions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "centrality_score": self.centrality_score,
            "cascade_contribution_score": self.cascade_contribution_score,
            "vulnerability_score": self.vulnerability_score,
            "stabilization_priority": self.stabilization_priority,
            "recommended_actions": self.recommended_actions
        }

class DigitalTwinCascadeForecastEngine:
    """Real-time cascade prediction and pre-stabilization engine"""
    
    def __init__(self):
        self.nodes: Dict[str, InfrastructureNode] = {}
        self.edges: Dict[str, DependencyEdge] = {}
        self.dependency_graph: Dict[str, List[str]] = defaultdict(list)
        self.reverse_dependency_graph: Dict[str, List[str]] = defaultdict(list)
        self.cascade_predictions: List[CascadePrediction] = []
        self.critical_node_analyses: Dict[str, CriticalNodeAnalysis] = {}
        self.pre_stabilization_strategies: Dict[str, PreStabilizationStrategy] = {}
        
        # Initialize infrastructure network
        self._initialize_infrastructure_network()
        
        # Start continuous monitoring
        asyncio.create_task(self._continuous_monitoring())
    
    def _initialize_infrastructure_network(self):
        """Initialize realistic infrastructure dependency network"""
        
        # Create infrastructure nodes
        node_configs = [
            # Power infrastructure
            {"id": "power_main_mumbai", "name": "Mumbai Main Power Station", "type": NodeType.POWER_GRID, "lat": 19.0760, "lon": 72.8777, "capacity": 1000, "criticality": 0.95},
            {"id": "power_suburban_1", "name": "Suburban Power Substation 1", "type": NodeType.POWER_GRID, "lat": 19.1160, "lon": 72.9177, "capacity": 500, "criticality": 0.8},
            {"id": "power_suburban_2", "name": "Suburban Power Substation 2", "type": NodeType.POWER_GRID, "lat": 19.0360, "lon": 72.8377, "capacity": 500, "criticality": 0.8},
            {"id": "power_industrial", "name": "Industrial Power Plant", "type": NodeType.POWER_GRID, "lat": 19.1560, "lon": 72.9577, "capacity": 800, "criticality": 0.85},
            
            # Telecom infrastructure
            {"id": "telecom_main_mumbai", "name": "Mumbai Main Telecom Tower", "type": NodeType.TELECOM_TOWER, "lat": 19.0860, "lon": 72.8877, "capacity": 100, "criticality": 0.9},
            {"id": "telecom_south", "name": "South Mumbai Tower", "type": NodeType.TELECOM_TOWER, "lat": 19.0260, "lon": 72.8277, "capacity": 80, "criticality": 0.7},
            {"id": "telecom_north", "name": "North Mumbai Tower", "type": NodeType.TELECOM_TOWER, "lat": 19.1460, "lon": 72.9477, "capacity": 80, "criticality": 0.7},
            {"id": "telecom_west", "name": "West Mumbai Tower", "type": NodeType.TELECOM_TOWER, "lat": 19.0760, "lon": 72.8177, "capacity": 60, "criticality": 0.6},
            
            # Water infrastructure
            {"id": "water_main_mumbai", "name": "Mumbai Main Water Plant", "type": NodeType.WATER_SYSTEM, "lat": 19.0560, "lon": 72.8577, "capacity": 2000, "criticality": 0.9},
            {"id": "water_east", "name": "East Water Treatment", "type": NodeType.WATER_SYSTEM, "lat": 19.1260, "lon": 72.9277, "capacity": 800, "criticality": 0.75},
            {"id": "water_west", "name": "West Water Treatment", "type": NodeType.WATER_SYSTEM, "lat": 19.0060, "lon": 72.7877, "capacity": 800, "criticality": 0.75},
            
            # Transport infrastructure
            {"id": "bridge_sealink", "name": "Sea Link Bridge", "type": NodeType.TRANSPORT_BRIDGE, "lat": 19.0160, "lon": 72.8177, "capacity": 500, "criticality": 0.85},
            {"id": "bridge_eastern", "name": "Eastern Express Bridge", "type": NodeType.TRANSPORT_BRIDGE, "lat": 19.1060, "lon": 72.9077, "capacity": 300, "criticality": 0.7},
            
            # Healthcare infrastructure
            {"id": "hospital_main", "name": "Mumbai Main Hospital", "type": NodeType.HOSPITAL, "lat": 19.1360, "lon": 72.9377, "capacity": 1000, "criticality": 0.95},
            {"id": "hospital_south", "name": "South Mumbai Hospital", "type": NodeType.HOSPITAL, "lat": 19.0060, "lon": 72.8077, "capacity": 500, "criticality": 0.8},
            {"id": "hospital_north", "name": "North Mumbai Hospital", "type": NodeType.HOSPITAL, "lat": 19.1660, "lon": 72.9677, "capacity": 500, "criticality": 0.8},
            
            # Communication centers
            {"id": "comm_control", "name": "Communication Control Center", "type": NodeType.COMMUNICATION_CENTER, "lat": 19.0760, "lon": 72.8777, "capacity": 200, "criticality": 0.98},
            {"id": "comm_backup", "name": "Backup Communication Center", "type": NodeType.COMMUNICATION_CENTER, "lat": 19.1460, "lon": 72.9477, "capacity": 100, "criticality": 0.85}
        ]
        
        # Create nodes
        for config in node_configs:
            node = InfrastructureNode(
                node_id=config["id"],
                name=config["name"],
                node_type=config["type"],
                location={"lat": config["lat"], "lon": config["lon"]},
                capacity=config["capacity"],
                current_load=np.random.uniform(0.3, 0.9) * config["capacity"],
                health_score=np.random.uniform(0.7, 1.0),
                redundancy_level=np.random.randint(1, 4),
                repair_time_hours=np.random.uniform(2, 24),
                criticality_score=config["criticality"]
            )
            self.nodes[node.node_id] = node
        
        # Create realistic dependencies
        dependencies = [
            # Power dependencies
            ("power_main_mumbai", "telecom_main_mumbai", "power_supply", 0.9, 0.8, 5.0),
            ("power_main_mumbai", "water_main_mumbai", "power_supply", 0.85, 0.9, 8.0),
            ("power_main_mumbai", "hospital_main", "power_supply", 0.95, 0.9, 3.0),
            ("power_main_mumbai", "comm_control", "power_supply", 0.98, 0.95, 2.0),
            ("power_suburban_1", "telecom_south", "power_supply", 0.8, 0.7, 3.0),
            ("power_suburban_2", "telecom_north", "power_supply", 0.8, 0.7, 3.0),
            ("power_industrial", "bridge_sealink", "power_supply", 0.7, 0.6, 10.0),
            
            # Telecom dependencies
            ("telecom_main_mumbai", "comm_control", "data_link", 0.9, 0.8, 1.0),
            ("telecom_south", "hospital_south", "emergency_comm", 0.7, 0.6, 2.0),
            ("telecom_north", "hospital_north", "emergency_comm", 0.7, 0.6, 2.0),
            
            # Water dependencies
            ("water_main_mumbai", "hospital_main", "water_supply", 0.9, 0.8, 2.0),
            ("water_main_mumbai", "power_main_mumbai", "cooling_water", 0.6, 0.5, 5.0),
            ("water_east", "hospital_south", "water_supply", 0.8, 0.7, 1.0),
            ("water_west", "hospital_north", "water_supply", 0.8, 0.7, 1.0),
            
            # Transport dependencies
            ("bridge_sealink", "hospital_main", "patient_transport", 0.6, 0.5, 8.0),
            ("bridge_eastern", "hospital_south", "patient_transport", 0.5, 0.4, 5.0),
            
            # Communication dependencies
            ("comm_control", "power_main_mumbai", "control_signals", 0.8, 0.7, 2.0),
            ("comm_backup", "comm_control", "backup_link", 0.9, 0.8, 15.0),
            
            # Cross-dependencies
            ("telecom_main_mumbai", "power_suburban_1", "coordination", 0.3, 0.2, 7.0),
            ("hospital_main", "telecom_main_mumbai", "medical_coordination", 0.4, 0.3, 1.0),
            ("water_main_mumbai", "telecom_main_mumbai", "sensor_data", 0.2, 0.1, 3.0)
        ]
        
        # Create dependency edges
        for source, target, dep_type, prop_weight, rec_dep, distance in dependencies:
            edge_id = f"{source}_{target}"
            edge = DependencyEdge(
                source_node=source,
                target_node=target,
                dependency_type=dep_type,
                failure_propagation_weight=prop_weight,
                recovery_dependency=rec_dep,
                distance_km=distance
            )
            self.edges[edge_id] = edge
            
            # Update dependency graphs
            self.dependency_graph[source].append(target)
            self.reverse_dependency_graph[target].append(source)
            
            # Update node dependencies
            self.nodes[source].dependents.append(target)
            self.nodes[target].dependencies.append(source)
        
        # Calculate critical node analyses
        self._calculate_critical_node_analyses()
    
    def _calculate_critical_node_analyses(self):
        """Calculate critical node analyses for all nodes"""
        for node_id, node in self.nodes.items():
            # Calculate centrality score (number of connections weighted by criticality)
            centrality_score = 0
            for dependent_id in node.dependents:
                centrality_score += self.nodes[dependent_id].criticality_score * 0.5
            for dependency_id in node.dependencies:
                centrality_score += self.nodes[dependency_id].criticality_score * 0.3
            
            # Normalize centrality score
            max_centrality = max(len(node.dependents) + len(node.dependencies), 1)
            centrality_score = min(1.0, centrality_score / max_centrality)
            
            # Calculate cascade contribution score
            cascade_contribution_score = self._calculate_cascade_contribution(node_id)
            
            # Calculate vulnerability score
            vulnerability_score = (1 - node.health_score) * (1 - node.redundancy_level / 5) * node.criticality_score
            
            # Calculate stabilization priority
            stabilization_priority = (centrality_score * 0.4 + 
                                   cascade_contribution_score * 0.4 + 
                                   vulnerability_score * 0.2)
            
            # Generate recommended actions
            recommended_actions = []
            if vulnerability_score > 0.7:
                recommended_actions.append("increase_redundancy")
            if centrality_score > 0.8:
                recommended_actions.append("enhance_monitoring")
            if cascade_contribution_score > 0.7:
                recommended_actions.append("pre_stabilization")
            
            analysis = CriticalNodeAnalysis(
                node_id=node_id,
                centrality_score=centrality_score,
                cascade_contribution_score=cascade_contribution_score,
                vulnerability_score=vulnerability_score,
                stabilization_priority=stabilization_priority,
                recommended_actions=recommended_actions
            )
            
            self.critical_node_analyses[node_id] = analysis
    
    def _calculate_cascade_contribution(self, node_id: str) -> float:
        """Calculate how much a node contributes to cascades"""
        total_contribution = 0
        visited = set()
        
        def dfs_contribution(current_node: str, depth: int) -> float:
            if current_node in visited or depth > 5:
                return 0
            
            visited.add(current_node)
            contribution = 0
            
            for dependent_id in self.nodes[current_node].dependents:
                edge_id = f"{current_node}_{dependent_id}"
                if edge_id in self.edges:
                    edge = self.edges[edge_id]
                    weight = edge.failure_propagation_weight
                    contribution += weight * (1 - depth * 0.1)  # Decrease with depth
                    contribution += dfs_contribution(dependent_id, depth + 1) * weight * 0.5
            
            return contribution
        
        return min(1.0, dfs_contribution(node_id, 0) / 10)
    
    async def _continuous_monitoring(self):
        """Continuous monitoring for cascade risks"""
        while True:
            try:
                # Update node health scores (simulate degradation)
                for node in self.nodes.values():
                    node.health_score *= np.random.uniform(0.98, 1.0)
                    node.current_load = np.random.uniform(0.3, 0.9) * node.capacity
                
                # Check for high-risk nodes
                high_risk_nodes = [node_id for node_id, node in self.nodes.items() 
                                 if node.health_score < 0.6 or node.current_load / node.capacity > 0.9]
                
                # Generate cascade predictions for high-risk nodes
                for node_id in high_risk_nodes:
                    await self._generate_cascade_prediction(node_id)
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                print(f"Monitoring error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _generate_cascade_prediction(self, initial_failure_node: str):
        """Generate cascade failure prediction"""
        try:
            node = self.nodes[initial_failure_node]
            
            # Determine failure mode based on node condition
            if node.current_load / node.capacity > 0.9:
                failure_mode = FailureMode.OVERLOAD
            elif node.health_score < 0.6:
                failure_mode = FailureMode.EQUIPMENT_FAILURE
            else:
                failure_mode = FailureMode.STRUCTURAL_DAMAGE
            
            # Simulate cascade propagation
            cascade_result = self._simulate_cascade_propagation(initial_failure_node, failure_mode)
            
            # Calculate cascade radius
            affected_nodes = cascade_result["affected_nodes"]
            if affected_nodes:
                locations = [self.nodes[node_id].location for node_id in affected_nodes if node_id in self.nodes]
                if locations:
                    max_distance = max(
                        self._calculate_distance(self.nodes[initial_failure_node].location, loc)
                        for loc in locations
                    )
                else:
                    max_distance = 0
            else:
                max_distance = 0
            
            # Create prediction
            prediction = CascadePrediction(
                prediction_id=f"pred_{uuid.uuid4().hex[:12]}",
                timestamp=datetime.now(),
                initial_failure_node=initial_failure_node,
                failure_mode=failure_mode,
                cascade_probability=cascade_result["cascade_probability"],
                predicted_radius_km=max_distance,
                affected_nodes=affected_nodes,
                cascade_timeline=cascade_result["timeline"],
                total_impact_score=cascade_result["total_impact"],
                confidence=0.85
            )
            
            self.cascade_predictions.append(prediction)
            
            # Keep only recent predictions
            if len(self.cascade_predictions) > 100:
                self.cascade_predictions = self.cascade_predictions[-100:]
            
            # Generate pre-stabilization strategies if high risk
            if prediction.cascade_probability > 0.7:
                await self._generate_pre_stabilization_strategies(prediction)
            
        except Exception as e:
            print(f"Cascade prediction error for {initial_failure_node}: {str(e)}")
    
    def _simulate_cascade_propagation(self, initial_node: str, failure_mode: FailureMode) -> Dict[str, Any]:
        """Simulate cascade failure propagation"""
        affected_nodes = [initial_node]
        failed_nodes = set([initial_node])
        timeline = []
        current_time = 0
        total_impact = 0
        
        # Initial failure
        timeline.append({
            "time_minutes": current_time,
            "event": "initial_failure",
            "node": initial_node,
            "failure_mode": failure_mode.value,
            "impact_score": self.nodes[initial_node].criticality_score
        })
        total_impact += self.nodes[initial_node].criticality_score
        
        # Propagate failure through dependencies
        propagation_queue = deque([(initial_node, 0)])
        
        while propagation_queue:
            current_node, depth = propagation_queue.popleft()
            
            if depth > 5:  # Limit propagation depth
                continue
            
            current_time += 5  # 5 minutes per propagation step
            
            for dependent_id in self.nodes[current_node].dependents:
                if dependent_id not in failed_nodes:
                    edge_id = f"{current_node}_{dependent_id}"
                    if edge_id in self.edges:
                        edge = self.edges[edge_id]
                        
                        # Calculate failure probability
                        failure_prob = edge.failure_propagation_weight
                        
                        # Adjust based on node health and redundancy
                        dependent_node = self.nodes[dependent_id]
                        failure_prob *= (1 - dependent_node.health_score) * (1 - dependent_node.redundancy_level / 5)
                        
                        # Adjust based on failure mode
                        if failure_mode == FailureMode.OVERLOAD:
                            failure_prob *= 1.2
                        elif failure_mode == FailureMode.POWER_OUTAGE and dependent_node.node_type == NodeType.POWER_GRID:
                            failure_prob *= 1.5
                        
                        # Simulate failure
                        if np.random.random() < failure_prob:
                            failed_nodes.add(dependent_id)
                            affected_nodes.append(dependent_id)
                            
                            timeline.append({
                                "time_minutes": current_time,
                                "event": "cascade_failure",
                                "node": dependent_id,
                                "source_node": current_node,
                                "failure_probability": failure_prob,
                                "impact_score": dependent_node.criticality_score
                            })
                            
                            total_impact += dependent_node.criticality_score
                            propagation_queue.append((dependent_id, depth + 1))
        
        # Calculate overall cascade probability
        cascade_probability = min(1.0, len(failed_nodes) / len(self.nodes))
        
        return {
            "affected_nodes": affected_nodes,
            "cascade_probability": cascade_probability,
            "timeline": timeline,
            "total_impact": total_impact
        }
    
    def _calculate_distance(self, loc1: Dict[str, float], loc2: Dict[str, float]) -> float:
        """Calculate distance between two locations (simplified)"""
        lat_diff = loc1["lat"] - loc2["lat"]
        lon_diff = loc1["lon"] - loc2["lon"]
        return np.sqrt(lat_diff**2 + lon_diff**2) * 111  # Approximate km per degree
    
    async def _generate_pre_stabilization_strategies(self, prediction: CascadePrediction):
        """Generate pre-stabilization strategies"""
        strategies = []
        
        # Strategy 1: Stabilize critical nodes in cascade path
        critical_nodes = []
        for node_id in prediction.affected_nodes[:5]:  # Top 5 affected nodes
            if node_id in self.critical_node_analyses:
                analysis = self.critical_node_analyses[node_id]
                if analysis.stabilization_priority > 0.7:
                    critical_nodes.append(node_id)
        
        if critical_nodes:
            strategy = PreStabilizationStrategy(
                strategy_id=f"strategy_{uuid.uuid4().hex[:12]}",
                target_nodes=critical_nodes,
                stabilization_actions=[
                    {
                        "action_type": "load_reduction",
                        "target_nodes": critical_nodes,
                        "reduction_percentage": 0.3
                    },
                    {
                        "action_type": "backup_activation",
                        "target_nodes": critical_nodes[:2],
                        "backup_systems": 2
                    }
                ],
                expected_cascade_reduction=0.6,
                implementation_cost=50000,
                implementation_time_minutes=30,
                priority_score=0.8
            )
            strategies.append(strategy)
        
        # Strategy 2: Strengthen dependencies
        dependency_edges = []
        for node_id in prediction.affected_nodes[:3]:
            for dependent_id in self.nodes[node_id].dependents:
                if dependent_id in prediction.affected_nodes:
                    edge_id = f"{node_id}_{dependent_id}"
                    if edge_id in self.edges:
                        dependency_edges.append(edge_id)
        
        if dependency_edges:
            strategy = PreStabilizationStrategy(
                strategy_id=f"strategy_{uuid.uuid4().hex[:12]}",
                target_nodes=[edge.split("_")[1] for edge in dependency_edges],
                stabilization_actions=[
                    {
                        "action_type": "dependency_strengthening",
                        "target_edges": dependency_edges,
                        "strengthening_factor": 0.5
                    }
                ],
                expected_cascade_reduction=0.4,
                implementation_cost=30000,
                implementation_time_minutes=45,
                priority_score=0.6
            )
            strategies.append(strategy)
        
        # Store strategies
        for strategy in strategies:
            self.pre_stabilization_strategies[strategy.strategy_id] = strategy
    
    async def predict_cascade(self, initial_failure_node: str, failure_mode: str) -> Dict[str, Any]:
        """Predict cascade failure for specific node"""
        try:
            failure_mode_enum = FailureMode(failure_mode.lower())
            await self._generate_cascade_prediction(initial_failure_node)
            
            # Get latest prediction for this node
            for prediction in reversed(self.cascade_predictions):
                if prediction.initial_failure_node == initial_failure_node:
                    return prediction.to_dict()
            
            return {"error": "No prediction found for this node"}
            
        except ValueError:
            return {"error": f"Invalid failure mode: {failure_mode}"}
        except Exception as e:
            return {"error": f"Prediction failed: {str(e)}"}
    
    def get_real_time_cascade_probability(self) -> Dict[str, Any]:
        """Get real-time cascade probability for all nodes"""
        cascade_probabilities = {}
        
        for node_id, node in self.nodes.items():
            # Calculate individual node risk
            node_risk = (1 - node.health_score) * (node.current_load / node.capacity) * node.criticality_score
            
            # Calculate cascade contribution
            cascade_contrib = self.critical_node_analyses[node_id].cascade_contribution_score if node_id in self.critical_node_analyses else 0
            
            # Combined cascade probability
            cascade_prob = min(1.0, node_risk * 0.6 + cascade_contrib * 0.4)
            
            cascade_probabilities[node_id] = {
                "node_id": node_id,
                "cascade_probability": cascade_prob,
                "risk_level": self._get_risk_level(cascade_prob),
                "health_score": node.health_score,
                "load_percentage": node.current_load / node.capacity,
                "criticality_score": node.criticality_score
            }
        
        return {
            "cascade_probabilities": cascade_probabilities,
            "high_risk_nodes": [node_id for node_id, prob in cascade_probabilities.items() if prob["cascade_probability"] > 0.7],
            "system_risk_level": self._calculate_system_risk_level(cascade_probabilities),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_risk_level(self, probability: float) -> str:
        """Get risk level from probability"""
        if probability > 0.8:
            return "critical"
        elif probability > 0.6:
            return "high"
        elif probability > 0.4:
            return "medium"
        else:
            return "low"
    
    def _calculate_system_risk_level(self, cascade_probabilities: Dict[str, Any]) -> str:
        """Calculate overall system risk level"""
        if not cascade_probabilities:
            return "low"
        
        avg_probability = np.mean([prob["cascade_probability"] for prob in cascade_probabilities.values()])
        return self._get_risk_level(avg_probability)
    
    def get_critical_nodes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get critical nodes for pre-stabilization"""
        sorted_nodes = sorted(
            self.critical_node_analyses.items(),
            key=lambda x: x[1].stabilization_priority,
            reverse=True
        )
        
        return [analysis.to_dict() for node_id, analysis in sorted_nodes[:limit]]
    
    def get_pre_stabilization_strategies(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recommended pre-stabilization strategies"""
        sorted_strategies = sorted(
            self.pre_stabilization_strategies.values(),
            key=lambda x: x.priority_score,
            reverse=True
        )
        
        return [strategy.to_dict() for strategy in sorted_strategies[:limit]]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get cascade forecast engine metrics"""
        return {
            "total_nodes": len(self.nodes),
            "total_dependencies": len(self.edges),
            "active_predictions": len(self.cascade_predictions),
            "critical_nodes_count": len([n for n in self.critical_node_analyses.values() if n.stabilization_priority > 0.7]),
            "available_strategies": len(self.pre_stabilization_strategies),
            "system_health": {
                "average_health_score": np.mean([node.health_score for node in self.nodes.values()]),
                "average_load_percentage": np.mean([node.current_load / node.capacity for node in self.nodes.values()]),
                "high_risk_nodes": len([n for n in self.nodes.values() if n.health_score < 0.6 or n.current_load / n.capacity > 0.9])
            },
            "timestamp": datetime.now().isoformat()
        }

# Global cascade forecast engine
cascade_forecast_engine = DigitalTwinCascadeForecastEngine()
