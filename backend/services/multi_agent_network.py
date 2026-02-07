"""
Multi-Agent Autonomous Response Network
Distributed agents for drones, rescue teams, medical units, infrastructure nodes, and supply chains
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json

class AgentType(Enum):
    DRONE = "drone"
    RESCUE_TEAM = "rescue_team"
    MEDICAL_UNIT = "medical_unit"
    INFRASTRUCTURE_NODE = "infrastructure_node"
    SUPPLY_CHAIN = "supply_chain"
    COMMUNICATION_NODE = "communication_node"

class AgentStatus(Enum):
    IDLE = "idle"
    DEPLOYING = "deploying"
    ACTIVE = "active"
    RETURNING = "returning"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

class TaskPriority(Enum):
    CRITICAL = 5    # Life-threatening situations
    HIGH = 4        # Infrastructure collapse
    MEDIUM = 3      # Evacuation and rescue
    LOW = 2         # Supply and support
    ROUTINE = 1     # Maintenance and monitoring

class TaskType(Enum):
    SEARCH_RESCUE = "search_rescue"
    MEDICAL_RESPONSE = "medical_response"
    INFRASTRUCTURE_ASSESSMENT = "infrastructure_assessment"
    SUPPLY_DELIVERY = "supply_delivery"
    EVACUATION_SUPPORT = "evacuation_support"
    COMMUNICATION_RELAY = "communication_relay"
    SURVEILLANCE = "surveillance"

@dataclass
class Task:
    task_id: str
    task_type: TaskType
    priority: TaskPriority
    location: Dict  # lat, lon, altitude if applicable
    requirements: Dict[str, Any]  # Special requirements
    estimated_duration_minutes: int
    risk_level: float  # 0-1
    created_at: datetime
    deadline: Optional[datetime] = None
    assigned_agent_id: Optional[str] = None
    status: str = "pending"

@dataclass
class AgentCapability:
    capability_type: str
    proficiency: float  # 0-1
    availability: float  # 0-1
    cost_per_hour: float

@dataclass
class Agent:
    agent_id: str
    agent_type: AgentType
    name: str
    location: Dict  # lat, lon, altitude if applicable
    status: AgentStatus
    capabilities: List[AgentCapability]
    current_task: Optional[Task] = None
    task_history: List[Task] = field(default_factory=list)
    communication_range: float = 10.0  # km
    max_speed: float = 50.0  # km/h
    battery_level: float = 100.0  # percentage
    last_heartbeat: datetime = field(default_factory=datetime.now)

class NegotiationProtocol:
    """Risk-weighted priority arbitration for task allocation"""
    
    def __init__(self):
        self.negotiation_history: List[Dict] = []
        self.risk_weights = {
            TaskPriority.CRITICAL: 1.0,
            TaskPriority.HIGH: 0.8,
            TaskPriority.MEDIUM: 0.6,
            TaskPriority.LOW: 0.4,
            TaskPriority.ROUTINE: 0.2
        }
    
    async def negotiate_task_allocation(self, agents: List[Agent], tasks: List[Task]) -> Dict[str, str]:
        """Negotiate task allocation among agents using risk-weighted priority"""
        
        allocation_result = {}
        available_agents = [agent for agent in agents if agent.status == AgentStatus.IDLE]
        
        # Sort tasks by risk-weighted priority
        sorted_tasks = sorted(tasks, key=lambda t: self._calculate_task_priority(t), reverse=True)
        
        for task in sorted_tasks:
            if not available_agents:
                break
            
            # Find best agent for this task
            best_agent = await self._find_best_agent(task, available_agents)
            
            if best_agent:
                allocation_result[task.task_id] = best_agent.agent_id
                best_agent.current_task = task
                best_agent.status = AgentStatus.DEPLOYING
                available_agents.remove(best_agent)
                
                # Log negotiation
                self.negotiation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "task_id": task.task_id,
                    "agent_id": best_agent.agent_id,
                    "negotiation_score": self._calculate_negotiation_score(task, best_agent)
                })
        
        return allocation_result
    
    def _calculate_task_priority(self, task: Task) -> float:
        """Calculate risk-weighted priority for task"""
        base_priority = task.priority.value
        risk_weight = self.risk_weights.get(task.priority, 0.5)
        urgency_factor = 1.0
        
        # Add urgency factor if deadline is approaching
        if task.deadline:
            time_remaining = (task.deadline - datetime.now()).total_seconds() / 3600
            if time_remaining < 2:  # Less than 2 hours
                urgency_factor = 2.0
            elif time_remaining < 6:  # Less than 6 hours
                urgency_factor = 1.5
        
        return base_priority * risk_weight * urgency_factor
    
    async def _find_best_agent(self, task: Task, available_agents: List[Agent]) -> Optional[Agent]:
        """Find best agent for task based on capability and proximity"""
        
        best_agent = None
        best_score = 0.0
        
        for agent in available_agents:
            score = await self._calculate_agent_task_score(agent, task)
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent
    
    async def _calculate_agent_task_score(self, agent: Agent, task: Task) -> float:
        """Calculate compatibility score between agent and task"""
        
        # Capability matching score
        capability_score = 0.0
        for capability in agent.capabilities:
            if self._capability_matches_task(capability.capability_type, task.task_type):
                capability_score = max(capability_score, capability.proficiency * capability.availability)
        
        # Proximity score (closer is better)
        distance = self._calculate_distance(agent.location, task.location)
        proximity_score = max(0, 1.0 - (distance / agent.communication_range))
        
        # Battery level score
        battery_score = agent.battery_level / 100.0
        
        # Task-specific scoring
        task_score = 0.0
        if task.task_type == TaskType.SEARCH_RESCUE and agent.agent_type == AgentType.DRONE:
            task_score = 0.9
        elif task.task_type == TaskType.MEDICAL_RESPONSE and agent.agent_type == AgentType.MEDICAL_UNIT:
            task_score = 0.9
        elif task.task_type == TaskType.INFRASTRUCTURE_ASSESSMENT and agent.agent_type == AgentType.DRONE:
            task_score = 0.8
        elif task.task_type == TaskType.SUPPLY_DELIVERY and agent.agent_type == AgentType.SUPPLY_CHAIN:
            task_score = 0.8
        
        # Weighted combination
        total_score = (
            capability_score * 0.4 +
            proximity_score * 0.3 +
            battery_score * 0.2 +
            task_score * 0.1
        )
        
        return total_score
    
    def _capability_matches_task(self, capability_type: str, task_type: TaskType) -> bool:
        """Check if agent capability matches task requirements"""
        capability_task_map = {
            "surveillance": [TaskType.SURVEILLANCE, TaskType.INFRASTRUCTURE_ASSESSMENT],
            "search": [TaskType.SEARCH_RESCUE],
            "medical": [TaskType.MEDICAL_RESPONSE],
            "transport": [TaskType.SUPPLY_DELIVERY, TaskType.EVACUATION_SUPPORT],
            "communication": [TaskType.COMMUNICATION_RELAY],
            "repair": [TaskType.INFRASTRUCTURE_ASSESSMENT]
        }
        
        return task_type in capability_task_map.get(capability_type, [])
    
    def _calculate_distance(self, location1: Dict, location2: Dict) -> float:
        """Calculate distance between two locations"""
        lat1, lon1 = location1.get("lat", 0), location1.get("lon", 0)
        lat2, lon2 = location2.get("lat", 0), location2.get("lon", 0)
        
        # Simple distance calculation (in km)
        return np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111

class MultiAgentNetwork:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.negotiation_protocol = NegotiationProtocol()
        self.task_queue: List[Task] = []
        self.allocation_history: List[Dict] = []
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize autonomous agents"""
        
        # Initialize drone agents
        for i in range(5):
            drone = Agent(
                agent_id=f"drone_{i+1:03d}",
                agent_type=AgentType.DRONE,
                name=f"Search Drone {i+1}",
                location={
                    "lat": 19.0760 + np.random.uniform(-0.5, 0.5),
                    "lon": 72.8777 + np.random.uniform(-0.5, 0.5),
                    "altitude": 100
                },
                status=AgentStatus.IDLE,
                capabilities=[
                    AgentCapability("surveillance", 0.9, 0.8, 500),
                    AgentCapability("search", 0.8, 0.9, 600),
                    AgentCapability("communication", 0.7, 0.7, 400)
                ],
                communication_range=15.0,
                max_speed=80.0,
                battery_level=np.random.uniform(60, 100)
            )
            self.agents[drone.agent_id] = drone
        
        # Initialize rescue team agents
        for i in range(3):
            team = Agent(
                agent_id=f"rescue_team_{i+1:03d}",
                agent_type=AgentType.RESCUE_TEAM,
                name=f"Rescue Team {i+1}",
                location={
                    "lat": 19.0760 + np.random.uniform(-1.0, 1.0),
                    "lon": 72.8777 + np.random.uniform(-1.0, 1.0)
                },
                status=AgentStatus.IDLE,
                capabilities=[
                    AgentCapability("search", 0.9, 0.8, 200),
                    AgentCapability("transport", 0.8, 0.9, 150),
                    AgentCapability("medical_basic", 0.6, 0.7, 100)
                ],
                communication_range=20.0,
                max_speed=60.0,
                battery_level=np.random.uniform(70, 100)
            )
            self.agents[team.agent_id] = team
        
        # Initialize medical unit agents
        for i in range(2):
            medical = Agent(
                agent_id=f"medical_unit_{i+1:03d}",
                agent_type=AgentType.MEDICAL_UNIT,
                name=f"Medical Unit {i+1}",
                location={
                    "lat": 19.0760 + np.random.uniform(-0.8, 0.8),
                    "lon": 72.8777 + np.random.uniform(-0.8, 0.8)
                },
                status=AgentStatus.IDLE,
                capabilities=[
                    AgentCapability("medical", 0.9, 0.9, 300),
                    AgentCapability("transport", 0.7, 0.8, 200),
                    AgentCapability("triage", 0.8, 0.8, 250)
                ],
                communication_range=15.0,
                max_speed=50.0,
                battery_level=np.random.uniform(80, 100)
            )
            self.agents[medical.agent_id] = medical
        
        # Initialize supply chain agents
        for i in range(3):
            supply = Agent(
                agent_id=f"supply_chain_{i+1:03d}",
                agent_type=AgentType.SUPPLY_CHAIN,
                name=f"Supply Chain {i+1}",
                location={
                    "lat": 19.0760 + np.random.uniform(-1.2, 1.2),
                    "lon": 72.8777 + np.random.uniform(-1.2, 1.2)
                },
                status=AgentStatus.IDLE,
                capabilities=[
                    AgentCapability("transport", 0.9, 0.8, 100),
                    AgentCapability("logistics", 0.8, 0.9, 150),
                    AgentCapability("distribution", 0.7, 0.8, 120)
                ],
                communication_range=25.0,
                max_speed=70.0,
                battery_level=np.random.uniform(60, 100)
            )
            self.agents[supply.agent_id] = supply
    
    async def create_task(self,
                        task_type: TaskType,
                        priority: TaskPriority,
                        location: Dict,
                        requirements: Dict[str, Any],
                        estimated_duration_minutes: int,
                        risk_level: float = 0.5,
                        deadline_hours: Optional[int] = None) -> str:
        """Create a new task for agent allocation"""
        
        task_id = f"task_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        deadline = None
        if deadline_hours:
            deadline = datetime.now() + timedelta(hours=deadline_hours)
        
        task = Task(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            location=location,
            requirements=requirements,
            estimated_duration_minutes=estimated_duration_minutes,
            risk_level=risk_level,
            created_at=datetime.now(),
            deadline=deadline
        )
        
        self.tasks[task_id] = task
        self.task_queue.append(task)
        
        # Trigger task allocation
        await self._allocate_tasks()
        
        return task_id
    
    async def _allocate_tasks(self):
        """Allocate tasks to agents using negotiation protocol"""
        if not self.task_queue:
            return
        
        available_agents = [agent for agent in self.agents.values() if agent.status == AgentStatus.IDLE]
        
        if not available_agents:
            return
        
        # Negotiate task allocation
        allocation_result = await self.negotiation_protocol.negotiate_task_allocation(
            available_agents, self.task_queue
        )
        
        # Update task assignments
        for task_id, agent_id in allocation_result.items():
            if task_id in self.tasks:
                self.tasks[task_id].assigned_agent_id = agent_id
                self.tasks[task_id].status = "assigned"
            
            if agent_id in self.agents:
                self.agents[agent_id].current_task = self.tasks[task_id]
                self.agents[agent_id].status = AgentStatus.DEPLOYING
        
        # Remove allocated tasks from queue
        self.task_queue = [task for task in self.task_queue if task.status == "pending"]
        
        # Record allocation
        self.allocation_history.append({
            "timestamp": datetime.now().isoformat(),
            "allocations": allocation_result,
            "available_agents": len(available_agents),
            "total_tasks": len(self.tasks)
        })
    
    async def complete_task(self, task_id: str, agent_id: str, success: bool, outcome: Dict[str, Any]):
        """Mark task as completed and update agent status"""
        
        if task_id in self.tasks and agent_id in self.agents:
            task = self.tasks[task_id]
            agent = self.agents[agent_id]
            
            # Update task status
            task.status = "completed" if success else "failed"
            
            # Update agent
            agent.current_task = None
            agent.status = AgentStatus.IDLE
            agent.task_history.append(task)
            
            # Move task to history
            if len(agent.task_history) > 50:
                agent.task_history = agent.task_history[-50:]
            
            # Trigger reallocation for pending tasks
            await self._allocate_tasks()
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of all agents"""
        agent_status = {}
        
        for agent_id, agent in self.agents.items():
            agent_status[agent_id] = {
                "agent_id": agent_id,
                "agent_type": agent.agent_type.value,
                "name": agent.name,
                "location": agent.location,
                "status": agent.status.value,
                "battery_level": agent.battery_level,
                "current_task": agent.current_task.task_id if agent.current_task else None,
                "capabilities": [
                    {
                        "type": cap.capability_type,
                        "proficiency": cap.proficiency,
                        "availability": cap.availability
                    }
                    for cap in agent.capabilities
                ],
                "last_heartbeat": agent.last_heartbeat.isoformat()
            }
        
        return agent_status
    
    def get_task_status(self) -> Dict[str, Any]:
        """Get current status of all tasks"""
        task_status = {}
        
        for task_id, task in self.tasks.items():
            task_status[task_id] = {
                "task_id": task_id,
                "task_type": task.task_type.value,
                "priority": task.priority.value,
                "location": task.location,
                "status": task.status,
                "risk_level": task.risk_level,
                "assigned_agent_id": task.assigned_agent_id,
                "created_at": task.created_at.isoformat(),
                "deadline": task.deadline.isoformat() if task.deadline else None,
                "estimated_duration_minutes": task.estimated_duration_minutes
            }
        
        return task_status
    
    def get_network_metrics(self) -> Dict[str, Any]:
        """Get network performance metrics"""
        
        total_agents = len(self.agents)
        active_agents = len([a for a in self.agents.values() if a.status in [AgentStatus.ACTIVE, AgentStatus.DEPLOYING]])
        idle_agents = len([a for a in self.agents.values() if a.status == AgentStatus.IDLE])
        
        total_tasks = len(self.tasks)
        completed_tasks = len([t for t in self.tasks.values() if t.status == "completed"])
        failed_tasks = len([t for t in self.tasks.values() if t.status == "failed"])
        
        agent_type_distribution = {}
        for agent in self.agents.values():
            agent_type = agent.agent_type.value
            agent_type_distribution[agent_type] = agent_type_distribution.get(agent_type, 0) + 1
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "idle_agents": idle_agents,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "agent_type_distribution": agent_type_distribution,
            "negotiation_history_count": len(self.negotiation_protocol.negotiation_history),
            "pending_tasks": len(self.task_queue),
            "timestamp": datetime.now().isoformat()
        }

# Global instance
multi_agent_network = MultiAgentNetwork()
