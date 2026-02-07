"""
National Crisis Memory & Learning Engine
Crisis Experience Graph for learning from every disaster event
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import hashlib

from services.national_digital_twin import DisasterType, InfrastructureType

class LearningMetricType(Enum):
    PREDICTION_ACCURACY = "prediction_accuracy"
    RESPONSE_EFFECTIVENESS = "response_effectiveness"
    CASCADE_CONTAINMENT = "cascade_containment"
    RECOVERY_TIME = "recovery_time"
    CASUALTY_REDUCTION = "casualty_reduction"
    ECONOMIC_IMPACT = "economic_impact"

class CrisisSeverity(Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"

@dataclass
class CrisisEvent:
    event_id: str
    disaster_type: DisasterType
    location: Dict
    severity: CrisisSeverity
    timestamp: datetime
    prediction_accuracy: float
    actual_cascade_nodes: List[str]
    predicted_cascade_nodes: List[str]
    response_actions: List[str]
    response_effectiveness: float
    recovery_time_hours: float
    casualties_prevented: int
    economic_impact_usd: float
    lessons_learned: List[str]

@dataclass
class PatternMatch:
    similarity_score: float
    matched_events: List[str]
    recommended_strategy: str
    confidence_level: float
    historical_outcomes: Dict[str, float]
    key_factors: List[str]

class CrisisLearningEngine:
    def __init__(self):
        self.crisis_memory: Dict[str, CrisisEvent] = {}
        self.pattern_matches: Dict[str, List[PatternMatch]] = {}
        self.learning_weights = {
            LearningMetricType.PREDICTION_ACCURACY: 0.25,
            LearningMetricType.RESPONSE_EFFECTIVENESS: 0.30,
            LearningMetricType.CASCADE_CONTAINMENT: 0.20,
            LearningMetricType.RECOVERY_TIME: 0.15,
            LearningMetricType.CASUALTY_REDUCTION: 0.10
        }
        
        # Initialize with historical crisis patterns
        self._initialize_historical_patterns()
    
    def _initialize_historical_patterns(self):
        """Initialize with synthetic historical crisis data for learning"""
        historical_events = [
            # Mumbai Flood 2005 pattern
            CrisisEvent(
                event_id="hist_mumbai_flood_2005",
                disaster_type=DisasterType.FLOOD,
                location={"lat": 19.0760, "lon": 72.8777, "city": "mumbai"},
                severity=CrisisSeverity.CATASTROPHIC,
                timestamp=datetime(2005, 7, 26),
                prediction_accuracy=0.65,
                actual_cascade_nodes=["mumbai_power_0", "mumbai_telecom_0", "mumbai_transport_0"],
                predicted_cascade_nodes=["mumbai_power_0", "mumbai_hospital_0"],
                response_actions=["emergency_broadcast", "hospital_evacuation", "power_grid_isolation"],
                response_effectiveness=0.70,
                recovery_time_hours=168,  # 7 days
                casualties_prevented=5000,
                economic_impact_usd=50000000,
                lessons_learned=[
                    "Telecom redundancy critical for coordination",
                    "Early evacuation reduces casualties by 60%",
                    "Power grid isolation prevents wider cascade"
                ]
            ),
            # Gujarat Earthquake 2001 pattern
            CrisisEvent(
                event_id="hist_gujarat_earthquake_2001",
                disaster_type=DisasterType.EARTHQUAKE,
                location={"lat": 23.2159, "lon": 69.6672, "city": "bhuj"},
                severity=CrisisSeverity.CATASTROPHIC,
                timestamp=datetime(2001, 1, 26),
                prediction_accuracy=0.80,
                actual_cascade_nodes=["gujarat_power_0", "gujarat_hospital_0", "gujarat_water_0"],
                predicted_cascade_nodes=["gujarat_power_0", "gujarat_hospital_0"],
                response_actions=["search_rescue_deployment", "medical_aid", "water_distribution"],
                response_effectiveness=0.85,
                recovery_time_hours=240,  # 10 days
                casualties_prevented=8000,
                economic_impact_usd=80000000,
                lessons_learned=[
                    "Search and rescue within first 6 hours critical",
                    "Medical supply chains must be pre-positioned",
                    "Water systems most vulnerable to seismic damage"
                ]
            ),
            # Chennai Cyclone 2015 pattern
            CrisisEvent(
                event_id="hist_chennai_cyclone_2015",
                disaster_type=DisasterType.CYCLONE,
                location={"lat": 13.0827, "lon": 80.2707, "city": "chennai"},
                severity=CrisisSeverity.SEVERE,
                timestamp=datetime(2015, 11, 12),
                prediction_accuracy=0.75,
                actual_cascade_nodes=["chennai_power_0", "chennai_telecom_0"],
                predicted_cascade_nodes=["chennai_power_0"],
                response_actions=["power_backup_activation", "telecom_redundancy", "evacuation"],
                response_effectiveness=0.90,
                recovery_time_hours=96,  # 4 days
                casualties_prevented=2000,
                economic_impact_usd=30000000,
                lessons_learned=[
                    "Telecom backup systems maintain coordination",
                    "Power redundancy essential for hospitals",
                    "Coastal evacuation reduces impact by 40%"
                ]
            )
        ]
        
        for event in historical_events:
            self.crisis_memory[event.event_id] = event
    
    async def record_crisis_event(self,
                                disaster_type: DisasterType,
                                location: Dict,
                                severity: CrisisSeverity,
                                prediction_accuracy: float,
                                actual_cascade_nodes: List[str],
                                predicted_cascade_nodes: List[str],
                                response_actions: List[str],
                                response_effectiveness: float,
                                recovery_time_hours: float,
                                casualties_prevented: int,
                                economic_impact_usd: float) -> str:
        """Record a new crisis event for learning"""
        event_id = f"crisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(location)) % 10000:04d}"
        
        # Generate lessons learned automatically
        lessons_learned = await self._generate_lessons_learned(
            prediction_accuracy, response_effectiveness, actual_cascade_nodes, predicted_cascade_nodes
        )
        
        event = CrisisEvent(
            event_id=event_id,
            disaster_type=disaster_type,
            location=location,
            severity=severity,
            timestamp=datetime.now(),
            prediction_accuracy=prediction_accuracy,
            actual_cascade_nodes=actual_cascade_nodes,
            predicted_cascade_nodes=predicted_cascade_nodes,
            response_actions=response_actions,
            response_effectiveness=response_effectiveness,
            recovery_time_hours=recovery_time_hours,
            casualties_prevented=casualties_prevented,
            economic_impact_usd=economic_impact_usd,
            lessons_learned=lessons_learned
        )
        
        self.crisis_memory[event_id] = event
        
        return event_id
    
    async def _generate_lessons_learned(self,
                                     prediction_accuracy: float,
                                     response_effectiveness: float,
                                     actual_cascade_nodes: List[str],
                                     predicted_cascade_nodes: List[str]) -> List[str]:
        """Generate lessons learned from crisis outcomes"""
        lessons = []
        
        # Prediction accuracy lessons
        if prediction_accuracy < 0.7:
            lessons.append("Prediction models need improvement for this disaster type")
        elif prediction_accuracy > 0.8:
            lessons.append("High prediction accuracy enables proactive response")
        
        # Response effectiveness lessons
        if response_effectiveness < 0.6:
            lessons.append("Response coordination requires improvement")
        elif response_effectiveness > 0.8:
            lessons.append("Current response strategies highly effective")
        
        # Cascade prediction lessons
        missed_nodes = set(actual_cascade_nodes) - set(predicted_cascade_nodes)
        if missed_nodes:
            lessons.append(f"Unpredicted cascade nodes: {list(missed_nodes)}")
        
        # Recovery time lessons
        if response_effectiveness > 0.8:
            lessons.append("Effective response reduces recovery time")
        
        return lessons
    
    async def find_crisis_patterns(self,
                                 disaster_type: DisasterType,
                                 location: Dict,
                                 severity: CrisisSeverity,
                                 current_predictions: List[str]) -> PatternMatch:
        """Find similar historical crisis patterns and recommend strategies"""
        try:
            # Calculate similarity scores with historical events
            matches = []
            
            for event_id, event in self.crisis_memory.items():
                similarity = await self._calculate_similarity(
                    disaster_type, location, severity, current_predictions, event
                )
                
                if similarity > 0.3:  # Threshold for pattern matching
                    matches.append((event_id, similarity, event))
            
            # Sort by similarity score
            matches.sort(key=lambda x: x[1], reverse=True)
            
            if not matches:
                # No similar patterns found
                return PatternMatch(
                    similarity_score=0.0,
                    matched_events=[],
                    recommended_strategy="STANDARD_RESPONSE_PROTOCOL",
                    confidence_level=0.5,
                    historical_outcomes={},
                    key_factors=["No historical patterns found"]
                )
            
            # Get top matches
            top_matches = matches[:3]
            matched_event_ids = [match[0] for match in top_matches]
            matched_events = [match[2] for match in top_matches]
            
            # Generate recommended strategy based on best historical outcomes
            recommended_strategy = await self._generate_recommended_strategy(matched_events)
            
            # Calculate confidence level
            confidence_level = sum(match[1] for match in top_matches) / len(top_matches)
            
            # Compile historical outcomes
            historical_outcomes = {
                "average_response_effectiveness": sum(e.response_effectiveness for e in matched_events) / len(matched_events),
                "average_recovery_time": sum(e.recovery_time_hours for e in matched_events) / len(matched_events),
                "average_casualties_prevented": sum(e.casualties_prevented for e in matched_events) / len(matched_events),
                "most_effective_actions": await self._find_most_effective_actions(matched_events)
            }
            
            # Identify key factors
            key_factors = await self._identify_key_factors(disaster_type, matched_events)
            
            return PatternMatch(
                similarity_score=matches[0][1],  # Best match score
                matched_events=matched_event_ids,
                recommended_strategy=recommended_strategy,
                confidence_level=confidence_level,
                historical_outcomes=historical_outcomes,
                key_factors=key_factors
            )
            
        except Exception as e:
            raise Exception(f"Pattern matching failed: {str(e)}")
    
    async def _calculate_similarity(self,
                                  disaster_type: DisasterType,
                                  location: Dict,
                                  severity: CrisisSeverity,
                                  current_predictions: List[str],
                                  historical_event: CrisisEvent) -> float:
        """Calculate similarity score between current situation and historical event"""
        similarity_factors = []
        
        # Disaster type similarity
        type_similarity = 1.0 if disaster_type == historical_event.disaster_type else 0.3
        similarity_factors.append(type_similarity)
        
        # Severity similarity
        severity_order = {
            CrisisSeverity.MINOR: 1,
            CrisisSeverity.MODERATE: 2,
            CrisisSeverity.SEVERE: 3,
            CrisisSeverity.CATASTROPHIC: 4
        }
        severity_diff = abs(severity_order[severity] - severity_order[historical_event.severity])
        severity_similarity = max(0, 1 - (severity_diff / 4))
        similarity_factors.append(severity_similarity)
        
        # Location similarity (simplified - same city = 1.0, same region = 0.7, different = 0.3)
        location_similarity = 0.3  # Default
        if location.get("city", "").lower() == historical_event.location.get("city", "").lower():
            location_similarity = 1.0
        elif abs(location.get("lat", 0) - historical_event.location.get("lat", 0)) < 5:
            location_similarity = 0.7
        similarity_factors.append(location_similarity)
        
        # Prediction overlap similarity
        if current_predictions and historical_event.predicted_cascade_nodes:
            overlap = len(set(current_predictions) & set(historical_event.predicted_cascade_nodes))
            union = len(set(current_predictions) | set(historical_event.predicted_cascade_nodes))
            prediction_similarity = overlap / union if union > 0 else 0
            similarity_factors.append(prediction_similarity)
        else:
            similarity_factors.append(0.5)
        
        # Weighted average
        weights = [0.3, 0.25, 0.25, 0.2]
        return sum(factor * weight for factor, weight in zip(similarity_factors, weights))
    
    async def _generate_recommended_strategy(self, matched_events: List[CrisisEvent]) -> str:
        """Generate recommended strategy based on historical outcomes"""
        # Find most effective response actions from matched events
        action_effectiveness = {}
        
        for event in matched_events:
            for action in event.response_actions:
                if action not in action_effectiveness:
                    action_effectiveness[action] = []
                action_effectiveness[action].append(event.response_effectiveness)
        
        # Calculate average effectiveness per action
        avg_effectiveness = {
            action: sum(effectiveness) / len(effectiveness)
            for action, effectiveness in action_effectiveness.items()
        }
        
        # Get top 3 most effective actions
        top_actions = sorted(avg_effectiveness.items(), key=lambda x: x[1], reverse=True)[:3]
        
        strategy = f"RECOMMENDED_ACTIONS: {', '.join([action[0] for action in top_actions])}"
        return strategy
    
    async def _find_most_effective_actions(self, matched_events: List[CrisisEvent]) -> List[str]:
        """Find most effective actions across matched events"""
        action_counts = {}
        
        for event in matched_events:
            if event.response_effectiveness > 0.8:  # Only consider highly effective responses
                for action in event.response_actions:
                    action_counts[action] = action_counts.get(action, 0) + 1
        
        # Sort by frequency
        return [action for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
    
    async def _identify_key_factors(self, disaster_type: DisasterType, matched_events: List[CrisisEvent]) -> List[str]:
        """Identify key factors from matched events"""
        all_lessons = []
        for event in matched_events:
            all_lessons.extend(event.lessons_learned)
        
        # Count frequency of lessons
        lesson_counts = {}
        for lesson in all_lessons:
            lesson_counts[lesson] = lesson_counts.get(lesson, 0) + 1
        
        # Return most common lessons
        return [lesson for lesson, count in sorted(lesson_counts.items(), key=lambda x: x[1], reverse=True)[:3]]
    
    def get_learning_statistics(self) -> Dict:
        """Get learning engine statistics"""
        if not self.crisis_memory:
            return {"message": "No crisis events recorded"}
        
        events = list(self.crisis_memory.values())
        
        # Calculate statistics
        avg_prediction_accuracy = sum(e.prediction_accuracy for e in events) / len(events)
        avg_response_effectiveness = sum(e.response_effectiveness for e in events) / len(events)
        avg_recovery_time = sum(e.recovery_time_hours for e in events) / len(events)
        
        # Disaster type distribution
        disaster_distribution = {}
        for event in events:
            disaster_type = event.disaster_type.value
            disaster_distribution[disaster_type] = disaster_distribution.get(disaster_type, 0) + 1
        
        # Severity distribution
        severity_distribution = {}
        for event in events:
            severity = event.severity.value
            severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
        
        return {
            "total_events_recorded": len(events),
            "average_prediction_accuracy": round(avg_prediction_accuracy, 3),
            "average_response_effectiveness": round(avg_response_effectiveness, 3),
            "average_recovery_time_hours": round(avg_recovery_time, 1),
            "disaster_type_distribution": disaster_distribution,
            "severity_distribution": severity_distribution,
            "total_casualties_prevented": sum(e.casualties_prevented for e in events),
            "total_economic_impact_usd": sum(e.economic_impact_usd for e in events),
            "most_common_lessons": self._get_most_common_lessons(events)
        }
    
    def _get_most_common_lessons(self, events: List[CrisisEvent]) -> List[str]:
        """Get most common lessons across all events"""
        all_lessons = []
        for event in events:
            all_lessons.extend(event.lessons_learned)
        
        lesson_counts = {}
        for lesson in all_lessons:
            lesson_counts[lesson] = lesson_counts.get(lesson, 0) + 1
        
        return [lesson for lesson, count in sorted(lesson_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

# Global instance
crisis_learning_engine = CrisisLearningEngine()
