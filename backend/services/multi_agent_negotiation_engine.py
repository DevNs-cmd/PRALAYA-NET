"""
Autonomous Multi-Agent Negotiation Engine
Distributed response agents with risk-weighted priority arbitration
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import defaultdict

class AgentType(Enum):
    POWER_GRID = "power_grid"
    TELECOM = "telecom"
    TRANSPORT = "transport"
    MEDICAL_LOGISTICS = "medical_logistics"
    DRONE_COMMAND = "drone_command"

class TaskStatus(Enum):
    PENDING = "pending"
    NEGOTIATING = "negotiating"
    ASSIGNED = "assigned"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentStatus(Enum):
    IDLE = "idle"
    NEGOTIATING = "negotiating"
    ASSIGNED = "assigned"
    EXECUTING = "executing"
    UNAVAILABLE = "unavailable"

@dataclass
class ResourceRequirement:
    resource_type: str
    quantity: float
    priority: int
    urgency: float  # 0-1

@dataclass
class Task:
    task_id: str
    task_type: str
    infrastructure_node: str
    risk_level: float
    resource_requirements: List[ResourceRequirement]
    deadline: datetime
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    negotiation_rounds: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "infrastructure_node": self.infrastructure_node,
            "risk_level": self.risk_level,
            "resource_requirements": [
                {
                    "resource_type": req.resource_type,
                    "quantity": req.quantity,
                    "priority": req.priority,
                    "urgency": req.urgency
                } for req in self.resource_requirements
            ],
            "deadline": self.deadline.isoformat(),
            "status": self.status.value,
            "assigned_agent": self.assigned_agent,
            "created_at": self.created_at.isoformat(),
            "negotiation_rounds": self.negotiation_rounds
        }

@dataclass
class AgentBid:
    bid_id: str
    agent_id: str
    task_id: str
    capability_match_score: float  # 0-1
    proximity_score: float  # 0-1
    resource_availability_score: float  # 0-1
    estimated_completion_time: int  # minutes
    confidence_level: float  # 0-1
    bid_amount: float  # priority points
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "bid_id": self.bid_id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "capability_match_score": self.capability_match_score,
            "proximity_score": self.proximity_score,
            "resource_availability_score": self.resource_availability_score,
            "estimated_completion_time": self.estimated_completion_time,
            "confidence_level": self.confidence_level,
            "bid_amount": self.bid_amount,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class AutonomousAgent:
    agent_id: str
    agent_type: AgentType
    capabilities: List[str]
    location: Dict[str, float]  # lat, lon
    resources: Dict[str, float]
    max_capacity: float
    current_load: float
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    performance_history: List[float] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "capabilities": self.capabilities,
            "location": self.location,
            "resources": self.resources,
            "max_capacity": self.max_capacity,
            "current_load": self.current_load,
            "status": self.status.value,
            "current_task": self.current_task,
            "performance_score": np.mean(self.performance_history) if self.performance_history else 0.0
        }

class MultiAgentNegotiationEngine:
    """Distributed multi-agent negotiation with risk-weighted priority arbitration"""
    
    def __init__(self):
        self.agents: Dict[str, AutonomousAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.active_bids: Dict[str, List[AgentBid]] = defaultdict(list)
        self.negotiation_history: List[Dict[str, Any]] = []
        self.arbitration_decisions: List[Dict[str, Any]] = []
        
        # Initialize agents
        self._initialize_agents()
        
        # Start background negotiation
        asyncio.create_task(self._continuous_negotiation())
        asyncio.create_task(self._task_monitoring())
    
    def _initialize_agents(self):
        """Initialize distributed response agents"""
        # Power Grid Agent
        self.agents["power_grid_001"] = AutonomousAgent(
            agent_id="power_grid_001",
            agent_type=AgentType.POWER_GRID,
            capabilities=["load_redistribution", "backup_activation", "grid_isolation", "emergency_rerouting"],
            location={"lat": 19.0760, "lon": 72.8777},  # Mumbai
            resources={"power_capacity": 1000, "technicians": 50},
            max_capacity=1000,
            current_load=300
        )
        
        # Power Grid Agent - Delhi
        self.agents["power_grid_002"] = AutonomousAgent(
            agent_id="power_grid_002",
            agent_type=AgentType.POWER_GRID,
            capabilities=["load_redistribution", "backup_activation", "grid_isolation"],
            location={"lat": 28.7041, "lon": 77.1025},  # Delhi
            resources={"power_capacity": 1200, "technicians": 60},
            max_capacity=1200,
            current_load=400
        )
        
        # Telecom Agent
        self.agents["telecom_001"] = AutonomousAgent(
            agent_id="telecom_001",
            agent_type=AgentType.TELECOM,
            capabilities=["backup_switching", "emergency_rerouting", "bandwidth_reallocation"],
            location={"lat": 19.0760, "lon": 72.8777},  # Mumbai
            resources={"bandwidth": 500, "technicians": 30},
            max_capacity=500,
            current_load=200
        )
        
        # Telecom Agent - Delhi
        self.agents["telecom_002"] = AutonomousAgent(
            agent_id="telecom_002",
            agent_type=AgentType.TELECOM,
            capabilities=["backup_switching", "emergency_rerouting"],
            location={"lat": 28.7041, "lon": 77.1025},  # Delhi
            resources={"bandwidth": 600, "technicians": 35},
            max_capacity=600,
            current_load=250
        )
        
        # Transport Agent
        self.agents["transport_001"] = AutonomousAgent(
            agent_id="transport_001",
            agent_type=AgentType.TRANSPORT,
            capabilities=["corridor_opening", "emergency_routing", "traffic_management"],
            location={"lat": 19.0760, "lon": 72.8777},  # Mumbai
            resources={"vehicles": 100, "personnel": 80},
            max_capacity=100,
            current_load=40
        )
        
        # Transport Agent - Delhi
        self.agents["transport_002"] = AutonomousAgent(
            agent_id="transport_002",
            agent_type=AgentType.TRANSPORT,
            capabilities=["corridor_opening", "emergency_routing"],
            location={"lat": 28.7041, "lon": 77.1025},  # Delhi
            resources={"vehicles": 120, "personnel": 90},
            max_capacity=120,
            current_load=50
        )
        
        # Medical Logistics Agent
        self.agents["medical_001"] = AutonomousAgent(
            agent_id="medical_001",
            agent_type=AgentType.MEDICAL_LOGISTICS,
            capabilities=["patient_transport", "medical_supply_delivery", "hospital_coordination"],
            location={"lat": 19.0760, "lon": 72.8777},  # Mumbai
            resources={"ambulances": 50, "medical_supplies": 1000},
            max_capacity=50,
            current_load=20
        )
        
        # Medical Logistics Agent - Delhi
        self.agents["medical_002"] = AutonomousAgent(
            agent_id="medical_002",
            agent_type=AgentType.MEDICAL_LOGISTICS,
            capabilities=["patient_transport", "medical_supply_delivery"],
            location={"lat": 28.7041, "lon": 77.1025},  # Delhi
            resources={"ambulances": 60, "medical_supplies": 1200},
            max_capacity=60,
            current_load=25
        )
        
        # Drone Command Agent
        self.agents["drone_command_001"] = AutonomousAgent(
            agent_id="drone_command_001",
            agent_type=AgentType.DRONE_COMMAND,
            capabilities=["surveillance", "search_rescue", "delivery", "assessment"],
            location={"lat": 19.0760, "lon": 72.8777},  # Mumbai
            resources={"drones": 20, "operators": 15},
            max_capacity=20,
            current_load=8
        )
        
        # Drone Command Agent - Delhi
        self.agents["drone_command_002"] = AutonomousAgent(
            agent_id="drone_command_002",
            agent_type=AgentType.DRONE_COMMAND,
            capabilities=["surveillance", "search_rescue", "delivery"],
            location={"lat": 28.7041, "lon": 77.1025},  # Delhi
            resources={"drones": 25, "operators": 18},
            max_capacity=25,
            current_load=10
        )
    
    async def _continuous_negotiation(self):
        """Continuous negotiation process"""
        while True:
            try:
                # Process pending tasks
                await self._process_pending_tasks()
                
                # Collect bids
                await self._collect_bids()
                
                # Arbitrate and assign tasks
                await self._arbitrate_tasks()
                
                # Monitor task execution
                await self._monitor_execution()
                
                await asyncio.sleep(5)  # Process every 5 seconds
                
            except Exception as e:
                print(f"Negotiation error: {str(e)}")
                await asyncio.sleep(10)
    
    async def _process_pending_tasks(self):
        """Process tasks awaiting negotiation"""
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.NEGOTIATING
                task.negotiation_rounds = 1
                
                # Notify agents of new task
                await self._notify_agents_of_task(task)
    
    async def _notify_agents_of_task(self, task: Task):
        """Notify capable agents of new task"""
        capable_agents = []
        
        for agent in self.agents.values():
            if agent.status == AgentStatus.IDLE:
                # Check if agent has relevant capabilities
                if self._agent_can_handle_task(agent, task):
                    capable_agents.append(agent)
        
        # Agents will submit bids in the next cycle
        for agent in capable_agents:
            await self._generate_agent_bid(agent, task)
    
    def _agent_can_handle_task(self, agent: AutonomousAgent, task: Task) -> bool:
        """Check if agent can handle the task"""
        # Simple capability matching
        task_capabilities = {
            "power_stabilization": ["load_redistribution", "backup_activation"],
            "telecom_restoration": ["backup_switching", "emergency_rerouting"],
            "transport_management": ["corridor_opening", "emergency_routing"],
            "medical_response": ["patient_transport", "medical_supply_delivery"],
            "surveillance": ["surveillance", "assessment"]
        }
        
        required_capabilities = task_capabilities.get(task.task_type, [])
        return any(cap in agent.capabilities for cap in required_capabilities)
    
    async def _generate_agent_bid(self, agent: AutonomousAgent, task: Task):
        """Generate bid from agent for task"""
        # Calculate capability match score
        capability_match = self._calculate_capability_match(agent, task)
        
        # Calculate proximity score
        proximity_score = self._calculate_proximity_score(agent, task)
        
        # Calculate resource availability
        resource_score = self._calculate_resource_availability(agent, task)
        
        # Calculate estimated completion time
        completion_time = self._estimate_completion_time(agent, task)
        
        # Calculate confidence level
        confidence = (capability_match + proximity_score + resource_score) / 3
        
        # Calculate bid amount (risk-weighted priority)
        bid_amount = confidence * task.risk_level * 100
        
        bid = AgentBid(
            bid_id=f"bid_{uuid.uuid4().hex[:12]}",
            agent_id=agent.agent_id,
            task_id=task.task_id,
            capability_match_score=capability_match,
            proximity_score=proximity_score,
            resource_availability_score=resource_score,
            estimated_completion_time=completion_time,
            confidence_level=confidence,
            bid_amount=bid_amount
        )
        
        self.active_bids[task.task_id].append(bid)
    
    def _calculate_capability_match(self, agent: AutonomousAgent, task: Task) -> float:
        """Calculate capability match score"""
        task_capabilities = {
            "power_stabilization": ["load_redistribution", "backup_activation", "grid_isolation"],
            "telecom_restoration": ["backup_switching", "emergency_rerouting", "bandwidth_reallocation"],
            "transport_management": ["corridor_opening", "emergency_routing", "traffic_management"],
            "medical_response": ["patient_transport", "medical_supply_delivery", "hospital_coordination"],
            "surveillance": ["surveillance", "search_rescue", "assessment"]
        }
        
        required_capabilities = task_capabilities.get(task.task_type, [])
        matching_capabilities = [cap for cap in required_capabilities if cap in agent.capabilities]
        
        return len(matching_capabilities) / max(len(required_capabilities), 1)
    
    def _calculate_proximity_score(self, agent: AutonomousAgent, task: Task) -> float:
        """Calculate proximity score based on agent location and task location"""
        # Simple distance calculation (would use real geodesic distance in production)
        task_locations = {
            "power_grid_mumbai": {"lat": 19.0760, "lon": 72.8777},
            "power_grid_delhi": {"lat": 28.7041, "lon": 77.1025},
            "telecom_mumbai": {"lat": 19.0760, "lon": 72.8777},
            "telecom_delhi": {"lat": 28.7041, "lon": 77.1025},
            "transport_mumbai": {"lat": 19.0760, "lon": 72.8777},
            "transport_delhi": {"lat": 28.7041, "lon": 77.1025},
            "medical_mumbai": {"lat": 19.0760, "lon": 72.8777},
            "medical_delhi": {"lat": 28.7041, "lon": 77.1025}
        }
        
        task_location = task_locations.get(task.infrastructure_node, {"lat": 19.0760, "lon": 72.8777})
        
        # Simple Euclidean distance (normalized)
        lat_diff = abs(agent.location["lat"] - task_location["lat"])
        lon_diff = abs(agent.location["lon"] - task_location["lon"])
        distance = np.sqrt(lat_diff**2 + lon_diff**2)
        
        # Convert to proximity score (closer = higher score)
        return max(0, 1 - distance / 10)  # Normalize by max expected distance
    
    def _calculate_resource_availability(self, agent: AutonomousAgent, task: Task) -> float:
        """Calculate resource availability score"""
        # Check if agent has sufficient resources
        availability_ratio = (agent.max_capacity - agent.current_load) / agent.max_capacity
        
        # Factor in resource requirements
        if task.resource_requirements:
            total_required = sum(req.quantity for req in task.resource_requirements)
            available_resources = sum(agent.resources.values())
            resource_ratio = min(1, available_resources / max(total_required, 1))
        else:
            resource_ratio = 1.0
        
        return (availability_ratio + resource_ratio) / 2
    
    def _estimate_completion_time(self, agent: AutonomousAgent, task: Task) -> int:
        """Estimate task completion time in minutes"""
        base_time = {
            "power_stabilization": 30,
            "telecom_restoration": 20,
            "transport_management": 25,
            "medical_response": 15,
            "surveillance": 45
        }
        
        base = base_time.get(task.task_type, 30)
        
        # Adjust based on agent performance
        performance_factor = 1.0
        if agent.performance_history:
            avg_performance = np.mean(agent.performance_history)
            performance_factor = 2.0 - avg_performance  # Better performance = less time
        
        # Adjust based on current load
        load_factor = 1 + (agent.current_load / agent.max_capacity)
        
        return int(base * performance_factor * load_factor)
    
    async def _collect_bids(self):
        """Collect bids from agents for negotiating tasks"""
        # Bids are generated in _notify_agents_of_task
        pass
    
    async def _arbitrate_tasks(self):
        """Arbitrate tasks using risk-weighted priority"""
        for task_id, bids in self.active_bids.items():
            if len(bids) >= 2 and self.tasks[task_id].status == TaskStatus.NEGOTIATING:
                # Perform arbitration
                winning_bid = await self._risk_weighted_arbitration(task_id, bids)
                
                if winning_bid:
                    # Assign task to winning agent
                    await self._assign_task_to_agent(task_id, winning_bid)
    
    async def _risk_weighted_arbitration(self, task_id: str, bids: List[AgentBid]) -> Optional[AgentBid]:
        """Risk-weighted priority arbitration"""
        task = self.tasks[task_id]
        
        # Calculate weighted scores
        for bid in bids:
            # Weight by risk level, capability, and confidence
            weighted_score = (
                bid.bid_amount * 0.4 +  # Risk-weighted priority
                bid.capability_match_score * 0.3 +  # Capability
                bid.confidence_level * 0.3  # Confidence
            )
            bid.bid_amount = weighted_score
        
        # Select winning bid
        winning_bid = max(bids, key=lambda b: b.bid_amount)
        
        # Record arbitration decision
        decision = {
            "task_id": task_id,
            "winning_bid": winning_bid.to_dict(),
            "all_bids": [bid.to_dict() for bid in bids],
            "arbitration_method": "risk_weighted_priority",
            "timestamp": datetime.now().isoformat()
        }
        
        self.arbitration_decisions.append(decision)
        
        return winning_bid
    
    async def _assign_task_to_agent(self, task_id: str, bid: AgentBid):
        """Assign task to winning agent"""
        task = self.tasks[task_id]
        agent = self.agents[bid.agent_id]
        
        # Update task
        task.status = TaskStatus.ASSIGNED
        task.assigned_agent = bid.agent_id
        
        # Update agent
        agent.status = AgentStatus.ASSIGNED
        agent.current_task = task_id
        agent.current_load += 10  # Increment load
        
        # Start execution
        execution_time = self._estimate_completion_time(agent, task)
        await self._start_task_execution(task, agent, execution_time)
    
    async def _start_task_execution(self, task: Task, agent: AutonomousAgent, execution_time: int):
        """Start task execution"""
        task.status = TaskStatus.EXECUTING
        agent.status = AgentStatus.EXECUTING
        
        # Schedule completion
        asyncio.create_task(self._complete_task_execution(task, agent, execution_time))
    
    async def _complete_task_execution(self, task: Task, agent: AutonomousAgent, execution_time: int):
        """Complete task execution"""
        await asyncio.sleep(execution_time)
        
        # Update task
        task.status = TaskStatus.COMPLETED
        
        # Update agent
        agent.status = AgentStatus.IDLE
        agent.current_task = None
        agent.current_load = max(0, agent.current_load - 10)
        
        # Record performance
        performance_score = np.random.uniform(0.7, 1.0)  # Simulated performance
        agent.performance_history.append(performance_score)
        
        # Keep only recent performance history
        if len(agent.performance_history) > 20:
            agent.performance_history = agent.performance_history[-20:]
        
        # Clear bids for this task
        if task.task_id in self.active_bids:
            del self.active_bids[task.task_id]
    
    async def _monitor_execution(self):
        """Monitor task execution and handle failures"""
        for task in self.tasks.values():
            if task.status == TaskStatus.EXECUTING:
                # Check for timeout
                if datetime.now() > task.deadline:
                    task.status = TaskStatus.FAILED
                    
                    # Update agent
                    if task.assigned_agent and task.assigned_agent in self.agents:
                        agent = self.agents[task.assigned_agent]
                        agent.status = AgentStatus.IDLE
                        agent.current_task = None
                        agent.current_load = max(0, agent.current_load - 10)
    
    async def _task_monitoring(self):
        """Background task monitoring"""
        while True:
            try:
                # Clean up old tasks
                await self._cleanup_old_tasks()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Task monitoring error: {str(e)}")
                await asyncio.sleep(120)
    
    async def _cleanup_old_tasks(self):
        """Clean up old completed tasks"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        old_tasks = [
            task_id for task_id, task in self.tasks.items()
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and 
            task.created_at < cutoff_time
        ]
        
        for task_id in old_tasks:
            del self.tasks[task_id]
    
    def create_task(self, task_type: str, infrastructure_node: str, risk_level: float, 
                   resource_requirements: List[Dict[str, Any]]) -> str:
        """Create new task for negotiation"""
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        
        # Convert resource requirements
        requirements = [
            ResourceRequirement(
                resource_type=req["resource_type"],
                quantity=req["quantity"],
                priority=req.get("priority", 1),
                urgency=req.get("urgency", 0.5)
            )
            for req in resource_requirements
        ]
        
        task = Task(
            task_id=task_id,
            task_type=task_type,
            infrastructure_node=infrastructure_node,
            risk_level=risk_level,
            resource_requirements=requirements,
            deadline=datetime.now() + timedelta(hours=6)
        )
        
        self.tasks[task_id] = task
        return task_id
    
    def get_agent_status(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        return [agent.to_dict() for agent in self.agents.values()]
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get active tasks"""
        return [task.to_dict() for task in self.tasks.values() 
                if task.status in [TaskStatus.PENDING, TaskStatus.NEGOTIATING, TaskStatus.ASSIGNED, TaskStatus.EXECUTING]]
    
    def get_negotiation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get negotiation history"""
        return self.arbitration_decisions[-limit:] if self.arbitration_decisions else []
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        total_agents = len(self.agents)
        available_agents = len([a for a in self.agents.values() if a.status == AgentStatus.IDLE])
        active_tasks = len(self.get_active_tasks())
        
        # Calculate average performance
        all_performances = []
        for agent in self.agents.values():
            if agent.performance_history:
                all_performances.extend(agent.performance_history)
        
        avg_performance = np.mean(all_performances) if all_performances else 0.0
        
        return {
            "total_agents": total_agents,
            "available_agents": available_agents,
            "active_tasks": active_tasks,
            "average_agent_performance": avg_performance,
            "total_negotiations": len(self.arbitration_decisions),
            "success_rate": 0.85  # Simulated success rate
        }

# Global multi-agent negotiation engine
multi_agent_negotiation_engine = MultiAgentNegotiationEngine()
