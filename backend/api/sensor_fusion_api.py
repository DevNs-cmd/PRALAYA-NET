"""
Real-Time Sensor Fusion Pipeline API
Integrates camera streams, satellite/weather APIs, and IoT telemetry into unified probabilistic state map
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from services.sensor_fusion_pipeline import (
    sensor_fusion_engine,
    SensorType,
    DataQuality
)

router = APIRouter(prefix="/sensors", tags=["sensor-fusion"])

class SensorDataRequest(BaseModel):
    sensor_id: str = Field(..., description="Sensor identifier")
    sensor_type: str = Field(..., description="Type of sensor")
    location: Dict = Field(..., description="Sensor location {lat, lon, altitude}")
    data: Dict = Field(..., description="Sensor data payload")
    confidence: float = Field(default=0.8, ge=0, le=1, description="Data confidence 0-1")
    quality: str = Field(default="good", description="Data quality")

class CameraStreamRequest(BaseModel):
    camera_id: str = Field(..., description="Camera identifier")
    source_type: str = Field(default="webcam", description="Camera source type")

class UnifiedStateResponse(BaseModel):
    state_map: Dict[str, Dict]
    total_points: int
    average_risk: float
    average_confidence: float
    sensor_types_active: List[str]
    timestamp: str

class SensorStatisticsResponse(BaseModel):
    total_sensor_data_points: int
    total_fused_points: int
    sensor_type_distribution: Dict[str, int]
    quality_distribution: Dict[str, int]
    camera_streams: Dict[str, Dict]
    average_confidence: float
    timestamp: str

@router.post("/ingest-data")
async def ingest_sensor_data(request: SensorDataRequest, background_tasks: BackgroundTasks):
    """
    Ingest sensor data into fusion pipeline
    
    This endpoint processes sensor data and performs real-time fusion
    """
    try:
        # Validate sensor type
        try:
            sensor_type = SensorType(request.sensor_type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sensor type. Must be one of: {[st.value for st in SensorType]}"
            )
        
        # Validate data quality
        try:
            quality = DataQuality(request.quality.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid quality. Must be one of: {[dq.value for dq in DataQuality]}"
            )
        
        # Create sensor data object
        from services.sensor_fusion_pipeline import SensorData
        sensor_data = SensorData(
            sensor_id=request.sensor_id,
            sensor_type=sensor_type,
            timestamp=datetime.now(),
            location=request.location,
            data=request.data,
            confidence=request.confidence,
            quality=quality
        )
        
        # Ingest data
        data_id = await sensor_fusion_engine.ingest_sensor_data(sensor_data)
        
        return {
            "data_id": data_id,
            "status": "ingested",
            "message": "Sensor data ingested successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data ingestion failed: {str(e)}")

@router.post("/start-camera")
async def start_camera_stream(request: CameraStreamRequest):
    """
    Start processing camera stream for real-time disaster detection
    
    This endpoint connects to laptop camera for live drone feed simulation
    """
    try:
        camera_id = await sensor_fusion_engine.camera_processor.start_camera_stream(
            camera_id=request.camera_id,
            source_type=request.source_type
        )
        
        return {
            "camera_id": camera_id,
            "status": "started",
            "message": "Camera stream started successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Camera stream start failed: {str(e)}")

@router.post("/stop-camera/{camera_id}")
async def stop_camera_stream(camera_id: str):
    """Stop processing camera stream"""
    try:
        sensor_fusion_engine.camera_processor.stop_camera_stream(camera_id)
        
        return {
            "camera_id": camera_id,
            "status": "stopped",
            "message": "Camera stream stopped successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Camera stream stop failed: {str(e)}")

@router.get("/unified-state", response_model=UnifiedStateResponse)
async def get_unified_state_map():
    """
    Get unified probabilistic state map
    
    This endpoint returns the fused sensor data as a unified state map
    """
    try:
        state_map = sensor_fusion_engine.get_unified_state_map()
        return state_map
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"State map retrieval failed: {str(e)}")

@router.get("/statistics", response_model=SensorStatisticsResponse)
async def get_sensor_statistics():
    """Get sensor fusion statistics"""
    try:
        stats = sensor_fusion_engine.get_sensor_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")

@router.get("/camera-status")
async def get_camera_status():
    """Get status of all camera streams"""
    try:
        status = sensor_fusion_engine.camera_processor.get_camera_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Camera status retrieval failed: {str(e)}")

@router.get("/sensor-types")
async def get_sensor_types():
    """Get available sensor types and their descriptions"""
    return {
        "sensor_types": [st.value for st in SensorType],
        "sensor_descriptions": {
            "camera_stream": "Real-time camera feeds for visual disaster detection",
            "satellite": "Satellite imagery and thermal data",
            "weather": "Weather data from meteorological services",
            "iot_telemetry": "IoT sensor telemetry from connected devices",
            "seismic": "Seismic sensor data for earthquake detection",
            "social_media": "Social media analysis for emerging crisis signals",
            "drone_telemetry": "Drone telemetry and reconnaissance data"
        }
    }

@router.get("/data-quality")
async def get_data_quality_levels():
    """Get data quality levels and their meanings"""
    return {
        "quality_levels": [dq.value for dq in DataQuality],
        "quality_descriptions": {
            "excellent": "High-quality data with high confidence and reliability",
            "good": "Reliable data with moderate to high confidence",
            "fair": "Usable data with moderate confidence, some limitations",
            "poor": "Low-quality data with limited confidence",
            "unknown": "Data quality cannot be determined"
        }
    }

@router.get("/fusion-weights")
async def get_fusion_weights():
    """Get sensor fusion weights"""
    return {
        "fusion_weights": {
            sensor_type.value: weight 
            for sensor_type, weight in sensor_fusion_engine.fusion_weights.items()
        },
        "total_weight": sum(sensor_fusion_engine.fusion_weights.values())
    }

@router.get("/recent-data")
async def get_recent_sensor_data(limit: int = 100):
    """Get recent sensor data points"""
    try:
        recent_data = sensor_fusion_engine.sensor_data[-limit:] if sensor_fusion_engine.sensor_data else []
        
        formatted_data = []
        for data in recent_data:
            formatted_data.append({
                "sensor_id": data.sensor_id,
                "sensor_type": data.sensor_type.value,
                "timestamp": data.timestamp.isoformat(),
                "location": data.location,
                "confidence": data.confidence,
                "quality": data.quality.value,
                "processing_timestamp": data.processing_timestamp.isoformat()
            })
        
        return {
            "recent_data": formatted_data,
            "total_points": len(formatted_data),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recent data retrieval failed: {str(e)}")

@router.get("/fused-data")
async def get_fused_data(limit: int = 50):
    """Get recent fused data points"""
    try:
        recent_fused = sensor_fusion_engine.fused_data[-limit:] if sensor_fusion_engine.fused_data else []
        
        formatted_fused = []
        for data in recent_fused:
            formatted_fused.append({
                "fused_id": data.fused_id,
                "timestamp": data.timestamp.isoformat(),
                "location": data.location,
                "fused_value": data.fused_value,
                "confidence": data.confidence,
                "contributing_sensors": data.contributing_sensors,
                "fusion_method": data.fusion_method,
                "metadata": data.metadata
            })
        
        return {
            "fused_data": formatted_fused,
            "total_points": len(formatted_fused),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fused data retrieval failed: {str(e)}")
