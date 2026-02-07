"""
National Digital Twin Layer - District-level Infrastructure Modeling
Real-time cascade simulation and failure prediction for India-scale deployment
"""

import asyncio
import networkx as nx
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import json
from enum import Enum

class InfrastructureType(Enum):
    POWER_SUBSTATION = "power_substation"
    HOSPITAL = "hospital"
    TELECOM_TOWER = "telecom_tower"
    WATER_PLANT = "water_plant"
    TRANSPORT_HUB = "transport_hub"

class DisasterType(Enum):
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    CYCLONE = "cyclone"
    FIRE = "fire"
    TERRORISM = "terrorism"

@dataclass
class InfrastructureNode:
    id: str
    name: str
    type: InfrastructureType
    district: str
    lat: float
    lon: float
    capacity: float  # Service capacity (MW for power, beds for hospital, etc.)
    current_load: float = 0.0
    health_score: float = 1.0  # 0-1, 1 = fully operational
    redundancy_level: int = 1  # Number of backup systems
    recovery_time_hours: float = 24.0  # Base recovery time
    population_served: int = 0
    criticality_score: float = 0.5  # 0-1, importance to national infrastructure
    
@dataclass
class DependencyEdge:
    source_id: str
    target_id: str
    dependency_type: str  # "power", "telecom", "water", "transport"
    weight: float = 1.0  # Failure propagation weight
    capacity_threshold: float = 0.8  # When source fails below this, target affected
    recovery_coupling: float = 0.3  # How much source recovery helps target

@dataclass
class CascadeSimulation:
    disaster_type: DisasterType
    epicenter_lat: float
    epicenter_lon: float
    severity: float  # 0-1
    affected_nodes: List[str] = field(default_factory=list)
    cascade_timeline: List[Dict] = field(default_factory=list)
    cascading_failure_probability: float = 0.0
    estimated_population_impact: int = 0
    service_outage_duration_hours: float = 0.0
    economic_impact_usd: float = 0.0

