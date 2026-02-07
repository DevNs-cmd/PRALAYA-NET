"""
Multi-Agent Negotiation Protocol
Advanced agent coordination with bidding, arbitration, and coalition formation
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np

class AgentCapability(Enum):
    SURVEILLANCE = "surveillance"
    SEARCH_RESCUE = "search_rescue"
    MEDICAL_RESPONSE = "medical_response"
    INFRASTRUCTURE_REPAIR = "infrastructure_repair"
    TRANSPORT = "transport"
    COMMUNICATION = "communication"
    LOGISTICS = "logistics"
    SECURITY = "security"

class TaskType(Enum):
    SEARCH_RESCUE = "search_rescue"
    MEDICAL_EVACUATION = "medical_evacuation"
    INFRASTRUCTURE_ASSESSMENT = "infrastructure_assessment"
    SUPPLY_DELIVERY = "supply_delivery"
    COMMUNICATION_RELAY = "communication_relay"
    SECURITY_PATROL = "security_patrol"
    EVACUATION_SUPPORT = "evacuation_support"
    DAMAGE_ASSESSMENT = "damage_assessment"

class NegotiationStatus(Enum):
    INITIATED = "initiated"
    BIDDING = "bidding"
    ARBITRATION = "arbitration"
    COALITION_FORMED = "coalition_formed"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentProfile:
    """Agent capability and resource profile"""
    agent_id: str
    agent_type: str
    capabilities: List[AgentCapability]
    capability_scores: Dict[AgentCapability, float]  # 0-1 proficiency
    current_location: Dict[str, float]  # lat, lon, altitude
    energy_level: float  # 0-1
    max_range_km: float
    speed_kmh: float
    payload_capacity: float
    communication_range: float
    current_task: Optional[str] = None
    availability: float = 1.0  # 0-1, 1 is fully available
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": [cap.value for cap in self.capabilities],
            "capability_scores": {cap.value: score for cap, score in self.capability_scores.items()},
            "current_location": self.current_location,
            "energy_level": self.energy_level,
            "max_range_km": self.max_range_km,
            "speed_kmh": self.speed_kmh,
            "payload_capacity": self.payload_capacity,
            "communication_range": self.communication_range,
            "current_task": self.current_task,
            "availability": self.availability
        }

@dataclass
class TaskRequirement:
    """Task requirement specification"""
    task_id: str
    task_type: TaskType
    location: Dict[str, float]
    priority: int  # 1-10, 1 is highest
    urgency: float  # 0-1
    required_capabilities: List[AgentCapability]
    minimum_capability_scores: Dict[AgentCapability, float]
    estimated_duration_minutes: int
    deadline: datetime
    resource_requirements: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "location": self.location,
            "priority": self.priority,
            "urgency": self.urgency,
            "required_capabilities": [cap.value for cap in self.required_capabilities],
            "minimum_capability_scores": {cap.value: score for cap, score in self.minimum_capability_scores.items()},
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "deadline": self.deadline.isoformat(),
            "resource_requirements": self.resource_requirements
        }

@dataclass
class AgentBid:
    """Agent bid for task participation"""
    bid_id: str
    agent_id: str
    task_id: str
    bid_amount: float  # 0-1, higher is better
    capability_match_score: float
    proximity_score: float
    energy_cost: float
    time_to_complete: int  # minutes
    confidence: float
    bid_reasoning: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "bid_id": self.bid_id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "bid_amount": self.bid_amount,
            "capability_match_score": self.capability_match_score,
            "proximity_score": self.proximity_score,
            "energy_cost": self.energy_cost,
            "time_to_complete": self.time_to_complete,
            "confidence": self.confidence,
            "bid_reasoning": self.bid_reasoning,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class Coalition:
    """Agent coalition for task execution"""
    coalition_id: str
    task_id: str
    member_agents: List[str]
    lead_agent: str
    formation_time: datetime
    status: NegotiationStatus
    coordination_protocol: str
    communication_links: List[Dict[str, Any]]
    execution_plan: Dict[str, Any]
    success_probability: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "coalition_id": self.coalition_id,
            "task_id": self.task_id,
            "member_agents": self.member_agents,
            "lead_agent": self.lead_agent,
            "formation_time": self.formation_time.isoformat(),
            "status": self.status.value,
            "coordination_protocol": self.coordination_protocol,
            "communication_links": self.communication_links,
            "execution_plan": self.execution_plan,
            "success_probability": self.success_probability
        }

class MultiAgentNegotiationProtocol:
    """Advanced multi-agent negotiation and coordination system"""
    
    def __init__(self):
        self.agents: Dict[str, AgentProfile] = {}
        self.tasks: Dict[str, TaskRequirement] = {}
        self.active_bids: Dict[str, List[AgentBid]] = {}
        self.coalitions: Dict[str, Coalition] = {}
        self.negotiation_history: List[Dict[str, Any]] = []
        self.agent_performance_history: Dict[str, List[float]] = defaultdict(list)
        
        # Initialize agents
        self._initialize_agents()
        
        # Start background coordination
        asyncio.create_task(self._continuous_coordination())
    
    def _initialize_agents(self):
        """Initialize agent profiles with realistic capabilities"""
        
        # Drone agents
        drone_configs = [
            {
                "id": "drone_surveillance_1",
                "type": "surveillance_drone",
                "capabilities": [AgentCapability.SURVEILLANCE, AgentCapability.COMMUNICATION],
                "capability_scores": {AgentCapability.SURVEILLANCE: 0.9, AgentCapability.COMMUNICATION: 0.7},
                "location": {"lat": 19.0760, "lon": 72.8777, "altitude": 100},
                "max_range": 50, "speed": 60, "payload": 5
            },
            {
                "id": "drone_surveillance_2",
                "type": "surveillance_drone",
                "capabilities": [AgentCapability.SURVEILLANCE, AgentCapability.COMMUNICATION],
                "capability_scores": {AgentCapability.SURVEILLANCE: 0.85, AgentCapability.COMMUNICATION: 0.75},
                "location": {"lat": 19.1260, "lon": 72.9277, "altitude": 100},
                "max_range": 45, "speed": 55, "payload": 5
            },
            {
                "id": "drone_surveillance_3",
                "type": "surveillance_drone",
                "capabilities": [AgentCapability.SURVEILLANCE, AgentCapability.COMMUNICATION],
                "capability_scores": {AgentCapability.SURVEILLANCE: 0.8, AgentCapability.COMMUNICATION: 0.8},
                "location": {"lat": 19.0360, "lon": 72.8377, "altitude": 100},
                "max_range": 55, "speed": 65, "payload": 5
            },
            {
                "id": "drone_search_1",
                "type": "search_drone",
                "capabilities": [AgentCapability.SEARCH_RESCUE, AgentCapability.SURVEILLANCE],
                "capability_scores": {AgentCapability.SEARCH_RESCUE: 0.9, AgentCapability.SURVEILLANCE: 0.7},
                "location": {"lat": 19.1560, "lon": 72.9577, "altitude": 50},
                "max_range": 40, "speed": 50, "payload": 10
            },
            {
                "id": "drone_search_2",
                "type": "search_drone",
                "capabilities": [AgentCapability.SEARCH_RESCUE, AgentCapability.SURVEILLANCE],
                "capability_scores": {AgentCapability.SEARCH_RESCUE: 0.85, AgentCapability.SURVEILLANCE: 0.75},
                "location": {"lat": 19.0060, "lon": 72.8077, "altitude": 50},
                "max_range": 45, "speed": 55, "payload": 10
            }
        ]
        
        # Ground team agents
        ground_configs = [
            {
                "id": "rescue_team_1",
                "type": "rescue_team",
                "capabilities": [AgentCapability.SEARCH_RESCUE, AgentCapability.MEDICAL_RESPONSE, AgentCapability.TRANSPORT],
                "capability_scores": {AgentCapability.SEARCH_RESCUE: 0.9, AgentCapability.MEDICAL_RESPONSE: 0.7, AgentCapability.TRANSPORT: 0.8},
                "location": {"lat": 19.0860, "lon": 72.8877, "altitude": 0},
                "max_range": 20, "speed": 30, "payload": 100
            },
            {
                "id": "rescue_team_2",
                "type": "rescue_team",
                "capabilities": [AgentCapability.SEARCH_RESCUE, AgentCapability.MEDICAL_RESPONSE, AgentCapability.TRANSPORT],
                "capability_scores": {AgentCapability.SEARCH_RESCUE: 0.85, AgentCapability.MEDICAL_RESPONSE: 0.8, AgentCapability.TRANSPORT: 0.7},
                "location": {"lat": 19.1160, "lon": 72.9177, "altitude": 0},
                "max_range": 25, "speed": 35, "payload": 80
            },
            {
                "id": "rescue_team_3",
                "type": "rescue_team",
                "capabilities": [AgentCapability.SEARCH_RESCUE, AgentCapability.MEDICAL_RESPONSE, AgentCapability.SECURITY],
                "capability_scores": {AgentCapability.SEARCH_RESCUE: 0.8, AgentCapability.MEDICAL_RESPONSE: 0.9, AgentCapability.SECURITY: 0.7},
                "location": {"lat": 19.0560, "lon": 72.8577, "altitude": 0},
                "max_range": 15, "speed": 25, "payload": 60
            }
        ]
        
        # Medical unit agents
        medical_configs = [
            {
                "id": "medical_unit_1",
                "type": "medical_unit",
                "capabilities": [AgentCapability.MEDICAL_RESPONSE, AgentCapability.TRANSPORT],
                "capability_scores": {AgentCapability.MEDICAL_RESPONSE: 0.95, AgentCapability.TRANSPORT: 0.6},
                "location": {"lat": 19.1360, "lon": 72.9377, "altitude": 0},
                "max_range": 30, "speed": 40, "payload": 200
            },
            {
                "id": "medical_unit_2",
                "type": "medical_unit",
                "capabilities": [AgentCapability.MEDICAL_RESPONSE, AgentCapability.TRANSPORT],
                "capability_scores": {AgentCapability.MEDICAL_RESPONSE: 0.9, AgentCapability.TRANSPORT: 0.7},
                "location": {"lat": 19.0060, "lon": 72.8077, "altitude": 0},
                "max_range": 25, "speed": 35, "payload": 150
            }
        ]
        
        # Supply chain agents
        supply_configs = [
            {
                "id": "supply_chain_1",
                "type": "supply_vehicle",
                "capabilities": [AgentCapability.LOGISTICS, AgentCapability.TRANSPORT],
                "capability_scores": {AgentCapability.LOGISTICS: 0.9, AgentCapability.TRANSPORT: 0.8},
                "location": {"lat": 19.1460, "lon": 72.9477, "altitude": 0},
                "max_range": 100, "speed": 60, "payload": 500
            },
            {
                "id": "supply_chain_2",
                "type": "supply_vehicle",
                "capabilities": [AgentCapability.LOGISTICS, AgentCapability.TRANSPORT],
                "capability_scores": {AgentCapability.LOGISTICS: 0.85, AgentCapability.TRANSPORT: 0.85},
                "location": {"lat": 19.0260, "lon": 72.8277, "altitude": 0},
                "max_range": 80, "speed": 50, "payload": 400
            },
            {
                "id": "supply_chain_3",
                "type": "supply_vehicle",
                "capabilities": [AgentCapability.LOGISTICS, AgentCapability.INFRASTRUCTURE_REPAIR],
                "capability_scores": {AgentCapability.LOGISTICS: 0.8, AgentCapability.INFRASTRUCTURE_REPAIR: 0.7},
                "location": {"lat": 19.1660, "lon": 72.9677, "altitude": 0},
                "max_range": 70, "speed": 45, "payload": 300
            }
        ]
        
        # Create all agents
        all_configs = drone_configs + ground_configs + medical_configs + supply_configs
        
        for config in all_configs:
            agent = AgentProfile(
                agent_id=config["id"],
                agent_type=config["type"],
                capabilities=config["capabilities"],
                capability_scores=config["capability_scores"],
                current_location=config["location"],
                energy_level=np.random.uniform(0.7, 1.0),
                max_range_km=config["max_range"],
                speed_kmh=config["speed"],
                payload_capacity=config["payload"],
                communication_range=10.0  # Standard communication range
            )
            self.agents[agent.agent_id] = agent
    
    async def _continuous_coordination(self):
        """Continuous background coordination"""
        while True:
            try:
                # Update agent availability
                await self._update_agent_availability()
                
                # Process pending negotiations
                await self._process_pending_negotiations()
                
                # Monitor coalition performance
                await self._monitor_coalition_performance()
                
                await asyncio.sleep(10)  # Coordinate every 10 seconds
                
            except Exception as e:
                print(f"Coordination error: {str(e)}")
                await asyncio.sleep(30)
    
    async def _update_agent_availability(self):
        """Update agent availability based on energy and current tasks"""
        for agent in self.agents.values():
            # Energy consumption
            if agent.current_task:
                agent.energy_level *= 0.995  # Gradual energy consumption
            else:
                agent.energy_level = min(1.0, agent.energy_level + 0.01)  # Slow recovery
            
            # Availability calculation
            energy_factor = agent.energy_level
            task_factor = 0.3 if agent.current_task else 1.0
            agent.availability = energy_factor * task_factor
    
    async def _process_pending_negotiations(self):
        """Process pending negotiations and form coalitions"""
        for task_id, bids in self.active_bids.items():
            if len(bids) >= 2:  # Minimum bids for coalition
                await self._arbitrate_and_form_coalition(task_id, bids)
    
    async def _monitor_coalition_performance(self):
        """Monitor coalition performance and update agent performance history"""
        for coalition in self.coalitions.values():
            if coalition.status == NegotiationStatus.EXECUTING:
                # Simulate performance monitoring
                performance_score = np.random.uniform(0.6, 1.0)
                
                for agent_id in coalition.member_agents:
                    self.agent_performance_history[agent_id].append(performance_score)
                    
                    # Keep only recent performance history
                    if len(self.agent_performance_history[agent_id]) > 100:
                        self.agent_performance_history[agent_id] = self.agent_performance_history[agent_id][-100:]
    
    async def create_task(self, task_data: Dict[str, Any]) -> str:
        """Create new task and initiate negotiation"""
        try:
            task = TaskRequirement(
                task_id=task_data.get("task_id", f"task_{uuid.uuid4().hex[:12]}"),
                task_type=TaskType(task_data["task_type"]),
                location=task_data["location"],
                priority=task_data["priority"],
                urgency=task_data["urgency"],
                required_capabilities=[AgentCapability(cap) for cap in task_data["required_capabilities"]],
                minimum_capability_scores={AgentCapability(cap): score for cap, score in task_data["minimum_capability_scores"].items()},
                estimated_duration_minutes=task_data["estimated_duration_minutes"],
                deadline=datetime.fromisoformat(task_data["deadline"]),
                resource_requirements=task_data.get("resource_requirements", {})
            )
            
            self.tasks[task.task_id] = task
            
            # Initiate bidding process
            await self._initiate_bidding(task)
            
            return task.task_id
            
        except Exception as e:
            raise ValueError(f"Task creation failed: {str(e)}")
    
    async def _initiate_bidding(self, task: TaskRequirement):
        """Initiate bidding process for task"""
        bids = []
        
        for agent_id, agent in self.agents.items():
            if agent.availability > 0.3:  # Only available agents
                bid = await self._generate_agent_bid(agent, task)
                if bid and bid.bid_amount > 0.3:  # Minimum bid threshold
                    bids.append(bid)
        
        self.active_bids[task.task_id] = bids
        
        # Record negotiation initiation
        self.negotiation_history.append({
            "event": "bidding_initiated",
            "task_id": task.task_id,
            "timestamp": datetime.now().isoformat(),
            "total_bids": len(bids),
            "participating_agents": [bid.agent_id for bid in bids]
        })
    
    async def _generate_agent_bid(self, agent: AgentProfile, task: TaskRequirement) -> Optional[AgentBid]:
        """Generate bid from agent for task"""
        try:
            # Check capability match
            capability_match = await self._calculate_capability_match(agent, task)
            if capability_match < 0.3:
                return None
            
            # Calculate proximity score
            proximity_score = await self._calculate_proximity_score(agent, task)
            
            # Calculate energy cost
            energy_cost = await self._calculate_energy_cost(agent, task)
            
            # Calculate time to complete
            time_to_complete = await self._calculate_time_to_complete(agent, task)
            
            # Calculate confidence based on performance history
            confidence = 0.7  # Base confidence
            if agent.agent_id in self.agent_performance_history:
                recent_performance = self.agent_performance_history[agent.agent_id][-10:]
                if recent_performance:
                    confidence = np.mean(recent_performance)
            
            # Calculate overall bid amount
            bid_amount = (
                capability_match * 0.4 +
                proximity_score * 0.2 +
                (1 - energy_cost) * 0.2 +
                (1 - time_to_complete / task.estimated_duration_minutes) * 0.1 +
                confidence * 0.1
            )
            
            # Generate bid reasoning
            bid_reasoning = {
                "capability_match": capability_match,
                "proximity_score": proximity_score,
                "energy_cost": energy_cost,
                "time_efficiency": 1 - time_to_complete / task.estimated_duration_minutes,
                "confidence": confidence,
                "agent_load": 1 - agent.availability
            }
            
            bid = AgentBid(
                bid_id=f"bid_{uuid.uuid4().hex[:12]}",
                agent_id=agent.agent_id,
                task_id=task.task_id,
                bid_amount=bid_amount,
                capability_match_score=capability_match,
                proximity_score=proximity_score,
                energy_cost=energy_cost,
                time_to_complete=time_to_complete,
                confidence=confidence,
                bid_reasoning=bid_reasoning,
                timestamp=datetime.now()
            )
            
            return bid
            
        except Exception as e:
            print(f"Bid generation error for {agent.agent_id}: {str(e)}")
            return None
    
    async def _calculate_capability_match(self, agent: AgentProfile, task: TaskRequirement) -> float:
        """Calculate capability match score"""
        total_score = 0
        required_count = len(task.required_capabilities)
        
        for required_cap in task.required_capabilities:
            if required_cap in agent.capability_scores:
                agent_score = agent.capability_scores[required_cap]
                min_score = task.minimum_capability_scores.get(required_cap, 0.5)
                
                if agent_score >= min_score:
                    total_score += min(1.0, agent_score / min_score)
                else:
                    total_score += agent_score / min_score * 0.5  # Partial credit
        
        return total_score / required_count if required_count > 0 else 0
    
    async def _calculate_proximity_score(self, agent: AgentProfile, task: TaskRequirement) -> float:
        """Calculate proximity score based on distance"""
        agent_loc = agent.current_location
        task_loc = task.location
        
        # Calculate distance (simplified)
        lat_diff = agent_loc["lat"] - task_loc["lat"]
        lon_diff = agent_loc["lon"] - task_loc["lon"]
        distance = np.sqrt(lat_diff**2 + lon_diff**2) * 111  # Approximate km
        
        # Calculate proximity score (closer is better)
        if distance <= agent.max_range_km:
            return 1.0 - (distance / agent.max_range_km)
        else:
            return max(0, 1.0 - (distance - agent.max_range_km) / agent.max_range_km * 0.5)
    
    async def _calculate_energy_cost(self, agent: AgentProfile, task: TaskRequirement) -> float:
        """Calculate energy cost for task execution"""
        base_cost = 0.2  # Base energy cost
        
        # Distance cost
        agent_loc = agent.current_location
        task_loc = task.location
        lat_diff = agent_loc["lat"] - task_loc["lat"]
        lon_diff = agent_loc["lon"] - task_loc["lon"]
        distance = np.sqrt(lat_diff**2 + lon_diff**2) * 111
        
        distance_cost = (distance / agent.max_range_km) * 0.3
        
        # Duration cost
        duration_cost = (task.estimated_duration_minutes / 120) * 0.3  # Normalize to 2 hours
        
        # Capability cost
        capability_cost = len(task.required_capabilities) * 0.05
        
        total_cost = base_cost + distance_cost + duration_cost + capability_cost
        return min(1.0, total_cost)
    
    async def _calculate_time_to_complete(self, agent: AgentProfile, task: TaskRequirement) -> int:
        """Calculate time to complete task"""
        base_time = task.estimated_duration_minutes
        
        # Adjust based on agent capability scores
        capability_factor = 1.0
        for required_cap in task.required_capabilities:
            if required_cap in agent.capability_scores:
                capability_factor *= (2.0 - agent.capability_scores[required_cap])  # Higher score = faster
        
        # Adjust based on proximity
        agent_loc = agent.current_location
        task_loc = task.location
        lat_diff = agent_loc["lat"] - task_loc["lat"]
        lon_diff = agent_loc["lon"] - task_loc["lon"]
        distance = np.sqrt(lat_diff**2 + lon_diff**2) * 111
        
        travel_time = (distance / agent.speed_kmh) * 60  # Convert to minutes
        
        return int(base_time * capability_factor + travel_time)
    
    async def _arbitrate_and_form_coalition(self, task_id: str, bids: List[AgentBid]):
        """Arbitrate bids and form optimal coalition"""
        try:
            # Sort bids by bid amount
            sorted_bids = sorted(bids, key=lambda x: x.bid_amount, reverse=True)
            
            # Select top bids for coalition
            task = self.tasks[task_id]
            coalition_size = min(len(sorted_bids), 5)  # Max 5 agents per coalition
            
            selected_bids = sorted_bids[:coalition_size]
            
            # Form coalition
            coalition_id = f"coalition_{uuid.uuid4().hex[:12]}"
            member_agents = [bid.agent_id for bid in selected_bids]
            lead_agent = selected_bids[0].agent_id  # Highest bid becomes lead
            
            # Calculate coalition success probability
            avg_bid_amount = np.mean([bid.bid_amount for bid in selected_bids])
            success_probability = avg_bid_amount * 0.8 + 0.2  # Base 20% success rate
            
            # Create communication links
            communication_links = []
            for i, agent_id in enumerate(member_agents):
                for j, other_agent_id in enumerate(member_agents[i+1:], i+1):
                    agent1 = self.agents[agent_id]
                    agent2 = self.agents[other_agent_id]
                    
                    # Calculate communication link quality
                    lat_diff = agent1.current_location["lat"] - agent2.current_location["lat"]
                    lon_diff = agent1.current_location["lon"] - agent2.current_location["lon"]
                    distance = np.sqrt(lat_diff**2 + lon_diff**2) * 111
                    
                    link_quality = max(0.1, 1.0 - distance / max(agent1.communication_range, agent2.communication_range))
                    
                    communication_links.append({
                        "agent1": agent_id,
                        "agent2": other_agent_id,
                        "distance_km": distance,
                        "link_quality": link_quality,
                        "bandwidth_mbps": 10 * link_quality
                    })
            
            # Create execution plan
            execution_plan = {
                "coordination_strategy": "distributed",
                "lead_agent": lead_agent,
                "task_allocation": {
                    bid.agent_id: {
                        "primary_role": self._assign_primary_role(bid, task),
                        "estimated_contribution": bid.bid_amount,
                        "start_time": datetime.now().isoformat(),
                        "expected_completion": (datetime.now() + timedelta(minutes=bid.time_to_complete)).isoformat()
                    }
                    for bid in selected_bids
                },
                "communication_protocol": "peer_to_peer",
                "decision_making": "consensus_based",
                "contingency_plan": "lead_agent_override"
            }
            
            coalition = Coalition(
                coalition_id=coalition_id,
                task_id=task_id,
                member_agents=member_agents,
                lead_agent=lead_agent,
                formation_time=datetime.now(),
                status=NegotiationStatus.COALITION_FORMED,
                coordination_protocol="peer_to_peer",
                communication_links=communication_links,
                execution_plan=execution_plan,
                success_probability=success_probability
            )
            
            self.coalitions[coalition_id] = coalition
            
            # Update agent statuses
            for bid in selected_bids:
                self.agents[bid.agent_id].current_task = task_id
                self.agents[bid.agent_id].availability *= 0.5  # Reduce availability when in coalition
            
            # Remove from active bids
            del self.active_bids[task_id]
            
            # Start execution
            await self._start_coalition_execution(coalition)
            
            # Record negotiation completion
            self.negotiation_history.append({
                "event": "coalition_formed",
                "task_id": task_id,
                "coalition_id": coalition_id,
                "timestamp": datetime.now().isoformat(),
                "member_count": len(member_agents),
                "lead_agent": lead_agent,
                "success_probability": success_probability
            })
            
        except Exception as e:
            print(f"Coalition formation error: {str(e)}")
    
    def _assign_primary_role(self, bid: AgentBid, task: TaskRequirement) -> str:
        """Assign primary role to agent based on capabilities"""
        agent = self.agents[bid.agent_id]
        
        # Find best matching capability
        best_capability = None
        best_score = 0
        
        for required_cap in task.required_capabilities:
            if required_cap in agent.capability_scores:
                score = agent.capability_scores[required_cap]
                if score > best_score:
                    best_score = score
                    best_capability = required_cap
        
        return best_capability.value if best_capability else "support"
    
    async def _start_coalition_execution(self, coalition: Coalition):
        """Start coalition task execution"""
        coalition.status = NegotiationStatus.EXECUTING
        
        # Simulate task execution
        execution_time = np.random.randint(30, 120)  # 30-120 minutes
        
        # Schedule completion
        asyncio.create_task(self._complete_coalition_execution(coalition, execution_time))
    
    async def _complete_coalition_execution(self, coalition: Coalition, execution_time_minutes: int):
        """Complete coalition task execution"""
        await asyncio.sleep(execution_time_minutes * 0.1)  # Simulate with shorter time
        
        # Determine success
        success = np.random.random() < coalition.success_probability
        
        if success:
            coalition.status = NegotiationStatus.COMPLETED
            
            # Update agent performance history
            for agent_id in coalition.member_agents:
                performance_score = np.random.uniform(0.7, 1.0)
                self.agent_performance_history[agent_id].append(performance_score)
        else:
            coalition.status = NegotiationStatus.FAILED
        
        # Release agents
        for agent_id in coalition.member_agents:
            self.agents[agent_id].current_task = None
            self.agents[agent_id].availability = min(1.0, self.agents[agent_id].availability * 2)  # Restore availability
        
        # Record completion
        self.negotiation_history.append({
            "event": "coalition_completed",
            "coalition_id": coalition.coalition_id,
            "task_id": coalition.task_id,
            "status": coalition.status.value,
            "timestamp": datetime.now().isoformat(),
            "execution_time_minutes": execution_time_minutes,
            "success": success
        })
    
    def get_agent_status(self) -> List[Dict[str, Any]]:
        """Get current agent status"""
        return [agent.to_dict() for agent in self.agents.values()]
    
    def get_active_coalitions(self) -> List[Dict[str, Any]]:
        """Get active coalitions"""
        return [coalition.to_dict() for coalition in self.coalitions.values() 
                if coalition.status in [NegotiationStatus.COALITION_FORMED, NegotiationStatus.EXECUTING]]
    
    def get_negotiation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get negotiation history"""
        return self.negotiation_history[-limit:] if self.negotiation_history else []
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get negotiation system metrics"""
        total_agents = len(self.agents)
        available_agents = len([a for a in self.agents.values() if a.availability > 0.5])
        active_coalitions = len([c for c in self.coalitions.values() if c.status == NegotiationStatus.EXECUTING])
        
        # Calculate average performance
        all_performances = []
        for performances in self.agent_performance_history.values():
            all_performances.extend(performances)
        
        avg_performance = np.mean(all_performances) if all_performances else 0
        
        return {
            "total_agents": total_agents,
            "available_agents": available_agents,
            "active_coalitions": active_coalitions,
            "average_agent_performance": avg_performance,
            "total_negotiations": len(self.negotiation_history),
            "success_rate": len([h for h in self.negotiation_history if h.get("success", False)]) / max(len(self.negotiation_history), 1),
            "timestamp": datetime.now().isoformat()
        }

# Global negotiation protocol instance
multi_agent_negotiation = MultiAgentNegotiationProtocol()
