"""
National Resilience Score Engine
Real-time district-level resilience scoring and heatmap generation
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json

from services.national_digital_twin import national_digital_twin
from services.crowd_intelligence import crowd_intelligence_service

class ResilienceCategory(Enum):
    INFRASTRUCTURE = "infrastructure"
    HEALTHCARE = "healthcare"
    TELECOM = "telecom"
    ENERGY = "energy"
    WATER = "water"
    TRANSPORT = "transport"

@dataclass
class DistrictResilienceScore:
    district: str
    overall_score: float
    category_scores: Dict[str, float]
    population_served: int
    infrastructure_health: float
    weather_risk: float
    healthcare_load: float
    telecom_availability: float
    energy_redundancy: float
    timestamp: datetime
    trend: str  # improving, stable, declining
    risk_level: str  # critical, high, medium, low

class NationalResilienceEngine:
    def __init__(self):
        self.resilience_scores: Dict[str, DistrictResilienceScore] = {}
        self.historical_scores: List[Dict] = []
        self.weight_factors = {
            "infrastructure_health": 0.25,
            "weather_risk": 0.20,
            "healthcare_load": 0.20,
            "telecom_availability": 0.15,
            "energy_redundancy": 0.20
        }
        
    async def calculate_national_resilience(self) -> Dict[str, DistrictResilienceScore]:
        """Calculate real-time resilience scores for all districts"""
        for district in national_digital_twin.districts.keys():
            score = await self._calculate_district_resilience(district)
            self.resilience_scores[district] = score
        
        return self.resilience_scores
    
    async def _calculate_district_resilience(self, district: str) -> DistrictResilienceScore:
        """Calculate resilience score for a specific district"""
        # Get infrastructure health
        infrastructure_health = national_digital_twin.get_district_resilience_score(district)
        
        # Simulate weather risk (in production, integrate with weather APIs)
        weather_risk = np.random.uniform(0.1, 0.8)
        
        # Simulate healthcare load
        healthcare_load = np.random.uniform(0.3, 0.9)
        
        # Simulate telecom availability
        telecom_availability = np.random.uniform(0.7, 0.95)
        
        # Simulate energy redundancy
        energy_redundancy = np.random.uniform(0.4, 0.9)
        
        # Calculate category scores
        category_scores = {
            "infrastructure": infrastructure_health,
            "healthcare": 1.0 - healthcare_load,
            "telecom": telecom_availability,
            "energy": energy_redundancy,
            "water": infrastructure_health * 0.9,  # Correlated with infrastructure
            "transport": infrastructure_health * 0.85
        }
        
        # Calculate overall score
        overall_score = (
            infrastructure_health * self.weight_factors["infrastructure_health"] +
            (1.0 - weather_risk) * self.weight_factors["weather_risk"] +
            (1.0 - healthcare_load) * self.weight_factors["healthcare_load"] +
            telecom_availability * self.weight_factors["telecom_availability"] +
            energy_redundancy * self.weight_factors["energy_redundancy"]
        )
        
        # Determine trend and risk level
        trend = self._calculate_trend(district, overall_score)
        risk_level = self._determine_risk_level(overall_score)
        
        return DistrictResilienceScore(
            district=district,
            overall_score=overall_score,
            category_scores=category_scores,
            population_served=sum(
                national_digital_twin.nodes[nid].population_served
                for nid in national_digital_twin.districts[district]
            ),
            infrastructure_health=infrastructure_health,
            weather_risk=weather_risk,
            healthcare_load=healthcare_load,
            telecom_availability=telecom_availability,
            energy_redundancy=energy_redundancy,
            timestamp=datetime.now(),
            trend=trend,
            risk_level=risk_level
        )
    
    def _calculate_trend(self, district: str, current_score: float) -> str:
        """Calculate resilience trend based on historical data"""
        # Simplified - in production, analyze historical trends
        if current_score > 0.7:
            return "improving"
        elif current_score > 0.5:
            return "stable"
        else:
            return "declining"
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level based on resilience score"""
        if score < 0.3:
            return "critical"
        elif score < 0.5:
            return "high"
        elif score < 0.7:
            return "medium"
        else:
            return "low"
    
    def get_resilience_heatmap_data(self) -> Dict:
        """Get resilience data formatted for heatmap visualization"""
        heatmap_data = []
        
        for district, score in self.resilience_scores.items():
            # Get district coordinates (simplified)
            coords = self._get_district_coordinates(district)
            
            heatmap_data.append({
                "district": district,
                "lat": coords["lat"],
                "lon": coords["lon"],
                "resilience_score": score.overall_score,
                "risk_level": score.risk_level,
                "population": score.population_served,
                "category_scores": score.category_scores,
                "trend": score.trend
            })
        
        return {
            "heatmap_data": heatmap_data,
            "national_average": np.mean([s.overall_score for s in self.resilience_scores.values()]),
            "critical_districts": len([s for s in self.resilience_scores.values() if s.risk_level == "critical"]),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_district_coordinates(self, district: str) -> Dict:
        """Get district coordinates (simplified)"""
        coordinates = {
            "mumbai": {"lat": 19.0760, "lon": 72.8777},
            "delhi": {"lat": 28.7041, "lon": 77.1025},
            "bangalore": {"lat": 12.9716, "lon": 77.5946},
            "kolkata": {"lat": 22.5726, "lon": 88.3639},
            "chennai": {"lat": 13.0827, "lon": 80.2707},
            "hyderabad": {"lat": 17.3850, "lon": 78.4867},
            "pune": {"lat": 18.5204, "lon": 73.8567},
            "ahmedabad": {"lat": 23.0225, "lon": 72.5714},
            "jaipur": {"lat": 26.9124, "lon": 75.7873},
            "surat": {"lat": 21.1702, "lon": 72.8311}
        }
        return coordinates.get(district, {"lat": 20.5937, "lon": 78.9629})

# Global instance
national_resilience_engine = NationalResilienceEngine()
