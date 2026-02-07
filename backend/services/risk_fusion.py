"""
Multi-Layer Risk Fusion Intelligence
Unified Risk Field Map combining satellite, weather, infrastructure, citizen, and drone data
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

class DataSourceType(Enum):
    SATELLITE = "satellite"
    WEATHER_FORECAST = "weather_forecast"
    INFRASTRUCTURE_LOADS = "infrastructure_loads"
    CITIZEN_TELEMETRY = "citizen_telemetry"
    DRONE_RECONNAISSANCE = "drone_reconnaissance"
    SEISMIC_SENSORS = "seismic_sensors"
    SOCIAL_MEDIA = "social_media"

class RiskIntensity(Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskDataPoint:
    source_type: DataSourceType
    location: Dict
    timestamp: datetime
    risk_value: float  # 0-1
    confidence: float  # 0-1
    metadata: Dict
    data_id: str

@dataclass
class UnifiedRiskField:
    field_id: str
    timestamp: datetime
    grid_resolution: float  # degrees
    risk_grid: np.ndarray
    intensity_map: Dict[str, RiskIntensity]
    fusion_weights: Dict[str, float]
    data_sources: List[str]
    coverage_area: Dict
    highest_risk_location: Dict
    overall_risk_score: float

class RiskFusionEngine:
    def __init__(self):
        self.risk_data_points: List[RiskDataPoint] = []
        self.unified_fields: Dict[str, UnifiedRiskField] = []
        self.fusion_weights = {
            DataSourceType.SATELLITE: 0.25,
            DataSourceType.WEATHER_FORECAST: 0.20,
            DataSourceType.INFRASTRUCTURE_LOADS: 0.25,
            DataSourceType.CITIZEN_TELEMETRY: 0.15,
            DataSourceType.DRONE_RECONNAISSANCE: 0.10,
            DataSourceType.SEISMIC_SENSORS: 0.05
        }
        
        # Risk field parameters
        self.grid_resolution = 0.01  # ~1km grid
        self.india_bounds = {
            "min_lat": 6.0, "max_lat": 38.0,
            "min_lon": 68.0, "max_lon": 97.0
        }
        
        # Initialize with synthetic data
        self._initialize_risk_data()
    
    def _initialize_risk_data(self):
        """Initialize with synthetic multi-layer risk data"""
        current_time = datetime.now()
        
        # Generate synthetic satellite data
        for i in range(20):
            risk_point = RiskDataPoint(
                source_type=DataSourceType.SATELLITE,
                location={
                    "lat": np.random.uniform(8, 35),
                    "lon": np.random.uniform(70, 95)
                },
                timestamp=current_time - timedelta(minutes=np.random.randint(0, 60)),
                risk_value=np.random.uniform(0.1, 0.8),
                confidence=np.random.uniform(0.7, 0.95),
                metadata={
                    "satellite": "INSAT-3D",
                    "sensor": "MODIS",
                    "cloud_cover": np.random.uniform(0, 0.5),
                    "anomaly_type": "thermal_hotspot"
                },
                data_id=f"sat_{i}_{int(current_time.timestamp())}"
            )
            self.risk_data_points.append(risk_point)
        
        # Generate synthetic weather data
        for i in range(15):
            risk_point = RiskDataPoint(
                source_type=DataSourceType.WEATHER_FORECAST,
                location={
                    "lat": np.random.uniform(10, 30),
                    "lon": np.random.uniform(72, 88)
                },
                timestamp=current_time - timedelta(minutes=np.random.randint(0, 30)),
                risk_value=np.random.uniform(0.05, 0.6),
                confidence=np.random.uniform(0.8, 0.95),
                metadata={
                    "model": "GFS",
                    "forecast_hour": np.random.randint(0, 24),
                    "precipitation_mm": np.random.uniform(0, 100),
                    "wind_speed_kmh": np.random.uniform(0, 80)
                },
                data_id=f"weather_{i}_{int(current_time.timestamp())}"
            )
            self.risk_data_points.append(risk_point)
        
        # Generate synthetic infrastructure load data
        for i in range(25):
            risk_point = RiskDataPoint(
                source_type=DataSourceType.INFRASTRUCTURE_LOADS,
                location={
                    "lat": np.random.uniform(12, 28),
                    "lon": np.random.uniform(74, 92)
                },
                timestamp=current_time - timedelta(minutes=np.random.randint(0, 15)),
                risk_value=np.random.uniform(0.0, 0.9),
                confidence=np.random.uniform(0.9, 1.0),
                metadata={
                    "infrastructure_type": np.random.choice(["power", "telecom", "water", "transport"]),
                    "load_percentage": np.random.uniform(0.3, 1.0),
                    "health_score": np.random.uniform(0.4, 1.0),
                    "redundancy_level": np.random.randint(1, 4)
                },
                data_id=f"infra_{i}_{int(current_time.timestamp())}"
            )
            self.risk_data_points.append(risk_point)
        
        # Generate synthetic citizen telemetry
        for i in range(30):
            risk_point = RiskDataPoint(
                source_type=DataSourceType.CITIZEN_TELEMETRY,
                location={
                    "lat": np.random.uniform(15, 25),
                    "lon": np.random.uniform(75, 85)
                },
                timestamp=current_time - timedelta(minutes=np.random.randint(0, 10)),
                risk_value=np.random.uniform(0.0, 0.7),
                confidence=np.random.uniform(0.6, 0.9),
                metadata={
                    "device_count": np.random.randint(10, 1000),
                    "anomaly_reports": np.random.randint(0, 50),
                    "trust_score": np.random.uniform(0.5, 0.9),
                    "sensor_type": np.random.choice(["accelerometer", "camera", "microphone"])
                },
                data_id=f"citizen_{i}_{int(current_time.timestamp())}"
            )
            self.risk_data_points.append(risk_point)
    
    async def ingest_risk_data(self, 
                             source_type: DataSourceType,
                             location: Dict,
                             risk_value: float,
                             confidence: float,
                             metadata: Dict) -> str:
        """Ingest new risk data point"""
        data_id = f"{source_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(location)) % 10000:04d}"
        
        risk_point = RiskDataPoint(
            source_type=source_type,
            location=location,
            timestamp=datetime.now(),
            risk_value=risk_value,
            confidence=confidence,
            metadata=metadata,
            data_id=data_id
        )
        
        self.risk_data_points.append(risk_point)
        
        # Keep only recent data (last 2 hours)
        cutoff_time = datetime.now() - timedelta(hours=2)
        self.risk_data_points = [
            rp for rp in self.risk_data_points 
            if rp.timestamp > cutoff_time
        ]
        
        return data_id
    
    async def generate_unified_risk_field(self) -> UnifiedRiskField:
        """Generate unified risk field map from all data sources"""
        try:
            field_id = f"risk_field_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create risk grid
            lat_range = self.india_bounds["max_lat"] - self.india_bounds["min_lat"]
            lon_range = self.india_bounds["max_lon"] - self.india_bounds["min_lon"]
            
            lat_steps = int(lat_range / self.grid_resolution)
            lon_steps = int(lon_range / self.grid_resolution)
            
            risk_grid = np.zeros((lat_steps, lon_steps))
            weight_grid = np.zeros((lat_steps, lon_steps))
            
            # Process each data point
            for data_point in self.risk_data_points:
                # Convert location to grid coordinates
                lat_idx = int((data_point.location["lat"] - self.india_bounds["min_lat"]) / self.grid_resolution)
                lon_idx = int((data_point.location["lon"] - self.india_bounds["min_lon"]) / self.grid_resolution)
                
                if 0 <= lat_idx < lat_steps and 0 <= lon_idx < lon_steps:
                    # Apply fusion weights and confidence
                    weight = self.fusion_weights[data_point.source_type] * data_point.confidence
                    risk_grid[lat_idx, lon_idx] += data_point.risk_value * weight
                    weight_grid[lat_idx, lon_idx] += weight
            
            # Normalize by weights
            risk_grid = np.divide(risk_grid, weight_grid, where=weight_grid > 0, out=np.zeros_like(risk_grid))
            
            # Apply spatial smoothing
            risk_grid = self._apply_spatial_smoothing(risk_grid)
            
            # Create intensity map
            intensity_map = self._create_intensity_map(risk_grid)
            
            # Find highest risk location
            max_idx = np.unravel_index(np.argmax(risk_grid), risk_grid.shape)
            highest_risk_location = {
                "lat": self.india_bounds["min_lat"] + max_idx[0] * self.grid_resolution,
                "lon": self.india_bounds["min_lon"] + max_idx[1] * self.grid_resolution,
                "risk_value": float(risk_grid[max_idx]),
                "intensity": intensity_map[f"{max_idx[0]}_{max_idx[1]}"].value
            }
            
            # Calculate overall risk score
            overall_risk_score = np.mean(risk_grid[risk_grid > 0]) if np.any(risk_grid > 0) else 0.0
            
            # Create unified field
            unified_field = UnifiedRiskField(
                field_id=field_id,
                timestamp=datetime.now(),
                grid_resolution=self.grid_resolution,
                risk_grid=risk_grid,
                intensity_map=intensity_map,
                fusion_weights={k.value: v for k, v in self.fusion_weights.items()},
                data_sources=list(set(rp.source_type.value for rp in self.risk_data_points)),
                coverage_area=self.india_bounds,
                highest_risk_location=highest_risk_location,
                overall_risk_score=overall_risk_score
            )
            
            self.unified_fields.append(unified_field)
            
            # Keep only recent fields (last 10)
            if len(self.unified_fields) > 10:
                self.unified_fields = self.unified_fields[-10:]
            
            return unified_field
            
        except Exception as e:
            raise Exception(f"Risk field generation failed: {str(e)}")
    
    def _apply_spatial_smoothing(self, risk_grid: np.ndarray) -> np.ndarray:
        """Apply spatial smoothing to risk grid"""
        # Simple Gaussian smoothing
        smoothed_grid = np.copy(risk_grid)
        
        for i in range(1, risk_grid.shape[0] - 1):
            for j in range(1, risk_grid.shape[1] - 1):
                # 3x3 neighborhood average
                neighborhood = risk_grid[i-1:i+2, j-1:j+2]
                smoothed_grid[i, j] = np.mean(neighborhood)
        
        return smoothed_grid
    
    def _create_intensity_map(self, risk_grid: np.ndarray) -> Dict[str, RiskIntensity]:
        """Create intensity classification map"""
        intensity_map = {}
        
        for i in range(risk_grid.shape[0]):
            for j in range(risk_grid.shape[1]):
                risk_value = risk_grid[i, j]
                
                if risk_value < 0.25:
                    intensity = RiskIntensity.LOW
                elif risk_value < 0.5:
                    intensity = RiskIntensity.MODERATE
                elif risk_value < 0.75:
                    intensity = RiskIntensity.HIGH
                else:
                    intensity = RiskIntensity.CRITICAL
                
                intensity_map[f"{i}_{j}"] = intensity
        
        return intensity_map
    
    def get_risk_field_data(self, field_id: str) -> Dict:
        """Get risk field data for visualization"""
        field = next((f for f in self.unified_fields if f.field_id == field_id), None)
        
        if not field:
            raise ValueError(f"Risk field {field_id} not found")
        
        # Convert grid to visualization format
        grid_data = []
        for i in range(field.risk_grid.shape[0]):
            for j in range(field.risk_grid.shape[1]):
                if field.risk_grid[i, j] > 0.01:  # Only include significant risk values
                    grid_data.append({
                        "lat": field.coverage_area["min_lat"] + i * field.grid_resolution,
                        "lon": field.coverage_area["min_lon"] + j * field.grid_resolution,
                        "risk_value": float(field.risk_grid[i, j]),
                        "intensity": field.intensity_map[f"{i}_{j}"].value
                    })
        
        return {
            "field_id": field.field_id,
            "timestamp": field.timestamp.isoformat(),
            "grid_resolution": field.grid_resolution,
            "risk_data": grid_data,
            "highest_risk_location": field.highest_risk_location,
            "overall_risk_score": field.overall_risk_score,
            "data_sources": field.data_sources,
            "fusion_weights": field.fusion_weights
        }
    
    def get_risk_statistics(self) -> Dict:
        """Get risk fusion statistics"""
        if not self.risk_data_points:
            return {"message": "No risk data available"}
        
        # Data source distribution
        source_distribution = {}
        for data_point in self.risk_data_points:
            source = data_point.source_type.value
            source_distribution[source] = source_distribution.get(source, 0) + 1
        
        # Risk level distribution
        risk_levels = {"low": 0, "moderate": 0, "high": 0, "critical": 0}
        for data_point in self.risk_data_points:
            if data_point.risk_value < 0.25:
                risk_levels["low"] += 1
            elif data_point.risk_value < 0.5:
                risk_levels["moderate"] += 1
            elif data_point.risk_value < 0.75:
                risk_levels["high"] += 1
            else:
                risk_levels["critical"] += 1
        
        # Average confidence by source
        confidence_by_source = {}
        for source_type in DataSourceType:
            source_data = [rp for rp in self.risk_data_points if rp.source_type == source_type]
            if source_data:
                confidence_by_source[source_type.value] = np.mean([rp.confidence for rp in source_data])
        
        return {
            "total_data_points": len(self.risk_data_points),
            "source_distribution": source_distribution,
            "risk_level_distribution": risk_levels,
            "average_confidence_by_source": confidence_by_source,
            "active_fields": len(self.unified_fields),
            "latest_field_id": self.unified_fields[-1].field_id if self.unified_fields else None,
            "data_freshness_minutes": max(
                [(datetime.now() - rp.timestamp).total_seconds() / 60 for rp in self.risk_data_points]
            ) if self.risk_data_points else 0
        }

# Global instance
risk_fusion_engine = RiskFusionEngine()
