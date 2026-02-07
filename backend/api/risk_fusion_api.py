"""
Multi-Layer Risk Fusion Intelligence API
GET /risk/unified-field
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from services.risk_fusion import (
    risk_fusion_engine,
    DataSourceType,
    RiskIntensity
)

router = APIRouter(prefix="/risk", tags=["risk-fusion"])

class RiskDataIngestionRequest(BaseModel):
    source_type: str = Field(..., description="Data source type")
    location: Dict = Field(..., description="Location {lat, lon}")
    risk_value: float = Field(ge=0, le=1, description="Risk value (0-1)")
    confidence: float = Field(ge=0, le=1, description="Data confidence (0-1)")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")

@router.get("/unified-field")
async def get_unified_risk_field():
    """
    Get unified risk field map
    
    Returns a real-time intensity surface map combining all data sources
    """
    try:
        # Generate unified risk field
        unified_field = await risk_fusion_engine.generate_unified_risk_field()
        
        # Get field data for visualization
        field_data = risk_fusion_engine.get_risk_field_data(unified_field.field_id)
        
        return field_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk field generation failed: {str(e)}")

@router.post("/ingest-data")
async def ingest_risk_data(request: RiskDataIngestionRequest):
    """
    Ingest new risk data point
    
    Adds new data to the multi-layer risk fusion system
    """
    try:
        # Validate source type
        try:
            source_type = DataSourceType(request.source_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid source type. Must be one of: {[st.value for st in DataSourceType]}"
            )
        
        # Ingest data
        data_id = await risk_fusion_engine.ingest_risk_data(
            source_type=source_type,
            location=request.location,
            risk_value=request.risk_value,
            confidence=request.confidence,
            metadata=request.metadata
        )
        
        return {
            "data_id": data_id,
            "status": "ingested",
            "message": "Risk data point ingested successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data ingestion failed: {str(e)}")

@router.get("/field/{field_id}")
async def get_risk_field(field_id: str):
    """Get specific risk field data"""
    try:
        field_data = risk_fusion_engine.get_risk_field_data(field_id)
        return field_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get risk field: {str(e)}")

@router.get("/fusion-statistics")
async def get_fusion_statistics():
    """Get risk fusion engine statistics"""
    try:
        stats = risk_fusion_engine.get_risk_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.get("/data-sources")
async def get_data_sources():
    """Get supported data sources and their characteristics"""
    return {
        "data_sources": [source_type.value for source_type in DataSourceType],
        "source_descriptions": {
            "satellite": "Satellite imagery and thermal data for large-scale monitoring",
            "weather_forecast": "Meteorological predictions for weather-related risks",
            "infrastructure_loads": "Real-time infrastructure load and health monitoring",
            "citizen_telemetry": "Crowd-sourced sensor data from mobile devices",
            "drone_reconnaissance": "High-resolution aerial surveillance data",
            "seismic_sensors": "Ground-based seismic activity monitoring",
            "social_media": "Social media analysis for emerging crisis signals"
        },
        "fusion_weights": {
            "satellite": 0.25,
            "weather_forecast": 0.20,
            "infrastructure_loads": 0.25,
            "citizen_telemetry": 0.15,
            "drone_reconnaissance": 0.10,
            "seismic_sensors": 0.05
        },
        "risk_intensity_levels": [intensity.value for intensity in RiskIntensity],
        "intensity_thresholds": {
            "low": 0.25,
            "moderate": 0.5,
            "high": 0.75,
            "critical": 1.0
        },
        "grid_resolution": 0.01,  # ~1km
        "coverage_area": {
            "india_bounds": {
                "min_lat": 6.0, "max_lat": 38.0,
                "min_lon": 68.0, "max_lon": 97.0
            },
            "description": "Complete India coverage with 1km resolution"
        }
    }

@router.get("/risk-hotspots")
async def get_risk_hotspots():
    """Get current risk hotspots from unified field"""
    try:
        if not risk_fusion_engine.unified_fields:
            return {"message": "No risk field available"}
        
        latest_field = risk_fusion_engine.unified_fields[-1]
        
        # Find hotspots (high and critical risk areas)
        hotspots = []
        threshold = 0.5  # Moderate and above
        
        for i in range(latest_field.risk_grid.shape[0]):
            for j in range(latest_field.risk_grid.shape[1]):
                risk_value = latest_field.risk_grid[i, j]
                
                if risk_value >= threshold:
                    lat = latest_field.coverage_area["min_lat"] + i * latest_field.grid_resolution
                    lon = latest_field.coverage_area["min_lon"] + j * latest_field.grid_resolution
                    
                    hotspots.append({
                        "location": {"lat": lat, "lon": lon},
                        "risk_value": float(risk_value),
                        "intensity": latest_field.intensity_map[f"{i}_{j}"].value,
                        "grid_coordinates": {"row": i, "col": j}
                    })
        
        # Sort by risk value
        hotspots.sort(key=lambda x: x["risk_value"], reverse=True)
        
        return {
            "hotspots": hotspots[:20],  # Top 20 hotspots
            "total_hotspots": len(hotspots),
            "highest_risk": hotspots[0] if hotspots else None,
            "field_id": latest_field.field_id,
            "timestamp": latest_field.timestamp.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get hotspots: {str(e)}")

@router.get("/temporal-analysis")
async def get_temporal_analysis():
    """Get temporal risk analysis across multiple fields"""
    try:
        if len(risk_fusion_engine.unified_fields) < 2:
            return {"message": "Insufficient data for temporal analysis"}
        
        # Analyze risk trends over time
        temporal_data = []
        
        for field in risk_fusion_engine.unified_fields[-5:]:  # Last 5 fields
            temporal_data.append({
                "timestamp": field.timestamp.isoformat(),
                "overall_risk_score": field.overall_risk_score,
                "highest_risk_value": field.highest_risk_location["risk_value"],
                "data_sources_count": len(field.data_sources)
            })
        
        # Calculate trend
        if len(temporal_data) >= 2:
            recent_scores = [d["overall_risk_score"] for d in temporal_data[-3:]]
            older_scores = [d["overall_risk_score"] for d in temporal_data[:-3]]
            
            if len(recent_scores) > 0 and len(older_scores) > 0:
                recent_avg = sum(recent_scores) / len(recent_scores)
                older_avg = sum(older_scores) / len(older_scores)
                
                if recent_avg > older_avg * 1.1:
                    trend = "increasing"
                elif recent_avg < older_avg * 0.9:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "unknown"
        else:
            trend = "insufficient_data"
        
        return {
            "temporal_data": temporal_data,
            "trend": trend,
            "analysis_period_hours": (
                datetime.fromisoformat(temporal_data[-1]["timestamp"]) - 
                datetime.fromisoformat(temporal_data[0]["timestamp"])
            ).total_seconds() / 3600 if len(temporal_data) >= 2 else 0,
            "risk_volatility": np.std([d["overall_risk_score"] for d in temporal_data]) if len(temporal_data) >= 2 else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Temporal analysis failed: {str(e)}")

@router.get("/source-contribution")
async def get_source_contribution():
    """Get risk contribution by data source"""
    try:
        if not risk_fusion_engine.unified_fields:
            return {"message": "No risk field available"}
        
        latest_field = risk_fusion_engine.unified_fields[-1]
        
        # Calculate contribution by source
        source_contributions = {}
        
        for data_point in risk_fusion_engine.risk_data_points:
            source = data_point.source_type.value
            
            if source not in source_contributions:
                source_contributions[source] = {
                    "data_points": 0,
                    "total_risk": 0,
                    "average_confidence": 0,
                    "fusion_weight": latest_field.fusion_weights.get(source, 0)
                }
            
            source_contributions[source]["data_points"] += 1
            source_contributions[source]["total_risk"] += data_point.risk_value
            source_contributions[source]["average_confidence"] += data_point.confidence
        
        # Calculate averages
        for source in source_contributions:
            if source_contributions[source]["data_points"] > 0:
                source_contributions[source]["average_confidence"] /= source_contributions[source]["data_points"]
                source_contributions[source]["average_risk"] = (
                    source_contributions[source]["total_risk"] / source_contributions[source]["data_points"]
                )
            else:
                source_contributions[source]["average_risk"] = 0
        
        return {
            "source_contributions": source_contributions,
            "field_id": latest_field.field_id,
            "timestamp": latest_field.timestamp.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Source contribution analysis failed: {str(e)}")
