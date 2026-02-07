"""
API endpoints for Digital Twin Cascade Forecast Engine
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.services.digital_twin_cascade_forecast import cascade_forecast_engine

router = APIRouter(prefix="/cascade", tags=["cascade_forecast"])

class CascadePredictionRequest(BaseModel):
    initial_failure_node: str
    failure_mode: str

class CascadePredictionResponse(BaseModel):
    prediction_id: str
    timestamp: str
    initial_failure_node: str
    failure_mode: str
    cascade_probability: float
    predicted_radius_km: float
    affected_nodes: List[str]
    cascade_timeline: List[Dict[str, Any]]
    total_impact_score: float
    confidence: float

class RealTimeProbabilityResponse(BaseModel):
    cascade_probabilities: Dict[str, Dict[str, Any]]
    high_risk_nodes: List[str]
    system_risk_level: str
    timestamp: str

class CriticalNodeResponse(BaseModel):
    node_id: str
    centrality_score: float
    cascade_contribution_score: float
    vulnerability_score: float
    stabilization_priority: float
    recommended_actions: List[str]

class PreStabilizationStrategyResponse(BaseModel):
    strategy_id: str
    target_nodes: List[str]
    stabilization_actions: List[Dict[str, Any]]
    expected_cascade_reduction: float
    implementation_cost: float
    implementation_time_minutes: int
    priority_score: float

class SystemMetricsResponse(BaseModel):
    total_nodes: int
    total_dependencies: int
    active_predictions: int
    critical_nodes_count: int
    available_strategies: int
    system_health: Dict[str, Any]
    timestamp: str

@router.post("/predict", response_model=CascadePredictionResponse)
async def predict_cascade(request: CascadePredictionRequest):
    """Predict cascade failure for specific node"""
    try:
        prediction = await cascade_forecast_engine.predict_cascade(
            request.initial_failure_node,
            request.failure_mode
        )
        
        if "error" in prediction:
            raise HTTPException(status_code=400, detail=prediction["error"])
        
        return CascadePredictionResponse(**prediction)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cascade prediction failed: {str(e)}")

@router.get("/real-time-probability", response_model=RealTimeProbabilityResponse)
async def get_real_time_cascade_probability():
    """Get real-time cascade probability for all nodes"""
    try:
        probabilities = cascade_forecast_engine.get_real_time_cascade_probability()
        return RealTimeProbabilityResponse(**probabilities)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Real-time probability retrieval failed: {str(e)}")

@router.get("/critical-nodes", response_model=List[CriticalNodeResponse])
async def get_critical_nodes(limit: int = 10):
    """Get critical nodes for pre-stabilization"""
    try:
        nodes = cascade_forecast_engine.get_critical_nodes(limit)
        return [CriticalNodeResponse(**node) for node in nodes]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Critical nodes retrieval failed: {str(e)}")

@router.get("/pre-stabilization-strategies", response_model=List[PreStabilizationStrategyResponse])
async def get_pre_stabilization_strategies(limit: int = 5):
    """Get recommended pre-stabilization strategies"""
    try:
        strategies = cascade_forecast_engine.get_pre_stabilization_strategies(limit)
        return [PreStabilizationStrategyResponse(**strategy) for strategy in strategies]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pre-stabilization strategies retrieval failed: {str(e)}")

@router.get("/node/{node_id}/dependencies")
async def get_node_dependencies(node_id: str):
    """Get dependencies for specific node"""
    try:
        # Get node information
        if node_id not in cascade_forecast_engine.nodes:
            raise HTTPException(status_code=404, detail="Node not found")
        
        node = cascade_forecast_engine.nodes[node_id]
        
        # Get dependencies
        dependencies = []
        for dep_id in node.dependencies:
            if dep_id in cascade_forecast_engine.nodes:
                edge_id = f"{dep_id}_{node_id}"
                if edge_id in cascade_forecast_engine.edges:
                    edge = cascade_forecast_engine.edges[edge_id]
                    dependencies.append({
                        "source_node": dep_id,
                        "dependency_type": edge.dependency_type,
                        "failure_propagation_weight": edge.failure_propagation_weight,
                        "recovery_dependency": edge.recovery_dependency,
                        "distance_km": edge.distance_km
                    })
        
        # Get dependents
        dependents = []
        for dep_id in node.dependents:
            if dep_id in cascade_forecast_engine.nodes:
                edge_id = f"{node_id}_{dep_id}"
                if edge_id in cascade_forecast_engine.edges:
                    edge = cascade_forecast_engine.edges[edge_id]
                    dependents.append({
                        "target_node": dep_id,
                        "dependency_type": edge.dependency_type,
                        "failure_propagation_weight": edge.failure_propagation_weight,
                        "recovery_dependency": edge.recovery_dependency,
                        "distance_km": edge.distance_km
                    })
        
        return {
            "node_id": node_id,
            "node_info": node.to_dict(),
            "dependencies": dependencies,
            "dependents": dependents,
            "total_connections": len(dependencies) + len(dependents),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Node dependencies retrieval failed: {str(e)}")

@router.get("/system-metrics", response_model=SystemMetricsResponse)
async def get_system_metrics():
    """Get cascade forecast engine metrics"""
    try:
        metrics = cascade_forecast_engine.get_system_metrics()
        return SystemMetricsResponse(**metrics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System metrics retrieval failed: {str(e)}")

@router.get("/infrastructure-graph")
async def get_infrastructure_graph():
    """Get complete infrastructure dependency graph"""
    try:
        nodes = []
        for node_id, node in cascade_forecast_engine.nodes.items():
            nodes.append(node.to_dict())
        
        edges = []
        for edge_id, edge in cascade_forecast_engine.edges.items():
            edges.append(edge.to_dict())
        
        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "node_types": list(set(node["node_type"] for node in nodes)),
            "dependency_types": list(set(edge["dependency_type"] for edge in edges)),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Infrastructure graph retrieval failed: {str(e)}")

@router.get("/health")
async def get_cascade_forecast_health():
    """Get cascade forecast system health"""
    try:
        metrics = cascade_forecast_engine.get_system_metrics()
        real_time = cascade_forecast_engine.get_real_time_cascade_probability()
        
        return {
            "system_status": "healthy",
            "total_nodes": metrics["total_nodes"],
            "active_predictions": metrics["active_predictions"],
            "high_risk_nodes": len(real_time["high_risk_nodes"]),
            "system_risk_level": real_time["system_risk_level"],
            "last_update": datetime.now().isoformat(),
            "components": {
                "dependency_modeling": "operational",
                "cascade_prediction": "operational",
                "critical_node_analysis": "operational",
                "pre_stabilization": "operational",
                "real_time_monitoring": "operational"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
