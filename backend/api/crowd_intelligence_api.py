"""
Crowd-Sensed Intelligence API
POST /crowd/sensor-stream
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, File, UploadFile, Form
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
from datetime import datetime

from services.crowd_intelligence import crowd_intelligence_service, SensorType, AnomalyType

router = APIRouter(prefix="/crowd", tags=["crowd-intelligence"])

class DeviceRegistrationRequest(BaseModel):
    device_id: str = Field(..., description="Unique device identifier")
    device_type: str = Field(default="android", description="Device OS type")
    os_version: str = Field(default="unknown", description="Operating system version")
    app_version: str = Field(default="1.0.0", description="App version")
    sensor_accuracy: Dict[str, float] = Field(default_factory=dict, description="Sensor accuracy specifications")

class SensorReadingData(BaseModel):
    sensor_type: str = Field(..., description="Type of sensor")
    timestamp: str = Field(..., description="ISO timestamp")
    data: Dict = Field(..., description="Sensor data")
    location: Dict = Field(..., description="GPS location {lat, lon, accuracy}")
    confidence: float = Field(default=0.5, ge=0, le=1, description="Reading confidence")
    battery_level: float = Field(default=100, ge=0, le=100, description="Battery percentage")
    network_type: str = Field(default="unknown", description="Network connectivity type")

class SensorStreamRequest(BaseModel):
    device_id: str = Field(..., description="Device identifier")
    readings: List[SensorReadingData] = Field(..., description="Array of sensor readings")

class AnomalyReportResponse(BaseModel):
    report_id: str
    anomaly_type: str
    confidence: float
    location: Dict
    timestamp: str
    verified_by: List[str]
    cluster_id: Optional[str]
    trust_weight: float

class DeviceStatisticsResponse(BaseModel):
    total_devices: int
    active_devices: int
    trust_distribution: Dict[str, int]
    average_trust_score: float
    total_readings_24h: int

@router.post("/register-device")
async def register_device(request: DeviceRegistrationRequest):
    """
    Register a mobile device in the crowd intelligence mesh
    
    This creates a citizen-powered early warning mesh where mobile phones
    become distributed sensors for disaster detection.
    """
    try:
        result = await crowd_intelligence_service.register_device(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Device registration failed: {str(e)}")

@router.post("/sensor-stream", response_model=Dict)
async def ingest_sensor_stream(request: SensorStreamRequest, background_tasks: BackgroundTasks):
    """
    Ingest sensor data stream from mobile devices
    
    Mobile phones send:
    - Accelerometer anomaly spikes (earthquake detection mesh)
    - Camera snapshots for damage classification
    - Connectivity outage signals
    """
    try:
        result = await crowd_intelligence_service.ingest_sensor_stream(
            request.dict(),
            background_tasks
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sensor stream ingestion failed: {str(e)}")

@router.post("/damage-image")
async def ingest_damage_image(
    device_id: str = Form(...),
    image: UploadFile = File(...),
    location_lat: float = Form(...),
    location_lon: float = Form(...),
    location_accuracy: float = Form(default=10.0),
    timestamp: str = Form(default_factory=lambda: datetime.now().isoformat())
):
    """
    Upload camera images for damage classification
    
    Citizens can upload photos of infrastructure damage for AI analysis
    and verification by other nearby devices.
    """
    try:
        metadata = {
            "location": {
                "lat": location_lat,
                "lon": location_lon,
                "accuracy": location_accuracy
            },
            "timestamp": timestamp
        }
        
        result = await crowd_intelligence_service.ingest_damage_image(
            device_id, image, metadata
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@router.get("/anomaly-map")
async def get_anomaly_map():
    """
    Get real-time anomaly map from crowd intelligence
    
    Returns clustered anomaly reports with verification status
    """
    try:
        anomaly_map = crowd_intelligence_service.get_anomaly_map()
        return anomaly_map
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get anomaly map: {str(e)}")

@router.get("/device-statistics", response_model=DeviceStatisticsResponse)
async def get_device_statistics():
    """
    Get statistics about registered devices and trust distribution
    """
    try:
        stats = crowd_intelligence_service.get_device_statistics()
        return DeviceStatisticsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.get("/anomalies/recent")
async def get_recent_anomalies(
    hours: int = 1,
    anomaly_type: Optional[str] = None,
    verified_only: bool = False
):
    """
    Get recent anomaly reports with filtering options
    """
    try:
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_anomalies = []
        for anomaly in crowd_intelligence_service.anomaly_reports:
            if anomaly.timestamp < cutoff_time:
                continue
            
            if anomaly_type and anomaly.anomaly_type.value != anomaly_type:
                continue
            
            if verified_only and len(anomaly.verified_by) == 0:
                continue
            
            recent_anomalies.append({
                "report_id": anomaly.report_id,
                "device_id": anomaly.device_id,
                "anomaly_type": anomaly.anomaly_type.value,
                "confidence": anomaly.confidence,
                "location": anomaly.location,
                "timestamp": anomaly.timestamp.isoformat(),
                "verified_by": anomaly.verified_by,
                "cluster_id": anomaly.cluster_id,
                "trust_weight": anomaly.trust_weight,
                "verified": len(anomaly.verified_by) > 0
            })
        
        return {
            "anomalies": recent_anomalies,
            "total_count": len(recent_anomalies),
            "verified_count": len([a for a in recent_anomalies if a["verified"]]),
            "filter_hours": hours,
            "anomaly_type_filter": anomaly_type,
            "verified_only": verified_only
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent anomalies: {str(e)}")

@router.get("/clusters/active")
async def get_active_clusters():
    """
    Get currently active anomaly clusters
    
    Clusters represent multiple devices reporting similar anomalies
    in the same geographic area and time window.
    """
    try:
        active_clusters = []
        
        for cluster_id, anomalies in crowd_intelligence_service.anomaly_clusters.items():
            # Check if cluster is recent (last 2 hours)
            recent_anomalies = [
                a for a in anomalies 
                if (datetime.now() - a.timestamp).total_seconds() < 7200
            ]
            
            if len(recent_anomalies) >= 2:  # At least 2 recent reports
                cluster_info = {
                    "cluster_id": cluster_id,
                    "anomaly_types": list(set(a.anomaly_type.value for a in recent_anomalies)),
                    "device_count": len(set(a.device_id for a in recent_anomalies)),
                    "average_confidence": sum(a.confidence for a in recent_anomalies) / len(recent_anomalies),
                    "location": {
                        "lat": sum(a.location.get("lat", 0) for a in recent_anomalies) / len(recent_anomalies),
                        "lon": sum(a.location.get("lon", 0) for a in recent_anomalies) / len(recent_anomalies)
                    },
                    "latest_report": max(a.timestamp for a in recent_anomalies).isoformat(),
                    "verified": any(len(a.verified_by) > 0 for a in recent_anomalies),
                    "severity": "high" if len(recent_anomalies) >= 5 else "moderate"
                }
                active_clusters.append(cluster_info)
        
        return {
            "active_clusters": active_clusters,
            "total_clusters": len(active_clusters),
            "high_priority_clusters": len([c for c in active_clusters if c["severity"] == "high"]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active clusters: {str(e)}")

@router.get("/device/{device_id}/trust-score")
async def get_device_trust_score(device_id: str):
    """
    Get trust score and level for a specific device
    """
    try:
        device = crowd_intelligence_service.devices.get(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        return {
            "device_id": device_id,
            "trust_score": device.trust_score,
            "trust_level": device.trust_level.value,
            "reputation_score": device.reputation_score,
            "registration_time": device.registration_time.isoformat(),
            "last_active": device.last_active.isoformat(),
            "total_reports": len([
                a for a in crowd_intelligence_service.anomaly_reports 
                if a.device_id == device_id
            ]),
            "verified_reports": len([
                a for a in crowd_intelligence_service.anomaly_reports 
                if a.device_id == device_id and len(a.verified_by) > 0
            ])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get device trust score: {str(e)}")

@router.get("/sensor-types/supported")
async def get_supported_sensor_types():
    """
    Get list of supported sensor types for crowd intelligence
    """
    return {
        "sensor_types": [sensor.value for sensor in SensorType],
        "anomaly_types": [anomaly.value for anomaly in AnomalyType],
        "detection_capabilities": {
            "earthquake_detection": {
                "sensors": ["accelerometer", "gyroscope"],
                "threshold": "2.0 m/s² acceleration",
                "description": "Detects seismic activity through device motion sensors"
            },
            "flood_detection": {
                "sensors": ["camera", "barometer", "gps"],
                "threshold": "0.5m water level",
                "description": "Detects flooding through image analysis and pressure changes"
            },
            "structural_damage": {
                "sensors": ["camera", "accelerometer"],
                "threshold": "5.0 Hz vibration",
                "description": "Detects building damage through visual analysis and vibration patterns"
            },
            "connectivity_outage": {
                "sensors": ["connectivity"],
                "threshold": "300 seconds offline",
                "description": "Detects network infrastructure failures"
            },
            "noise_anomaly": {
                "sensors": ["microphone"],
                "threshold": "85 dB",
                "description": "Detects unusual noise patterns indicating emergencies"
            }
        }
    }

@router.get("/analytics/trust-distribution")
async def get_trust_distribution_analytics():
    """
    Get detailed analytics about device trust distribution
    """
    try:
        devices = list(crowd_intelligence_service.devices.values())
        
        if not devices:
            return {"message": "No devices registered"}
        
        # Trust score distribution
        trust_ranges = {
            "0.0-0.2": 0, "0.2-0.4": 0, "0.4-0.6": 0,
            "0.6-0.8": 0, "0.8-1.0": 0
        }
        
        for device in devices:
            score = device.trust_score
            if score <= 0.2:
                trust_ranges["0.0-0.2"] += 1
            elif score <= 0.4:
                trust_ranges["0.2-0.4"] += 1
            elif score <= 0.6:
                trust_ranges["0.4-0.6"] += 1
            elif score <= 0.8:
                trust_ranges["0.6-0.8"] += 1
            else:
                trust_ranges["0.8-1.0"] += 1
        
        # Device type distribution
        device_types = {}
        for device in devices:
            device_type = device.device_type
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        # Registration timeline
        registration_timeline = {}
        for device in devices:
            date_key = device.registration_time.strftime("%Y-%m-%d")
            registration_timeline[date_key] = registration_timeline.get(date_key, 0) + 1
        
        return {
            "total_devices": len(devices),
            "trust_distribution": trust_ranges,
            "device_type_distribution": device_types,
            "registration_timeline": registration_timeline,
            "average_trust_score": sum(d.trust_score for d in devices) / len(devices),
            "verified_devices": len([d for d in devices if d.trust_level.value == "verified"]),
            "high_trust_devices": len([d for d in devices if d.trust_score > 0.8])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trust analytics: {str(e)}")
