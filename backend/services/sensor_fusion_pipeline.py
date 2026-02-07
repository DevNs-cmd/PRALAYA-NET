"""
Real-Time Sensor Fusion Pipeline
Integrates camera streams, satellite/weather APIs, and IoT telemetry into unified probabilistic state map
"""

import asyncio
import numpy as np
import cv2
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import queue
import time
import requests
import random

class SensorType(Enum):
    CAMERA_STREAM = "camera_stream"
    SATELLITE = "satellite"
    WEATHER = "weather"
    IOT_TELEMETRY = "iot_telemetry"
    SEISMIC = "seismic"
    SOCIAL_MEDIA = "social_media"
    DRONE_TELEMETRY = "drone_telemetry"

class DataQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"

@dataclass
class SensorData:
    sensor_id: str
    sensor_type: SensorType
    timestamp: datetime
    location: Dict  # lat, lon, altitude if applicable
    data: Dict[str, Any]
    confidence: float  # 0-1
    quality: DataQuality
    processing_timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class FusedDataPoint:
    fused_id: str
    timestamp: datetime
    location: Dict
    fused_value: float  # 0-1 (risk level)
    confidence: float  # 0-1
    contributing_sensors: List[str]
    fusion_method: str
    metadata: Dict[str, Any]

class CameraStreamProcessor:
    """Process real-time camera streams for disaster detection"""
    
    def __init__(self):
        self.camera_streams = {}
        self.processing_threads = {}
        self.frame_queues = {}
        self.running = False
    
    async def start_camera_stream(self, camera_id: str, source_type: str = "webcam") -> str:
        """Start processing camera stream"""
        
        if camera_id in self.camera_streams:
            return camera_id
        
        # Initialize camera
        if source_type == "webcam":
            cap = cv2.VideoCapture(0)  # Default webcam
        else:
            # For IP cameras, you would use RTSP URL
            cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open camera {camera_id}")
        
        self.camera_streams[camera_id] = cap
        self.frame_queues[camera_id] = queue.Queue(maxsize=30)
        
        # Start processing thread
        self.processing_threads[camera_id] = threading.Thread(
            target=self._process_camera_frames,
            args=(camera_id,),
            daemon=True
        )
        self.processing_threads[camera_id].start()
        
        self.running = True
        return camera_id
    
    def _process_camera_frames(self, camera_id: str):
        """Process frames from camera stream"""
        
        cap = self.camera_streams[camera_id]
        frame_queue = self.frame_queues[camera_id]
        
        while self.running and camera_id in self.camera_streams:
            ret, frame = cap.read()
            
            if ret:
                try:
                    # Process frame for disaster detection
                    processed_data = self._analyze_frame(frame, camera_id)
                    
                    if processed_data:
                        frame_queue.put(processed_data)
                except Exception as e:
                    print(f"Error processing frame from {camera_id}: {e}")
            
            time.sleep(0.033)  # ~30 FPS
    
    def _analyze_frame(self, frame: np.ndarray, camera_id: str) -> Optional[Dict[str, Any]]:
        """Analyze frame for disaster indicators"""
        
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Motion detection
            if hasattr(self, '_prev_frame'):
                diff = cv2.absdiff(gray, self._prev_frame)
                motion_level = np.mean(diff)
                
                # Detect significant motion
                if motion_level > 30:
                    # Analyze motion patterns
                    contours, _ = cv2.findContours(diff.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    if contours:
                        largest_contour = max(contours, key=cv2.contourArea)
                        
                        # Get bounding box
                        x, y, w, h = cv2.boundingRect(largest_contour)
                        
                        # Classify motion type
                        motion_type = self._classify_motion(gray[y:y+h, x:x+w], camera_id)
                        
                        return {
                            "sensor_id": camera_id,
                            "sensor_type": SensorType.CAMERA_STREAM,
                            "timestamp": datetime.now(),
                            "location": {"lat": 19.0760, "lon": 72.8777},  # Default location
                            "data": {
                                "motion_detected": True,
                                "motion_level": float(motion_level),
                                "motion_type": motion_type,
                                "bounding_box": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                                "frame_shape": frame.shape
                            },
                            "confidence": min(0.9, motion_level / 100),
                            "quality": DataQuality.GOOD
                        }
            
            # Store previous frame for motion detection
            self._prev_frame = gray.copy()
            
            # Check for visual anomalies
            anomalies = self._detect_visual_anomalies(frame, camera_id)
            
            if anomalies:
                return {
                    "sensor_id": camera_id,
                    "sensor_type": SensorType.CAMERA_STREAM,
                    "timestamp": datetime.now(),
                    "location": {"lat": 19.0760, "lon": 72.8777},
                    "data": {
                        "anomalies_detected": True,
                        "anomaly_types": anomalies,
                        "frame_shape": frame.shape
                    },
                    "confidence": 0.7,
                    "quality": DataQuality.FAIR
                }
            
            return None
            
        except Exception as e:
            print(f"Error analyzing frame: {e}")
            return None
    
    def _classify_motion(self, roi: np.ndarray, camera_id: str) -> str:
        """Classify type of motion detected"""
        
        # Calculate motion characteristics
        motion_intensity = np.mean(roi)
        motion_variance = np.var(roi)
        
        # Simple classification based on motion patterns
        if motion_intensity > 100:
            return "explosion"
        elif motion_variance > 2000:
            return "chaotic_movement"
        elif motion_intensity > 50:
            return "rapid_movement"
        elif motion_intensity > 20:
            return "moderate_movement"
        else:
            return "minor_movement"
    
    def _detect_visual_anomalies(self, frame: np.ndarray, camera_id: str) -> List[str]:
        """Detect visual anomalies in frame"""
        
        anomalies = []
        
        try:
            # Check for smoke/fire (high red/orange values)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Fire detection (high red values)
            lower_fire = np.array([0, 50, 50])
            upper_fire = np.array([20, 255, 255])
            fire_mask = cv2.inRange(hsv, lower_fire, upper_fire)
            
            fire_ratio = np.sum(fire_mask) / fire_mask.size if fire_mask.size > 0 else 0
            
            if fire_ratio > 0.05:  # More than 5% of frame has fire colors
                anomalies.append("fire_detected")
            
            # Check for smoke (high gray values in certain patterns)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, smoke_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            
            smoke_ratio = np.sum(smoke_mask) / smoke_mask.size if smoke_mask.size > 0 else 0
            
            if smoke_ratio > 0.1:  # More than 10% smoke
                anomalies.append("smoke_detected")
            
            # Check for structural damage (edge detection)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size if edges.size > 0 else 0
            
            if edge_density > 0.3:  # High edge density
                anomalies.append("structural_anomaly")
            
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
        
        return anomalies
    
    def stop_camera_stream(self, camera_id: str):
        """Stop processing camera stream"""
        
        if camera_id in self.camera_streams:
            self.camera_streams[camera_id].release()
            del self.camera_streams[camera_id]
        
        if camera_id in self.processing_threads:
            self.processing_threads[camera_id].join()
            del self.processing_threads[camera_id]
        
        if camera_id in self.frame_queues:
            del self.frame_queues[camera_id]
        
        if not self.camera_streams:
            self.running = False
    
    def get_camera_status(self) -> Dict[str, Any]:
        """Get status of all camera streams"""
        
        status = {}
        
        for camera_id, cap in self.camera_streams.items():
            status[camera_id] = {
                "active": cap.isOpened(),
                "queue_size": self.frame_queues[camera_id].qsize() if camera_id in self.frame_queues else 0,
                "processing_thread": camera_id in self.processing_threads and self.processing_threads[camera_id].is_alive()
            }
        
        return status

class WeatherDataProcessor:
    """Process weather data from APIs"""
    
    def __init__(self):
        self.api_key = None
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.cache_duration = timedelta(minutes=10)
        self.cache = {}
    
    async def get_weather_data(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get weather data for location"""
        
        cache_key = f"{lat:.2f}_{lon:.2f}"
        current_time = datetime.now()
        
        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if current_time - cached_time < self.cache_duration:
                return cached_data
        
        try:
            # Fetch from OpenWeatherMap API
            url = f"{self.base_url}/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            
            # In production, you would use actual API key
            # For demo, simulate weather data
            weather_data = self._simulate_weather_data(lat, lon)
            
            # Cache the data
            self.cache[cache_key] = (weather_data, current_time)
            
            return weather_data
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    def _simulate_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Simulate weather data for demo purposes"""
        
        # Generate realistic weather based on location and time
        weather_conditions = ["clear", "clouds", "rain", "thunderstorm", "fog", "haze"]
        temperatures = np.random.uniform(15, 35)
        humidity = np.random.uniform(30, 90)
        
        # Add risk factors based on conditions
        risk_factors = []
        if "rain" in weather_conditions or "thunderstorm" in weather_conditions:
            risk_factors.append("flood_risk")
        if "fog" in weather_conditions or "haze" in weather_conditions:
            risk_factors.append("visibility_risk")
        
        return {
            "sensor_id": f"weather_{lat:.2f}_{lon:.2f}",
            "sensor_type": SensorType.WEATHER,
            "timestamp": datetime.now(),
            "location": {"lat": lat, "lon": lon},
            "data": {
                "temperature": temperatures,
                "humidity": humidity,
                "conditions": np.random.choice(weather_conditions),
                "wind_speed": np.random.uniform(0, 20),
                "pressure": np.random.uniform(990, 1030),
                "visibility": np.random.uniform(1, 10),
                "risk_factors": risk_factors
            },
            "confidence": 0.9,
            "quality": DataQuality.EXCELLENT
        }

class SensorFusionEngine:
    """Main sensor fusion engine"""
    
    def __init__(self):
        self.camera_processor = CameraStreamProcessor()
        self.weather_processor = WeatherDataProcessor()
        self.sensor_data: List[SensorData] = []
        self.fused_data: List[FusedDataPoint] = []
        self.fusion_weights = {
            SensorType.CAMERA_STREAM: 0.3,
            SensorType.SATELLITE: 0.2,
            SensorType.WEATHER: 0.2,
            SensorType.IOT_TELEMETRY: 0.15,
            SensorType.SEISMIC: 0.1,
            SensorType.SOCIAL_MEDIA: 0.05
        }
        
        # Start camera stream
        self.camera_processor.start_camera_stream("drone_camera", "webcam")
    
    async def ingest_sensor_data(self, sensor_data: SensorData) -> str:
        """Ingest sensor data into fusion pipeline"""
        
        # Add timestamp
        sensor_data.processing_timestamp = datetime.now()
        
        # Add to sensor data list
        self.sensor_data.append(sensor_data)
        
        # Keep only recent data (last 1 hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.sensor_data = [
            s for s in self.sensor_data 
            if s.timestamp > cutoff_time
        ]
        
        # Trigger fusion
        await self._perform_fusion()
        
        return sensor_data.sensor_id
    
    async def _perform_fusion(self):
        """Perform sensor data fusion"""
        
        if len(self.sensor_data) < 2:
            return
        
        # Group sensor data by location (simplified grid-based approach)
        location_grids = {}
        
        for data in self.sensor_data:
            grid_key = f"{data.location['lat']:.3f}_{data.location['lon']:.3f}"
            
            if grid_key not in location_grids:
                location_grids[grid_key] = []
            
            location_grids[grid_key].append(data)
        
        # Fuse data for each location
        for grid_key, sensors in location_grids.items():
            fused_data = await self._fuse_sensor_data(sensors)
            
            if fused_data:
                self.fused_data.append(fused_data)
        
        # Keep only recent fused data (last 30 minutes)
        cutoff_time = datetime.now() - timedelta(minutes=30)
        self.fused_data = [
            f for f in self.fused_data 
            if f.timestamp > cutoff_time
        ]
    
    async def _fuse_sensor_data(self, sensors: List[SensorData]) -> Optional[FusedDataPoint]:
        """Fuse multiple sensor data points"""
        
        if not sensors:
            return None
        
        # Calculate weighted average based on confidence and quality
        total_weight = 0
        weighted_sum = 0
        
        for sensor in sensors:
            weight = self.fusion_weights.get(sensor.sensor_type, 0.1)
            confidence = sensor.confidence
            quality_factor = {
                DataQuality.EXCELLENT: 1.0,
                DataQuality.GOOD: 0.8,
                DataQuality.FAIR: 0.6,
                DataQuality.POOR: 0.4,
                DataQuality.UNKNOWN: 0.2
            }.get(sensor.quality, 0.5)
            
            total_weight += weight * confidence * quality_factor
            weighted_sum += sensor.data.get("risk_level", 0.5) * weight * confidence * quality_factor
        
        if total_weight == 0:
            return None
        
        # Calculate fused risk value
        fused_value = weighted_sum / total_weight
        
        # Create fused data point
        fused_data = FusedDataPoint(
            fused_id=f"fused_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(sensors[0].location)) % 10000:04d}",
            timestamp=datetime.now(),
            location=sensors[0].location,
            fused_value=fused_value,
            confidence=total_weight / len(self.fusion_weights),
            contributing_sensors=[s.sensor_id for s in sensors],
            fusion_method="weighted_average",
            metadata={
                "sensor_types": [s.sensor_type.value for s in sensors],
                "average_confidence": np.mean([s.confidence for s in sensors]),
                "data_count": len(sensors)
            }
        )
        
        return fused_data
    
    def get_unified_state_map(self) -> Dict[str, Any]:
        """Get unified probabilistic state map"""
        
        if not self.fused_data:
            return {
                "message": "No fused data available",
                "timestamp": datetime.now().isoformat()
            }
        
        # Create grid-based state map
        state_map = {}
        
        for data in self.fused_data:
            grid_key = f"{data.location['lat']:.3f}_{data.location['lon']:.3f}"
            
            state_map[grid_key] = {
                "location": data.location,
                "risk_level": data.fused_value,
                "confidence": data.confidence,
                "contributing_sensors": data.contributing_sensors,
                "timestamp": data.timestamp.isoformat(),
                "fusion_method": data.fusion_method,
                "sensor_types": data.metadata.get("sensor_types", [])
            }
        
        return {
            "state_map": state_map,
            "total_points": len(state_map),
            "average_risk": np.mean([d["risk_level"] for d in state_map.values()]) if state_map else 0,
            "average_confidence": np.mean([d["confidence"] for d in state_map.values()]) if state_map else 0,
            "sensor_types_active": list(set([s for d in state_map.values() for s in d["sensor_types"]])),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_sensor_statistics(self) -> Dict[str, Any]:
        """Get sensor fusion statistics"""
        
        sensor_type_distribution = {}
        for data in self.sensor_data:
            sensor_type = data.sensor_type.value
            sensor_type_distribution[sensor_type] = sensor_type_distribution.get(sensor_type, 0) + 1
        
        quality_distribution = {}
        for data in self.sensor_data:
            quality = data.quality.value
            quality_distribution[quality] = quality_distribution.get(quality, 0) + 1
        
        return {
            "total_sensor_data_points": len(self.sensor_data),
            "total_fused_points": len(self.fused_data),
            "sensor_type_distribution": sensor_type_distribution,
            "quality_distribution": quality_distribution,
            "camera_streams": self.camera_processor.get_camera_status(),
            "average_confidence": np.mean([s.confidence for s in self.sensor_data]) if self.sensor_data else 0,
            "timestamp": datetime.now().isoformat()
        }

# Global instance
sensor_fusion_engine = SensorFusionEngine()
