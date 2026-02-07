"""
Decision Explainability Engine
Provides detailed reasoning for autonomous decisions
"""

import asyncio
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import numpy as np
from collections import defaultdict

class SignalType(Enum):
    INFRASTRUCTURE_RISK = "infrastructure_risk"
    CASCADE_PROBABILITY = "cascade_probability"
    AGENT_AVAILABILITY = "agent_availability"
    HISTORICAL_PATTERN = "historical_pattern"
    RESOURCE_CONSTRAINTS = "resource_constraints"
    TIME_PRESSURE = "time_pressure"

class DecisionType(Enum):
    STABILIZATION_ACTION = "stabilization_action"
    AGENT_ALLOCATION = "agent_allocation"
    INTENT_GENERATION = "intent_generation"
    EMERGENCY_RESPONSE = "emergency_response"

@dataclass
class DecisionSignal:
    signal_id: str
    signal_type: SignalType
    value: float
    confidence: float
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type.value,
            "value": self.value,
            "confidence": self.confidence,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }

@dataclass
class DecisionAlternative:
    alternative_id: str
    action: str
    expected_impact: float
    confidence: float
    resource_cost: float
    execution_time: int
    risk_level: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alternative_id": self.alternative_id,
            "action": self.action,
            "expected_impact": self.expected_impact,
            "confidence": self.confidence,
            "resource_cost": self.resource_cost,
            "execution_time": self.execution_time,
            "risk_level": self.risk_level
        }

@dataclass
class DecisionExplanation:
    explanation_id: str
    intent_id: str
    decision_type: DecisionType
    signals_used: List[DecisionSignal]
    alternatives_evaluated: List[DecisionAlternative]
    chosen_action: str
    reasoning: str
    predicted_impact: Dict[str, float]
    measured_impact: Optional[Dict[str, float]] = None
    confidence_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "explanation_id": self.explanation_id,
            "intent_id": self.intent_id,
            "decision_type": self.decision_type.value,
            "signals_used": [signal.to_dict() for signal in self.signals_used],
            "alternatives_evaluated": [alt.to_dict() for alt in self.alternatives_evaluated],
            "chosen_action": self.chosen_action,
            "reasoning": self.reasoning,
            "predicted_impact": self.predicted_impact,
            "measured_impact": self.measured_impact,
            "confidence_score": self.confidence_score,
            "timestamp": self.timestamp.isoformat()
        }

