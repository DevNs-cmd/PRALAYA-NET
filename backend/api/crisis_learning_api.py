"""
National Crisis Memory & Learning API
GET /learning/crisis-pattern-match
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
from datetime import datetime

from services.crisis_learning import (
    crisis_learning_engine,
    LearningMetricType,
    CrisisSeverity
)
from services.national_digital_twin import DisasterType

router = APIRouter(prefix="/learning", tags=["crisis-learning"])

class CrisisPatternMatchRequest(BaseModel):
    disaster_type: str = Field(..., description="Type of disaster")
    location: Dict = Field(..., description="Current location {lat, lon, city}")
    severity: str = Field(..., description="Severity level")
    current_predictions: List[str] = Field(default=[], description="Current cascade predictions")

class CrisisEventRecordRequest(BaseModel):
    disaster_type: str = Field(..., description="Type of disaster")
    location: Dict = Field(..., description="Event location {lat, lon, city}")
    severity: str = Field(..., description="Severity level")
    prediction_accuracy: float = Field(ge=0, le=1, description="Prediction accuracy (0-1)")
    actual_cascade_nodes: List[str] = Field(..., description="Actual affected nodes")
    predicted_cascade_nodes: List[str] = Field(..., description="Predicted affected nodes")
    response_actions: List[str] = Field(..., description="Response actions taken")
    response_effectiveness: float = Field(ge=0, le=1, description="Response effectiveness (0-1)")
    recovery_time_hours: float = Field(ge=0, description="Recovery time in hours")
    casualties_prevented: int = Field(ge=0, description="Number of casualties prevented")
    economic_impact_usd: float = Field(ge=0, description="Economic impact in USD")

class PatternMatchResponse(BaseModel):
    similarity_score: float
    matched_events: List[str]
    recommended_strategy: str
    confidence_level: float
    historical_outcomes: Dict[str, Union[float, List[str]]]
    key_factors: List[str]

@router.post("/crisis-pattern-match", response_model=PatternMatchResponse)
async def find_crisis_patterns(request: CrisisPatternMatchRequest):
    """
    Find historical crisis patterns and recommend best strategies
    
    This endpoint creates a learning national crisis brain that improves
    response recommendations based on historical experience.
    """
    try:
        # Validate disaster type
        try:
            disaster_type = DisasterType(request.disaster_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid disaster type. Must be one of: {[dt.value for dt in DisasterType]}"
            )
        
        # Validate severity
        try:
            severity = CrisisSeverity(request.severity.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid severity. Must be one of: {[s.value for s in CrisisSeverity]}"
            )
        
        # Find pattern matches
        pattern_match = await crisis_learning_engine.find_crisis_patterns(
            disaster_type=disaster_type,
            location=request.location,
            severity=severity,
            current_predictions=request.current_predictions
        )
        
        return PatternMatchResponse(
            similarity_score=pattern_match.similarity_score,
            matched_events=pattern_match.matched_events,
            recommended_strategy=pattern_match.recommended_strategy,
            confidence_level=pattern_match.confidence_level,
            historical_outcomes=pattern_match.historical_outcomes,
            key_factors=pattern_match.key_factors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern matching failed: {str(e)}")

@router.post("/record-crisis-event")
async def record_crisis_event(request: CrisisEventRecordRequest):
    """
    Record a crisis event for learning and improvement
    
    This endpoint continuously improves the system's response recommendations
    based on real-world outcomes.
    """
    try:
        # Validate disaster type
        try:
            disaster_type = DisasterType(request.disaster_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid disaster type. Must be one of: {[dt.value for dt in DisasterType]}"
            )
        
        # Validate severity
        try:
            severity = CrisisSeverity(request.severity.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid severity. Must be one of: {[s.value for s in CrisisSeverity]}"
            )
        
        # Record the crisis event
        event_id = await crisis_learning_engine.record_crisis_event(
            disaster_type=disaster_type,
            location=request.location,
            severity=severity,
            prediction_accuracy=request.prediction_accuracy,
            actual_cascade_nodes=request.actual_cascade_nodes,
            predicted_cascade_nodes=request.predicted_cascade_nodes,
            response_actions=request.response_actions,
            response_effectiveness=request.response_effectiveness,
            recovery_time_hours=request.recovery_time_hours,
            casualties_prevented=request.casualties_prevented,
            economic_impact_usd=request.economic_impact_usd
        )
        
        return {
            "event_id": event_id,
            "status": "recorded",
            "message": "Crisis event recorded for learning",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event recording failed: {str(e)}")

@router.get("/learning-statistics")
async def get_learning_statistics():
    """Get crisis learning engine statistics"""
    try:
        stats = crisis_learning_engine.get_learning_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.get("/crisis-memory")
async def get_crisis_memory():
    """Get all recorded crisis events"""
    try:
        events = []
        for event_id, event in crisis_learning_engine.crisis_memory.items():
            events.append({
                "event_id": event_id,
                "disaster_type": event.disaster_type.value,
                "location": event.location,
                "severity": event.severity.value,
                "timestamp": event.timestamp.isoformat(),
                "prediction_accuracy": event.prediction_accuracy,
                "response_effectiveness": event.response_effectiveness,
                "recovery_time_hours": event.recovery_time_hours,
                "casualties_prevented": event.casualties_prevented,
                "economic_impact_usd": event.economic_impact_usd,
                "lessons_learned": event.lessons_learned
            })
        
        return {
            "crisis_events": events,
            "total_events": len(events),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get crisis memory: {str(e)}")

@router.get("/learning-metrics")
async def get_learning_metrics():
    """Get available learning metrics and their weights"""
    return {
        "learning_metrics": [metric.value for metric in LearningMetricType],
        "metric_weights": {
            "prediction_accuracy": 0.25,
            "response_effectiveness": 0.30,
            "cascade_containment": 0.20,
            "recovery_time": 0.15,
            "casualty_reduction": 0.10
        },
        "severity_levels": [severity.value for severity in CrisisSeverity],
        "improvement_areas": [
            "Increase prediction accuracy through better modeling",
            "Improve response coordination and effectiveness",
            "Reduce cascade propagation through proactive stabilization",
            "Minimize recovery time through better resource allocation",
            "Maximize casualty reduction through early warning"
        ]
    }

@router.get("/historical-patterns/{disaster_type}")
async def get_historical_patterns(disaster_type: str):
    """Get historical patterns for a specific disaster type"""
    try:
        # Validate disaster type
        try:
            disaster_type_enum = DisasterType(disaster_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid disaster type. Must be one of: {[dt.value for dt in DisasterType]}"
            )
        
        # Filter events by disaster type
        filtered_events = []
        for event_id, event in crisis_learning_engine.crisis_memory.items():
            if event.disaster_type == disaster_type_enum:
                filtered_events.append({
                    "event_id": event_id,
                    "location": event.location,
                    "severity": event.severity.value,
                    "timestamp": event.timestamp.isoformat(),
                    "prediction_accuracy": event.prediction_accuracy,
                    "response_effectiveness": event.response_effectiveness,
                    "recovery_time_hours": event.recovery_time_hours,
                    "lessons_learned": event.lessons_learned
                })
        
        # Calculate patterns
        if filtered_events:
            avg_effectiveness = sum(e["response_effectiveness"] for e in filtered_events) / len(filtered_events)
            avg_recovery = sum(e["recovery_time_hours"] for e in filtered_events) / len(filtered_events)
            
            # Most common effective actions
            all_actions = []
            for event in crisis_learning_engine.crisis_memory.values():
                if event.disaster_type == disaster_type_enum and event.response_effectiveness > 0.8:
                    all_actions.extend(event.response_actions)
            
            action_counts = {}
            for action in all_actions:
                action_counts[action] = action_counts.get(action, 0) + 1
            
            most_effective_actions = sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        else:
            avg_effectiveness = 0
            avg_recovery = 0
            most_effective_actions = []
        
        return {
            "disaster_type": disaster_type,
            "historical_events": filtered_events,
            "total_events": len(filtered_events),
            "average_response_effectiveness": round(avg_effectiveness, 3),
            "average_recovery_time_hours": round(avg_recovery, 1),
            "most_effective_actions": most_effective_actions,
            "recommended_strategies": [action[0] for action in most_effective_actions]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get historical patterns: {str(e)}")

@router.get("/learning-improvements")
async def get_learning_improvements():
    """Get learning improvement recommendations"""
    try:
        stats = crisis_learning_engine.get_learning_statistics()
        
        if "message" in stats:
            return {"message": "Insufficient data for improvement recommendations"}
        
        improvements = []
        
        # Prediction accuracy improvements
        if stats["average_prediction_accuracy"] < 0.8:
            improvements.append({
                "area": "Prediction Accuracy",
                "current_score": stats["average_prediction_accuracy"],
                "target_score": 0.85,
                "recommendations": [
                    "Enhance infrastructure dependency modeling",
                    "Improve real-time data integration",
                    "Refine cascade propagation algorithms"
                ]
            })
        
        # Response effectiveness improvements
        if stats["average_response_effectiveness"] < 0.8:
            improvements.append({
                "area": "Response Effectiveness",
                "current_score": stats["average_response_effectiveness"],
                "target_score": 0.85,
                "recommendations": [
                    "Optimize resource allocation algorithms",
                    "Improve inter-agency coordination",
                    "Enhance communication systems"
                ]
            })
        
        # Recovery time improvements
        if stats["average_recovery_time_hours"] > 120:  # More than 5 days
            improvements.append({
                "area": "Recovery Time",
                "current_score": stats["average_recovery_time_hours"],
                "target_score": 96,  # 4 days
                "recommendations": [
                    "Pre-position emergency supplies",
                    "Improve infrastructure redundancy",
                    "Enhance repair crew deployment"
                ]
            })
        
        return {
            "improvement_areas": improvements,
            "overall_learning_score": (stats["average_prediction_accuracy"] + stats["average_response_effectiveness"]) / 2,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get improvements: {str(e)}")
