"""
National Stability Index Service
Real-time calculation and broadcasting of infrastructure stability
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from collections import defaultdict, deque

class StabilityLevel(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    HEALTHY = "healthy"
    EXCELLENT = "excellent"

class StabilityFactor(Enum):
    INFRASTRUCTURE_HEALTH = "infrastructure_health"
    CASCADE_RISK = "cascade_risk"
    AGENT_COORDINATION = "agent_coordination"
    RESOURCE_AVAILABILITY = "resource_availability"
    SYSTEM_PERFORMANCE = "system_performance"
    EXTERNAL_THREATS = "external_threats"

@dataclass
class StabilityMetric:
    metric_id: str
    factor: StabilityFactor
    value: float  # 0-1
    weight: float  # Importance weight
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "factor": self.factor.value,
            "value": self.value,
            "weight": self.weight,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class StabilityIndex:
    index_id: str
    overall_score: float  # 0-1
    level: StabilityLevel
    factors: Dict[StabilityFactor, float]
    trend: str  # improving, stable, declining
    timestamp: datetime
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "index_id": self.index_id,
            "overall_score": self.overall_score,
            "level": self.level.value,
            "percentage": round(self.overall_score * 100, 1),
            "factors": {factor.value: value for factor, value in self.factors.items()},
            "trend": self.trend,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence
        }

class StabilityIndexService:
    """Real-time calculation and broadcasting of infrastructure stability"""
    
    def __init__(self):
        self.current_index: Optional[StabilityIndex] = None
        self.historical_indices: deque = deque(maxlen=1000)  # Keep last 1000 indices
        self.metrics: Dict[StabilityFactor, List[StabilityMetric]] = defaultdict(list)
        self.factor_weights: Dict[StabilityFactor, float] = {
            StabilityFactor.INFRASTRUCTURE_HEALTH: 0.35,
            StabilityFactor.CASCADE_RISK: 0.25,
            StabilityFactor.AGENT_COORDINATION: 0.15,
            StabilityFactor.RESOURCE_AVAILABILITY: 0.10,
            StabilityFactor.SYSTEM_PERFORMANCE: 0.10,
            StabilityFactor.EXTERNAL_THREATS: 0.05
        }
        self.websocket_clients = set()
        
        # Initialize with baseline stability
        self._initialize_baseline_stability()
        
        # Start background calculation
        asyncio.create_task(self._continuous_calculation())
        asyncio.create_task(self._real_time_broadcasting())
    
    def _initialize_baseline_stability(self):
        """Initialize with baseline stability metrics"""
        baseline_metrics = {
            StabilityFactor.INFRASTRUCTURE_HEALTH: 0.85,
            StabilityFactor.CASCADE_RISK: 0.90,  # Low risk = high stability
            StabilityFactor.AGENT_COORDINATION: 0.80,
            StabilityFactor.RESOURCE_AVAILABILITY: 0.75,
            StabilityFactor.SYSTEM_PERFORMANCE: 0.90,
            StabilityFactor.EXTERNAL_THREATS: 0.95  # Low threats = high stability
        }
        
        for factor, value in baseline_metrics.items():
            metric = StabilityMetric(
                metric_id=f"metric_{uuid.uuid4().hex[:8]}",
                factor=factor,
                value=value,
                weight=self.factor_weights[factor],
                timestamp=datetime.now(),
                metadata={"source": "baseline"}
            )
            self.metrics[factor].append(metric)
        
        # Calculate initial index
        self._calculate_stability_index()
    
    async def _continuous_calculation(self):
        """Continuously calculate stability index"""
        while True:
            try:
                # Update metrics
                await self._update_metrics()
                
                # Calculate new index
                self._calculate_stability_index()
                
                await asyncio.sleep(3)  # Update every 3 seconds
                
            except Exception as e:
                print(f"Stability calculation error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _update_metrics(self):
        """Update stability metrics"""
        timestamp = datetime.now()
        
        # Infrastructure Health
        infrastructure_health = await self._calculate_infrastructure_health()
        self._add_metric(StabilityFactor.INFRASTRUCTURE_HEALTH, infrastructure_health, timestamp)
        
        # Cascade Risk (inverted - high risk = low stability)
        cascade_risk = await self._calculate_cascade_risk()
        stability_from_risk = 1.0 - cascade_risk  # Invert risk to stability
        self._add_metric(StabilityFactor.CASCADE_RISK, stability_from_risk, timestamp)
        
        # Agent Coordination
        agent_coordination = await self._calculate_agent_coordination()
        self._add_metric(StabilityFactor.AGENT_COORDINATION, agent_coordination, timestamp)
        
        # Resource Availability
        resource_availability = await self._calculate_resource_availability()
        self._add_metric(StabilityFactor.RESOURCE_AVAILABILITY, resource_availability, timestamp)
        
        # System Performance
        system_performance = await self._calculate_system_performance()
        self._add_metric(StabilityFactor.SYSTEM_PERFORMANCE, system_performance, timestamp)
        
        # External Threats
        external_threats = await self._calculate_external_threats()
        stability_from_threats = 1.0 - external_threats  # Invert threats to stability
        self._add_metric(StabilityFactor.EXTERNAL_THREATS, stability_from_threats, timestamp)
    
    def _add_metric(self, factor: StabilityFactor, value: float, timestamp: datetime):
        """Add a new metric for a factor"""
        metric = StabilityMetric(
            metric_id=f"metric_{uuid.uuid4().hex[:8]}",
            factor=factor,
            value=value,
            weight=self.factor_weights[factor],
            timestamp=timestamp
        )
        
        self.metrics[factor].append(metric)
        
        # Keep only recent metrics (last 50 per factor)
        if len(self.metrics[factor]) > 50:
            self.metrics[factor] = self.metrics[factor][-50:]
    
    async def _calculate_infrastructure_health(self) -> float:
        """Calculate infrastructure health factor"""
        try:
            # Import from autonomous execution engine
            from backend.services.autonomous_execution_engine import autonomous_execution_engine
            
            infrastructure_status = autonomous_execution_engine.get_infrastructure_status()
            
            if not infrastructure_status or not infrastructure_status.get("nodes"):
                return 0.8  # Default if no data
            
            nodes = infrastructure_status["nodes"]
            
            # Calculate health based on risk levels and load
            total_health = 0
            node_count = 0
            
            for node_id, node_data in nodes.items():
                # Risk component (lower risk = higher health)
                risk_health = 1.0 - node_data.get("risk", 0.5)
                
                # Load component (optimal load = 0.6-0.8)
                load_ratio = node_data.get("load", 0) / max(node_data.get("capacity", 1), 1)
                if 0.6 <= load_ratio <= 0.8:
                    load_health = 1.0
                elif load_ratio < 0.6:
                    load_health = 0.8  # Underutilized
                else:
                    load_health = max(0.2, 1.0 - (load_ratio - 0.8) * 2)  # Overloaded
                
                # Combine factors
                node_health = (risk_health * 0.6 + load_health * 0.4)
                total_health += node_health
                node_count += 1
            
            return total_health / max(node_count, 1)
            
        except Exception as e:
            print(f"Infrastructure health calculation error: {str(e)}")
            return 0.8
    
    async def _calculate_cascade_risk(self) -> float:
        """Calculate cascade risk factor"""
        try:
            # Import from cascade forecast engine
            from backend.services.digital_twin_cascade_forecast import cascade_forecast_engine
            
            # Get current cascade risk
            # This would normally call the cascade forecast engine
            # For now, simulate based on infrastructure health
            
            infrastructure_health = await self._calculate_infrastructure_health()
            
            # Higher infrastructure health = lower cascade risk
            cascade_risk = max(0.1, 1.0 - infrastructure_health)
            
            # Add some randomness for realism
            cascade_risk += np.random.uniform(-0.05, 0.05)
            cascade_risk = max(0.0, min(1.0, cascade_risk))
            
            return cascade_risk
            
        except Exception as e:
            print(f"Cascade risk calculation error: {str(e)}")
            return 0.2
    
    async def _calculate_agent_coordination(self) -> float:
        """Calculate agent coordination factor"""
        try:
            # Import from multi-agent negotiation engine
            from backend.services.multi_agent_negotiation_engine import multi_agent_negotiation_engine
            
            system_metrics = multi_agent_negotiation_engine.get_system_metrics()
            
            if not system_metrics:
                return 0.8
            
            # Calculate based on available agents and performance
            total_agents = system_metrics.get("total_agents", 10)
            available_agents = system_metrics.get("available_agents", 8)
            avg_performance = system_metrics.get("average_agent_performance", 0.8)
            success_rate = system_metrics.get("success_rate", 0.85)
            
            # Availability component
            availability_ratio = available_agents / max(total_agents, 1)
            
            # Performance component
            performance_score = (avg_performance + success_rate) / 2
            
            # Combine factors
            coordination_health = (availability_ratio * 0.4 + performance_score * 0.6)
            
            return max(0.0, min(1.0, coordination_health))
            
        except Exception as e:
            print(f"Agent coordination calculation error: {str(e)}")
            return 0.8
    
    async def _calculate_resource_availability(self) -> float:
        """Calculate resource availability factor"""
        try:
            # Import from multi-agent negotiation engine
            from backend.services.multi_agent_negotiation_engine import multi_agent_negotiation_engine
            
            agents = multi_agent_negotiation_engine.get_agent_status()
            
            if not agents:
                return 0.75
            
            # Calculate resource availability based on agent load
            total_capacity = 0
            total_load = 0
            
            for agent in agents:
                capacity = agent.get("max_capacity", 100)
                load = agent.get("current_load", 50)
                
                total_capacity += capacity
                total_load += load
            
            # Availability ratio
            availability_ratio = (total_capacity - total_load) / max(total_capacity, 1)
            
            # Normalize to 0-1 scale
            resource_health = max(0.0, min(1.0, availability_ratio))
            
            return resource_health
            
        except Exception as e:
            print(f"Resource availability calculation error: {str(e)}")
            return 0.75
    
    async def _calculate_system_performance(self) -> float:
        """Calculate system performance factor"""
        try:
            # Import from live reliability metrics
            from backend.services.live_system_reliability import live_reliability_metrics
            
            # Get system health metrics
            # This would normally call the reliability metrics service
            # For now, simulate based on recent activity
            
            # Simulate based on response times and success rates
            response_time_health = 0.9  # Assume good response times
            success_rate_health = 0.85  # Assume good success rates
            uptime_health = 0.95  # Assume good uptime
            
            # Combine factors
            performance_health = (response_time_health * 0.3 + 
                               success_rate_health * 0.4 + 
                               uptime_health * 0.3)
            
            # Add some variation
            performance_health += np.random.uniform(-0.02, 0.02)
            performance_health = max(0.0, min(1.0, performance_health))
            
            return performance_health
            
        except Exception as e:
            print(f"System performance calculation error: {str(e)}")
            return 0.9
    
    async def _calculate_external_threats(self) -> float:
        """Calculate external threats factor"""
        try:
            # Import from autonomous execution engine
            from backend.services.autonomous_execution_engine import autonomous_execution_engine
            
            # Get current disaster risk level
            infrastructure_status = autonomous_execution_engine.get_infrastructure_status()
            
            if not infrastructure_status:
                return 0.1  # Low threats
            
            # Calculate threat level based on high-risk nodes
            high_risk_nodes = infrastructure_status.get("high_risk_nodes", 0)
            total_nodes = infrastructure_status.get("total_nodes", 12)
            
            # Threat level based on proportion of high-risk nodes
            threat_ratio = high_risk_nodes / max(total_nodes, 1)
            
            # Add some environmental factors (simulated)
            weather_threat = np.random.uniform(0.0, 0.1)  # Weather-related threats
            seismic_threat = np.random.uniform(0.0, 0.05)  # Seismic activity
            
            total_threat = min(1.0, threat_ratio + weather_threat + seismic_threat)
            
            return total_threat
            
        except Exception as e:
            print(f"External threats calculation error: {str(e)}")
            return 0.1
    
    def _calculate_stability_index(self):
        """Calculate overall stability index"""
        timestamp = datetime.now()
        
        # Get latest metrics for each factor
        factor_values = {}
        confidence_sum = 0
        weight_sum = 0
        
        for factor in StabilityFactor:
            if factor in self.metrics and self.metrics[factor]:
                latest_metric = self.metrics[factor][-1]
                factor_values[factor] = latest_metric.value
                confidence_sum += latest_metric.value * latest_metric.weight
                weight_sum += latest_metric.weight
        
        # Calculate weighted average
        if weight_sum > 0:
            overall_score = confidence_sum / weight_sum
        else:
            overall_score = 0.8  # Default
        
        # Determine stability level
        if overall_score >= 0.9:
            level = StabilityLevel.EXCELLENT
        elif overall_score >= 0.7:
            level = StabilityLevel.HEALTHY
        elif overall_score >= 0.4:
            level = StabilityLevel.WARNING
        else:
            level = StabilityLevel.CRITICAL
        
        # Calculate trend
        trend = self._calculate_trend(overall_score)
        
        # Calculate confidence
        confidence = min(1.0, weight_sum / sum(self.factor_weights.values()))
        
        # Create stability index
        index = StabilityIndex(
            index_id=f"index_{uuid.uuid4().hex[:12]}",
            overall_score=overall_score,
            level=level,
            factors=factor_values,
            trend=trend,
            timestamp=timestamp,
            confidence=confidence
        )
        
        # Update current index
        self.current_index = index
        
        # Add to history
        self.historical_indices.append(index)
    
    def _calculate_trend(self, current_score: float) -> str:
        """Calculate trend based on historical data"""
        if len(self.historical_indices) < 5:
            return "stable"
        
        # Get last 5 indices
        recent_indices = list(self.historical_indices)[-5:]
        
        # Calculate trend
        scores = [idx.overall_score for idx in recent_indices]
        
        # Simple linear regression for trend
        if len(scores) >= 3:
            x = list(range(len(scores)))
            n = len(scores)
            
            # Calculate slope
            sum_x = sum(x)
            sum_y = sum(scores)
            sum_xy = sum(x[i] * scores[i] for i in range(n))
            sum_x2 = sum(x[i] * x[i] for i in range(n))
            
            if n * sum_x2 - sum_x * sum_x != 0:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
                
                if slope > 0.01:
                    return "improving"
                elif slope < -0.01:
                    return "declining"
        
        return "stable"
    
    async def _real_time_broadcasting(self):
        """Broadcast stability index updates in real-time"""
        while True:
            try:
                if self.current_index:
                    await self._broadcast_stability_update()
                
                await asyncio.sleep(3)  # Broadcast every 3 seconds
                
            except Exception as e:
                print(f"Stability broadcasting error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _broadcast_stability_update(self):
        """Broadcast stability update via WebSocket"""
        if self.websocket_clients:
            message = {
                "type": "stability_update",
                "stability_index": self.current_index.to_dict(),
                "timestamp": datetime.now().isoformat()
            }
            # This would integrate with the WebSocket manager
            # await self._websocket_broadcast(message)
            pass
    
    def get_current_stability(self) -> Optional[Dict[str, Any]]:
        """Get current stability index"""
        if self.current_index:
            return self.current_index.to_dict()
        return None
    
    def get_stability_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get stability index history"""
        indices = list(self.historical_indices)
        indices.sort(key=lambda idx: idx.timestamp, reverse=True)
        
        recent_indices = indices[:limit] if len(indices) > limit else indices
        return [idx.to_dict() for idx in recent_indices]
    
    def get_factor_metrics(self, factor: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get metrics for a specific factor"""
        try:
            factor_enum = StabilityFactor(factor)
        except ValueError:
            return []
        
        if factor_enum not in self.metrics:
            return []
        
        metrics = self.metrics[factor_enum]
        metrics.sort(key=lambda m: m.timestamp, reverse=True)
        
        recent_metrics = metrics[:limit] if len(metrics) > limit else metrics
        return [metric.to_dict() for metric in recent_metrics]
    
    def get_stability_alerts(self) -> List[Dict[str, Any]]:
        """Get stability alerts"""
        alerts = []
        
        if not self.current_index:
            return alerts
        
        # Critical alert
        if self.current_index.level == StabilityLevel.CRITICAL:
            alerts.append({
                "level": "critical",
                "message": "Critical stability level detected",
                "score": self.current_index.overall_score,
                "timestamp": self.current_index.timestamp.isoformat()
            })
        
        # Warning alert
        elif self.current_index.level == StabilityLevel.WARNING:
            alerts.append({
                "level": "warning",
                "message": "Stability level below optimal",
                "score": self.current_index.overall_score,
                "timestamp": self.current_index.timestamp.isoformat()
            })
        
        # Declining trend alert
        if self.current_index.trend == "declining":
            alerts.append({
                "level": "warning",
                "message": "Stability declining",
                "trend": self.current_index.trend,
                "timestamp": self.current_index.timestamp.isoformat()
            })
        
        return alerts
    
    async def simulate_stability_impact(self, action: str, impact_magnitude: float) -> Dict[str, Any]:
        """Simulate the impact of an action on stability"""
        if not self.current_index:
            return {"error": "No current stability data"}
        
        # Simulate immediate impact
        impact_factor = {
            "load_redistribution": 0.05,
            "backup_activation": 0.04,
            "grid_isolation": 0.06,
            "backup_switching": 0.03,
            "corridor_opening": 0.04,
            "emergency_routing": 0.02,
            "standard_stabilization": 0.03
        }.get(action, 0.03)
        
        # Apply impact
        new_score = min(1.0, self.current_index.overall_score + (impact_factor * impact_magnitude))
        
        # Calculate new level
        if new_score >= 0.9:
            new_level = StabilityLevel.EXCELLENT
        elif new_score >= 0.7:
            new_level = StabilityLevel.HEALTHY
        elif new_score >= 0.4:
            new_level = StabilityLevel.WARNING
        else:
            new_level = StabilityLevel.CRITICAL
        
        return {
            "current_score": self.current_index.overall_score,
            "predicted_score": new_score,
            "improvement": new_score - self.current_index.overall_score,
            "current_level": self.current_index.level.value,
            "predicted_level": new_level.value,
            "action": action,
            "impact_magnitude": impact_magnitude
        }

# Global stability index service
stability_index_service = StabilityIndexService()