class NationalDigitalTwin:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, InfrastructureNode] = {}
        self.edges: Dict[str, DependencyEdge] = {}
        self.districts: Dict[str, List[str]] = {}
        self._initialize_india_infrastructure()
        
    def _initialize_india_infrastructure(self):
        """Initialize with realistic India district-level infrastructure data"""
        # Major districts and their infrastructure
        districts_data = {
            "mumbai": {"lat": 19.0760, "lon": 72.8777, "population": 12442373},
            "delhi": {"lat": 28.7041, "lon": 77.1025, "population": 16787941},
            "bangalore": {"lat": 12.9716, "lon": 77.5946, "population": 8443675},
            "kolkata": {"lat": 22.5726, "lon": 88.3639, "population": 4496694},
            "chennai": {"lat": 13.0827, "lon": 80.2707, "population": 4646732},
            "hyderabad": {"lat": 17.3850, "lon": 78.4867, "population": 6809970},
            "pune": {"lat": 18.5204, "lon": 73.8567, "population": 3124458},
            "ahmedabad": {"lat": 23.0225, "lon": 72.5714, "population": 5577940},
            "jaipur": {"lat": 26.9124, "lon": 75.7873, "population": 3073350},
            "surat": {"lat": 21.1702, "lon": 72.8311, "population": 4467797},
        }
        
        # Create infrastructure nodes for each district
        for district, data in districts_data.items():
            self.districts[district] = []
            
            # Power infrastructure
            for i in range(3):  # 3 major substations per district
                node_id = f"{district}_power_{i}"
                node = InfrastructureNode(
                    id=node_id,
                    name=f"{district.title()} Power Substation {i+1}",
                    type=InfrastructureType.POWER_SUBSTATION,
                    district=district,
                    lat=data["lat"] + np.random.uniform(-0.1, 0.1),
                    lon=data["lon"] + np.random.uniform(-0.1, 0.1),
                    capacity=np.random.uniform(200, 500),  # MW
                    redundancy_level=np.random.choice([1, 2]),
                    recovery_time_hours=np.random.uniform(12, 48),
                    population_served=data["population"] // 3,
                    criticality_score=0.9
                )
                self.add_node(node)
                self.districts[district].append(node_id)
            
            # Healthcare infrastructure
            for i in range(2):  # 2 major hospitals per district
                node_id = f"{district}_hospital_{i}"
                node = InfrastructureNode(
                    id=node_id,
                    name=f"{district.title()} Central Hospital {i+1}",
                    type=InfrastructureType.HOSPITAL,
                    district=district,
                    lat=data["lat"] + np.random.uniform(-0.05, 0.05),
                    lon=data["lon"] + np.random.uniform(-0.05, 0.05),
                    capacity=np.random.uniform(500, 2000),  # beds
                    redundancy_level=1,
                    recovery_time_hours=np.random.uniform(24, 72),
                    population_served=data["population"] // 2,
                    criticality_score=0.95
                )
                self.add_node(node)
                self.districts[district].append(node_id)
            
            # Telecom infrastructure
            for i in range(4):  # 4 telecom towers per district
                node_id = f"{district}_telecom_{i}"
                node = InfrastructureNode(
                    id=node_id,
                    name=f"{district.title()} Telecom Tower {i+1}",
                    type=InfrastructureType.TELECOM_TOWER,
                    district=district,
                    lat=data["lat"] + np.random.uniform(-0.08, 0.08),
                    lon=data["lon"] + np.random.uniform(-0.08, 0.08),
                    capacity=np.random.uniform(10000, 50000),  # connections
                    redundancy_level=2,
                    recovery_time_hours=np.random.uniform(6, 24),
                    population_served=data["population"] // 4,
                    criticality_score=0.8
                )
                self.add_node(node)
                self.districts[district].append(node_id)
            
            # Water infrastructure
            node_id = f"{district}_water_0"
            node = InfrastructureNode(
                id=node_id,
                name=f"{district.title()} Water Treatment Plant",
                type=InfrastructureType.WATER_PLANT,
                district=district,
                lat=data["lat"] + np.random.uniform(-0.05, 0.05),
                lon=data["lon"] + np.random.uniform(-0.05, 0.05),
                capacity=np.random.uniform(100, 500),  # MLD (million liters per day)
                redundancy_level=1,
                recovery_time_hours=np.random.uniform(24, 96),
                population_served=data["population"],
                criticality_score=0.85
            )
            self.add_node(node)
            self.districts[district].append(node_id)
        
        # Create dependency edges (interconnections)
        self._create_dependency_edges()
    
    def _create_dependency_edges(self):
        """Create realistic dependency edges between infrastructure nodes"""
        for district, node_ids in self.districts.items():
            # Power dependencies (hospitals, telecom, water plants need power)
            power_nodes = [nid for nid in node_ids if "power" in nid]
            hospital_nodes = [nid for nid in node_ids if "hospital" in nid]
            telecom_nodes = [nid for nid in node_ids if "telecom" in nid]
            water_nodes = [nid for nid in node_ids if "water" in nid]
            
            # Connect hospitals to power
            for hospital in hospital_nodes:
                for power in power_nodes[:2]:  # Each hospital connected to 2 power sources
                    self.add_edge(DependencyEdge(
                        source_id=power,
                        target_id=hospital,
                        dependency_type="power",
                        weight=0.9,
                        capacity_threshold=0.7,
                        recovery_coupling=0.4
                    ))
            
            # Connect telecom towers to power
            for telecom in telecom_nodes:
                for power in power_nodes[:1]:  # Each telecom tower to 1 power source
                    self.add_edge(DependencyEdge(
                        source_id=power,
                        target_id=telecom,
                        dependency_type="power",
                        weight=0.8,
                        capacity_threshold=0.6,
                        recovery_coupling=0.3
                    ))
            
            # Connect water plants to power
            for water in water_nodes:
                for power in power_nodes[:1]:  # Each water plant to 1 power source
                    self.add_edge(DependencyEdge(
                        source_id=power,
                        target_id=water,
                        dependency_type="power",
                        weight=0.95,
                        capacity_threshold=0.8,
                        recovery_coupling=0.5
                    ))
            
            # Inter-district connections (power grid)
            if district != "mumbai":  # Connect to Mumbai as hub
                for power in power_nodes[:1]:
                    mumbai_power = [nid for nid in self.districts["mumbai"] if "power" in nid][0]
                    self.add_edge(DependencyEdge(
                        source_id=mumbai_power,
                        target_id=power,
                        dependency_type="power",
                        weight=0.6,
                        capacity_threshold=0.5,
                        recovery_coupling=0.2
                    ))
    
    def add_node(self, node: InfrastructureNode):
        """Add infrastructure node to digital twin"""
        self.nodes[node.id] = node
        self.graph.add_node(node.id, **node.__dict__)
    
    def add_edge(self, edge: DependencyEdge):
        """Add dependency edge to digital twin"""
        edge_id = f"{edge.source_id}->{edge.target_id}"
        self.edges[edge_id] = edge
        self.graph.add_edge(edge.source_id, edge.target_id, **edge.__dict__)
    
    async def simulate_cascade(self, 
                           disaster_type: DisasterType,
                           epicenter_lat: float,
                           epicenter_lon: float,
                           severity: float) -> CascadeSimulation:
        """
        Simulate cascading infrastructure failures
        
        Returns:
            CascadeSimulation with detailed impact analysis
        """
        simulation = CascadeSimulation(
            disaster_type=disaster_type,
            epicenter_lat=epicenter_lat,
            epicenter_lon=epicenter_lon,
            severity=severity
        )
        
        # Step 1: Identify initially affected nodes based on disaster epicenter
        affected_nodes = self._get_initially_affected_nodes(epicenter_lat, epicenter_lon, severity, disaster_type)
        simulation.affected_nodes = affected_nodes
        
        # Step 2: Simulate cascade propagation
        cascade_timeline = []
        failed_nodes = set(affected_nodes)
        current_time = 0
        
        while current_time < 72:  # Simulate 72 hours
            hour_events = []
            
            # Check for new failures due to dependencies
            newly_failed = set()
            for node_id in failed_nodes:
                # Find dependent nodes
                for successor in self.graph.successors(node_id):
                    if successor not in failed_nodes:
                        edge_data = self.edges.get(f"{node_id}->{successor}")
                        if edge_data and self._should_fail_cascade(successor, edge_data, severity):
                            newly_failed.add(successor)
                            hour_events.append({
                                "time_hours": current_time,
                                "node_id": successor,
                                "node_name": self.nodes[successor].name,
                                "failure_type": "cascade",
                                "source_node": node_id,
                                "dependency_type": edge_data.dependency_type
                            })
            
            # Add newly failed nodes
            failed_nodes.update(newly_failed)
            cascade_timeline.extend(hour_events)
            
            if not newly_failed:
                break  # Cascade stopped
            
            current_time += 1
        
        simulation.cascade_timeline = cascade_timeline
        simulation.cascading_failure_probability = len(failed_nodes) / len(self.nodes)
        
        # Calculate impact metrics
        simulation.estimated_population_impact = sum(
            self.nodes[nid].population_served for nid in failed_nodes
        )
        
        simulation.service_outage_duration_hours = self._calculate_outage_duration(failed_nodes, disaster_type)
        simulation.economic_impact_usd = self._calculate_economic_impact(failed_nodes, disaster_type)
        
        return simulation
    
    def _get_initially_affected_nodes(self, lat: float, lon: float, severity: float, disaster_type: DisasterType) -> List[str]:
        """Get nodes initially affected by disaster based on location and severity"""
        affected = []
        
        for node_id, node in self.nodes.items():
            # Calculate distance from epicenter
            distance = np.sqrt((node.lat - lat)**2 + (node.lon - lon)**2) * 111  # Approximate km
            
            # Disaster-specific impact radius
            if disaster_type == DisasterType.EARTHQUAKE:
                impact_radius = severity * 200  # Up to 200km for severe earthquake
            elif disaster_type == DisasterType.FLOOD:
                impact_radius = severity * 100  # Up to 100km for severe flood
            elif disaster_type == DisasterType.CYCLONE:
                impact_radius = severity * 300  # Up to 300km for severe cyclone
            else:
                impact_radius = severity * 50  # Default 50km
            
            if distance <= impact_radius:
                # Probability of initial failure based on distance and severity
                failure_prob = severity * (1 - distance / impact_radius)
                if np.random.random() < failure_prob:
                    affected.append(node_id)
        
        return affected
    
    def _should_fail_cascade(self, node_id: str, edge: DependencyEdge, severity: float) -> bool:
        """Determine if a node should fail due to cascade"""
        node = self.nodes[node_id]
        
        # Consider redundancy
        if node.redundancy_level > 1:
            # Check if there are other working sources
            working_sources = 0
            for predecessor in self.graph.predecessors(node_id):
                if predecessor not in [n.id for n in self.nodes.values() if n.health_score < 0.3]:
                    working_sources += 1
            
            if working_sources >= node.redundancy_level:
                return False
        
        # Failure probability based on edge weight and severity
        cascade_prob = edge.weight * severity * (1 - edge.capacity_threshold)
        return np.random.random() < cascade_prob
    
    def _calculate_outage_duration(self, failed_nodes: List[str], disaster_type: DisasterType) -> float:
        """Calculate average service outage duration in hours"""
        if not failed_nodes:
            return 0.0
        
        total_duration = 0
        for node_id in failed_nodes:
            node = self.nodes[node_id]
            base_duration = node.recovery_time_hours
            
            # Adjust based on disaster type
            if disaster_type == DisasterType.EARTHQUAKE:
                base_duration *= 1.5
            elif disaster_type == DisasterType.FLOOD:
                base_duration *= 2.0
            elif disaster_type == DisasterType.CYCLONE:
                base_duration *= 1.3
            
            total_duration += base_duration
        
        return total_duration / len(failed_nodes)
    
    def _calculate_economic_impact(self, failed_nodes: List[str], disaster_type: DisasterType) -> float:
        """Calculate economic impact in USD"""
        total_impact = 0
        
        for node_id in failed_nodes:
            node = self.nodes[node_id]
            
            # Base economic impact per node type
            if node.type == InfrastructureType.POWER_SUBSTATION:
                daily_impact = 1000000  # $1M/day per substation
            elif node.type == InfrastructureType.HOSPITAL:
                daily_impact = 500000  # $500K/day per hospital
            elif node.type == InfrastructureType.TELECOM_TOWER:
                daily_impact = 100000  # $100K/day per tower
            elif node.type == InfrastructureType.WATER_PLANT:
                daily_impact = 2000000  # $2M/day per water plant
            else:
                daily_impact = 200000  # $200K/day for transport hubs
            
            # Multiply by outage duration
            outage_duration = node.recovery_time_hours / 24
            total_impact += daily_impact * outage_duration
        
        return total_impact
    
    def get_district_resilience_score(self, district: str) -> float:
        """Calculate resilience score for a specific district"""
        if district not in self.districts:
            return 0.0
        
        node_ids = self.districts[district]
        total_health = sum(self.nodes[nid].health_score for nid in node_ids)
        return total_health / len(node_ids)
    
    def get_national_resilience_map(self) -> Dict[str, float]:
        """Get resilience scores for all districts"""
        return {
            district: self.get_district_resilience_score(district)
            for district in self.districts.keys()
        }

# Global instance
national_digital_twin = NationalDigitalTwin()
