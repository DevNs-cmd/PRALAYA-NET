"""
Closed-Loop Infrastructure Stabilization System
Continuous monitoring, stabilization, and learning system
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np

class StabilizationPhase(Enum):
    MONITORING = "monitoring"
    RISK_DETECTION = "risk_detection"
    INTENT_GENERATION = "intent_generation"
    AGENT_DEPLOYMENT = "agent_deployment"
    INFRASTRUCTURE_CONTROL = "infrastructure_control"
    STABILIZATION_EVALUATION = "stabilization_evaluation"
    LEARNING_UPDATE = "learning_update"

class StabilizationStatus(Enum):
    STABLE = "stable"
    AT_RISK = "at_risk"
    STABILIZING = "stabilizing"
    FAILED = "failed"
    RECOVERING = "recovering"

@dataclass
class RiskDetection:
    """Risk detection event"""
    detection_id: str
    timestamp: datetime
    risk_type: str
    risk_level: float  # 0-1
    affected_nodes: List[str]
    cascade_probability: float
    risk_factors: Dict[str, float]
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "detection_id": self.detection_id,
            "timestamp": self.timestamp.isoformat(),
            "risk_type": self.risk_type,
            "risk_level": self.risk_level,
            "affected_nodes": self.affected_nodes,
            "cascade_probability": self.cascade_probability,
            "risk_factors": self.risk_factors,
            "confidence": self.confidence
        }

@dataclass
class StabilizationIntent:
    """Machine-enforceable stabilization intent"""
    intent_id: str
    generated_at: datetime
    risk_detection_id: str
    stabilization_actions: List[Dict[str, Any]]
    expected_risk_reduction: float
    execution_priority: int
    resource_requirements: Dict[str, int]
    success_probability: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "generated_at": self.generated_at.isoformat(),
            "risk_detection_id": self.risk_detection_id,
            "stabilization_actions": self.stabilization_actions,
            "expected_risk_reduction": self.expected_risk_reduction,
            "execution_priority": self.execution_priority,
            "resource_requirements": self.resource_requirements,
            "success_probability": self.success_probability
        }

@dataclass
class StabilizationEffectiveness:
    """Stabilization effectiveness metrics"""
    stabilization_id: str
    risk_reduction_delta: float
    infrastructure_recovery_speed: float
    cascade_containment_success: float
    overall_effectiveness: float
    measurement_window_minutes: int
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "stabilization_id": self.stabilization_id,
            "risk_reduction_delta": self.risk_reduction_delta,
            "infrastructure_recovery_speed": self.infrastructure_recovery_speed,
            "cascade_containment_success": self.cascade_containment_success,
            "overall_effectiveness": self.overall_effectiveness,
            "measurement_window_minutes": self.measurement_window_minutes,
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class StabilizationLoop:
    """Complete stabilization loop tracking"""
    loop_id: str
    start_time: datetime
    end_time: Optional[datetime]
    current_phase: StabilizationPhase
    status: StabilizationStatus
    risk_detection: Optional[RiskDetection]
    stabilization_intent: Optional[StabilizationIntent]
    agent_deployments: List[Dict[str, Any]]
    infrastructure_controls: List[Dict[str, Any]]
    effectiveness_metrics: Optional[StabilizationEffectiveness]
    learning_updates: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "loop_id": self.loop_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "current_phase": self.current_phase.value,
            "status": self.status.value,
            "risk_detection": self.risk_detection.to_dict() if self.risk_detection else None,
            "stabilization_intent": self.stabilization_intent.to_dict() if self.stabilization_intent else None,
            "agent_deployments": self.agent_deployments,
            "infrastructure_controls": self.infrastructure_controls,
            "effectiveness_metrics": self.effectiveness_metrics.to_dict() if self.effectiveness_metrics else None,
            "learning_updates": self.learning_updates
        }

class ClosedLoopStabilizationSystem:
    """Closed-loop infrastructure stabilization system"""
    
    def __init__(self):
        self.active_loops: Dict[str, StabilizationLoop] = {}
        self.completed_loops: List[StabilizationLoop] = []
        self.risk_thresholds: Dict[str, float] = {
            "cascade_probability": 0.7,
            "infrastructure_load": 0.85,
            "failure_rate": 0.3
        }
        self.stabilization_history: List[Dict[str, Any]] = []
        self.learning_weights: Dict[str, float] = {
            "risk_reduction": 0.4,
            "recovery_speed": 0.3,
            "cascade_containment": 0.3
        }
        self.effectiveness_history: List[StabilizationEffectiveness] = []
        
        # Start continuous monitoring
        asyncio.create_task(self._continuous_monitoring())
    
    async def _continuous_monitoring(self):
        """Continuous monitoring loop"""
        while True:
            try:
                await self._monitor_infrastructure()
                await asyncio.sleep(5)  # Monitor every 5 seconds
            except Exception as e:
                print(f"Monitoring error: {str(e)}")
                await asyncio.sleep(10)
    
    async def _monitor_infrastructure(self):
        """Monitor infrastructure for risks"""
        # Simulate infrastructure metrics (in real system, would get from sensors)
        current_metrics = await self._get_infrastructure_metrics()
        
        # Check for risk conditions
        risk_detections = await self._detect_risks(current_metrics)
        
        # Process each risk detection
        for risk_detection in risk_detections:
            await self._process_risk_detection(risk_detection)
    
    async def _get_infrastructure_metrics(self) -> Dict[str, Any]:
        """Get current infrastructure metrics"""
        # Simulate metrics (in real system, would get from monitoring systems)
        return {
            "cascade_probability": np.random.uniform(0.1, 0.9),
            "infrastructure_load": np.random.uniform(0.3, 0.95),
            "failure_rate": np.random.uniform(0.05, 0.4),
            "node_health_scores": {
                f"node_{i}": np.random.uniform(0.5, 1.0) for i in range(17)
            },
            "active_agents": 13,
            "system_load": np.random.uniform(0.2, 0.8)
        }
    
    async def _detect_risks(self, metrics: Dict[str, Any]) -> List[RiskDetection]:
        """Detect risks from infrastructure metrics"""
        risk_detections = []
        
        # Check cascade probability risk
        if metrics["cascade_probability"] > self.risk_thresholds["cascade_probability"]:
            risk_detection = RiskDetection(
                detection_id=f"risk_{uuid.uuid4().hex[:12]}",
                timestamp=datetime.now(),
                risk_type="cascade_probability",
                risk_level=metrics["cascade_probability"],
                affected_nodes=[f"node_{i}" for i in range(17) if metrics["node_health_scores"][f"node_{i}"] < 0.7],
                cascade_probability=metrics["cascade_probability"],
                risk_factors={
                    "infrastructure_load": metrics["infrastructure_load"],
                    "failure_rate": metrics["failure_rate"]
                },
                confidence=0.85
            )
            risk_detections.append(risk_detection)
        
        # Check infrastructure load risk
        if metrics["infrastructure_load"] > self.risk_thresholds["infrastructure_load"]:
            risk_detection = RiskDetection(
                detection_id=f"risk_{uuid.uuid4().hex[:12]}",
                timestamp=datetime.now(),
                risk_type="infrastructure_overload",
                risk_level=metrics["infrastructure_load"],
                affected_nodes=[f"node_{i}" for i in range(17) if metrics["node_health_scores"][f"node_{i}"] < 0.6],
                cascade_probability=metrics["cascade_probability"] * 1.2,  # Overload increases cascade risk
                risk_factors={
                    "system_load": metrics["system_load"],
                    "active_agents": metrics["active_agents"]
                },
                confidence=0.9
            )
            risk_detections.append(risk_detection)
        
        return risk_detections
    
    async def _process_risk_detection(self, risk_detection: RiskDetection):
        """Process detected risk through stabilization loop"""
        loop_id = f"loop_{uuid.uuid4().hex[:12]}"
        
        # Create new stabilization loop
        stabilization_loop = StabilizationLoop(
            loop_id=loop_id,
            start_time=datetime.now(),
            end_time=None,
            current_phase=StabilizationPhase.RISK_DETECTION,
            status=StabilizationStatus.AT_RISK,
            risk_detection=risk_detection,
            stabilization_intent=None,
            agent_deployments=[],
            infrastructure_controls=[],
            effectiveness_metrics=None,
            learning_updates=[]
        )
        
        self.active_loops[loop_id] = stabilization_loop
        
        # Process through stabilization phases
        await self._execute_stabilization_loop(stabilization_loop)
    
    async def _execute_stabilization_loop(self, loop: StabilizationLoop):
        """Execute complete stabilization loop"""
        try:
            # Phase 1: Intent Generation
            loop.current_phase = StabilizationPhase.INTENT_GENERATION
            stabilization_intent = await self._generate_stabilization_intent(loop.risk_detection)
            loop.stabilization_intent = stabilization_intent
            
            # Phase 2: Agent Deployment
            loop.current_phase = StabilizationPhase.AGENT_DEPLOYMENT
            agent_deployments = await self._deploy_agents(stabilization_intent)
            loop.agent_deployments = agent_deployments
            
            # Phase 3: Infrastructure Control
            loop.current_phase = StabilizationPhase.INFRASTRUCTURE_CONTROL
            infrastructure_controls = await self._execute_infrastructure_controls(stabilization_intent)
            loop.infrastructure_controls = infrastructure_controls
            
            # Phase 4: Stabilization Evaluation
            loop.current_phase = StabilizationPhase.STABILIZATION_EVALUATION
            effectiveness_metrics = await self._evaluate_stabilization_effectiveness(loop)
            loop.effectiveness_metrics = effectiveness_metrics
            
            # Phase 5: Learning Update
            loop.current_phase = StabilizationPhase.LEARNING_UPDATE
            learning_updates = await self._update_learning_models(loop, effectiveness_metrics)
            loop.learning_updates = learning_updates
            
            # Complete loop
            loop.end_time = datetime.now()
            loop.status = StabilizationStatus.STABLE if effectiveness_metrics.overall_effectiveness > 0.7 else StabilizationStatus.RECOVERING
            
            # Move to completed loops
            self.completed_loops.append(loop)
            del self.active_loops[loop.loop_id]
            
            # Keep only recent completed loops
            if len(self.completed_loops) > 100:
                self.completed_loops = self.completed_loops[-100:]
            
            print(f"✅ Stabilization loop completed: {loop.loop_id}")
            print(f"   Effectiveness: {effectiveness_metrics.overall_effectiveness:.2f}")
            print(f"   Duration: {(loop.end_time - loop.start_time).total_seconds():.1f}s")
            
        except Exception as e:
            loop.status = StabilizationStatus.FAILED
            loop.end_time = datetime.now()
            print(f"❌ Stabilization loop failed: {loop.loop_id} - {str(e)}")
    
    async def _generate_stabilization_intent(self, risk_detection: RiskDetection) -> StabilizationIntent:
        """Generate stabilization intent based on risk detection"""
        # Determine stabilization actions based on risk type
        stabilization_actions = []
        
        if risk_detection.risk_type == "cascade_probability":
            stabilization_actions = [
                {
                    "action_type": "load_redistribution",
                    "target_nodes": risk_detection.affected_nodes[:3],
                    "priority": 1,
                    "expected_impact": 0.6
                },
                {
                    "action_type": "backup_activation",
                    "target_nodes": risk_detection.affected_nodes[:2],
                    "priority": 2,
                    "expected_impact": 0.8
                }
            ]
        elif risk_detection.risk_type == "infrastructure_overload":
            stabilization_actions = [
                {
                    "action_type": "load_shedding",
                    "target_nodes": risk_detection.affected_nodes[:5],
                    "priority": 1,
                    "expected_impact": 0.7
                },
                {
                    "action_type": "resource_reallocation",
                    "target_nodes": risk_detection.affected_nodes[:3],
                    "priority": 2,
                    "expected_impact": 0.5
                }
            ]
        
        # Calculate expected risk reduction
        expected_risk_reduction = sum(action["expected_impact"] for action in stabilization_actions) / len(stabilization_actions)
        
        # Determine resource requirements
        resource_requirements = {
            "infrastructure_control": len(stabilization_actions),
            "monitoring_agents": 2,
            "repair_teams": 1 if risk_detection.risk_level > 0.8 else 0
        }
        
        # Calculate success probability
        success_probability = min(0.95, 0.7 + (1 - risk_detection.risk_level) * 0.25)
        
        return StabilizationIntent(
            intent_id=f"intent_{uuid.uuid4().hex[:12]}",
            generated_at=datetime.now(),
            risk_detection_id=risk_detection.detection_id,
            stabilization_actions=stabilization_actions,
            expected_risk_reduction=expected_risk_reduction,
            execution_priority=1 if risk_detection.risk_level > 0.8 else 2,
            resource_requirements=resource_requirements,
            success_probability=success_probability
        )
    
    async def _deploy_agents(self, intent: StabilizationIntent) -> List[Dict[str, Any]]:
        """Deploy agents for stabilization"""
        deployments = []
        
        # Simulate agent deployment
        for resource_type, quantity in intent.resource_requirements.items():
            if "agent" in resource_type:
                for i in range(quantity):
                    deployment = {
                        "deployment_id": f"deploy_{uuid.uuid4().hex[:8]}",
                        "agent_type": resource_type,
                        "deployment_time": datetime.now().isoformat(),
                        "target_nodes": intent.stabilization_actions[i]["target_nodes"] if i < len(intent.stabilization_actions) else [],
                        "status": "deployed",
                        "estimated_completion": (datetime.now() + timedelta(minutes=15)).isoformat()
                    }
                    deployments.append(deployment)
        
        return deployments
    
    async def _execute_infrastructure_controls(self, intent: StabilizationIntent) -> List[Dict[str, Any]]:
        """Execute infrastructure control actions"""
        controls = []
        
        for action in intent.stabilization_actions:
            control = {
                "control_id": f"control_{uuid.uuid4().hex[:8]}",
                "action_type": action["action_type"],
                "target_nodes": action["target_nodes"],
                "execution_time": datetime.now().isoformat(),
                "status": "executing",
                "expected_completion": (datetime.now() + timedelta(minutes=10)).isoformat(),
                "priority": action["priority"]
            }
            controls.append(control)
        
        return controls
    
    async def _evaluate_stabilization_effectiveness(self, loop: StabilizationLoop) -> StabilizationEffectiveness:
        """Evaluate stabilization effectiveness"""
        # Get post-stabilization metrics
        post_metrics = await self._get_infrastructure_metrics()
        pre_metrics = {
            "cascade_probability": loop.risk_detection.cascade_probability,
            "infrastructure_load": loop.risk_detection.risk_factors.get("infrastructure_load", 0.5),
            "failure_rate": loop.risk_detection.risk_factors.get("failure_rate", 0.2)
        }
        
        # Calculate risk reduction delta
        risk_reduction_delta = pre_metrics["cascade_probability"] - post_metrics["cascade_probability"]
        
        # Calculate infrastructure recovery speed (nodes recovered per minute)
        recovered_nodes = len([node for node in loop.risk_detection.affected_nodes 
                              if post_metrics["node_health_scores"].get(node, 0) > 0.8])
        recovery_speed = recovered_nodes / max(1, (datetime.now() - loop.start_time).total_seconds() / 60)
        
        # Calculate cascade containment success
        cascade_containment_success = 1.0 - post_metrics["cascade_probability"]
        
        # Calculate overall effectiveness using learning weights
        overall_effectiveness = (
            self.learning_weights["risk_reduction"] * risk_reduction_delta +
            self.learning_weights["recovery_speed"] * min(1.0, recovery_speed / 0.5) +
            self.learning_weights["cascade_containment"] * cascade_containment_success
        )
        
        effectiveness = StabilizationEffectiveness(
            stabilization_id=loop.loop_id,
            risk_reduction_delta=risk_reduction_delta,
            infrastructure_recovery_speed=recovery_speed,
            cascade_containment_success=cascade_containment_success,
            overall_effectiveness=overall_effectiveness,
            measurement_window_minutes=int((datetime.now() - loop.start_time).total_seconds() / 60),
            timestamp=datetime.now()
        )
        
        # Store effectiveness for learning
        self.effectiveness_history.append(effectiveness)
        if len(self.effectiveness_history) > 1000:
            self.effectiveness_history = self.effectiveness_history[-1000:]
        
        return effectiveness
    
    async def _update_learning_models(self, loop: StabilizationLoop, effectiveness: StabilizationEffectiveness) -> List[Dict[str, Any]]:
        """Update learning models based on stabilization results"""
        learning_updates = []
        
        # Update learning weights based on effectiveness
        if effectiveness.overall_effectiveness > 0.8:
            # High effectiveness - reinforce current strategy
            learning_updates.append({
                "update_type": "weight_reinforcement",
                "strategy": loop.stabilization_intent.stabilization_actions,
                "effectiveness": effectiveness.overall_effectiveness,
                "timestamp": datetime.now().isoformat()
            })
        elif effectiveness.overall_effectiveness < 0.5:
            # Low effectiveness - adjust weights
            # Increase weight for least effective component
            min_component = min([
                ("risk_reduction", effectiveness.risk_reduction_delta),
                ("recovery_speed", effectiveness.infrastructure_recovery_speed),
                ("cascade_containment", effectiveness.cascade_containment_success)
            ], key=lambda x: x[1])
            
            self.learning_weights[min_component[0]] = min(1.0, self.learning_weights[min_component[0]] + 0.1)
            
            learning_updates.append({
                "update_type": "weight_adjustment",
                "adjusted_component": min_component[0],
                "new_weight": self.learning_weights[min_component[0]],
                "reason": "low_effectiveness",
                "timestamp": datetime.now().isoformat()
            })
        
        # Update risk thresholds based on performance
        if effectiveness.overall_effectiveness > 0.9 and loop.risk_detection.risk_level > 0.8:
            # Very effective at high risk - can lower threshold slightly
            for threshold_type in self.risk_thresholds:
                self.risk_thresholds[threshold_type] *= 0.95
                learning_updates.append({
                    "update_type": "threshold_adjustment",
                    "threshold_type": threshold_type,
                    "new_threshold": self.risk_thresholds[threshold_type],
                    "reason": "high_effectiveness_at_risk",
                    "timestamp": datetime.now().isoformat()
                })
        
        return learning_updates
    
    def get_active_loops(self) -> List[Dict[str, Any]]:
        """Get active stabilization loops"""
        return [loop.to_dict() for loop in self.active_loops.values()]
    
    def get_completed_loops(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get completed stabilization loops"""
        return [loop.to_dict() for loop in self.completed_loops[-limit:]]
    
    def get_system_effectiveness(self) -> Dict[str, Any]:
        """Get overall system effectiveness metrics"""
        if not self.completed_loops:
            return {
                "total_loops": 0,
                "average_effectiveness": 0.0,
                "success_rate": 0.0,
                "average_duration": 0.0
            }
        
        successful_loops = [loop for loop in self.completed_loops if loop.status == StabilizationStatus.STABLE]
        
        effectiveness_scores = [loop.effectiveness_metrics.overall_effectiveness for loop in self.completed_loops if loop.effectiveness_metrics]
        durations = [(loop.end_time - loop.start_time).total_seconds() for loop in self.completed_loops if loop.end_time]
        
        return {
            "total_loops": len(self.completed_loops),
            "successful_loops": len(successful_loops),
            "success_rate": len(successful_loops) / len(self.completed_loops),
            "average_effectiveness": np.mean(effectiveness_scores) if effectiveness_scores else 0.0,
            "average_duration": np.mean(durations) if durations else 0.0,
            "current_risk_thresholds": self.risk_thresholds,
            "learning_weights": self.learning_weights,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time stabilization metrics"""
        return {
            "active_loops": len(self.active_loops),
            "current_phase_distribution": {
                phase.value: len([loop for loop in self.active_loops.values() if loop.current_phase == phase])
                for phase in StabilizationPhase
            },
            "status_distribution": {
                status.value: len([loop for loop in self.active_loops.values() if loop.status == status])
                for status in StabilizationStatus
            },
            "recent_effectiveness": [
                {
                    "loop_id": effect.stabilization_id,
                    "effectiveness": effect.overall_effectiveness,
                    "timestamp": effect.timestamp.isoformat()
                }
                for effect in self.effectiveness_history[-10:]
            ],
            "system_health": {
                "stabilization_success_rate": self.get_system_effectiveness()["success_rate"],
                "average_effectiveness": self.get_system_effectiveness()["average_effectiveness"],
                "active_stabilizations": len(self.active_loops)
            },
            "timestamp": datetime.now().isoformat()
        }

# Global closed-loop stabilization system
closed_loop_stabilization = ClosedLoopStabilizationSystem()
