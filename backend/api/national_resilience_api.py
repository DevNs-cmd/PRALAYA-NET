"""
National Resilience Score API
GET /national/resilience-map
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from services.national_resilience import national_resilience_engine

router = APIRouter(prefix="/national", tags=["national-resilience"])

class DistrictResilienceResponse(BaseModel):
    district: str
    overall_score: float
    category_scores: Dict[str, float]
    population_served: int
    infrastructure_health: float
    weather_risk: float
    healthcare_load: float
    telecom_availability: float
    energy_redundancy: float
    timestamp: str
    trend: str
    risk_level: str

class ResilienceHeatmapResponse(BaseModel):
    heatmap_data: List[Dict]
    national_average: float
    critical_districts: int
    timestamp: str

@router.get("/resilience-map", response_model=ResilienceHeatmapResponse)
async def get_resilience_map():
    """
    Get national resilience heatmap data
    
    Returns real-time district-level resilience scores for visualization
    """
    try:
        # Calculate current resilience scores
        await national_resilience_engine.calculate_national_resilience()
        
        # Get heatmap data
        heatmap_data = national_resilience_engine.get_resilience_heatmap_data()
        
        return ResilienceHeatmapResponse(**heatmap_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resilience map: {str(e)}")

@router.get("/resilience/{district}", response_model=DistrictResilienceResponse)
async def get_district_resilience(district: str):
    """Get detailed resilience score for a specific district"""
    try:
        # Ensure resilience scores are calculated
        if not national_resilience_engine.resilience_scores:
            await national_resilience_engine.calculate_national_resilience()
        
        score = national_resilience_engine.resilience_scores.get(district.lower())
        if not score:
            raise HTTPException(status_code=404, detail="District not found")
        
        return DistrictResilienceResponse(
            district=score.district,
            overall_score=score.overall_score,
            category_scores=score.category_scores,
            population_served=score.population_served,
            infrastructure_health=score.infrastructure_health,
            weather_risk=score.weather_risk,
            healthcare_load=score.healthcare_load,
            telecom_availability=score.telecom_availability,
            energy_redundancy=score.energy_redundancy,
            timestamp=score.timestamp.isoformat(),
            trend=score.trend,
            risk_level=score.risk_level
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get district resilience: {str(e)}")

@router.get("/resilience/summary")
async def get_resilience_summary():
    """Get national resilience summary statistics"""
    try:
        # Ensure resilience scores are calculated
        if not national_resilience_engine.resilience_scores:
            await national_resilience_engine.calculate_national_resilience()
        
        scores = list(national_resilience_engine.resilience_scores.values())
        
        if not scores:
            return {"message": "No resilience data available"}
        
        # Calculate statistics
        overall_scores = [s.overall_score for s in scores]
        
        risk_distribution = {
            "critical": len([s for s in scores if s.risk_level == "critical"]),
            "high": len([s for s in scores if s.risk_level == "high"]),
            "medium": len([s for s in scores if s.risk_level == "medium"]),
            "low": len([s for s in scores if s.risk_level == "low"])
        }
        
        trend_distribution = {
            "improving": len([s for s in scores if s.trend == "improving"]),
            "stable": len([s for s in scores if s.trend == "stable"]),
            "declining": len([s for s in scores if s.trend == "declining"])
        }
        
        # Category averages
        category_averages = {}
        if scores:
            for category in scores[0].category_scores.keys():
                category_averages[category] = np.mean([
                    s.category_scores[category] for s in scores
                ])
        
        return {
            "total_districts": len(scores),
            "national_average": np.mean(overall_scores),
            "highest_score": max(overall_scores),
            "lowest_score": min(overall_scores),
            "risk_distribution": risk_distribution,
            "trend_distribution": trend_distribution,
            "category_averages": category_averages,
            "total_population_served": sum(s.population_served for s in scores),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resilience summary: {str(e)}")

@router.get("/resilience/critical-districts")
async def get_critical_districts():
    """Get districts with critical resilience scores"""
    try:
        # Ensure resilience scores are calculated
        if not national_resilience_engine.resilience_scores:
            await national_resilience_engine.calculate_national_resilience()
        
        critical_districts = []
        
        for district, score in national_resilience_engine.resilience_scores.items():
            if score.risk_level in ["critical", "high"]:
                critical_districts.append({
                    "district": district,
                    "resilience_score": score.overall_score,
                    "risk_level": score.risk_level,
                    "population_served": score.population_served,
                    "main_risk_factors": _identify_main_risk_factors(score),
                    "recommended_actions": _get_recommended_actions(score)
                })
        
        # Sort by resilience score (lowest first)
        critical_districts.sort(key=lambda x: x["resilience_score"])
        
        return {
            "critical_districts": critical_districts,
            "total_critical": len([d for d in critical_districts if d["risk_level"] == "critical"]),
            "total_high_risk": len([d for d in critical_districts if d["risk_level"] == "high"]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get critical districts: {str(e)}")

def _identify_main_risk_factors(score) -> List[str]:
    """Identify main risk factors for a district"""
    risk_factors = []
    
    if score.infrastructure_health < 0.5:
        risk_factors.append("Poor infrastructure health")
    
    if score.weather_risk > 0.7:
        risk_factors.append("High weather risk")
    
    if score.healthcare_load > 0.8:
        risk_factors.append("Healthcare system overload")
    
    if score.telecom_availability < 0.6:
        risk_factors.append("Limited telecom connectivity")
    
    if score.energy_redundancy < 0.5:
        risk_factors.append("Insufficient energy redundancy")
    
    return risk_factors

def _get_recommended_actions(score) -> List[str]:
    """Get recommended actions for improving resilience"""
    actions = []
    
    if score.infrastructure_health < 0.5:
        actions.append("Infrastructure reinforcement and maintenance")
    
    if score.healthcare_load > 0.8:
        actions.append("Increase healthcare capacity and resources")
    
    if score.telecom_availability < 0.6:
        actions.append("Expand telecom infrastructure and backup systems")
    
    if score.energy_redundancy < 0.5:
        actions.append("Develop alternative energy sources and grid redundancy")
    
    if score.weather_risk > 0.7:
        actions.append("Enhance weather monitoring and early warning systems")
    
    return actions