class DecisionExplainabilityEngine:
    """Provides detailed reasoning for autonomous decisions"""
    
    def __init__(self):
        self.explanations: Dict[str, DecisionExplanation] = {}
        self.signal_history: List[DecisionSignal] = []
        self.decision_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        
    async def explain_decision(self, intent_id: str, decision_type: DecisionType, 
                             context: Dict[str, Any]) -> DecisionExplanation:
        """Generate detailed explanation for a decision"""
        
        # Collect relevant signals
        signals = await self._collect_decision_signals(context)
        
        # Generate alternatives
        alternatives = await self._generate_alternatives(context)
        
        # Select best action
        chosen_action, reasoning = await self._select_best_action(signals, alternatives, context)
        
        # Predict impact
        predicted_impact = await self._predict_impact(chosen_action, context)
        
        # Calculate confidence
        confidence = await self._calculate_confidence(signals, alternatives, chosen_action)
        
        # Create explanation
        explanation = DecisionExplanation(
            explanation_id=f"exp_{uuid.uuid4().hex[:12]}",
            intent_id=intent_id,
            decision_type=decision_type,
            signals_used=signals,
            alternatives_evaluated=alternatives,
            chosen_action=chosen_action,
            reasoning=reasoning,
            predicted_impact=predicted_impact,
            confidence_score=confidence
        )
        
        self.explanations[explanation.explanation_id] = explanation
        
        # Store decision pattern
        self._store_decision_pattern(explanation)
        
        return explanation
    
    async def _collect_decision_signals(self, context: Dict[str, Any]) -> List[DecisionSignal]:
        """Collect relevant signals for decision making"""
        signals = []
        
        # Infrastructure risk signal
        infrastructure_risk = context.get("infrastructure_risk", 0.5)
        signals.append(DecisionSignal(
            signal_id=f"signal_{uuid.uuid4().hex[:8]}",
            signal_type=SignalType.INFRASTRUCTURE_RISK,
            value=infrastructure_risk,
            confidence=0.9,
            source="infrastructure_monitoring",
            timestamp=datetime.now(),
            metadata={"node_id": context.get("target_node", "unknown")}
        ))
        
        # Cascade probability signal
        cascade_prob = context.get("cascade_probability", 0.3)
        signals.append(DecisionSignal(
            signal_id=f"signal_{uuid.uuid4().hex[:8]}",
            signal_type=SignalType.CASCADE_PROBABILITY,
            value=cascade_prob,
            confidence=0.85,
            source="cascade_forecast",
            timestamp=datetime.now(),
            metadata={"time_horizon": "6_hours"}
        ))
        
        # Agent availability signal
        agent_availability = context.get("agent_availability", 0.7)
        signals.append(DecisionSignal(
            signal_id=f"signal_{uuid.uuid4().hex[:8]}",
            signal_type=SignalType.AGENT_AVAILABILITY,
            value=agent_availability,
            confidence=0.95,
            source="agent_coordination",
            timestamp=datetime.now(),
            metadata={"available_agents": context.get("available_agents", 5)}
        ))
        
        # Historical pattern signal
        historical_match = context.get("historical_pattern_match", 0.6)
        signals.append(DecisionSignal(
            signal_id=f"signal_{uuid.uuid4().hex[:8]}",
            signal_type=SignalType.HISTORICAL_PATTERN,
            value=historical_match,
            confidence=0.8,
            source="crisis_memory",
            timestamp=datetime.now(),
            metadata={"similar_events": context.get("similar_events", 3)}
        ))
        
        # Resource constraints signal
        resource_constraint = context.get("resource_constraint", 0.4)
        signals.append(DecisionSignal(
            signal_id=f"signal_{uuid.uuid4().hex[:8]}",
            signal_type=SignalType.RESOURCE_CONSTRAINTS,
            value=resource_constraint,
            confidence=0.9,
            source="resource_monitoring",
            timestamp=datetime.now(),
            metadata={"resource_type": context.get("resource_type", "technicians")}
        ))
        
        # Time pressure signal
        time_pressure = context.get("time_pressure", 0.8)
        signals.append(DecisionSignal(
            signal_id=f"signal_{uuid.uuid4().hex[:8]}",
            signal_type=SignalType.TIME_PRESSURE,
            value=time_pressure,
            confidence=0.95,
            source="deadline_monitoring",
            timestamp=datetime.now(),
            metadata={"deadline_minutes": context.get("deadline_minutes", 30)}
        ))
        
        # Store signals
        self.signal_history.extend(signals)
        
        return signals
    
    async def _generate_alternatives(self, context: Dict[str, Any]) -> List[DecisionAlternative]:
        """Generate decision alternatives"""
        alternatives = []
        node_type = context.get("node_type", "power")
        
        if node_type == "power":
            alternatives = [
                DecisionAlternative(
                    alternative_id=f"alt_{uuid.uuid4().hex[:8]}",
                    action="load_redistribution",
                    expected_impact=0.15,
                    confidence=0.85,
                    resource_cost=0.3,
                    execution_time=15,
                    risk_level=0.2
                ),
                DecisionAlternative(
                    alternative_id=f"alt_{uuid.uuid4().hex[:8]}",
                    action="backup_activation",
                    expected_impact=0.12,
                    confidence=0.9,
                    resource_cost=0.5,
                    execution_time=10,
                    risk_level=0.1
                ),
                DecisionAlternative(
                    alternative_id=f"alt_{uuid.uuid4().hex[:8]}",
                    action="grid_isolation",
                    expected_impact=0.18,
                    confidence=0.75,
                    resource_cost=0.4,
                    execution_time=20,
                    risk_level=0.3
                )
            ]
        elif node_type == "telecom":
            alternatives = [
                DecisionAlternative(
                    alternative_id=f"alt_{uuid.uuid4().hex[:8]}",
                    action="backup_switching",
                    expected_impact=0.14,
                    confidence=0.9,
                    resource_cost=0.2,
                    execution_time=8,
                    risk_level=0.1
                ),
                DecisionAlternative(
                    alternative_id=f"alt_{uuid.uuid4().hex[:8]}",
                    action="bandwidth_reallocation",
                    expected_impact=0.10,
                    confidence=0.8,
                    resource_cost=0.1,
                    execution_time=5,
                    risk_level=0.05
                )
            ]
        elif node_type == "transport":
            alternatives = [
                DecisionAlternative(
                    alternative_id=f"alt_{uuid.uuid4().hex[:8]}",
                    action="corridor_opening",
                    expected_impact=0.13,
                    confidence=0.85,
                    resource_cost=0.3,
                    execution_time=25,
                    risk_level=0.15
                ),
                DecisionAlternative(
                    alternative_id=f"alt_{uuid.uuid4().hex[:8]}",
                    action="emergency_routing",
                    expected_impact=0.08,
                    confidence=0.9,
                    resource_cost=0.1,
                    execution_time=10,
                    risk_level=0.05
                )
            ]
        else:
            # Default alternatives
            alternatives = [
                DecisionAlternative(
                    alternative_id=f"alt_{uuid.uuid4().hex[:8]}",
                    action="standard_stabilization",
                    expected_impact=0.10,
                    confidence=0.8,
                    resource_cost=0.3,
                    execution_time=15,
                    risk_level=0.2
                )
            ]
        
        return alternatives
    
    async def _select_best_action(self, signals: List[DecisionSignal], 
                                alternatives: List[DecisionAlternative],
                                context: Dict[str, Any]) -> tuple[str, str]:
        """Select best action with reasoning"""
        
        # Calculate weighted scores for alternatives
        best_alternative = None
        best_score = -1
        
        for alt in alternatives:
            # Weight factors
            impact_weight = 0.4
            confidence_weight = 0.3
            cost_weight = 0.2
            risk_weight = 0.1
            
            # Calculate score (lower cost and risk are better)
            cost_score = 1.0 - alt.resource_cost
            risk_score = 1.0 - alt.risk_level
            
            weighted_score = (
                alt.expected_impact * impact_weight +
                alt.confidence * confidence_weight +
                cost_score * cost_weight +
                risk_score * risk_weight
            )
            
            if weighted_score > best_score:
                best_score = weighted_score
                best_alternative = alt
        
        # Generate reasoning
        reasoning = f"Selected {best_alternative.action} based on:\n"
        reasoning += f"- Expected impact: {best_alternative.expected_impact:.2f}\n"
        reasoning += f"- Confidence: {best_alternative.confidence:.2f}\n"
        reasoning += f"- Resource cost: {best_alternative.resource_cost:.2f}\n"
        reasoning += f"- Execution time: {best_alternative.execution_time} minutes\n"
        
        # Add signal-based reasoning
        high_risk = any(s.signal_type == SignalType.INFRASTRUCTURE_RISK and s.value > 0.7 for s in signals)
        if high_risk:
            reasoning += "- High infrastructure risk detected, requiring immediate action\n"
        
        time_critical = any(s.signal_type == SignalType.TIME_PRESSURE and s.value > 0.8 for s in signals)
        if time_critical:
            reasoning += "- Time pressure critical, favoring faster execution\n"
        
        resource_limited = any(s.signal_type == SignalType.RESOURCE_CONSTRAINTS and s.value > 0.6 for s in signals)
        if resource_limited:
            reasoning += "- Resource constraints considered, optimizing for efficiency\n"
        
        return best_alternative.action, reasoning
    
    async def _predict_impact(self, action: str, context: Dict[str, Any]) -> Dict[str, float]:
        """Predict impact of chosen action"""
        
        # Base impact predictions
        base_impacts = {
            "load_redistribution": {"risk_reduction": 0.15, "stability_improvement": 0.12, "cascade_prevention": 0.18},
            "backup_activation": {"risk_reduction": 0.12, "stability_improvement": 0.10, "cascade_prevention": 0.14},
            "grid_isolation": {"risk_reduction": 0.18, "stability_improvement": 0.15, "cascade_prevention": 0.22},
            "backup_switching": {"risk_reduction": 0.14, "stability_improvement": 0.11, "cascade_prevention": 0.16},
            "bandwidth_reallocation": {"risk_reduction": 0.10, "stability_improvement": 0.08, "cascade_prevention": 0.12},
            "corridor_opening": {"risk_reduction": 0.13, "stability_improvement": 0.10, "cascade_prevention": 0.15},
            "emergency_routing": {"risk_reduction": 0.08, "stability_improvement": 0.06, "cascade_prevention": 0.10},
            "standard_stabilization": {"risk_reduction": 0.10, "stability_improvement": 0.08, "cascade_prevention": 0.12}
        }
        
        predicted = base_impacts.get(action, {"risk_reduction": 0.08, "stability_improvement": 0.06, "cascade_prevention": 0.10})
        
        # Adjust based on context
        multiplier = 1.0
        if context.get("infrastructure_risk", 0) > 0.7:
            multiplier *= 1.2  # Higher impact for high-risk situations
        if context.get("cascade_probability", 0) > 0.6:
            multiplier *= 1.1  # Higher impact for cascade prevention
        
        # Apply multiplier
        for key in predicted:
            predicted[key] = min(1.0, predicted[key] * multiplier)
        
        return predicted
    
    async def _calculate_confidence(self, signals: List[DecisionSignal], 
                                 alternatives: List[DecisionAlternative],
                                 chosen_action: str) -> float:
        """Calculate overall confidence in decision"""
        
        # Signal confidence average
        signal_confidence = np.mean([s.confidence for s in signals])
        
        # Alternative confidence
        chosen_alt = next((alt for alt in alternatives if alt.action == chosen_action), None)
        alt_confidence = chosen_alt.confidence if chosen_alt else 0.5
        
        # Signal strength (how strong are the signals)
        signal_strength = np.mean([s.value for s in signals])
        
        # Overall confidence
        overall_confidence = (signal_confidence * 0.4 + alt_confidence * 0.4 + signal_strength * 0.2)
        
        return min(1.0, overall_confidence)
    
    def _store_decision_pattern(self, explanation: DecisionExplanation):
        """Store decision pattern for learning"""
        pattern = {
            "decision_type": explanation.decision_type.value,
            "chosen_action": explanation.chosen_action,
            "signals": [s.signal_type.value for s in explanation.signals_used],
            "confidence": explanation.confidence_score,
            "timestamp": explanation.timestamp.isoformat()
        }
        
        self.decision_patterns[explanation.decision_type.value].append(pattern)
        
        # Keep only recent patterns
        if len(self.decision_patterns[explanation.decision_type.value]) > 100:
            self.decision_patterns[explanation.decision_type.value] = self.decision_patterns[explanation.decision_type.value][-100:]
    
    async def update_measured_impact(self, explanation_id: str, measured_impact: Dict[str, float]):
        """Update explanation with measured impact"""
        if explanation_id in self.explanations:
            self.explanations[explanation_id].measured_impact = measured_impact
    
    def get_explanation(self, explanation_id: str) -> Optional[Dict[str, Any]]:
        """Get explanation by ID"""
        if explanation_id in self.explanations:
            return self.explanations[explanation_id].to_dict()
        return None
    
    def get_explanations_by_intent(self, intent_id: str) -> List[Dict[str, Any]]:
        """Get all explanations for an intent"""
        explanations = [exp for exp in self.explanations.values() if exp.intent_id == intent_id]
        return [exp.to_dict() for exp in explanations]
    
    def get_decision_patterns(self, decision_type: str = None) -> Dict[str, Any]:
        """Get decision patterns"""
        if decision_type:
            return {"patterns": self.decision_patterns.get(decision_type, [])}
        
        return {"patterns": dict(self.decision_patterns)}
    
    def get_signal_history(self, signal_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get signal history"""
        signals = self.signal_history
        
        if signal_type:
            signals = [s for s in signals if s.signal_type.value == signal_type]
        
        # Return recent signals
        recent_signals = signals[-limit:] if len(signals) > limit else signals
        return [signal.to_dict() for signal in recent_signals]

# Global decision explainability engine
decision_explainability_engine = DecisionExplainabilityEngine()
