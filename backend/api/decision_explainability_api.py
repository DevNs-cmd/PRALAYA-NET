"""
API endpoints for Decision Explainability Engine
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.services.decision_explainability_engine import decision_explainability_engine, DecisionType

router = APIRouter(prefix="/api/decision", tags=["Decision Explainability"])

class DecisionExplanationRequest(BaseModel):
    intent_id: str
    decision_type: str
    context: Dict[str, Any]

class ImpactUpdateRequest(BaseModel):
    explanation_id: str
    measured_impact: Dict[str, float]

@router.get("/explain/{intent_id}")
async def get_decision_explanation(intent_id: str):
    """Get decision explanation for an intent"""
    try:
        explanation = decision_explainability_engine.get_explanation_by_intent(intent_id)
        
        if not explanation:
            raise HTTPException(status_code=404, detail="No explanation found for this intent")
        
        return {
            "explanation": explanation,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get explanation: {str(e)}")

@router.get("/explain/{explanation_id}")
async def get_explanation_by_id(explanation_id: str):
    """Get explanation by explanation ID"""
    try:
        explanation = decision_explainability_engine.get_explanation(explanation_id)
        
        if not explanation:
            raise HTTPException(status_code=404, detail="Explanation not found")
        
        return {
            "explanation": explanation,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get explanation: {str(e)}")

@router.post("/explain")
async def create_decision_explanation(request: DecisionExplanationRequest):
    """Create a new decision explanation"""
    try:
        # Convert decision type string to enum
        try:
            decision_type = DecisionType(request.decision_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid decision type: {request.decision_type}")
        
        # Generate explanation
        explanation = await decision_explainability_engine.explain_decision(
            request.intent_id,
            decision_type,
            request.context
        )
        
        return {
            "explanation": explanation.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create explanation: {str(e)}")

@router.post("/update-impact")
async def update_measured_impact(request: ImpactUpdateRequest):
    """Update measured impact for an explanation"""
    try:
        await decision_explainability_engine.update_measured_impact(
            request.explanation_id,
            request.measured_impact
        )
        
        return {
            "status": "impact_updated",
            "explanation_id": request.explanation_id,
            "measured_impact": request.measured_impact,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update impact: {str(e)}")

@router.get("/patterns")
async def get_decision_patterns(decision_type: Optional[str] = None):
    """Get decision patterns for learning"""
    try:
        patterns = decision_explainability_engine.get_decision_patterns(decision_type)
        
        return {
            "patterns": patterns,
            "decision_type": decision_type,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get patterns: {str(e)}")

@router.get("/signals")
async def get_signal_history(signal_type: Optional[str] = None, limit: int = 100):
    """Get signal history"""
    try:
        signals = decision_explainability_engine.get_signal_history(signal_type, limit)
        
        return {
            "signals": signals,
            "signal_type": signal_type,
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get signals: {str(e)}")

@router.get("/explanations")
async def get_all_explanations(limit: int = 50):
    """Get all recent explanations"""
    try:
        explanations = []
        
        # Get explanations from the engine
        for exp_id, explanation in decision_explainability_engine.explanations.items():
            explanations.append(explanation.to_dict())
        
        # Sort by timestamp and limit
        explanations.sort(key=lambda x: x["timestamp"], reverse=True)
        recent_explanations = explanations[:limit] if len(explanations) > limit else explanations
        
        return {
            "explanations": recent_explanations,
            "total_count": len(explanations),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get explanations: {str(e)}")

@router.get("/analytics")
async def get_decision_analytics():
    """Get decision analytics and statistics"""
    try:
        explanations = list(decision_explainability_engine.explanations.values())
        
        if not explanations:
            return {
                "total_explanations": 0,
                "decision_types": {},
                "average_confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate statistics
        total_explanations = len(explanations)
        decision_types = {}
        confidence_scores = []
        
        for exp in explanations:
            # Count decision types
            dt = exp.decision_type.value
            decision_types[dt] = decision_types.get(dt, 0) + 1
            
            # Collect confidence scores
            confidence_scores.append(exp.confidence_score)
        
        # Calculate average confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return {
            "total_explanations": total_explanations,
            "decision_types": decision_types,
            "average_confidence": round(avg_confidence, 3),
            "confidence_distribution": {
                "high": len([c for c in confidence_scores if c > 0.8]),
                "medium": len([c for c in confidence_scores if 0.5 <= c <= 0.8]),
                "low": len([c for c in confidence_scores if c < 0.5])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")
