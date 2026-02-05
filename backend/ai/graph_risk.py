"""
Graph Risk Analysis - GNN for cascading failure prediction
Uses NetworkX to simulate cascading infrastructure failures
"""

import networkx as nx
from typing import Dict, List, Tuple, Optional
import random
import json
from datetime import datetime
from config import CRITICAL_INFRA, LOW_RISK, MEDIUM_RISK, HIGH_RISK

class CascadingRiskAnalyzer:
    """
    Graph Neural Network-based cascading failure analyzer
    Models infrastructure dependencies and predicts chain-reaction risks
    """
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_risks = {}
        self.risk_history = {}  # Track risk changes over time
        self._build_infrastructure_graph()
    
    def _build_infrastructure_graph(self):
        """Build the infrastructure dependency graph"""
        # Add nodes (infrastructure components)
        for infra in CRITICAL_INFRA:
            self.graph.add_node(
                infra["id"],
                name=infra["name"],
                type=infra["type"],
                lat=infra["lat"],
                lon=infra["lon"],
                risk=0.0,
                resilience=0.5  # Base resilience
            )
            self.node_risks[infra["id"]] = 0.0
        
        # Build dependency network
        # Power Grid is critical - everything depends on it
        self.graph.add_edge("power_grid_1", "hospital_1", 
                          weight=0.95, type="power_dependency", delay_minutes=15)
        self.graph.add_edge("power_grid_1", "water_supply_1", 
                          weight=0.85, type="power_dependency", delay_minutes=30)
        self.graph.add_edge("power_grid_1", "telecom_1", 
                          weight=0.80, type="power_dependency", delay_minutes=20)
        
        # Water Supply dependencies
        self.graph.add_edge("water_supply_1", "hospital_1", 
                          weight=0.70, type="water_dependency", delay_minutes=60)
        self.graph.add_edge("water_supply_1", "telecom_1", 
                          weight=0.50, type="water_dependency", delay_minutes=45)
        
        # Telecom dependencies (communications)
        self.graph.add_edge("telecom_1", "hospital_1", 
                          weight=0.60, type="communication_dependency", delay_minutes=120)
        
        # Reciprocal dependencies (cascading loops)
        self.graph.add_edge("hospital_1", "power_grid_1", 
                          weight=0.30, type="load_reduction", delay_minutes=240)
    
    def analyze_cascading_risk(self, 
                               initial_disaster: Dict,
                               propagation_steps: int = 4) -> Dict:
        """
        Analyze cascading failure risks with disaster-aware propagation
        """
        disaster_type = initial_disaster.get("type", "unknown")
        severity = initial_disaster.get("severity", 0.7)
        location = initial_disaster.get("location", {})
        
        # Find nearest infrastructure node
        affected_node = self._find_nearest_node(location)
        
        if not affected_node:
            # If no infrastructure nearby, create virtual node
            affected_node = self._create_virtual_affected_node(location, disaster_type)
        
        # Calculate initial impact based on disaster type
        initial_risk = self._calculate_initial_impact(disaster_type, severity, affected_node)
        
        # Set initial risk
        self.node_risks[affected_node] = initial_risk
        self.graph.nodes[affected_node]["risk"] = initial_risk
        
        # Track propagation
        propagation_path = [affected_node]
        affected_nodes = {affected_node: {
            "risk": initial_risk,
            "step": 0,
            "time_minutes": 0
        }}
        
        # Propagate risk through dependency network
        for step in range(1, propagation_steps + 1):
            new_affected = {}
            
            for node_id, node_state in list(affected_nodes.items()):
                current_risk = node_state["risk"]
                current_time = node_state["time_minutes"]
                
                # Propagate to dependent nodes
                for neighbor in self.graph.successors(node_id):
                    edge = self.graph[node_id][neighbor]
                    edge_weight = edge.get("weight", 0.5)
                    delay_minutes = edge.get("delay_minutes", 30)
                    
                    # Skip if already processed at this step (prevent duplicates)
                    if neighbor in affected_nodes and affected_nodes[neighbor]["step"] < step:
                        continue
                    
                    # Calculate propagated risk with time delay consideration
                    base_propagated = current_risk * edge_weight
                    
                    # Apply disaster-specific modifiers
                    risk_modifier = self._get_risk_modifier(disaster_type, neighbor, node_id)
                    propagated_risk = base_propagated * risk_modifier
                    
                    # Get target node resilience
                    target_resilience = self.graph.nodes[neighbor].get("resilience", 0.5)
                    final_risk = propagated_risk * (1 - target_resilience * 0.3)
                    
                    # Update if higher than current
                    current_target_risk = self.node_risks.get(neighbor, 0.0)
                    new_risk = max(current_target_risk, final_risk)
                    
                    if new_risk > current_target_risk:
                        new_affected[neighbor] = {
                            "risk": new_risk,
                            "step": step,
                            "time_minutes": current_time + delay_minutes
                        }
                        self.node_risks[neighbor] = new_risk
                        self.graph.nodes[neighbor]["risk"] = new_risk
                        propagation_path.append(neighbor)
            
            if not new_affected:
                break
            
            affected_nodes.update(new_affected)
        
        # Build result with enhanced information
        nodes_data = []
        edges_data = []
        
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            risk = self.node_risks[node]
            
            nodes_data.append({
                "id": node,
                "name": node_data["name"],
                "type": node_data["type"],
                "lat": node_data["lat"],
                "lon": node_data["lon"],
                "risk": round(risk, 3),
                "risk_level": self._get_risk_level(risk),
                "in_propagation_path": node in propagation_path
            })
        
        for edge in self.graph.edges(data=True):
            source, target, data = edge
            edges_data.append({
                "source": source,
                "target": target,
                "weight": data.get("weight", 0.5),
                "type": data.get("type", "dependency"),
                "delay_minutes": data.get("delay_minutes", 0)
            })
        
        # Identify critical nodes
        critical_nodes = [
            n for n in nodes_data 
            if self.node_risks.get(n["id"], 0) >= HIGH_RISK
        ]
        
        # Calculate cascade timeline
        cascade_timeline = self._calculate_cascade_timeline(affected_nodes)
        
        # Predict NEXT likely failure
        next_prediction = self._predict_next_failure(affected_nodes)
        
        return {
            "graph": {
                "nodes": nodes_data,
                "edges": edges_data
            },
            "initial_disaster": initial_disaster,
            "propagation_path": propagation_path,
            "critical_nodes": critical_nodes,
            "cascade_timeline": cascade_timeline,
            "next_failure_prediction": next_prediction,
            "max_risk": max([n["risk"] for n in nodes_data], default=0.0),
            "analyzed_at": datetime.now().isoformat()
        }

    def _predict_next_failure(self, affected_nodes: Dict) -> Optional[Dict]:
        """Predict the next component likely to fail and its probability"""
        potential_next = []
        
        for node_id, state in affected_nodes.items():
            if state["risk"] < HIGH_RISK:
                # This is a candidate for full failure soon
                probability = state["risk"] * 1.2 # Heuristic boost
                potential_next.append({
                    "node_id": node_id,
                    "name": self.graph.nodes[node_id].get("name"),
                    "probability": round(min(probability, 0.99), 2),
                    "estimated_time_min": state["time_minutes"]
                })
        
        if not potential_next: return None
        # Return the one with highest probability that hasn't failed yet
        return max(potential_next, key=lambda x: x["probability"])
    
    def _find_nearest_node(self, location: Dict) -> Optional[str]:
        """Find the nearest infrastructure node to a location"""
        min_distance = float('inf')
        nearest = None
        
        lat = location.get("lat", 0)
        lon = location.get("lon", 0)
        
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            lat_diff = abs(node_data["lat"] - lat)
            lon_diff = abs(node_data["lon"] - lon)
            distance = (lat_diff ** 2 + lon_diff ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                nearest = node
        
        # Consider node affected if within 0.05 degrees (~5km)
        if min_distance < 0.05:
            return nearest
        return None
    
    def _create_virtual_affected_node(self, location: Dict, disaster_type: str) -> str:
        """Create a virtual node when disaster is far from known infrastructure"""
        virtual_id = "disaster_zone"
        
        if virtual_id not in self.graph.nodes():
            self.graph.add_node(
                virtual_id,
                name="Disaster Zone",
                type=disaster_type,
                lat=location.get("lat", 28.6139),
                lon=location.get("lon", 77.2090),
                risk=0.0,
                virtual=True
            )
            self.node_risks[virtual_id] = 0.0
            
            # Connect to nearest infrastructure
            for infra in CRITICAL_INFRA:
                if infra["id"] != virtual_id:
                    self.graph.add_edge(
                        virtual_id, infra["id"],
                        weight=0.7,
                        type="proximity_impact",
                        delay_minutes=60
                    )
        
        return virtual_id
    
    def _calculate_initial_impact(self, disaster_type: str, severity: float, node_id: str) -> float:
        """Calculate initial impact based on disaster type and target infrastructure"""
        node_type = self.graph.nodes[node_id].get("type", "unknown")
        
        # Base impact multipliers by disaster type
        impact_matrix = {
            "flood": {
                "power": 0.85,      # Floods damage power infrastructure
                "water": 0.70,      # Water plants affected but may be resilient
                "healthcare": 0.75, # Hospitals affected
                "telecom": 0.65     # Telecom towers affected
            },
            "fire": {
                "power": 0.90,      # Fire directly damages electrical systems
                "water": 0.50,      # Less direct impact
                "healthcare": 0.80,
                "telecom": 0.85
            },
            "earthquake": {
                "power": 0.95,      # Earthquakes heavily damage infrastructure
                "water": 0.85,
                "healthcare": 0.90,
                "telecom": 0.90
            },
            "cyclone": {
                "power": 0.80,
                "water": 0.70,
                "healthcare": 0.75,
                "telecom": 0.85     # Wind damages towers
            }
        }
        
        base_multiplier = impact_matrix.get(disaster_type, {}).get(node_type, 0.75)
        initial_risk = severity * base_multiplier
        
        return min(1.0, initial_risk)
    
    def _get_risk_modifier(self, disaster_type: str, target_node: str, source_node: str) -> float:
        """Get risk propagation modifier based on disaster type and node types"""
        target_type = self.graph.nodes[target_node].get("type", "unknown")
        source_type = self.graph.nodes[source_node].get("type", "unknown")
        
        # Special propagation rules
        if disaster_type == "flood":
            # Floods spread through water systems
            if source_type == "water" and target_type == "power":
                return 1.2  # Enhanced propagation
        
        elif disaster_type == "fire":
            # Fire spreads through power lines
            if source_type == "power" and target_type in ["telecom", "healthcare"]:
                return 1.15
        
        elif disaster_type == "earthquake":
            # Earthquake affects everything similarly
            return 1.1
        
        return 1.0  # Default modifier
    
    def _calculate_cascade_timeline(self, affected_nodes: Dict) -> List[Dict]:
        """Calculate timeline of cascading failures"""
        timeline = []
        
        for node_id, state in affected_nodes.items():
            node_name = self.graph.nodes[node_id].get("name", node_id)
            timeline.append({
                "node": node_name,
                "node_id": node_id,
                "risk": round(state["risk"], 3),
                "time_minutes": state["time_minutes"],
                "step": state["step"]
            })
        
        timeline.sort(key=lambda x: (x["step"], x["time_minutes"]))
        return timeline
    
    def _get_risk_level(self, risk: float) -> str:
        """Convert risk score to level"""
        if risk >= HIGH_RISK:
            return "high"
        elif risk >= MEDIUM_RISK:
            return "medium"
        elif risk >= LOW_RISK:
            return "low"
        else:
            return "minimal"
    
    def get_current_graph_state(self) -> Dict:
        """Get current state of the risk graph"""
        nodes_data = []
        edges_data = []
        
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            nodes_data.append({
                "id": node,
                "name": node_data["name"],
                "type": node_data["type"],
                "lat": node_data["lat"],
                "lon": node_data["lon"],
                "risk": round(self.node_risks.get(node, 0.0), 3),
                "risk_level": self._get_risk_level(self.node_risks.get(node, 0.0))
            })
        
        for edge in self.graph.edges(data=True):
            source, target, data = edge
            edges_data.append({
                "source": source,
                "target": target,
                "weight": data.get("weight", 0.5),
                "type": data.get("type", "dependency")
            })
        
        return {
            "nodes": nodes_data,
            "edges": edges_data,
            "timestamp": datetime.now().isoformat()
        }
    
    def reset_risks(self):
        """Reset all risk scores to zero"""
        for node in self.graph.nodes():
            self.node_risks[node] = 0.0
            self.graph.nodes[node]["risk"] = 0.0
        self.risk_history = {}

# Global instance
cascading_risk_analyzer = CascadingRiskAnalyzer()
