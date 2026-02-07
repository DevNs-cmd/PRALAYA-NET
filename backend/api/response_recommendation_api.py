"""
Autonomous Response Recommendation API
GET /decision/recommend-response
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from services.response_recommendation import (
    response_recommendation_engine, 
    DisasterType, 
    ResponsePriority,
    EvacuationZoneType,
    ResourceType
)

router = APIRouter(prefix="/decision", tags=["response-recommendation"])

class ResponseRecommendationRequest(BaseModel):
    disaster_type: str = Field(..., description="Type of disaster")
    location: Dict = Field(..., description="Disaster location {lat, lon}")
    severity: float = Field(..., ge=0, le=1, description="Disaster severity (0-1)")
    population_density: float = Field(default=1000, description="People per square kilometer")
    hospital_load: float = Field(default=0.5, ge=0, le=1, description="Current hospital capacity utilization")
    include_cost_analysis: bool = Field(default=True, description="Include cost analysis")
    response_timeframe_hours: int = Field(default=24, description="Response planning timeframe")

class EvacuationZoneResponse(BaseModel):
    zone_id: str
    zone_type: str
    center_lat: float
    center_lon: float
    radius_km: float
    affected_population: int
    evacuation_routes: List[Dict]
    shelter_capacity: int
    estimated_evacuation_time_minutes: int
    priority: str
    risk_factors: List[str]
    infrastructure_at_risk: List[str]

class DroneDeploymentResponse(BaseModel):
    mission_id: str
    drone_type: str
    deployment_location: Dict
    mission_type: str
    priority: str
    flight_path: List[Dict]
    estimated_duration_minutes: int
    bandwidth_requirements: float
    alternative_landing_zones: List[Dict]
    communication_relay_points: List[Dict]

class ResourceAllocationResponse(BaseModel):
    allocation_id: str
    resource_type: str
    quantity: int
    source_location: Dict
    destination_location: Dict
    deployment_priority: str
    estimated_arrival_time_minutes: int
    transportation_method: str
    cost_estimate_usd: float

class ResponseRecommendationResponse(BaseModel):
    recommendation_id: str
    disaster_type: str
    location: Dict
    timestamp: str
    evacuation_zones: List[EvacuationZoneResponse]
    drone_deployments: List[DroneDeploymentResponse]
    resource_allocations: List[ResourceAllocationResponse]
    confidence_score: float
    rationale: List[str]
    execution_timeline: List[Dict]
    total_cost_estimate_usd: Optional[float]
    total_people_affected: int

@router.post("/recommend-response", response_model=ResponseRecommendationResponse)
async def recommend_response(request: ResponseRecommendationRequest, background_tasks: BackgroundTasks):
    """
    Generate autonomous response recommendations
    
    This endpoint transforms PRALAYA-NET from a data viewer into a
    decision intelligence engine for crisis response.
    
    Input:
    - disaster_type: Type of disaster
    - cascade_risk: Risk of cascading failures
    - population_density: People per square kilometer
    - hospital_load: Current hospital capacity utilization
    
    Output:
    - recommended evacuation zones
    - recommended drone deployment paths
    - recommended resource allocation
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
        
        # Generate response recommendations
        recommendation = await response_recommendation_engine.generate_response_recommendations(
            disaster_type=disaster_type,
            location=request.location,
            severity=request.severity,
            population_density=request.population_density,
            hospital_load=request.hospital_load,
            background_tasks=background_tasks
        )
        
        # Calculate total cost and people affected
        total_cost = None
        if request.include_cost_analysis:
            total_cost = sum(
                allocation.cost_estimate_usd 
                for allocation in recommendation.resource_allocations
            )
        
        total_people_affected = sum(
            zone.affected_population 
            for zone in recommendation.evacuation_zones
        )
        
        # Convert to response models
        evacuation_zones = [
            EvacuationZoneResponse(
                zone_id=zone.zone_id,
                zone_type=zone.zone_type.value,
                center_lat=zone.center_lat,
                center_lon=zone.center_lon,
                radius_km=zone.radius_km,
                affected_population=zone.affected_population,
                evacuation_routes=zone.evacuation_routes,
                shelter_capacity=zone.shelter_capacity,
                estimated_evacuation_time_minutes=zone.estimated_evacuation_time_minutes,
                priority=zone.priority.value,
                risk_factors=zone.risk_factors,
                infrastructure_at_risk=zone.infrastructure_at_risk
            )
            for zone in recommendation.evacuation_zones
        ]
        
        drone_deployments = [
            DroneDeploymentResponse(
                mission_id=deployment.mission_id,
                drone_type=deployment.drone_type,
                deployment_location=deployment.deployment_location,
                mission_type=deployment.mission_type,
                priority=deployment.priority.value,
                flight_path=deployment.flight_path,
                estimated_duration_minutes=deployment.estimated_duration_minutes,
                bandwidth_requirements=deployment.bandwidth_requirements,
                alternative_landing_zones=deployment.alternative_landing_zones,
                communication_relay_points=deployment.communication_relay_points
            )
            for deployment in recommendation.drone_deployments
        ]
        
        resource_allocations = [
            ResourceAllocationResponse(
                allocation_id=allocation.allocation_id,
                resource_type=allocation.resource_type.value,
                quantity=allocation.quantity,
                source_location=allocation.source_location,
                destination_location=allocation.destination_location,
                deployment_priority=allocation.deployment_priority.value,
                estimated_arrival_time_minutes=allocation.estimated_arrival_time_minutes,
                transportation_method=allocation.transportation_method,
                cost_estimate_usd=allocation.cost_estimate_usd
            )
            for allocation in recommendation.resource_allocations
        ]
        
        return ResponseRecommendationResponse(
            recommendation_id=recommendation.recommendation_id,
            disaster_type=recommendation.disaster_type.value,
            location=recommendation.location,
            timestamp=recommendation.timestamp.isoformat(),
            evacuation_zones=evacuation_zones,
            drone_deployments=drone_deployments,
            resource_allocations=resource_allocations,
            confidence_score=recommendation.confidence_score,
            rationale=recommendation.rationale,
            execution_timeline=recommendation.execution_timeline,
            total_cost_estimate_usd=total_cost,
            total_people_affected=total_people_affected
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response recommendation failed: {str(e)}")

@router.get("/active-recommendations")
async def get_active_recommendations():
    """Get all currently active response recommendations"""
    try:
        active_recommendations = []
        
        for rec_id, recommendation in response_recommendation_engine.active_recommendations.items():
            # Check if recommendation is still valid (less than 24 hours old)
            age_hours = (datetime.now() - recommendation.timestamp).total_seconds() / 3600
            
            if age_hours < 24:
                active_recommendations.append({
                    "recommendation_id": recommendation.recommendation_id,
                    "disaster_type": recommendation.disaster_type.value,
                    "location": recommendation.location,
                    "timestamp": recommendation.timestamp.isoformat(),
                    "confidence_score": recommendation.confidence_score,
                    "evacuation_zones_count": len(recommendation.evacuation_zones),
                    "drone_deployments_count": len(recommendation.drone_deployments),
                    "resource_allocations_count": len(recommendation.resource_allocations),
                    "age_hours": round(age_hours, 1),
                    "status": "active"
                })
        
        return {
            "active_recommendations": active_recommendations,
            "total_active": len(active_recommendations),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active recommendations: {str(e)}")

@router.get("/recommendation/{recommendation_id}")
async def get_recommendation_details(recommendation_id: str):
    """Get detailed information about a specific recommendation"""
    try:
        recommendation = response_recommendation_engine.active_recommendations.get(recommendation_id)
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        return {
            "recommendation_id": recommendation.recommendation_id,
            "disaster_type": recommendation.disaster_type.value,
            "location": recommendation.location,
            "timestamp": recommendation.timestamp.isoformat(),
            "confidence_score": recommendation.confidence_score,
            "rationale": recommendation.rationale,
            "execution_timeline": recommendation.execution_timeline,
            "evacuation_zones": [
                {
                    "zone_id": zone.zone_id,
                    "zone_type": zone.zone_type.value,
                    "center_lat": zone.center_lat,
                    "center_lon": zone.center_lon,
                    "radius_km": zone.radius_km,
                    "affected_population": zone.affected_population,
                    "estimated_evacuation_time_minutes": zone.estimated_evacuation_time_minutes,
                    "priority": zone.priority.value,
                    "risk_factors": zone.risk_factors,
                    "infrastructure_at_risk": zone.infrastructure_at_risk
                }
                for zone in recommendation.evacuation_zones
            ],
            "drone_deployments": [
                {
                    "mission_id": deployment.mission_id,
                    "drone_type": deployment.drone_type,
                    "deployment_location": deployment.deployment_location,
                    "mission_type": deployment.mission_type,
                    "priority": deployment.priority.value,
                    "estimated_duration_minutes": deployment.estimated_duration_minutes,
                    "bandwidth_requirements": deployment.bandwidth_requirements
                }
                for deployment in recommendation.drone_deployments
            ],
            "resource_allocations": [
                {
                    "allocation_id": allocation.allocation_id,
                    "resource_type": allocation.resource_type.value,
                    "quantity": allocation.quantity,
                    "source_location": allocation.source_location,
                    "destination_location": allocation.destination_location,
                    "deployment_priority": allocation.deployment_priority.value,
                    "estimated_arrival_time_minutes": allocation.estimated_arrival_time_minutes,
                    "transportation_method": allocation.transportation_method,
                    "cost_estimate_usd": allocation.cost_estimate_usd
                }
                for allocation in recommendation.resource_allocations
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation details: {str(e)}")

@router.get("/analytics/performance")
async def get_recommendation_performance():
    """Get performance analytics for response recommendations"""
    try:
        recommendations = response_recommendation_engine.historical_recommendations
        
        if not recommendations:
            return {
                "total_recommendations": 0,
                "average_confidence": 0,
                "disaster_type_distribution": {},
                "average_evacuation_zones": 0,
                "average_drone_deployments": 0,
                "average_resource_allocations": 0
            }
        
        # Calculate analytics
        total_recommendations = len(recommendations)
        average_confidence = sum(rec.confidence_score for rec in recommendations) / total_recommendations
        
        # Disaster type distribution
        disaster_distribution = {}
        for rec in recommendations:
            disaster_type = rec.disaster_type.value
            disaster_distribution[disaster_type] = disaster_distribution.get(disaster_type, 0) + 1
        
        # Average metrics
        avg_evacuation_zones = sum(len(rec.evacuation_zones) for rec in recommendations) / total_recommendations
        avg_drone_deployments = sum(len(rec.drone_deployments) for rec in recommendations) / total_recommendations
        avg_resource_allocations = sum(len(rec.resource_allocations) for rec in recommendations) / total_recommendations
        
        return {
            "total_recommendations": total_recommendations,
            "average_confidence": round(average_confidence, 3),
            "disaster_type_distribution": disaster_distribution,
            "average_evacuation_zones": round(avg_evacuation_zones, 1),
            "average_drone_deployments": round(avg_drone_deployments, 1),
            "average_resource_allocations": round(avg_resource_allocations, 1),
            "last_24h_recommendations": len([
                rec for rec in recommendations
                if (datetime.now() - rec.timestamp).total_seconds() < 86400
            ])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance analytics: {str(e)}")

@router.get("/resource-types/supported")
async def get_supported_resource_types():
    """Get supported resource types for allocation"""
    return {
        "resource_types": [rt.value for rt in ResourceType],
        "resource_descriptions": {
            "medical_teams": "Emergency medical response teams with equipment",
            "search_rescue": "Search and rescue teams with specialized equipment",
            "engineering_corps": "Engineering corps for infrastructure repair",
            "emergency_supplies": "Emergency supply kits (food, water, medical)",
            "transportation": "Transportation assets for evacuation and logistics",
            "communication_equipment": "Communication equipment for emergency networks"
        },
        "deployment_priorities": [priority.value for priority in ResponsePriority],
        "transportation_methods": {
            "air_ambulance": "Medical air transport for critical patients",
            "ground_sar_vehicles": "Search and rescue ground vehicles",
            "heavy_trucks": "Heavy trucks for equipment and supplies",
            "military_airlift": "Military aircraft for rapid deployment",
            "evacuation_buses": "Buses for civilian evacuation",
            "rapid_deployment_vehicles": "Light vehicles for rapid response"
        }
    }

@router.get("/evacuation-zone-types")
async def get_evacuation_zone_types():
    """Get evacuation zone types and their meanings"""
    return {
        "zone_types": [zt.value for zt in EvacuationZoneType],
        "zone_descriptions": {
            "immediate": "Immediate evacuation required - life-threatening conditions",
            "voluntary": "Voluntary evacuation recommended - high risk area",
            "shelter": "Move to designated shelters - moderate risk",
            "monitor": "Monitor situation - low risk area"
        },
        "evacuation_priorities": {
            "immediate": "Evacuate within 30 minutes",
            "voluntary": "Evacuate within 2 hours",
            "shelter": "Move to shelter within 4 hours",
            "monitor": "Stay alert, prepare for possible evacuation"
        }
    }

@router.post("/execute-recommendation/{recommendation_id}")
async def execute_recommendation(recommendation_id: str, background_tasks: BackgroundTasks):
    """
    Execute a specific response recommendation
    
    This would trigger actual deployment of resources in a production system.
    """
    try:
        recommendation = response_recommendation_engine.active_recommendations.get(recommendation_id)
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        # In production, this would coordinate with actual response teams
        # For now, simulate execution
        execution_plan = {
            "recommendation_id": recommendation_id,
            "execution_status": "initiated",
            "timestamp": datetime.now().isoformat(),
            "execution_steps": [
                {
                    "step": 1,
                    "action": "Activate emergency broadcast system",
                    "status": "pending",
                    "estimated_completion": "5 minutes"
                },
                {
                    "step": 2,
                    "action": "Deploy drone reconnaissance missions",
                    "status": "pending",
                    "estimated_completion": "30 minutes"
                },
                {
                    "step": 3,
                    "action": "Initiate evacuation procedures",
                    "status": "pending",
                    "estimated_completion": "1 hour"
                },
                {
                    "step": 4,
                    "action": "Deploy response teams",
                    "status": "pending",
                    "estimated_completion": "2 hours"
                }
            ]
        }
        
        # Trigger background execution
        background_tasks.add_task(
            _execute_response_plan,
            recommendation_id,
            execution_plan
        )
        
        return {
            "status": "execution_initiated",
            "recommendation_id": recommendation_id,
            "execution_plan": execution_plan,
            "message": "Response plan execution has been initiated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

async def _execute_response_plan(recommendation_id: str, execution_plan: Dict):
    """Execute response plan (simulated)"""
    print(f"EXECUTING RESPONSE PLAN: {recommendation_id}")
    
    for step in execution_plan["execution_steps"]:
        # Simulate step execution
        await asyncio.sleep(1)  # Simulate processing time
        step["status"] = "completed"
        print(f"Step {step['step']}: {step['action']} - COMPLETED")
    
    print(f"RESPONSE PLAN EXECUTION COMPLETED: {recommendation_id}")
