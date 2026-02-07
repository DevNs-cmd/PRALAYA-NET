"""
Emergency Broadcast API
POST /emergency/broadcast
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
from datetime import datetime

from services.emergency_broadcast import emergency_broadcast_service, BroadcastType, AlertSeverity, TargetingMode

router = APIRouter(prefix="/emergency", tags=["emergency-broadcast"])

class GeofencedTarget(BaseModel):
    type: str = Field(..., description="Target type: district, radius, polygon, national")
    district: Optional[str] = Field(None, description="District name for district targeting")
    lat: Optional[float] = Field(None, description="Center latitude for radius targeting")
    lon: Optional[float] = Field(None, description="Center longitude for radius targeting")
    radius_km: Optional[float] = Field(None, description="Radius in kilometers for radius targeting")
    polygon_coords: Optional[List[List[float]]] = Field(None, description="Polygon coordinates [[lat, lon], ...]")
    area_km2: Optional[float] = Field(None, description="Area in km² for polygon targeting")
    population: Optional[int] = Field(None, description="Population for targeting")

class EmergencyBroadcastRequest(BaseModel):
    broadcast_type: str = Field(..., description="Broadcast type: cell_broadcast, sms_batch, email_alert")
    severity: str = Field(..., description="Severity: critical, severe, moderate, low")
    title: str = Field(..., description="Alert title")
    content: Dict[str, str] = Field(..., description="Multilingual content {lang: message}")
    targeting_mode: str = Field(..., description="Targeting mode: district, geo_polygon, radius, national")
    target_areas: List[GeofencedTarget] = Field(..., description="Target areas")
    sender: str = Field(default="PRALAYA-NET", description="Sender identifier")
    expiry_hours: int = Field(default=6, description="Expiry time in hours")
    requires_ack: bool = Field(default=False, description="Requires acknowledgment")
    priority: int = Field(default=5, ge=1, le=10, description="Priority 1-10")

class BroadcastResponse(BaseModel):
    message_id: str
    status: str
    timestamp: str
    targeted_population: int
    delivery_results: Dict
    estimated_delivery_time_minutes: int

class BroadcastStatusResponse(BaseModel):
    message_id: str
    status: str
    delivery_progress: Dict[str, int]
    success_rate: float
    estimated_completion: str
    errors: List[str]

@router.post("/broadcast", response_model=BroadcastResponse)
async def send_emergency_broadcast(request: EmergencyBroadcastRequest, background_tasks: BackgroundTasks):
    """
    Send emergency broadcast to targeted population
    
    This endpoint transforms PRALAYA-NET into an operationally usable
    emergency alert system for national authorities.
    """
    try:
        # Validate broadcast type
        try:
            broadcast_type = BroadcastType(request.broadcast_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid broadcast type. Must be one of: {[bt.value for bt in BroadcastType]}"
            )
        
        # Validate severity
        try:
            severity = AlertSeverity(request.severity.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid severity. Must be one of: {[s.value for s in AlertSeverity]}"
            )
        
        # Validate targeting mode
        try:
            targeting_mode = TargetingMode(request.targeting_mode.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid targeting mode. Must be one of: {[tm.value for tm in TargetingMode]}"
            )
        
        # Convert target areas
        target_areas = []
        for area in request.target_areas:
            target_areas.append({
                "type": area.type,
                "district": area.district,
                "lat": area.lat,
                "lon": area.lon,
                "radius_km": area.radius_km,
                "polygon_coords": area.polygon_coords,
                "area_km2": area.area_km2,
                "population": area.population
            })
        
        # Create broadcast request
        broadcast_request = {
            "broadcast_type": broadcast_type.value,
            "severity": severity.value,
            "title": request.title,
            "content": request.content,
            "targeting_mode": targeting_mode.value,
            "target_areas": target_areas,
            "sender": request.sender,
            "expiry_hours": request.expiry_hours,
            "requires_ack": request.requires_ack,
            "priority": request.priority
        }
        
        # Send broadcast
        result = await emergency_broadcast_service.send_emergency_broadcast(
            broadcast_request,
            background_tasks
        )
        
        # Calculate estimated delivery time
        estimated_time = _calculate_delivery_time(broadcast_type, severity, result.get("targeted_population", 0))
        
        return BroadcastResponse(
            message_id=result["message_id"],
            status=result["status"],
            timestamp=result["timestamp"],
            targeted_population=result["targeted_population"],
            delivery_results=result["delivery_results"],
            estimated_delivery_time_minutes=estimated_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Broadcast failed: {str(e)}")

@router.get("/broadcast/{message_id}/status", response_model=BroadcastStatusResponse)
async def get_broadcast_status(message_id: str):
    """Get status of a broadcast message"""
    try:
        # Get broadcast from active broadcasts
        broadcast = emergency_broadcast_service.active_broadcasts.get(message_id)
        if not broadcast:
            raise HTTPException(status_code=404, detail="Broadcast message not found")
        
        # Calculate delivery progress
        delivery_progress = {}
        total_delivered = 0
        total_targeted = 0
        
        # Check cell broadcast delivery
        if broadcast.broadcast_type == BroadcastType.CELL_BROADCAST:
            for provider, result in broadcast.delivery_results.items():
                if result.get("status") == "sent":
                    delivered = result.get("estimated_reach", 0)
                    delivery_progress[f"cell_{provider}"] = delivered
                    total_delivered += delivered
        
        # Check SMS delivery
        if broadcast.broadcast_type == BroadcastType.SMS_BATCH:
            for provider, result in broadcast.delivery_results.items():
                if result.get("status") == "sent":
                    delivered = result.get("numbers_count", 0)
                    delivery_progress[f"sms_{provider}"] = delivered
                    total_delivered += delivered
        
        # Get total targeted population
        total_targeted = await emergency_broadcast_service._estimate_targeted_population(broadcast)
        
        # Calculate success rate
        success_rate = (total_delivered / total_targeted * 100) if total_targeted > 0 else 0
        
        return BroadcastStatusResponse(
            message_id=message_id,
            status="active" if broadcast.expiry_time > datetime.now() else "expired",
            delivery_progress=delivery_progress,
            success_rate=round(success_rate, 2),
            estimated_completion=broadcast.expiry_time.isoformat() if broadcast.expiry_time else None,
            errors=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.get("/broadcast/active")
async def get_active_broadcasts():
    """Get all currently active broadcasts"""
    active_broadcasts = []
    current_time = datetime.now()
    
    for message_id, broadcast in emergency_broadcast_service.active_broadcasts.items():
        if broadcast.expiry_time and broadcast.expiry_time > current_time:
            active_broadcasts.append({
                "message_id": message_id,
                "title": broadcast.title,
                "severity": broadcast.severity.value,
                "broadcast_type": broadcast.broadcast_type.value,
                "targeting_mode": broadcast.targeting_mode.value,
                "timestamp": broadcast.timestamp.isoformat(),
                "expiry_time": broadcast.expiry_time.isoformat(),
                "targeted_population": await emergency_broadcast_service._estimate_targeted_population(broadcast),
                "priority": broadcast.priority
            })
    
    return {
        "active_broadcasts": active_broadcasts,
        "total_active": len(active_broadcasts),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/providers/status")
async def get_telecom_providers_status():
    """Get status of telecom providers"""
    providers_status = {}
    
    for provider, config in emergency_broadcast_service.telecom_providers.items():
        # Simulate provider health check
        import random
        is_healthy = random.random() > 0.05  # 95% uptime
        
        providers_status[provider] = {
            "status": "healthy" if is_healthy else "degraded",
            "rate_limit": config["rate_limit"],
            "last_check": datetime.now().isoformat(),
            "api_endpoint": config["api_endpoint"]
        }
    
    return {
        "providers": providers_status,
        "total_providers": len(providers_status),
        "healthy_providers": sum(1 for p in providers_status.values() if p["status"] == "healthy")
    }

@router.get("/languages/supported")
async def get_supported_languages():
    """Get supported languages for multilingual broadcasting"""
    return {
        "languages": emergency_broadcast_service.language_mappings,
        "primary_languages": ["en", "hi", "bn", "te", "mr", "ta", "gu", "kn", "ml", "pa"],
        "coverage_percentage": {
            "en": 60,  # English speakers
            "hi": 44,  # Hindi speakers
            "bn": 8,   # Bengali speakers
            "te": 7,   # Telugu speakers
            "mr": 7,   # Marathi speakers
            "ta": 6,   # Tamil speakers
            "gu": 4,   # Gujarati speakers
            "kn": 3,   # Kannada speakers
            "ml": 3,   # Malayalam speakers
            "pa": 3    # Punjabi speakers
        }
    }

@router.get("/analytics/delivery")
async def get_delivery_analytics():
    """Get broadcast delivery analytics"""
    logs = emergency_broadcast_service.delivery_logs
    
    if not logs:
        return {
            "total_broadcasts": 0,
            "success_rate": 0,
            "average_delivery_time_minutes": 0,
            "most_used_severity": None,
            "provider_performance": {}
        }
    
    # Calculate analytics
    total_broadcasts = len(logs)
    successful_broadcasts = sum(1 for log in logs if log.get("status") == "completed")
    success_rate = (successful_broadcasts / total_broadcasts * 100) if total_broadcasts > 0 else 0
    
    # Provider performance
    provider_performance = {}
    for log in logs[-100:]:  # Last 100 broadcasts
        delivery_results = log.get("delivery_results", {})
        for provider, result in delivery_results.items():
            if provider not in provider_performance:
                provider_performance[provider] = {"sent": 0, "failed": 0}
            
            if result.get("status") == "sent":
                provider_performance[provider]["sent"] += 1
            else:
                provider_performance[provider]["failed"] += 1
    
    return {
        "total_broadcasts": total_broadcasts,
        "success_rate": round(success_rate, 2),
        "average_delivery_time_minutes": 2.5,  # Simulated
        "provider_performance": provider_performance,
        "last_24h_broadcasts": len([log for log in logs if 
                                    (datetime.now() - datetime.fromisoformat(log["timestamp"])).days < 1])
    }

def _calculate_delivery_time(broadcast_type: BroadcastType, severity: AlertSeverity, population: int) -> int:
    """Calculate estimated delivery time in minutes"""
    base_time = {
        BroadcastType.CELL_BROADCAST: 1,   # 1 minute for cell broadcast
        BroadcastType.SMS_BATCH: 5,        # 5 minutes for SMS batch
        BroadcastType.EMAIL_ALERT: 10,      # 10 minutes for email
        BroadcastType.SOCIAL_MEDIA: 2      # 2 minutes for social media
    }
    
    severity_multiplier = {
        AlertSeverity.CRITICAL: 0.5,  # Faster for critical
        AlertSeverity.SEVERE: 0.8,
        AlertSeverity.MODERATE: 1.0,
        AlertSeverity.LOW: 1.2
    }
    
    population_factor = min(population / 1000000, 2.0)  # Max 2x for large populations
    
    base = base_time.get(broadcast_type, 5)
    multiplier = severity_multiplier.get(severity, 1.0)
    
    return int(base * multiplier * population_factor)
