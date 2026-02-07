"""
Drone Capacity Intelligence Engine
Calculates optimal drone fleet size and mission parameters based on area analysis
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math
import numpy as np
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TerrainType(Enum):
    URBAN = "urban"
    RURAL = "rural"
    MOUNTAINOUS = "mountainous"
    COASTAL = "coastal"
    FOREST = "forest"
    DESERT = "desert"

class MissionPriority(Enum):
    SEARCH_AND_RESCUE = "search_and_rescue"
    DAMAGE_ASSESSMENT = "damage_assessment"
    SURVEILLANCE = "surveillance"
    COMMUNICATION_RELAY = "communication_relay"

class DisasterType(Enum):
    EARTHQUAKE = "earthquake"
    FLOOD = "flood"
    WILDFIRE = "wildfire"
    LANDSLIDE = "landslide"
    TSUNAMI = "tsunami"
    CYCLONE = "cyclone"

@dataclass
class AreaAnalysis:
    area_sq_km: float
    perimeter_km: float
    terrain_type: TerrainType
    building_density: float  # 0.0 to 1.0
    accessibility_score: float  # 0.0 to 1.0
    
@dataclass
class DroneSpecification:
    model: str
    max_range_km: float
    flight_time_hours: float
    camera_resolution: str
    max_altitude_m: int
    payload_capacity_kg: float
    max_speed_kmh: float
    battery_consumption_rate: float  # % per hour
    
@dataclass
class MissionRequirements:
    area_analysis: AreaAnalysis
    disaster_type: DisasterType
    priority: MissionPriority
    required_coverage_percentage: float
    overlap_percentage: float
    environmental_conditions: Dict[str, float]

class DroneCapacityIntelligence:
    """Main capacity intelligence engine"""
    
    def __init__(self):
        # Standard drone fleet specifications
        self.drone_specs = {
            "standard": DroneSpecification(
                model="DJI Mavic 3 Enterprise",
                max_range_km=15.0,
                flight_time_hours=1.5,
                camera_resolution="4K",
                max_altitude_m=5000,
                payload_capacity_kg=1.2,
                max_speed_kmh=65,
                battery_consumption_rate=66.7  # 100%/1.5h
            ),
            "heavy_lifter": DroneSpecification(
                model="DJI Matrice 300 RTK",
                max_range_km=18.0,
                flight_time_hours=2.0,
                camera_resolution="6K",
                max_altitude_m=7000,
                payload_capacity_kg=2.7,
                max_speed_kmh=65,
                battery_consumption_rate=50.0
            ),
            "long_range": DroneSpecification(
                model="Autel EVO II Dual",
                max_range_km=25.0,
                flight_time_hours=1.8,
                camera_resolution="8K",
                max_altitude_m=6000,
                payload_capacity_kg=1.5,
                max_speed_kmh=72,
                battery_consumption_rate=55.6
            )
        }
        
        # Environmental factors
        self.environmental_factors = {
            "wind_speed_kmh": 15,
            "weather_condition": "clear",  # clear, cloudy, rainy, stormy
            "temperature_c": 25,
            "terrain_type": "urban"
        }
        
        # Mission parameters
        self.mission_priority = MissionPriority.SEARCH_AND_RESCUE
        self.required_coverage_percentage = 0.95  # 95% area coverage
        self.overlap_percentage = 0.30  # 30% overlap between drone paths
        
        logger.info("🧠 Drone Capacity Intelligence Engine initialized")
    
    def analyze_area(self, coordinates: List[Tuple[float, float]], 
                    terrain_type: TerrainType = TerrainType.URBAN) -> AreaAnalysis:
        """Analyze disaster area and calculate requirements"""
        
        # Calculate area using shoelace formula
        area_sq_km = self._calculate_area_km2(coordinates)
        
        # Calculate perimeter
        perimeter_km = self._calculate_perimeter_km(coordinates)
        
        # Estimate building density based on terrain type
        building_density = self._estimate_building_density(terrain_type)
        
        # Calculate accessibility score
        accessibility_score = self._calculate_accessibility(terrain_type, building_density)
        
        area_analysis = AreaAnalysis(
            area_sq_km=area_sq_km,
            perimeter_km=perimeter_km,
            terrain_type=terrain_type,
            building_density=building_density,
            accessibility_score=accessibility_score
        )
        
        logger.info(f"📊 Area Analysis: {area_sq_km:.2f} km², {perimeter_km:.2f} km perimeter")
        return area_analysis
    
    def _calculate_area_km2(self, coordinates: List[Tuple[float, float]]) -> float:
        """Calculate area in km² using polygon coordinates"""
        if len(coordinates) < 3:
            return 0.0
        
        # Using shoelace formula
        n = len(coordinates)
        area = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            area += coordinates[i][0] * coordinates[j][1]
            area -= coordinates[j][0] * coordinates[i][1]
        
        area = abs(area) / 2.0
        
        # Convert to km² (assuming coordinates are in degrees)
        # Rough approximation - 1 degree ≈ 111 km
        area_km2 = area * (111 * 111)
        return round(area_km2, 2)
    
    def _calculate_perimeter_km(self, coordinates: List[Tuple[float, float]]) -> float:
        """Calculate perimeter in km"""
        if len(coordinates) < 2:
            return 0.0
        
        perimeter = 0.0
        n = len(coordinates)
        
        for i in range(n):
            j = (i + 1) % n
            lat1, lon1 = coordinates[i]
            lat2, lon2 = coordinates[j]
            
            # Haversine distance calculation
            distance = self._haversine_distance(lat1, lon1, lat2, lon2)
            perimeter += distance
        
        return round(perimeter, 2)
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in km"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _estimate_building_density(self, terrain_type: TerrainType) -> float:
        """Estimate building density based on terrain type"""
        density_map = {
            TerrainType.URBAN: 0.8,
            TerrainType.RURAL: 0.3,
            TerrainType.MOUNTAINOUS: 0.2,
            TerrainType.COASTAL: 0.4,
            TerrainType.FOREST: 0.1,
            TerrainType.DESERT: 0.1
        }
        return density_map.get(terrain_type, 0.4)
    
    def _calculate_accessibility(self, terrain_type: TerrainType, building_density: float) -> float:
        """Calculate area accessibility score"""
        # Base accessibility by terrain type
        terrain_accessibility = {
            TerrainType.URBAN: 0.9,
            TerrainType.RURAL: 0.7,
            TerrainType.MOUNTAINOUS: 0.4,
            TerrainType.COASTAL: 0.6,
            TerrainType.FOREST: 0.5,
            TerrainType.DESERT: 0.8
        }
        
        base_accessibility = terrain_accessibility.get(terrain_type, 0.6)
        
        # Adjust for building density (higher density = lower accessibility for drones)
        accessibility = base_accessibility * (1.0 - building_density * 0.3)
        
        return max(0.1, accessibility)  # Minimum 10% accessibility
    
    def calculate_drone_requirements(self, area_analysis: AreaAnalysis, 
                                   disaster_type: DisasterType,
                                   priority: MissionPriority = MissionPriority.SEARCH_AND_RESCUE,
                                   available_drones: Optional[Dict[str, int]] = None) -> Dict:
        """Calculate optimal drone deployment requirements"""
        
        if available_drones is None:
            # Default fleet
            available_drones = {
                "standard": 20,
                "heavy_lifter": 8,
                "long_range": 5
            }
        
        # Calculate effective coverage area
        effective_area = area_analysis.area_sq_km * self.required_coverage_percentage
        
        # Calculate coverage per drone type (considering environmental factors)
        coverage_per_drone = {}
        for drone_type, specs in self.drone_specs.items():
            effective_range = self._calculate_effective_range(specs)
            # Coverage area = π × (range)² with overlap consideration
            single_coverage = math.pi * (effective_range ** 2) * (1 - self.overlap_percentage)
            coverage_per_drone[drone_type] = single_coverage
        
        # Calculate required drones
        drone_allocation = {}
        remaining_area = effective_area
        
        # Priority order: heavy_lifter > long_range > standard
        priority_order = ["heavy_lifter", "long_range", "standard"]
        
        for drone_type in priority_order:
            if remaining_area <= 0:
                break
                
            if drone_type in available_drones and available_drones[drone_type] > 0:
                coverage_per_unit = coverage_per_drone[drone_type]
                required_units = min(
                    math.ceil(remaining_area / coverage_per_unit),
                    available_drones[drone_type]
                )
                
                if required_units > 0:
                    drone_allocation[drone_type] = required_units
                    covered_area = required_units * coverage_per_unit
                    remaining_area -= covered_area
        
        # Calculate mission parameters
        total_drones = sum(drone_allocation.values())
        
        # Grid pattern calculation
        grid_dimensions = self._calculate_grid_pattern(
            area_analysis, 
            drone_allocation, 
            coverage_per_drone
        )
        
        # Mission duration estimation
        mission_duration = self._estimate_mission_duration(
            area_analysis, 
            drone_allocation,
            disaster_type,
            priority
        )
        
        # Success probability calculation
        success_probability = self._calculate_success_probability(
            area_analysis, 
            drone_allocation,
            disaster_type,
            priority
        )
        
        # Risk assessment
        risk_level = self._assess_mission_risk(area_analysis, disaster_type, priority)
        
        return {
            "area_analysis": {
                "total_area_km2": area_analysis.area_sq_km,
                "effective_area_km2": round(effective_area, 2),
                "perimeter_km": area_analysis.perimeter_km,
                "terrain_type": area_analysis.terrain_type.value,
                "building_density": area_analysis.building_density,
                "accessibility_score": area_analysis.accessibility_score
            },
            "mission_requirements": {
                "disaster_type": disaster_type.value,
                "priority": priority.value,
                "required_coverage_percentage": self.required_coverage_percentage,
                "overlap_percentage": self.overlap_percentage
            },
            "drone_allocation": drone_allocation,
            "total_drones_required": total_drones,
            "coverage_grid": grid_dimensions,
            "mission_duration_hours": round(mission_duration, 2),
            "success_probability": round(success_probability, 3),
            "risk_level": risk_level,
            "coverage_per_drone_type": {k: round(v, 2) for k, v in coverage_per_drone.items()},
            "deployment_efficiency": round((effective_area - remaining_area) / effective_area, 3) if effective_area > 0 else 0
        }
    
    def _calculate_effective_range(self, specs: DroneSpecification) -> float:
        """Calculate effective range considering environmental factors"""
        # Wind penalty (simplified model)
        wind_penalty = min(0.3, self.environmental_factors["wind_speed_kmh"] / 100.0)
        
        # Terrain bonus/penalty
        terrain_modifiers = {
            "urban": 0.9,    # Slight penalty due to obstacles
            "rural": 1.0,    # Standard
            "mountainous": 0.8,  # Penalty for complex terrain
            "coastal": 1.1,  # Bonus for open areas
            "forest": 0.85,  # Penalty for tree coverage
            "desert": 1.05   # Slight bonus for open desert
        }
        
        terrain_factor = terrain_modifiers.get(self.environmental_factors["terrain_type"], 1.0)
        
        effective_range = specs.max_range_km * (1 - wind_penalty) * terrain_factor
        return max(effective_range * 0.7, specs.max_range_km * 0.5)  # Minimum 50% of max range
    
    def _calculate_grid_pattern(self, area_analysis: AreaAnalysis, 
                              drone_allocation: Dict[str, int], 
                              coverage_per_drone: Dict[str, float]) -> Dict:
        """Calculate optimal grid pattern for drone deployment"""
        area_km2 = area_analysis.area_sq_km
        
        # Calculate total coverage
        total_coverage = sum(
            drone_allocation.get(dt, 0) * coverage 
            for dt, coverage in coverage_per_drone.items()
        )
        
        # Assume rectangular area for grid calculation
        side_length = math.sqrt(area_km2)
        
        if total_coverage > 0:
            # Calculate grid cells
            cells_per_side = math.ceil(math.sqrt(total_coverage / area_km2))
            cell_size_km = side_length / cells_per_side
            
            return {
                "grid_rows": cells_per_side,
                "grid_columns": cells_per_side,
                "cell_size_km": round(cell_size_km, 2),
                "total_cells": cells_per_side ** 2
            }
        
        return {"grid_rows": 1, "grid_columns": 1, "cell_size_km": side_length, "total_cells": 1}
    
    def _estimate_mission_duration(self, area_analysis: AreaAnalysis, 
                                 drone_allocation: Dict[str, int],
                                 disaster_type: DisasterType,
                                 priority: MissionPriority) -> float:
        """Estimate mission duration in hours"""
        area_km2 = area_analysis.area_sq_km
        
        # Base time per km²
        base_time_per_km2 = 0.5  # hours per km²
        
        # Disaster type modifiers
        disaster_modifiers = {
            DisasterType.EARTHQUAKE: 1.2,  # More thorough search needed
            DisasterType.FLOOD: 0.8,
            DisasterType.WILDFIRE: 1.0,
            DisasterType.LANDSLIDE: 1.3,
            DisasterType.TSUNAMI: 1.1,
            DisasterType.CYCLONE: 0.9
        }
        
        # Priority modifiers
        priority_modifiers = {
            MissionPriority.SEARCH_AND_RESCUE: 1.3,  # Highest priority, more thorough
            MissionPriority.DAMAGE_ASSESSMENT: 1.0,
            MissionPriority.SURVEILLANCE: 0.8,
            MissionPriority.COMMUNICATION_RELAY: 0.7
        }
        
        base_time = (area_km2 * base_time_per_km2 * 
                    disaster_modifiers.get(disaster_type, 1.0) * 
                    priority_modifiers.get(priority, 1.0))
        
        # Add buffer time for complexity
        complexity_buffer = 1.0 + (area_km2 / 500.0)  # 1 hour buffer per 500 km²
        
        return base_time * complexity_buffer
    
    def _calculate_success_probability(self, area_analysis: AreaAnalysis, 
                                     drone_allocation: Dict[str, int],
                                     disaster_type: DisasterType,
                                     priority: MissionPriority) -> float:
        """Calculate mission success probability"""
        if sum(drone_allocation.values()) == 0:
            return 0.0
        
        # Base probability factors
        base_probability = 0.7
        
        # Area size factor (larger = harder)
        area_factor = max(0.5, 1.0 - (area_analysis.area_sq_km / 2000.0))
        
        # Accessibility factor
        accessibility_factor = area_analysis.accessibility_score
        
        # Terrain complexity factor
        terrain_complexity = {
            TerrainType.URBAN: 0.8,
            TerrainType.RURAL: 0.9,
            TerrainType.MOUNTAINOUS: 0.6,
            TerrainType.COASTAL: 0.85,
            TerrainType.FOREST: 0.7,
            TerrainType.DESERT: 0.9
        }
        terrain_factor = terrain_complexity.get(area_analysis.terrain_type, 0.8)
        
        # Disaster type factor
        disaster_factors = {
            DisasterType.EARTHQUAKE: 0.75,
            DisasterType.FLOOD: 0.85,
            DisasterType.WILDFIRE: 0.8,
            DisasterType.LANDSLIDE: 0.7,
            DisasterType.TSUNAMI: 0.8,
            DisasterType.CYCLONE: 0.75
        }
        disaster_factor = disaster_factors.get(disaster_type, 0.8)
        
        # Drone diversity bonus (more drone types = better coverage)
        diversity_bonus = 1.0 + (len(drone_allocation) * 0.05)
        
        # Calculate final probability
        probability = (base_probability * area_factor * accessibility_factor * 
                      terrain_factor * disaster_factor * diversity_bonus)
        
        return min(0.99, probability)  # Cap at 99%
    
    def _assess_mission_risk(self, area_analysis: AreaAnalysis, 
                           disaster_type: DisasterType,
                           priority: MissionPriority) -> str:
        """Assess overall mission risk level"""
        risk_score = 0.0
        
        # Area size risk
        area_risk = min(0.5, area_analysis.area_sq_km / 1000.0)
        risk_score += area_risk
        
        # Terrain complexity risk
        terrain_risk = {
            TerrainType.URBAN: 0.3,
            TerrainType.RURAL: 0.2,
            TerrainType.MOUNTAINOUS: 0.6,
            TerrainType.COASTAL: 0.25,
            TerrainType.FOREST: 0.4,
            TerrainType.DESERT: 0.2
        }
        risk_score += terrain_risk.get(area_analysis.terrain_type, 0.3)
        
        # Disaster type risk
        disaster_risk = {
            DisasterType.EARTHQUAKE: 0.8,
            DisasterType.FLOOD: 0.6,
            DisasterType.WILDFIRE: 0.7,
            DisasterType.LANDSLIDE: 0.9,
            DisasterType.TSUNAMI: 0.85,
            DisasterType.CYCLONE: 0.75
        }
        risk_score += disaster_risk.get(disaster_type, 0.7)
        
        # Priority risk (higher priority = higher acceptable risk)
        priority_risk = {
            MissionPriority.SEARCH_AND_RESCUE: 0.1,  # Accept higher risk for rescue
            MissionPriority.DAMAGE_ASSESSMENT: 0.2,
            MissionPriority.SURVEILLANCE: 0.3,
            MissionPriority.COMMUNICATION_RELAY: 0.25
        }
        risk_score += priority_risk.get(priority, 0.2)
        
        if risk_score >= 1.8:
            return "critical"
        elif risk_score >= 1.3:
            return "high"
        elif risk_score >= 0.8:
            return "medium"
        else:
            return "low"

# Global instance
capacity_intelligence = DroneCapacityIntelligence()

# Example usage function
def analyze_disaster_response(area_coordinates: List[Tuple[float, float]], 
                            terrain_type: str,
                            disaster_type: str,
                            priority: str = "search_and_rescue",
                            available_drones: Optional[Dict[str, int]] = None) -> Dict:
    """Main function to analyze disaster response requirements"""
    
    try:
        terrain_enum = TerrainType(terrain_type.lower())
        disaster_enum = DisasterType(disaster_type.lower())
        priority_enum = MissionPriority(priority.lower())
    except ValueError as e:
        logger.error(f"Invalid parameter: {e}")
        raise
    
    # Analyze area
    area_analysis = capacity_intelligence.analyze_area(area_coordinates, terrain_enum)
    
    # Calculate requirements
    requirements = capacity_intelligence.calculate_drone_requirements(
        area_analysis, disaster_enum, priority_enum, available_drones
    )
    
    logger.info(f"✅ Capacity analysis complete for {disaster_type} response")
    return requirements