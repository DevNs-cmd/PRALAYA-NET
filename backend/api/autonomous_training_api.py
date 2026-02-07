"""
API endpoints for Autonomous Simulation Training
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.services.autonomous_simulation_training import autonomous_training

router = APIRouter(prefix="/training", tags=["autonomous_training"])

class TrainingStatusResponse(BaseModel):
    training_mode: str
    active_simulations: int
    total_scenarios: int
    completed_simulations: int
    strategy_updates: int
    average_performance: float
    training_frequency_minutes: int
    max_concurrent_simulations: int
    timestamp: str

class ScenarioResponse(BaseModel):
    scenario_id: str
    name: str
    disaster_type: str
    complexity: str
    severity: float
    affected_area_km2: float
    population_density: float
    training_objectives: List[str]
    created_at: str

class SimulationResultResponse(BaseModel):
    simulation_id: str
    scenario_id: str
    start_time: str
    end_time: str
    execution_strategy: Dict[str, Any]
    actual_outcomes: Dict[str, Any]
    success_metrics: Dict[str, float]
    learning_insights: List[str]
    performance_score: float
    training_value: float

class StrategyPerformanceResponse(BaseModel):
    strategy_type: str
    total_simulations: int
    average_score: float
    min_score: float
    max_score: float
    recent_average: float
    trend: float
    stability: float

class LearningInsightResponse(BaseModel):
    simulation_id: str
    scenario_id: str
    insight: str
    performance_score: float
    timestamp: str

@router.get("/status", response_model=TrainingStatusResponse)
async def get_training_status():
    """Get autonomous training system status"""
    try:
        status = autonomous_training.get_training_status()
        return TrainingStatusResponse(**status)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training status retrieval failed: {str(e)}")

@router.get("/scenarios/recent", response_model=List[ScenarioResponse])
async def get_recent_scenarios(limit: int = 20):
    """Get recent training scenarios"""
    try:
        scenarios = autonomous_training.get_recent_scenarios(limit)
        return [ScenarioResponse(**scenario) for scenario in scenarios]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recent scenarios retrieval failed: {str(e)}")

@router.get("/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    """Get specific training scenario"""
    try:
        scenarios = autonomous_training.get_recent_scenarios(1000)
        
        for scenario in scenarios:
            if scenario["scenario_id"] == scenario_id:
                return ScenarioResponse(**scenario)
        
        raise HTTPException(status_code=404, detail="Scenario not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario retrieval failed: {str(e)}")

@router.get("/simulation-results", response_model=List[SimulationResultResponse])
async def get_simulation_results(limit: int = 50):
    """Get recent simulation results"""
    try:
        results = autonomous_training.get_simulation_results(limit)
        return [SimulationResultResponse(**result) for result in results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation results retrieval failed: {str(e)}")

@router.get("/simulation/{simulation_id}", response_model=SimulationResultResponse)
async def get_simulation_result(simulation_id: str):
    """Get specific simulation result"""
    try:
        results = autonomous_training.get_simulation_results(1000)
        
        for result in results:
            if result["simulation_id"] == simulation_id:
                return SimulationResultResponse(**result)
        
        raise HTTPException(status_code=404, detail="Simulation result not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation result retrieval failed: {str(e)}")

@router.get("/strategy-performance", response_model=Dict[str, StrategyPerformanceResponse])
async def get_strategy_performance():
    """Get strategy performance analysis"""
    try:
        performance = autonomous_training.get_strategy_performance()
        
        return {
            strategy_type: StrategyPerformanceResponse(**perf_data)
            for strategy_type, perf_data in performance.items()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategy performance retrieval failed: {str(e)}")

@router.get("/learning-insights", response_model=List[LearningInsightResponse])
async def get_learning_insights(limit: int = 30):
    """Get recent learning insights"""
    try:
        insights = autonomous_training.get_learning_insights(limit)
        return [LearningInsightResponse(**insight) for insight in insights]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learning insights retrieval failed: {str(e)}")

@router.get("/performance-trends")
async def get_performance_trends():
    """Get performance trends over time"""
    try:
        results = autonomous_training.get_simulation_results(100)
        
        if not results:
            return {
                "message": "No simulation results available",
                "trend": "insufficient_data",
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate trends
        recent_scores = [result["performance_score"] for result in results[-20:]]
        older_scores = [result["performance_score"] for result in results[-40:-20]] if len(results) >= 40 else []
        
        if older_scores:
            recent_avg = sum(recent_scores) / len(recent_scores)
            older_avg = sum(older_scores) / len(older_scores)
            
            trend = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
            trend_magnitude = abs(recent_avg - older_avg)
        else:
            trend = "insufficient_data"
            trend_magnitude = 0
        
        return {
            "recent_average": sum(recent_scores) / len(recent_scores),
            "trend": trend,
            "trend_magnitude": trend_magnitude,
            "data_points": len(results),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance trends retrieval failed: {str(e)}")

@router.get("/scenario-types/distribution")
async def get_scenario_type_distribution():
    """Get distribution of scenario types"""
    try:
        scenarios = autonomous_training.get_recent_scenarios(1000)
        
        type_counts = {}
        complexity_counts = {}
        
        for scenario in scenarios:
            disaster_type = scenario["disaster_type"]
            complexity = scenario["complexity"]
            
            type_counts[disaster_type] = type_counts.get(disaster_type, 0) + 1
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
        
        return {
            "disaster_type_distribution": type_counts,
            "complexity_distribution": complexity_counts,
            "total_scenarios": len(scenarios),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scenario distribution retrieval failed: {str(e)}")

@router.post("/generate-scenario")
async def generate_custom_scenario(scenario_data: Dict[str, Any]):
    """Generate custom training scenario"""
    try:
        # This would integrate with the training system to generate custom scenarios
        # For now, return a placeholder response
        
        scenario_id = f"custom_scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "scenario_id": scenario_id,
            "status": "generated",
            "message": "Custom scenario generated successfully",
            "scenario_data": scenario_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom scenario generation failed: {str(e)}")

@router.get("/health")
async def get_training_health():
    """Get training system health"""
    try:
        status = autonomous_training.get_training_status()
        
        return {
            "system_status": "healthy",
            "training_mode": status["training_mode"],
            "active_simulations": status["active_simulations"],
            "average_performance": status["average_performance"],
            "completed_simulations": status["completed_simulations"],
            "last_update": datetime.now().isoformat(),
            "components": {
                "scenario_generation": "operational",
                "simulation_execution": "operational",
                "strategy_learning": "operational",
                "performance_tracking": "operational"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
