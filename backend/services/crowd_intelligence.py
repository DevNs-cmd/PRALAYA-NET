"""
Crowd-Sensed Intelligence Mesh
Mobile sensor ingestion SDK with trust scoring and anomaly clustering
"""

import asyncio
import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
from fastapi import APIRouter, HTTPException, BackgroundTasks, File, UploadFile
from pydantic import BaseModel, Field
import base64

class SensorType(Enum):
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"
    GPS = "gps"
    MICROPHONE = "microphone"
    CAMERA = "camera"
    CONNECTIVITY = "connectivity"
    BAROMETER = "barometer"
    MAGNETOMETER = "magnetometer"

class AnomalyType(Enum):
    EARTHQUAKE_DETECTION = "earthquake_detection"
    FLOOD_DETECTION = "flood_detection"
    STRUCTURAL_DAMAGE = "structural_damage"
    CONNECTIVITY_OUTAGE = "connectivity_outage"
    NOISE_ANOMALY = "noise_anomaly"
    MOVEMENT_ANOMALY = "movement_anomaly"

class DeviceTrustLevel(Enum):
    UNKNOWN = "unknown"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"

@dataclass
class MobileDevice:
    device_id: str
    device_type: str
    os_version: str
    app_version: str
    registration_time: datetime
    last_active: datetime
    trust_score: float = 0.5  # 0-1
    trust_level: DeviceTrustLevel = DeviceTrustLevel.UNKNOWN
    location_history: List[Dict] = field(default_factory=list)
    sensor_accuracy: Dict[str, float] = field(default_factory=dict)
    reputation_score: float = 0.5  # Based on historical accuracy
    verification_status: str = "unverified"

@dataclass
class SensorReading:
    device_id: str
    sensor_type: SensorType
    timestamp: datetime
    data: Dict
    location: Dict  # lat, lon, accuracy
    confidence: float
    battery_level: float
    network_type: str  # wifi, 4g, 5g, none

@dataclass
class AnomalyReport:
    report_id: str
    device_id: str
    anomaly_type: AnomalyType
    confidence: float
    location: Dict
    timestamp: datetime
    sensor_data: Dict
    verified_by: List[str] = field(default_factory=list)
    cluster_id: Optional[str] = None
    trust_weight: float = 0.5

