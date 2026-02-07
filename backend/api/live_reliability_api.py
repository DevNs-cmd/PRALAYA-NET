"""
API endpoints for Live System Reliability Metrics
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.services.live_system_reliability import live_reliability_metrics

router = APIRouter(prefix="/reliability", tags=["system_reliability"])

class MetricValueResponse(BaseModel):
    metric_type: str
    current_value: float
    average_10min: float
    min_10min: float
    max_10min: float
    trend: str

class SystemAlertResponse(BaseModel):
    alert_id: str
    metric_type: str
    alert_level: str
    message: str
    current_value: float
    threshold_value: float
    timestamp: str
    resolved: bool

class ReliabilityScoreResponse(BaseModel):
    score_id: str
    timestamp: str
    overall_score: float
    component_scores: Dict[str, float]
    health_status: str
    trends: Dict[str, str]
    recommendations: List[str]

class SystemHealthResponse(BaseModel):
    overall_health: str
    reliability_score: float
    active_alerts_count: int
    critical_alerts_count: int
    warning_alerts_count: int
    current_metrics: Dict[str, MetricValueResponse]
    recommendations: List[str]
    timestamp: str

class MetricHistoryResponse(BaseModel):
    metric_type: str
    history: List[Dict[str, Any]]
    data_points: int
    timestamp: str

@router.get("/current-metrics")
async def get_current_metrics():
    """Get current system metrics"""
    try:
        metrics = live_reliability_metrics.get_current_metrics()
        
        # Convert to response format
        current_metrics = {}
        for metric_type, metric_data in metrics.items():
            current_metrics[metric_type] = MetricValueResponse(**metric_data)
        
        return {
            "current_metrics": current_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Current metrics retrieval failed: {str(e)}")

@router.get("/alerts/active", response_model=List[SystemAlertResponse])
async def get_active_alerts():
    """Get active system alerts"""
    try:
        alerts = live_reliability_metrics.get_active_alerts()
        return [SystemAlertResponse(**alert) for alert in alerts]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Active alerts retrieval failed: {str(e)}")

@router.get("/reliability-score", response_model=ReliabilityScoreResponse)
async def get_reliability_score():
    """Get latest reliability score"""
    try:
        score = live_reliability_metrics.get_reliability_score()
        
        if not score:
            raise HTTPException(status_code=404, detail="No reliability score available")
        
        return ReliabilityScoreResponse(**score)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reliability score retrieval failed: {str(e)}")

@router.get("/system-health", response_model=SystemHealthResponse)
async def get_system_health():
    """Get overall system health summary"""
    try:
        health = live_reliability_metrics.get_system_health()
        
        # Convert metrics to response format
        current_metrics = {}
        for metric_type, metric_data in health["current_metrics"].items():
            current_metrics[metric_type] = MetricValueResponse(**metric_data)
        
        return SystemHealthResponse(
            overall_health=health["overall_health"],
            reliability_score=health["reliability_score"],
            active_alerts_count=health["active_alerts_count"],
            critical_alerts_count=health["critical_alerts_count"],
            warning_alerts_count=health["warning_alerts_count"],
            current_metrics=current_metrics,
            recommendations=health["recommendations"],
            timestamp=health["timestamp"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System health retrieval failed: {str(e)}")

@router.get("/metrics/{metric_type}/history", response_model=MetricHistoryResponse)
async def get_metric_history(metric_type: str, limit: int = 100):
    """Get historical values for specific metric"""
    try:
        history = live_reliability_metrics.get_metric_history(metric_type, limit)
        
        return MetricHistoryResponse(
            metric_type=metric_type,
            history=history,
            data_points=len(history),
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metric history retrieval failed: {str(e)}")

@router.get("/metrics/all")
async def get_all_metric_types():
    """Get all available metric types"""
    try:
        from backend.services.live_system_reliability import MetricType
        
        metric_types = [metric_type.value for metric_type in MetricType]
        
        # Get current values for each metric type
        current_metrics = live_reliability_metrics.get_current_metrics()
        
        metrics_info = []
        for metric_type in metric_types:
            if metric_type in current_metrics:
                metrics_info.append({
                    "metric_type": metric_type,
                    "current_value": current_metrics[metric_type]["current_value"],
                    "trend": current_metrics[metric_type]["trend"],
                    "status": "normal"
                })
            else:
                metrics_info.append({
                    "metric_type": metric_type,
                    "current_value": None,
                    "trend": "unknown",
                    "status": "no_data"
                })
        
        return {
            "metric_types": metric_types,
            "metrics_info": metrics_info,
            "total_metrics": len(metric_types),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metric types retrieval failed: {str(e)}")

@router.get("/thresholds")
async def get_metric_thresholds():
    """Get metric thresholds configuration"""
    try:
        from backend.services.live_system_reliability import MetricType
        
        thresholds = {}
        for metric_type in MetricType:
            if metric_type in live_reliability_metrics.metric_thresholds:
                threshold = live_reliability_metrics.metric_thresholds[metric_type]
                thresholds[metric_type.value] = {
                    "warning_threshold": threshold.warning_threshold,
                    "critical_threshold": threshold.critical_threshold,
                    "optimal_range": threshold.optimal_range,
                    "measurement_unit": threshold.measurement_unit
                }
        
        return {
            "thresholds": thresholds,
            "total_thresholds": len(thresholds),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Thresholds retrieval failed: {str(e)}")

@router.get("/performance-summary")
async def get_performance_summary():
    """Get performance summary for all metrics"""
    try:
        current_metrics = live_reliability_metrics.get_current_metrics()
        
        summary = {
            "metrics_summary": {},
            "overall_performance": "good",
            "critical_issues": [],
            "recommendations": []
        }
        
        # Analyze each metric
        for metric_type, metric_data in current_metrics.items():
            current_value = metric_data["current_value"]
            avg_value = metric_data["average_10min"]
            
            # Determine performance status
            if metric_type in ["response_latency", "error_rate"]:
                # Higher is worse
                status = "good" if current_value < avg_value * 0.8 else "warning" if current_value < avg_value * 1.2 else "critical"
            else:
                # Lower is worse
                status = "good" if current_value > avg_value * 0.8 else "warning" if current_value > avg_value * 0.6 else "critical"
            
            summary["metrics_summary"][metric_type] = {
                "current_value": current_value,
                "average_10min": avg_value,
                "status": status,
                "trend": metric_data["trend"]
            }
            
            # Track critical issues
            if status == "critical":
                summary["critical_issues"].append(f"{metric_type}: {status}")
        
        # Determine overall performance
        critical_count = len(summary["critical_issues"])
        if critical_count == 0:
            summary["overall_performance"] = "excellent"
        elif critical_count <= 2:
            summary["overall_performance"] = "good"
        elif critical_count <= 4:
            summary["overall_performance"] = "warning"
        else:
            summary["overall_performance"] = "critical"
        
        # Generate recommendations
        if summary["overall_performance"] != "excellent":
            summary["recommendations"].append("Investigate critical metrics immediately")
        
        if any("latency" in issue for issue in summary["critical_issues"]):
            summary["recommendations"].append("Optimize API response times")
        
        if any("error_rate" in issue for issue in summary["critical_issues"]):
            summary["recommendations"].append("Review error logs and fix issues")
        
        summary["timestamp"] = datetime.now().isoformat()
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance summary retrieval failed: {str(e)}")

@router.get("/dashboard-data")
async def get_dashboard_data():
    """Get comprehensive data for dashboard display"""
    try:
        # Get all relevant data
        current_metrics = live_reliability_metrics.get_current_metrics()
        active_alerts = live_reliability_metrics.get_active_alerts()
        reliability_score = live_reliability_metrics.get_reliability_score()
        
        return {
            "metrics": current_metrics,
            "alerts": active_alerts,
            "reliability_score": reliability_score,
            "alert_summary": {
                "total": len(active_alerts),
                "critical": len([a for a in active_alerts if a["alert_level"] == "critical"]),
                "warning": len([a for a in active_alerts if a["alert_level"] == "warning"]),
                "error": len([a for a in active_alerts if a["alert_level"] == "error"])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard data retrieval failed: {str(e)}")

@router.get("/health")
async def get_reliability_health():
    """Get reliability system health"""
    try:
        metrics = live_reliability_metrics.get_system_metrics()
        health = live_reliability_metrics.get_system_health()
        
        return {
            "system_status": "healthy",
            "reliability_score": health["reliability_score"],
            "health_status": health["overall_health"],
            "active_alerts": health["active_alerts_count"],
            "critical_alerts": health["critical_alerts_count"],
            "total_metrics_recorded": metrics["total_metrics_recorded"],
            "metric_types_tracked": metrics["metric_types_tracked"],
            "last_update": datetime.now().isoformat(),
            "components": {
                "metric_collection": "operational",
                "alert_processing": "operational",
                "reliability_scoring": "operational",
                "trend_analysis": "operational"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")
