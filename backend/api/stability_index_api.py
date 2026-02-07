"""
API endpoints for Stability Index Service
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.services.stability_index_service import stability_index_service

router = APIRouter(prefix="/api/stability", tags=["Stability Index"])

class StabilityImpactRequest(BaseModel):
    action: str
    impact_magnitude: float

@router.get("/current")
async def get_current_stability():
    """Get current stability index"""
    try:
        stability = stability_index_service.get_current_stability()
        
        if not stability:
            raise HTTPException(status_code=404, detail="No stability data available")
        
        return {
            "stability_index": stability,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stability index: {str(e)}")

@router.get("/history")
async def get_stability_history(limit: int = 100):
    """Get stability index history"""
    try:
        history = stability_index_service.get_stability_history(limit)
        
        return {
            "history": history,
            "total_count": len(history),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stability history: {str(e)}")

@router.get("/factors/{factor}")
async def get_factor_metrics(factor: str, limit: int = 50):
    """Get metrics for a specific stability factor"""
    try:
        metrics = stability_index_service.get_factor_metrics(factor, limit)
        
        if not metrics:
            raise HTTPException(status_code=404, detail=f"No metrics found for factor: {factor}")
        
        return {
            "factor": factor,
            "metrics": metrics,
            "total_count": len(metrics),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get factor metrics: {str(e)}")

@router.get("/alerts")
async def get_stability_alerts():
    """Get stability alerts"""
    try:
        alerts = stability_index_service.get_stability_alerts()
        
        return {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stability alerts: {str(e)}")

@router.post("/simulate-impact")
async def simulate_stability_impact(request: StabilityImpactRequest):
    """Simulate the impact of an action on stability"""
    try:
        impact = await stability_index_service.simulate_stability_impact(
            request.action,
            request.impact_magnitude
        )
        
        return {
            "impact_simulation": impact,
            "action": request.action,
            "impact_magnitude": request.impact_magnitude,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to simulate impact: {str(e)}")

@router.get("/factors")
async def get_all_factors():
    """Get all stability factors with current values"""
    try:
        current_stability = stability_index_service.get_current_stability()
        
        if not current_stability:
            raise HTTPException(status_code=404, detail="No stability data available")
        
        factors = current_stability.get("factors", {})
        
        # Add factor descriptions
        factor_descriptions = {
            "infrastructure_health": "Overall health of infrastructure nodes",
            "cascade_risk": "Risk of cascading failures (inverted for stability)",
            "agent_coordination": "Effectiveness of multi-agent coordination",
            "resource_availability": "Availability of system resources",
            "system_performance": "Overall system performance metrics",
            "external_threats": "External threat levels (inverted for stability)"
        }
        
        enhanced_factors = {}
        for factor_name, value in factors.items():
            enhanced_factors[factor_name] = {
                "value": value,
                "percentage": round(value * 100, 1),
                "description": factor_descriptions.get(factor_name, "Unknown factor"),
                "status": "excellent" if value > 0.9 else "good" if value > 0.7 else "warning" if value > 0.4 else "critical"
            }
        
        return {
            "factors": enhanced_factors,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get factors: {str(e)}")

@router.get("/trends")
async def get_stability_trends():
    """Get stability trends and analytics"""
    try:
        history = stability_index_service.get_stability_history(100)
        
        if not history:
            return {
                "trends": {},
                "analytics": {},
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate trends
        recent_scores = [idx["overall_score"] for idx in history[:20]]  # Last 20 entries
        older_scores = [idx["overall_score"] for idx in history[20:40]] if len(history) > 40 else []
        
        trends = {}
        
        if len(recent_scores) >= 3:
            # Recent trend
            recent_avg = sum(recent_scores) / len(recent_scores)
            if len(older_scores) > 0:
                older_avg = sum(older_scores) / len(older_scores)
                trend_direction = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
                trend_magnitude = abs(recent_avg - older_avg)
            else:
                trend_direction = "stable"
                trend_magnitude = 0
            
            trends["recent"] = {
                "direction": trend_direction,
                "magnitude": round(trend_magnitude, 3),
                "average_score": round(recent_avg, 3),
                "volatility": round(np.std(recent_scores), 3) if len(recent_scores) > 1 else 0
            }
        
        # Level distribution
        level_counts = {}
        for idx in history:
            level = idx.get("level", "unknown")
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # Analytics
        analytics = {
            "total_entries": len(history),
            "level_distribution": level_counts,
            "average_score": round(sum(idx["overall_score"] for idx in history) / len(history), 3),
            "highest_score": max(idx["overall_score"] for idx in history),
            "lowest_score": min(idx["overall_score"] for idx in history),
            "current_trend": history[0].get("trend", "stable") if history else "stable"
        }
        
        return {
            "trends": trends,
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")

@router.get("/dashboard")
async def get_stability_dashboard():
    """Get comprehensive stability dashboard data"""
    try:
        current = stability_index_service.get_current_stability()
        history = stability_index_service.get_stability_history(50)
        alerts = stability_index_service.get_stability_alerts()
        
        if not current:
            raise HTTPException(status_code=404, detail="No stability data available")
        
        # Prepare dashboard data
        dashboard_data = {
            "current_index": current,
            "recent_history": history[:10],  # Last 10 entries
            "alerts": alerts,
            "summary": {
                "status": current.get("level", "unknown"),
                "score": current.get("overall_score", 0),
                "percentage": current.get("percentage", 0),
                "trend": current.get("trend", "stable"),
                "confidence": current.get("confidence", 0)
            },
            "factors": current.get("factors", {}),
            "timestamp": datetime.now().isoformat()
        }
        
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

# Import numpy for trend calculations
import numpy as np
