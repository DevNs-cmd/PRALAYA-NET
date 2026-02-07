"""
Live System Reliability Metrics
Real-time operational health and reliability indicators
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
from collections import defaultdict, deque

class MetricType(Enum):
    RESPONSE_LATENCY = "response_latency"
    STABILIZATION_SUCCESS = "stabilization_success"
    CASCADE_CONTAINMENT = "cascade_containment"
    AGENT_COORDINATION = "agent_coordination"
    INFRASTRUCTURE_RESILIENCE = "infrastructure_resilience"
    SYSTEM_UPTIME = "system_uptime"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"

class HealthStatus(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    DEGRADED = "degraded"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class MetricValue:
    """Individual metric value with timestamp"""
    metric_id: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    source: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "metric_type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "metadata": self.metadata
        }

@dataclass
class MetricThreshold:
    """Threshold configuration for metrics"""
    metric_type: MetricType
    warning_threshold: float
    critical_threshold: float
    optimal_range: Tuple[float, float]
    measurement_unit: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_type": self.metric_type.value,
            "warning_threshold": self.warning_threshold,
            "critical_threshold": self.critical_threshold,
            "optimal_range": self.optimal_range,
            "measurement_unit": self.measurement_unit
        }

@dataclass
class SystemAlert:
    """System alert for metric violations"""
    alert_id: str
    metric_type: MetricType
    alert_level: AlertLevel
    message: str
    current_value: float
    threshold_value: float
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "metric_type": self.metric_type.value,
            "alert_level": self.alert_level.value,
            "message": self.message,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolution_time": self.resolution_time.isoformat() if self.resolution_time else None
        }

@dataclass
class ReliabilityScore:
    """Overall reliability score calculation"""
    score_id: str
    timestamp: datetime
    overall_score: float
    component_scores: Dict[str, float]
    health_status: HealthStatus
    trends: Dict[str, str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "score_id": self.score_id,
            "timestamp": self.timestamp.isoformat(),
            "overall_score": self.overall_score,
            "component_scores": self.component_scores,
            "health_status": self.health_status.value,
            "trends": self.trends,
            "recommendations": self.recommendations
        }

class LiveSystemReliabilityMetrics:
    """Real-time system reliability monitoring"""
    
    def __init__(self):
        self.metric_values: Dict[str, List[MetricValue]] = defaultdict(list)
        self.metric_thresholds: Dict[MetricType, MetricThreshold] = {}
        self.active_alerts: Dict[str, SystemAlert] = {}
        self.reliability_scores: List[ReliabilityScore] = []
        self.metric_history: Dict[MetricType, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Initialize thresholds
        self._initialize_thresholds()
        
        # Start background monitoring
        asyncio.create_task(self._continuous_monitoring())
        asyncio.create_task(self._metric_collection())
        asyncio.create_task(self._alert_processing())
    
    def _initialize_thresholds(self):
        """Initialize metric thresholds"""
        
        # Response latency thresholds (milliseconds)
        self.metric_thresholds[MetricType.RESPONSE_LATENCY] = MetricThreshold(
            metric_type=MetricType.RESPONSE_LATENCY,
            warning_threshold=1000,  # 1 second
            critical_threshold=5000,  # 5 seconds
            optimal_range=(0, 500),
            measurement_unit="ms"
        )
        
        # Stabilization success thresholds (percentage)
        self.metric_thresholds[MetricType.STABILIZATION_SUCCESS] = MetricThreshold(
            metric_type=MetricType.STABILIZATION_SUCCESS,
            warning_threshold=0.7,
            critical_threshold=0.5,
            optimal_range=(0.8, 1.0),
            measurement_unit="%"
        )
        
        # Cascade containment thresholds (percentage)
        self.metric_thresholds[MetricType.CASCADE_CONTAINMENT] = MetricThreshold(
            metric_type=MetricType.CASCADE_CONTAINMENT,
            warning_threshold=0.7,
            critical_threshold=0.5,
            optimal_range=(0.8, 1.0),
            measurement_unit="%"
        )
        
        # Agent coordination thresholds (percentage)
        self.metric_thresholds[MetricType.AGENT_COORDINATION] = MetricThreshold(
            metric_type=MetricType.AGENT_COORDINATION,
            warning_threshold=0.7,
            critical_threshold=0.5,
            optimal_range=(0.8, 1.0),
            measurement_unit="%"
        )
        
        # Infrastructure resilience thresholds (percentage)
        self.metric_thresholds[MetricType.INFRASTRUCTURE_RESILIENCE] = MetricThreshold(
            metric_type=MetricType.INFRASTRUCTURE_RESILIENCE,
            warning_threshold=0.7,
            critical_threshold=0.5,
            optimal_range=(0.8, 1.0),
            measurement_unit="%"
        )
        
        # System uptime thresholds (percentage)
        self.metric_thresholds[MetricType.SYSTEM_UPTIME] = MetricThreshold(
            metric_type=MetricType.SYSTEM_UPTIME,
            warning_threshold=0.95,
            critical_threshold=0.9,
            optimal_range=(0.99, 1.0),
            measurement_unit="%"
        )
        
        # Error rate thresholds (percentage)
        self.metric_thresholds[MetricType.ERROR_RATE] = MetricThreshold(
            metric_type=MetricType.ERROR_RATE,
            warning_threshold=0.05,
            critical_threshold=0.1,
            optimal_range=(0, 0.02),
            measurement_unit="%"
        )
        
        # Throughput thresholds (operations per second)
        self.metric_thresholds[MetricType.THROUGHPUT] = MetricThreshold(
            metric_type=MetricType.THROUGHPUT,
            warning_threshold=50,
            critical_threshold=20,
            optimal_range=(100, 1000),
            measurement_unit="ops/s"
        )
    
    async def _continuous_monitoring(self):
        """Continuous reliability monitoring"""
        while True:
            try:
                # Calculate reliability scores
                await self._calculate_reliability_scores()
                
                # Process alerts
                await self._process_alerts()
                
                # Generate recommendations
                await self._generate_recommendations()
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                print(f"Reliability monitoring error: {str(e)}")
                await asyncio.sleep(30)
    
    async def _metric_collection(self):
        """Collect metrics from various system components"""
        while True:
            try:
                # Collect response latency metrics
                await self._collect_response_latency()
                
                # Collect stabilization success metrics
                await self._collect_stabilization_success()
                
                # Collect cascade containment metrics
                await self._collect_cascade_containment()
                
                # Collect agent coordination metrics
                await self._collect_agent_coordination()
                
                # Collect infrastructure resilience metrics
                await self._collect_infrastructure_resilience()
                
                # Collect system uptime metrics
                await self._collect_system_uptime()
                
                # Collect error rate metrics
                await self._collect_error_rate()
                
                # Collect throughput metrics
                await self._collect_throughput()
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                print(f"Metric collection error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _collect_response_latency(self):
        """Collect response latency metrics"""
        # Simulate response latency measurements
        latency = np.random.exponential(scale=200)  # Exponential distribution
        latency = min(latency, 10000)  # Cap at 10 seconds
        
        await self._record_metric(
            MetricType.RESPONSE_LATENCY,
            latency,
            "api_gateway",
            {"endpoint": "decision_engine", "method": "POST"}
        )
    
    async def _collect_stabilization_success(self):
        """Collect stabilization success metrics"""
        # Simulate stabilization success rate
        success_rate = np.random.beta(8, 2)  # Beta distribution favoring high values
        
        await self._record_metric(
            MetricType.STABILIZATION_SUCCESS,
            success_rate,
            "stabilization_engine",
            {"stabilization_type": "load_redistribution", "infrastructure_nodes": 17}
        )
    
    async def _collect_cascade_containment(self):
        """Collect cascade containment metrics"""
        # Simulate cascade containment success
        containment_rate = np.random.beta(7, 3)  # Beta distribution
        
        await self._record_metric(
            MetricType.CASCADE_CONTAINMENT,
            containment_rate,
            "cascade_forecast_engine",
            {"cascade_probability": 0.6, "affected_nodes": 5}
        )
    
    async def _collect_agent_coordination(self):
        """Collect agent coordination metrics"""
        # Simulate agent coordination efficiency
        coordination_rate = np.random.beta(6, 2)  # Beta distribution
        
        await self._record_metric(
            MetricType.AGENT_COORDINATION,
            coordination_rate,
            "multi_agent_system",
            {"active_agents": 13, "coalition_size": 4}
        )
    
    async def _collect_infrastructure_resilience(self):
        """Collect infrastructure resilience metrics"""
        # Simulate infrastructure resilience
        resilience_score = np.random.beta(9, 2)  # Beta distribution favoring high values
        
        await self._record_metric(
            MetricType.INFRASTRUCTURE_RESILIENCE,
            resilience_score,
            "infrastructure_monitoring",
            {"healthy_nodes": 15, "total_nodes": 17}
        )
    
    async def _collect_system_uptime(self):
        """Collect system uptime metrics"""
        # Simulate system uptime (should be very high)
        uptime = np.random.beta(95, 5)  # Very high uptime
        
        await self._record_metric(
            MetricType.SYSTEM_UPTIME,
            uptime,
            "system_monitor",
            {"service": "main_api", "availability_window": "24h"}
        )
    
    async def _collect_error_rate(self):
        """Collect error rate metrics"""
        # Simulate error rate (should be low)
        error_rate = np.random.exponential(scale=0.01)  # Exponential distribution
        error_rate = min(error_rate, 0.2)  # Cap at 20%
        
        await self._record_metric(
            MetricType.ERROR_RATE,
            error_rate,
            "error_monitoring",
            {"error_type": "validation_error", "service": "api_gateway"}
        )
    
    async def _collect_throughput(self):
        """Collect throughput metrics"""
        # Simulate system throughput
        throughput = np.random.gamma(shape=2, scale=100)  # Gamma distribution
        throughput = min(throughput, 2000)  # Cap at 2000 ops/s
        
        await self._record_metric(
            MetricType.THROUGHPUT,
            throughput,
            "throughput_monitor",
            {"operation_type": "decision_processing", "concurrent_requests": 25}
        )
    
    async def _record_metric(self, metric_type: MetricType, value: float, 
                            source: str, metadata: Dict[str, Any]):
        """Record a metric value"""
        metric_id = f"metric_{uuid.uuid4().hex[:12]}"
        
        metric_value = MetricValue(
            metric_id=metric_id,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(),
            source=source,
            metadata=metadata
        )
        
        # Store metric
        self.metric_values[metric_type.value].append(metric_value)
        self.metric_history[metric_type].append(value)
        
        # Keep only recent values
        if len(self.metric_values[metric_type.value]) > 1000:
            self.metric_values[metric_type.value] = self.metric_values[metric_type.value][-1000:]
        
        # Check for alerts
        await self._check_metric_alerts(metric_value)
    
    async def _check_metric_alerts(self, metric_value: MetricValue):
        """Check if metric value triggers alerts"""
        threshold = self.metric_thresholds.get(metric_value.metric_type)
        if not threshold:
            return
        
        alert_level = None
        threshold_value = None
        message = ""
        
        # Check critical threshold
        if metric_value.metric_type in [MetricType.RESPONSE_LATENCY, MetricType.ERROR_RATE]:
            # For these metrics, higher is worse
            if metric_value.value >= threshold.critical_threshold:
                alert_level = AlertLevel.CRITICAL
                threshold_value = threshold.critical_threshold
                message = f"{metric_value.metric_type.value} exceeded critical threshold: {metric_value.value:.2f} >= {threshold_value:.2f}"
            elif metric_value.value >= threshold.warning_threshold:
                alert_level = AlertLevel.WARNING
                threshold_value = threshold.warning_threshold
                message = f"{metric_value.metric_type.value} exceeded warning threshold: {metric_value.value:.2f} >= {threshold_value:.2f}"
        else:
            # For these metrics, lower is worse
            if metric_value.value <= threshold.critical_threshold:
                alert_level = AlertLevel.CRITICAL
                threshold_value = threshold.critical_threshold
                message = f"{metric_value.metric_type.value} below critical threshold: {metric_value.value:.2f} <= {threshold_value:.2f}"
            elif metric_value.value <= threshold.warning_threshold:
                alert_level = AlertLevel.WARNING
                threshold_value = threshold.warning_threshold
                message = f"{metric_value.metric_type.value} below warning threshold: {metric_value.value:.2f} <= {threshold_value:.2f}"
        
        # Create alert if needed
        if alert_level:
            alert_id = f"alert_{uuid.uuid4().hex[:12]}"
            alert = SystemAlert(
                alert_id=alert_id,
                metric_type=metric_value.metric_type,
                alert_level=alert_level,
                message=message,
                current_value=metric_value.value,
                threshold_value=threshold_value,
                timestamp=metric_value.timestamp
            )
            
            self.active_alerts[alert_id] = alert
    
    async def _alert_processing(self):
        """Process and manage alerts"""
        while True:
            try:
                # Check for alert resolution
                await self._check_alert_resolution()
                
                # Auto-resolve old alerts
                await self._auto_resolve_alerts()
                
                await asyncio.sleep(60)  # Process every minute
                
            except Exception as e:
                print(f"Alert processing error: {str(e)}")
                await asyncio.sleep(120)
    
    async def _check_alert_resolution(self):
        """Check if alerts should be resolved"""
        for alert_id, alert in list(self.active_alerts.items()):
            # Get recent metric values
            recent_values = self.metric_history[alert.metric_type]
            if len(recent_values) < 5:
                continue
            
            recent_avg = np.mean(list(recent_values)[-5:])
            threshold = self.metric_thresholds[alert.metric_type]
            
            # Check if alert condition is resolved
            resolved = False
            if alert.metric_type in [MetricType.RESPONSE_LATENCY, MetricType.ERROR_RATE]:
                # Higher is worse
                resolved = recent_avg < threshold.warning_threshold
            else:
                # Lower is worse
                resolved = recent_avg > threshold.warning_threshold
            
            if resolved:
                alert.resolved = True
                alert.resolution_time = datetime.now()
                del self.active_alerts[alert_id]
    
    async def _auto_resolve_alerts(self):
        """Auto-resolve old alerts"""
        current_time = datetime.now()
        auto_resolve_time = timedelta(minutes=30)  # Auto-resolve after 30 minutes
        
        for alert_id, alert in list(self.active_alerts.items()):
            if current_time - alert.timestamp > auto_resolve_time:
                alert.resolved = True
                alert.resolution_time = current_time
                del self.active_alerts[alert_id]
    
    async def _calculate_reliability_scores(self):
        """Calculate overall reliability scores"""
        try:
            # Get current metric values
            current_metrics = {}
            for metric_type in MetricType:
                history = self.metric_history[metric_type]
                if history:
                    current_metrics[metric_type] = np.mean(list(history)[-10:])  # 10-minute average
            
            if not current_metrics:
                return
            
            # Calculate component scores
            component_scores = {}
            
            # Response latency score (inverse, lower is better)
            if MetricType.RESPONSE_LATENCY in current_metrics:
                latency = current_metrics[MetricType.RESPONSE_LATENCY]
                threshold = self.metric_thresholds[MetricType.RESPONSE_LATENCY]
                score = max(0, 1 - (latency - threshold.optimal_range[1]) / 
                          (threshold.critical_threshold - threshold.optimal_range[1]))
                component_scores["response_latency"] = score
            
            # Success metrics (higher is better)
            for metric_type in [MetricType.STABILIZATION_SUCCESS, MetricType.CASCADE_CONTAINMENT,
                              MetricType.AGENT_COORDINATION, MetricType.INFRASTRUCTURE_RESILIENCE,
                              MetricType.SYSTEM_UPTIME]:
                if metric_type in current_metrics:
                    value = current_metrics[metric_type]
                    score = value  # Already normalized 0-1
                    component_scores[metric_type.value] = score
            
            # Error rate score (inverse, lower is better)
            if MetricType.ERROR_RATE in current_metrics:
                error_rate = current_metrics[MetricType.ERROR_RATE]
                threshold = self.metric_thresholds[MetricType.ERROR_RATE]
                score = max(0, 1 - (error_rate / threshold.critical_threshold))
                component_scores["error_rate"] = score
            
            # Throughput score (higher is better, up to optimal)
            if MetricType.THROUGHPUT in current_metrics:
                throughput = current_metrics[MetricType.THROUGHPUT]
                threshold = self.metric_thresholds[MetricType.THROUGHPUT]
                optimal_max = threshold.optimal_range[1]
                score = min(1, throughput / optimal_max)
                component_scores["throughput"] = score
            
            # Calculate overall score
            if component_scores:
                overall_score = np.mean(list(component_scores.values()))
            else:
                overall_score = 0.5
            
            # Determine health status
            if overall_score >= 0.9:
                health_status = HealthStatus.EXCELLENT
            elif overall_score >= 0.8:
                health_status = HealthStatus.GOOD
            elif overall_score >= 0.6:
                health_status = HealthStatus.WARNING
            elif overall_score >= 0.4:
                health_status = HealthStatus.DEGRADED
            else:
                health_status = HealthStatus.CRITICAL
            
            # Calculate trends
            trends = {}
            for metric_type in MetricType:
                history = self.metric_history[metric_type]
                if len(history) >= 20:
                    recent_avg = np.mean(list(history)[-10:])
                    older_avg = np.mean(list(history)[-20:-10])
                    if recent_avg > older_avg:
                        trends[metric_type.value] = "improving"
                    elif recent_avg < older_avg:
                        trends[metric_type.value] = "declining"
                    else:
                        trends[metric_type.value] = "stable"
                else:
                    trends[metric_type.value] = "insufficient_data"
            
            # Generate recommendations
            recommendations = []
            if overall_score < 0.7:
                recommendations.append("System performance below optimal - investigate bottlenecks")
            
            if component_scores.get("response_latency", 1) < 0.6:
                recommendations.append("High response latency detected - optimize API performance")
            
            if component_scores.get("error_rate", 0) > 0.1:
                recommendations.append("Elevated error rate - review error logs and fix issues")
            
            if len(self.active_alerts) > 5:
                recommendations.append("Multiple active alerts - prioritize system stability")
            
            # Create reliability score
            score_id = f"score_{uuid.uuid4().hex[:12]}"
            reliability_score = ReliabilityScore(
                score_id=score_id,
                timestamp=datetime.now(),
                overall_score=overall_score,
                component_scores=component_scores,
                health_status=health_status,
                trends=trends,
                recommendations=recommendations
            )
            
            self.reliability_scores.append(reliability_score)
            
            # Keep only recent scores
            if len(self.reliability_scores) > 1000:
                self.reliability_scores = self.reliability_scores[-1000:]
            
        except Exception as e:
            print(f"Reliability score calculation error: {str(e)}")
    
    async def _process_alerts(self):
        """Process active alerts"""
        # Alert processing is handled in _alert_processing
        pass
    
    async def _generate_recommendations(self):
        """Generate system recommendations"""
        # Recommendations are generated in _calculate_reliability_scores
        pass
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        current_metrics = {}
        
        for metric_type in MetricType:
            history = self.metric_history[metric_type]
            if history:
                current_values = list(history)[-10:]  # Last 10 values
                current_metrics[metric_type.value] = {
                    "current_value": current_values[-1],
                    "average_10min": np.mean(current_values),
                    "min_10min": min(current_values),
                    "max_10min": max(current_values),
                    "trend": "stable"  # Would calculate actual trend
                }
        
        return current_metrics
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active system alerts"""
        return [alert.to_dict() for alert in self.active_alerts.values()]
    
    def get_reliability_score(self) -> Optional[Dict[str, Any]]:
        """Get latest reliability score"""
        if self.reliability_scores:
            return self.reliability_scores[-1].to_dict()
        return None
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        latest_score = self.get_reliability_score()
        current_metrics = self.get_current_metrics()
        active_alerts = self.get_active_alerts()
        
        return {
            "overall_health": latest_score["health_status"] if latest_score else "unknown",
            "reliability_score": latest_score["overall_score"] if latest_score else 0,
            "active_alerts_count": len(active_alerts),
            "critical_alerts_count": len([a for a in active_alerts if a["alert_level"] == "critical"]),
            "warning_alerts_count": len([a for a in active_alerts if a["alert_level"] == "warning"]),
            "current_metrics": current_metrics,
            "recommendations": latest_score["recommendations"] if latest_score else [],
            "timestamp": datetime.now().isoformat()
        }
    
    def get_metric_history(self, metric_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical values for a specific metric"""
        try:
            metric_enum = MetricType(metric_type)
            history = self.metric_history[metric_enum]
            
            values = list(history)[-limit:]
            return [
                {
                    "value": value,
                    "timestamp": (datetime.now() - timedelta(seconds=len(values) - i)).isoformat()
                }
                for i, value in enumerate(values)
            ]
        except ValueError:
            return []
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        latest_score = self.get_reliability_score()
        
        return {
            "total_metrics_recorded": sum(len(values) for values in self.metric_values.values()),
            "active_alerts": len(self.active_alerts),
            "reliability_score": latest_score["overall_score"] if latest_score else 0,
            "health_status": latest_score["health_status"].value if latest_score else "unknown",
            "metric_types_tracked": len(self.metric_thresholds),
            "data_points_per_metric": {
                metric_type.value: len(history) 
                for metric_type, history in self.metric_history.items()
            },
            "timestamp": datetime.now().isoformat()
        }

# Global reliability metrics instance
live_reliability_metrics = LiveSystemReliabilityMetrics()
