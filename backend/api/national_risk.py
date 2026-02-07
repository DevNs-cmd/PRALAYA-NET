"""
National Risk Simulation API
POST /national/risk-simulate
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
from dataclasses import asdict

from services.national_digital_twin import national_digital_twin, DisasterType

router = APIRouter(prefix="/national", tags=["national-risk"])

class CascadeSimulationRequest(BaseModel):
    disaster_type: str = Field(..., description="Type of disaster: earthquake, flood, cyclone, fire, terrorism")
    epicenter_lat: float = Field(..., ge=-90, le=90, description="Epicenter latitude")
    epicenter_lon: float = Field(..., ge=-180, le=180, description="Epicenter longitude")
    severity: float = Field(..., ge=0, le=1, description="Disaster severity (0-1)")
    simulation_hours: int = Field(default=72, ge=1, le=168, description="Simulation duration in hours")
    include_economic_impact: bool = Field(default=True, description="Include economic impact analysis")
    affected_districts: Optional[List[str]] = Field(default=None, description="Specific districts to analyze")

class CascadeSimulationResponse(BaseModel):
    simulation_id: str
    timestamp: str
    disaster_info: Dict
    cascading_failure_probability: float
    estimated_population_impact: int
    service_outage_duration_hours: float
    economic_impact_usd: Optional[float]
    affected_nodes_count: int
    total_nodes_count: int
    cascade_timeline: List[Dict]
    affected_districts: List[str]
    national_resilience_before: float
    national_resilience_after: float
    recommended_actions: List[str]

class DistrictImpact(BaseModel):
    district: str
    resilience_before: float
    resilience_after: float
    population_impacted: int
    critical_infrastructure_lost: List[str]
    estimated_recovery_time_hours: float

@router.post("/risk-simulate", response_model=CascadeSimulationResponse)
async def simulate_national_risk(request: CascadeSimulationRequest, background_tasks: BackgroundTasks):
    """
    Simulate cascading infrastructure failures at national scale
    
    This endpoint transforms PRALAYA-NET from a monitoring system into a
    predictive infrastructure consequence engine.
    """
    try:
        # Validate disaster type
        try:
            disaster_type = DisasterType(request.disaster_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid disaster type. Must be one of: {[d.value for d in DisasterType]}"
            )
        
        # Get baseline resilience
        resilience_before = national_digital_twin.get_national_resilience_map()
        national_avg_before = sum(resilience_before.values()) / len(resilience_before)
        
        # Run cascade simulation
        simulation = await national_digital_twin.simulate_cascade(
            disaster_type=disaster_type,
            epicenter_lat=request.epicenter_lat,
            epicenter_lon=request.epicenter_lon,
            severity=request.severity
        )
        
        # Calculate post-disaster resilience
        # Temporarily reduce health scores for affected nodes
        affected_nodes_health = {}
        for node_id in simulation.affected_nodes:
            affected_nodes_health[node_id] = national_digital_twin.nodes[node_id].health_score
            national_digital_twin.nodes[node_id].health_score = 0.1  # Severely damaged
        
        resilience_after = national_digital_twin.get_national_resilience_map()
        national_avg_after = sum(resilience_after.values()) / len(resilience_after)
        
        # Restore health scores
        for node_id, health in affected_nodes_health.items():
            national_digital_twin.nodes[node_id].health_score = health
        
        # Generate recommended actions
        recommended_actions = _generate_response_recommendations(simulation, disaster_type)
        
        # Generate simulation ID
        simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(request)) % 10000:04d}"
        
        # Store simulation results (in production, use database)
        background_tasks.add_task(
            _store_simulation_results,
            simulation_id,
            request.dict(),
            asdict(simulation)
        )
        
        # Trigger alerts if high impact
        if simulation.cascading_failure_probability > 0.3:
            # Alert would be triggered here in production
            print(f"HIGH CASCADE RISK ALERT: {simulation.cascading_failure_probability:.2f} probability")
        
        response = CascadeSimulationResponse(
            simulation_id=simulation_id,
            timestamp=datetime.now().isoformat(),
            disaster_info={
                "type": disaster_type.value,
                "epicenter": {"lat": request.epicenter_lat, "lon": request.epicenter_lon},
                "severity": request.severity,
                "simulation_hours": request.simulation_hours
            },
            cascading_failure_probability=simulation.cascading_failure_probability,
            estimated_population_impact=simulation.estimated_population_impact,
            service_outage_duration_hours=simulation.service_outage_duration_hours,
            economic_impact_usd=simulation.economic_impact_usd if request.include_economic_impact else None,
            affected_nodes_count=len(simulation.affected_nodes),
            total_nodes_count=len(national_digital_twin.nodes),
            cascade_timeline=simulation.cascade_timeline,
            affected_districts=list(set(
                national_digital_twin.nodes[nid].district 
                for nid in simulation.affected_nodes
            )),
            national_resilience_before=national_avg_before,
            national_resilience_after=national_avg_after,
            recommended_actions=recommended_actions
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.get("/district-impacts/{simulation_id}", response_model=List[DistrictImpact])
async def get_district_impacts(simulation_id: str):
    """Get detailed impact analysis by district for a simulation"""
    # In production, retrieve from database
    # For now, return sample data
    return [
        DistrictImpact(
            district="mumbai",
            resilience_before=0.85,
            resilience_after=0.42,
            population_impacted=8294782,
            critical_infrastructure_lost=["mumbai_power_0", "mumbai_hospital_0"],
            estimated_recovery_time_hours=48.0
        ),
        DistrictImpact(
            district="delhi",
            resilience_before=0.82,
            resilience_after=0.78,
            population_impacted=1245671,
            critical_infrastructure_lost=[],
            estimated_recovery_time_hours=12.0
        )
    ]

@router.get("/resilience-map")
async def get_national_resilience_map():
    """Get real-time national resilience heatmap data"""
    resilience_map = national_digital_twin.get_national_resilience_map()
    
    # Add metadata for each district
    enhanced_map = {}
    for district, score in resilience_map.items():
        district_nodes = national_digital_twin.districts.get(district, [])
        total_population = sum(
            national_digital_twin.nodes[nid].population_served 
            for nid in district_nodes
        )
        
        enhanced_map[district] = {
            "resilience_score": score,
            "population_served": total_population,
            "infrastructure_count": len(district_nodes),
            "critical_nodes": [
                nid for nid in district_nodes 
                if national_digital_twin.nodes[nid].criticality_score > 0.8
            ],
            "status": "critical" if score < 0.3 else "warning" if score < 0.6 else "stable"
        }
    
    return enhanced_map

def _generate_response_recommendations(simulation, disaster_type: DisasterType) -> List[str]:
    """Generate AI-powered response recommendations"""
    recommendations = []
    
    if simulation.cascading_failure_probability > 0.5:
        recommendations.append("IMMEDIATE: Activate national emergency response protocol")
        recommendations.append("DEPLOY: Mobile emergency power units to affected districts")
        recommendations.append("ACTIVATE: Cross-district resource sharing agreements")
    
    if simulation.estimated_population_impact > 1000000:
        recommendations.append("BROADCAST: National emergency alert via cell broadcast system")
        recommendations.append("DEPLOY: Medical teams from unaffected districts")
        recommendations.append("ESTABLISH: Temporary shelters and supply distribution points")
    
    if disaster_type == DisasterType.EARTHQUAKE:
        recommendations.append("INSPECT: Critical infrastructure for structural integrity")
        recommendations.append("DEPLOY: Search and rescue teams to high-risk zones")
    elif disaster_type == DisasterType.FLOOD:
        recommendations.append("DEPLOY: Water pumping and drainage equipment")
        recommendations.append("DISTRIBUTE: Emergency water purification units")
    elif disaster_type == DisasterType.CYCLONE:
        recommendations.append("EVACUATE: Low-lying coastal areas immediately")
        recommendations.append("SECURE: Critical infrastructure against wind damage")
    
    # Economic impact recommendations
    if simulation.economic_impact_usd > 100000000:  # > $100M
        recommendations.append("ACTIVATE: National disaster relief fund")
        recommendations.append("DEPLOY: Business continuity assistance teams")
    
    return recommendations

async def _store_simulation_results(simulation_id: str, request_data: Dict, simulation_data: Dict):
    """Store simulation results for historical analysis"""
    # In production, store in database
    # For now, just log
    print(f"Stored simulation {simulation_id}: {len(simulation_data.get('affected_nodes', []))} nodes affected")
