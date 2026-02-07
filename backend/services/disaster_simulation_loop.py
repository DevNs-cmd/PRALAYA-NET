"""
Automatic Disaster Simulation Loop
Continuously generates synthetic disaster events for demonstration
"""

import asyncio
import uuid
import random
from typing import Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

class DisasterType(Enum):
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    CYCLONE = "cyclone"
    FIRE = "fire"
    TERRORISM = "terrorism"
    INFRASTRUCTURE_FAILURE = "infrastructure_failure"
    WEATHER = "weather"
    CHEMICAL = "chemical"

class DisasterSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"

class DisasterSimulationLoop:
    """Automatic disaster simulation for demonstration"""
    
    def __init__(self):
        self.simulation_active = False
        self.last_disaster_time = None
        self.disaster_interval_minutes = 45  # Disaster every 45 minutes
        self.infrastructure_nodes = [
            "power_grid_mumbai", "power_grid_delhi", "telecom_mumbai", "telecom_delhi",
            "transport_mumbai", "transport_delhi", "water_mumbai", "water_delhi",
            "hospital_mumbai", "hospital_delhi", "bridge_sealink", "bridge_bandra"
        ]
        
        # Import services
        try:
            from backend.services.autonomous_execution_engine import autonomous_execution_engine
            from backend.services.multi_agent_negotiation_engine import multi_agent_negotiation_engine
            from backend.services.replay_engine import replay_engine
            from backend.services.stability_index_service import stability_index_service
            
            self.execution_engine = autonomous_execution_engine
            self.agent_engine = multi_agent_negotiation_engine
            self.replay_engine = replay_engine
            self.stability_service = stability_index_service
            
        except ImportError as e:
            print(f"Service import error: {str(e)}")
            self.execution_engine = None
            self.agent_engine = None
            self.replay_engine = None
            self.stability_service = None
    
    async def start_simulation(self):
        """Start automatic disaster simulation"""
        self.simulation_active = True
        print("🌪️ Disaster simulation loop started")
        
        while self.simulation_active:
            try:
                # Check if it's time for a new disaster
                if self._should_trigger_disaster():
                    await self._generate_disaster_event()
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Disaster simulation error: {str(e)}")
                await asyncio.sleep(120)  # Wait 2 minutes on error
    
    def stop_simulation(self):
        """Stop automatic disaster simulation"""
        self.simulation_active = False
        print("🛑 Disaster simulation loop stopped")
    
    def _should_trigger_disaster(self) -> bool:
        """Check if it's time to trigger a new disaster"""
        if self.last_disaster_time is None:
            return True
        
        time_since_last = datetime.now() - self.last_disaster_time
        return time_since_last.total_seconds() >= (self.disaster_interval_minutes * 60)
    
    async def _generate_disaster_event(self):
        """Generate a synthetic disaster event"""
        print(f"🚨 Generating disaster event at {datetime.now()}")
        
        # Select disaster type and severity
        disaster_type = random.choice(list(DisasterType))
        severity = random.choice(list(DisasterSeverity))
        
        # Select affected nodes
        num_affected = random.randint(2, 4)
        affected_nodes = random.sample(self.infrastructure_nodes, num_affected)
        
        # Calculate severity multiplier
        severity_multiplier = {
            DisasterSeverity.LOW: 0.3,
            DisasterSeverity.MEDIUM: 0.5,
            DisasterSeverity.HIGH: 0.7,
            DisasterSeverity.EXTREME: 0.9
        }[severity]
        
        # Record disaster event in replay engine
        if self.replay_engine:
            await self.replay_engine.record_event(
                self.replay_engine.EventType.DISASTER_DETECTED,
                {
                    "disaster_type": disaster_type.value,
                    "severity": severity.value,
                    "affected_nodes": affected_nodes,
                    "severity_multiplier": severity_multiplier,
                    "message": f"{disaster_type.value.capitalize()} detected with {severity.value} severity"
                },
                "disaster_simulator",
                "critical"
            )
        
        # Update infrastructure risk levels
        if self.execution_engine:
            for node_id in affected_nodes:
                if node_id in self.execution_engine.infrastructure_nodes:
                    # Increase risk dramatically
                    current_risk = self.execution_engine.infrastructure_nodes[node_id]["risk"]
                    new_risk = min(0.95, current_risk + (0.5 * severity_multiplier))
                    self.execution_engine.infrastructure_nodes[node_id]["risk"] = new_risk
                    
                    # Increase load
                    current_load = self.execution_engine.infrastructure_nodes[node_id]["load"]
                    capacity = self.execution_engine.infrastructure_nodes[node_id]["capacity"]
                    new_load = min(capacity * 0.95, current_load + (capacity * 0.3 * severity_multiplier))
                    self.execution_engine.infrastructure_nodes[node_id]["load"] = new_load
        
        # Trigger autonomous response
        await self._trigger_autonomous_response(affected_nodes, severity_multiplier)
        
        # Update last disaster time
        self.last_disaster_time = datetime.now()
        
        print(f"✅ Disaster event generated: {disaster_type.value} ({severity.value}) affecting {len(affected_nodes)} nodes")
    
    async def _trigger_autonomous_response(self, affected_nodes: List[str], severity_multiplier: float):
        """Trigger autonomous response to disaster"""
        if not self.execution_engine:
            return
        
        # Generate intents for high-risk nodes
        for node_id in affected_nodes:
            node_data = self.execution_engine.infrastructure_nodes.get(node_id, {})
            if node_data.get("risk", 0) > 0.6:
                # Intent will be generated automatically by the execution engine
                print(f"🎯 High risk detected for {node_id}, triggering autonomous response")
        
        # Create tasks for multi-agent negotiation
        if self.agent_engine:
            for node_id in affected_nodes:
                task_type = self._get_task_type_for_node(node_id)
                
                task_id = self.agent_engine.create_task(
                    task_type=task_type,
                    infrastructure_node=node_id,
                    risk_level=severity_multiplier,
                    resource_requirements=[
                        {
                            "resource_type": "technicians",
                            "quantity": int(10 * severity_multiplier),
                            "priority": 1,
                            "urgency": severity_multiplier
                        }
                    ]
                )
                
                print(f"🤖 Task created for {node_id}: {task_id}")
    
    def _get_task_type_for_node(self, node_id: str) -> str:
        """Get task type based on infrastructure node"""
        if "power" in node_id:
            return "power_stabilization"
        elif "telecom" in node_id:
            return "telecom_restoration"
        elif "transport" in node_id:
            return "transport_management"
        elif "water" in node_id:
            return "water_management"
        elif "hospital" in node_id:
            return "medical_response"
        else:
            return "infrastructure_stabilization"
    
    async def trigger_immediate_disaster(self, disaster_type: str = None, severity: str = None):
        """Trigger an immediate disaster for demonstration"""
        print(f"🚨 Immediate disaster triggered: {disaster_type or 'random'}")
        
        # Override random selection if specified
        if disaster_type:
            try:
                disaster_type = DisasterType(disaster_type)
            except ValueError:
                disaster_type = random.choice(list(DisasterType))
        else:
            disaster_type = random.choice(list(DisasterType))
        
        if severity:
            try:
                severity = DisasterSeverity(severity)
            except ValueError:
                severity = random.choice(list(DisasterSeverity))
        else:
            severity = DisasterSeverity.HIGH  # Default to high for demo
        
        # Select affected nodes (focus on Mumbai for demo)
        affected_nodes = ["power_grid_mumbai", "telecom_mumbai", "transport_mumbai"]
        
        # Calculate severity multiplier
        severity_multiplier = {
            DisasterSeverity.LOW: 0.3,
            DisasterSeverity.MEDIUM: 0.5,
            DisasterSeverity.HIGH: 0.7,
            DisasterSeverity.EXTREME: 0.9
        }[severity]
        
        # Record disaster event
        if self.replay_engine:
            await self.replay_engine.record_event(
                self.replay_engine.EventType.DISASTER_DETECTED,
                {
                    "disaster_type": disaster_type.value,
                    "severity": severity.value,
                    "affected_nodes": affected_nodes,
                    "severity_multiplier": severity_multiplier,
                    "message": f"DEMO: {disaster_type.value.capitalize()} with {severity.value} severity"
                },
                "disaster_simulator",
                "critical"
            )
        
        # Update infrastructure risk levels dramatically
        if self.execution_engine:
            for node_id in affected_nodes:
                if node_id in self.execution_engine.infrastructure_nodes:
                    # Set very high risk for demo
                    self.execution_engine.infrastructure_nodes[node_id]["risk"] = 0.8 + (random.random() * 0.15)
                    
                    # Set high load
                    capacity = self.execution_engine.infrastructure_nodes[node_id]["capacity"]
                    self.execution_engine.infrastructure_nodes[node_id]["load"] = capacity * (0.85 + (random.random() * 0.1))
        
        # Trigger immediate autonomous response
        await self._trigger_autonomous_response(affected_nodes, severity_multiplier)
        
        return {
            "disaster_type": disaster_type.value,
            "severity": severity.value,
            "affected_nodes": affected_nodes,
            "severity_multiplier": severity_multiplier,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_simulation_status(self) -> Dict[str, Any]:
        """Get current simulation status"""
        return {
            "simulation_active": self.simulation_active,
            "last_disaster_time": self.last_disaster_time.isoformat() if self.last_disaster_time else None,
            "disaster_interval_minutes": self.disaster_interval_minutes,
            "next_disaster_in_minutes": (
                ((self.last_disaster_time + timedelta(minutes=self.disaster_interval_minutes)) - datetime.now()).total_seconds() / 60
                if self.last_disaster_time else 0
            ),
            "infrastructure_nodes": len(self.infrastructure_nodes),
            "timestamp": datetime.now().isoformat()
        }

# Global disaster simulation loop
disaster_simulation_loop = DisasterSimulationLoop()