class CrowdIntelligenceService:
    def __init__(self):
        self.devices: Dict[str, MobileDevice] = {}
        self.sensor_readings: List[SensorReading] = []
        self.anomaly_reports: List[AnomalyReport] = []
        self.anomaly_clusters: Dict[str, List[AnomalyReport]] = {}
        self.verification_queue: List[AnomalyReport] = []
        
        # Trust scoring parameters
        self.trust_factors = {
            "device_age": 0.2,      # Older devices have higher trust
            "data_consistency": 0.3,  # Consistent readings increase trust
            "location_coherence": 0.2,  # Coherent location data
            "peer_verification": 0.2,   # Verified by other devices
            "historical_accuracy": 0.1   # Past accuracy of reports
        }
        
        # Anomaly detection thresholds
        self.detection_thresholds = {
            "earthquake_acceleration": 2.0,  # m/s²
            "flood_water_level": 0.5,        # meters
            "structural_vibration": 5.0,       # Hz
            "connectivity_loss_duration": 300,   # seconds
            "noise_level_db": 85               # dB
        }
    
    async def register_device(self, device_data: Dict) -> Dict:
        """Register a new mobile device in the intelligence mesh"""
        try:
            device_id = device_data.get("device_id")
            if not device_id:
                raise HTTPException(status_code=400, detail="Device ID required")
            
            # Check if device already exists
            if device_id in self.devices:
                return {"status": "already_registered", "device_id": device_id}
            
            # Create new device
            device = MobileDevice(
                device_id=device_id,
                device_type=device_data.get("device_type", "android"),
                os_version=device_data.get("os_version", "unknown"),
                app_version=device_data.get("app_version", "1.0.0"),
                registration_time=datetime.now(),
                last_active=datetime.now(),
                trust_score=0.5,
                trust_level=DeviceTrustLevel.UNKNOWN,
                sensor_accuracy=device_data.get("sensor_accuracy", {}),
                verification_status="pending"
            )
            
            self.devices[device_id] = device
            
            return {
                "status": "registered",
                "device_id": device_id,
                "trust_level": device.trust_level.value,
                "message": "Device registered successfully. Trust level will be updated based on data quality."
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Device registration failed: {str(e)}")
    
    async def ingest_sensor_stream(self, sensor_data: Dict, background_tasks: BackgroundTasks) -> Dict:
        """
        Ingest sensor data from mobile devices
        POST /crowd/sensor-stream
        """
        try:
            device_id = sensor_data.get("device_id")
            if not device_id or device_id not in self.devices:
                raise HTTPException(status_code=404, detail="Device not registered")
            
            # Update device last active
            self.devices[device_id].last_active = datetime.now()
            
            # Process sensor readings
            readings = []
            for reading in sensor_data.get("readings", []):
                sensor_reading = SensorReading(
                    device_id=device_id,
                    sensor_type=SensorType(reading.get("sensor_type")),
                    timestamp=datetime.fromisoformat(reading.get("timestamp")),
                    data=reading.get("data"),
                    location=reading.get("location"),
                    confidence=reading.get("confidence", 0.5),
                    battery_level=reading.get("battery_level", 100),
                    network_type=reading.get("network_type", "unknown")
                )
                readings.append(sensor_reading)
                self.sensor_readings.append(sensor_reading)
            
            # Detect anomalies
            anomalies = await self._detect_anomalies(readings)
            
            # Update trust scores
            await self._update_device_trust(device_id, readings)
            
            # Cluster anomalies
            if anomalies:
                background_tasks.add_task(self._cluster_anomalies, anomalies)
            
            # Keep only recent readings (last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.sensor_readings = [
                r for r in self.sensor_readings 
                if r.timestamp > cutoff_time
            ]
            
            return {
                "status": "ingested",
                "readings_processed": len(readings),
                "anomalies_detected": len(anomalies),
                "device_trust_score": self.devices[device_id].trust_score,
                "anomaly_reports": [a.report_id for a in anomalies]
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Sensor ingestion failed: {str(e)}")
    
    async def ingest_damage_image(self, device_id: str, image: UploadFile, metadata: Dict) -> Dict:
        """Ingest camera images for damage classification"""
        try:
            if device_id not in self.devices:
                raise HTTPException(status_code=404, detail="Device not registered")
            
            # Read image
            image_data = await image.read()
            
            # Process image for damage detection
            damage_analysis = await self._analyze_damage_image(image_data, metadata)
            
            # Create anomaly report if damage detected
            if damage_analysis.get("damage_detected", False):
                anomaly = AnomalyReport(
                    report_id=f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(image_data) % 10000:04d}",
                    device_id=device_id,
                    anomaly_type=AnomalyType.STRUCTURAL_DAMAGE,
                    confidence=damage_analysis.get("confidence", 0.5),
                    location=metadata.get("location"),
                    timestamp=datetime.now(),
                    sensor_data={"image_analysis": damage_analysis},
                    trust_weight=self.devices[device_id].trust_score
                )
                
                self.anomaly_reports.append(anomaly)
                
                return {
                    "status": "damage_detected",
                    "report_id": anomaly.report_id,
                    "damage_type": damage_analysis.get("damage_type"),
                    "confidence": damage_analysis.get("confidence"),
                    "severity": damage_analysis.get("severity", "moderate")
                }
            
            return {
                "status": "no_damage_detected",
                "confidence": damage_analysis.get("confidence", 0.1)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")
    
    async def _detect_anomalies(self, readings: List[SensorReading]) -> List[AnomalyReport]:
        """Detect anomalies in sensor readings"""
        anomalies = []
        
        for reading in readings:
            device = self.devices.get(reading.device_id)
            if not device:
                continue
            
            # Earthquake detection (accelerometer)
            if reading.sensor_type == SensorType.ACCELEROMETER:
                acceleration_magnitude = np.sqrt(
                    reading.data.get("x", 0)**2 + 
                    reading.data.get("y", 0)**2 + 
                    reading.data.get("z", 0)**2
                )
                
                if acceleration_magnitude > self.detection_thresholds["earthquake_acceleration"]:
                    anomaly = AnomalyReport(
                        report_id=f"eq_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(reading)) % 10000:04d}",
                        device_id=reading.device_id,
                        anomaly_type=AnomalyType.EARTHQUAKE_DETECTION,
                        confidence=min(acceleration_magnitude / 5.0, 1.0),
                        location=reading.location,
                        timestamp=reading.timestamp,
                        sensor_data={"acceleration": acceleration_magnitude, "raw": reading.data},
                        trust_weight=device.trust_score
                    )
                    anomalies.append(anomaly)
            
            # Connectivity outage detection
            elif reading.sensor_type == SensorType.CONNECTIVITY:
                if reading.data.get("status") == "offline":
                    # Check if this is a prolonged outage
                    recent_readings = [
                        r for r in self.sensor_readings
                        if (r.device_id == reading.device_id and 
                            r.sensor_type == SensorType.CONNECTIVITY and
                            (reading.timestamp - r.timestamp).total_seconds() < 3600)
                    ]
                    
                    if len(recent_readings) > 10:  # Multiple offline readings
                        anomaly = AnomalyReport(
                            report_id=f"conn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(reading)) % 10000:04d}",
                            device_id=reading.device_id,
                            anomaly_type=AnomalyType.CONNECTIVITY_OUTAGE,
                            confidence=0.8,
                            location=reading.location,
                            timestamp=reading.timestamp,
                            sensor_data={"outage_duration": len(recent_readings) * 60},  # seconds
                            trust_weight=device.trust_score
                        )
                        anomalies.append(anomaly)
            
            # Noise anomaly detection (microphone)
            elif reading.sensor_type == SensorType.MICROPHONE:
                noise_level = reading.data.get("decibels", 0)
                if noise_level > self.detection_thresholds["noise_level_db"]:
                    anomaly = AnomalyReport(
                        report_id=f"noise_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(reading)) % 10000:04d}",
                        device_id=reading.device_id,
                        anomaly_type=AnomalyType.NOISE_ANOMALY,
                        confidence=min(noise_level / 120, 1.0),
                        location=reading.location,
                        timestamp=reading.timestamp,
                        sensor_data={"noise_level": noise_level},
                        trust_weight=device.trust_score
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    async def _analyze_damage_image(self, image_data: bytes, metadata: Dict) -> Dict:
        """Analyze image for structural damage"""
        try:
            # Simplified image analysis without cv2
            # In production, use proper computer vision libraries
            
            # Simulate damage detection based on image size and random factors
            image_size = len(image_data)
            
            # Simulate damage detection
            damage_detected = image_size > 10000 and np.random.random() > 0.7
            
            if damage_detected:
                damage_types = ["fire", "flood", "structural"]
                damage_type = np.random.choice(damage_types)
                confidence = np.random.uniform(0.6, 0.9)
                severity = "high" if confidence > 0.8 else "moderate"
            else:
                damage_type = None
                confidence = np.random.uniform(0.1, 0.3)
                severity = "low"
            
            return {
                "damage_detected": damage_detected,
                "damage_type": damage_type,
                "confidence": confidence,
                "severity": severity,
                "analysis": {
                    "image_size": image_size,
                    "simplified_analysis": True
                }
            }
            
        except Exception as e:
            return {"damage_detected": False, "confidence": 0.0, "error": str(e)}
    
    async def _update_device_trust(self, device_id: str, readings: List[SensorReading]):
        """Update device trust score based on data quality"""
        device = self.devices.get(device_id)
        if not device:
            return
        
        # Calculate trust factors
        trust_score = 0.5
        
        # Device age factor (older devices get higher trust)
        device_age_days = (datetime.now() - device.registration_time).days
        age_factor = min(device_age_days / 30, 1.0) * self.trust_factors["device_age"]
        
        # Data consistency factor
        consistency_factor = 0.5
        if len(readings) > 1:
            # Check for consistent sensor readings
            for reading in readings:
                if reading.confidence > 0.7:
                    consistency_factor += 0.1
        consistency_factor = min(consistency_factor, 1.0) * self.trust_factors["data_consistency"]
        
        # Location coherence factor
        location_factor = 0.5
        valid_locations = [r for r in readings if r.location.get("accuracy", 100) < 100]
        if valid_locations:
            location_factor = len(valid_locations) / len(readings)
        location_factor *= self.trust_factors["location_coherence"]
        
        # Update trust score
        device.trust_score = min(age_factor + consistency_factor + location_factor, 1.0)
        
        # Update trust level
        if device.trust_score > 0.8:
            device.trust_level = DeviceTrustLevel.VERIFIED
        elif device.trust_score > 0.6:
            device.trust_level = DeviceTrustLevel.HIGH
        elif device.trust_score > 0.4:
            device.trust_level = DeviceTrustLevel.MEDIUM
        elif device.trust_score > 0.2:
            device.trust_level = DeviceTrustLevel.LOW
        else:
            device.trust_level = DeviceTrustLevel.UNKNOWN
    
    async def _cluster_anomalies(self, anomalies: List[AnomalyReport]):
        """Cluster anomalies to detect patterns and verify reports"""
        if len(anomalies) < 2:
            return
        
        # Simple distance-based clustering without sklearn
        clusters = {}
        cluster_id = 0
        
        for i, anomaly in enumerate(anomalies):
            # Check if anomaly belongs to existing cluster
            assigned_to_cluster = False
            
            for existing_cluster_id, cluster_anomalies in clusters.items():
                # Calculate distance to cluster center
                center_lat = np.mean([a.location.get("lat", 0) for a in cluster_anomalies])
                center_lon = np.mean([a.location.get("lon", 0) for a in cluster_anomalies])
                
                distance = np.sqrt(
                    (anomaly.location.get("lat", 0) - center_lat)**2 + 
                    (anomaly.location.get("lon", 0) - center_lon)**2
                )
                
                # If close enough, add to cluster (0.01 degrees ~ 1km)
                if distance < 0.01:
                    clusters[existing_cluster_id].append(anomaly)
                    anomaly.cluster_id = existing_cluster_id
                    assigned_to_cluster = True
                    break
            
            # If not assigned to any cluster, create new one
            if not assigned_to_cluster:
                cluster_id += 1
                new_cluster_id = f"cluster_{cluster_id}"
                clusters[new_cluster_id] = [anomaly]
                anomaly.cluster_id = new_cluster_id
        
        # Update anomaly clusters
        self.anomaly_clusters.update(clusters)
        
        # Verify clusters with multiple reports
        for cluster_id, cluster_anomalies in clusters.items():
            if len(cluster_anomalies) >= 3:  # At least 3 devices report similar anomaly
                for anomaly in cluster_anomalies:
                    anomaly.verified_by.extend([a.device_id for a in cluster_anomalies if a.device_id != anomaly.device_id])
                    anomaly.trust_weight = min(anomaly.trust_weight * 1.5, 1.0)  # Boost trust weight
    
    def get_anomaly_map(self) -> Dict:
        """Get current anomaly map for visualization"""
        current_anomalies = [
            a for a in self.anomaly_reports 
            if (datetime.now() - a.timestamp).total_seconds() < 3600  # Last hour
        ]
        
        # Group by location clusters
        anomaly_map = {}
        for anomaly in current_anomalies:
            location_key = f"{anomaly.location.get('lat', 0):.3f}_{anomaly.location.get('lon', 0):.3f}"
            
            if location_key not in anomaly_map:
                anomaly_map[location_key] = {
                    "lat": anomaly.location.get("lat"),
                    "lon": anomaly.location.get("lon"),
                    "anomaly_types": [],
                    "confidence_sum": 0,
                    "device_count": 0,
                    "verified": False
                }
            
            anomaly_map[location_key]["anomaly_types"].append(anomaly.anomaly_type.value)
            anomaly_map[location_key]["confidence_sum"] += anomaly.confidence * anomaly.trust_weight
            anomaly_map[location_key]["device_count"] += 1
            
            if len(anomaly.verified_by) > 0:
                anomaly_map[location_key]["verified"] = True
        
        # Calculate final confidence
        for location_data in anomaly_map.values():
            location_data["final_confidence"] = min(
                location_data["confidence_sum"] / max(location_data["device_count"], 1), 1.0
            )
        
        return {
            "anomalies": list(anomaly_map.values()),
            "total_anomalies": len(current_anomalies),
            "verified_anomalies": len([a for a in current_anomalies if len(a.verified_by) > 0]),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_device_statistics(self) -> Dict:
        """Get statistics about registered devices"""
        total_devices = len(self.devices)
        trust_distribution = {}
        
        for level in DeviceTrustLevel:
            trust_distribution[level.value] = sum(
                1 for device in self.devices.values() 
                if device.trust_level == level
            )
        
        active_devices = sum(
            1 for device in self.devices.values()
            if (datetime.now() - device.last_active).total_seconds() < 3600
        )
        
        return {
            "total_devices": total_devices,
            "active_devices": active_devices,
            "trust_distribution": trust_distribution,
            "average_trust_score": sum(d.trust_score for d in self.devices.values()) / max(total_devices, 1),
            "total_readings_24h": len([
                r for r in self.sensor_readings
                if (datetime.now() - r.timestamp).total_seconds() < 86400
            ])
        }

# Global service instance
crowd_intelligence_service = CrowdIntelligenceService()
