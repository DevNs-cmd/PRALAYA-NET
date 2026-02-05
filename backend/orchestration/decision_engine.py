"""
Decision Engine - Master Brain that combines AI outputs and triggers actions
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
import math

from ai.satellite_ai import satellite_ai
from ai.flood_predictor import flood_predictor
from ai.graph_risk import cascading_risk_analyzer
from ai.space_weather import space_weather_monitor
from config import CRITICAL_INFRA, HIGH_RISK, MEDIUM_RISK
from drone.drone_controller import drone_controller

# Import satellite_zones (shared list)
from api.satellite_api import satellite_zones

import asyncio
from services.ws_manager import ws_manager

class DecisionEngine:
    """
    Master decision engine that:
    1. Processes disasters from various sources
    2. Runs AI models to assess risks
    3. Determines cascading failure risks
    4. Generates action plans and alerts
    """
    
    def __init__(self):
        self.active_disasters = []
        self.decision_history = []
        self.risk_progression = {}  # Track risk over time
    
    def process_disaster(self,
                        disaster_type: str,
                        severity: float,
                        location: Dict,
                        metadata: Optional[Dict] = None) -> Dict:
        """
        Process a disaster and generate decision
        """
        disaster_id = f"disaster_{len(self.active_disasters) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        disaster = {
            "id": disaster_id,
            "type": disaster_type,
            "severity": severity,
            "location": location,
            "metadata": metadata or {},
            "detected_at": datetime.now().isoformat(),
            "radius": self._calculate_disaster_radius(disaster_type, severity)
        }
        self.active_disasters.append(disaster)
        
        # Register disaster zone on map
        self._register_disaster_zone(disaster)
        
        # Run AI models with disaster-aware logic
        ai_results = self._run_ai_models(disaster)
        
        # Analyze cascading risks with disaster-specific propagation
        cascading_analysis = cascading_risk_analyzer.analyze_cascading_risk({
            "type": disaster_type,
            "location": location,
            "severity": severity,
            "disaster_id": disaster_id
        })
        
        # Generate intelligent action plan
        action_plan = self._generate_action_plan(
            disaster,
            ai_results,
            cascading_analysis
        )
        
        # Execute actions (deploy drones, etc.)
        self._execute_actions(action_plan, disaster)
        
        # Generate alerts
        alerts = self._generate_alerts(
            disaster,
            cascading_analysis,
            action_plan
        )
        
        decision = {
            "disaster_id": disaster_id,
            "disaster": disaster,
            "ai_results": ai_results,
            "cascading_analysis": cascading_analysis,
            "action_plan": action_plan,
            "alerts": alerts,
            "timestamp": datetime.now().isoformat()
        }
        
        self.decision_history.append(decision)
        self.risk_progression[disaster_id] = {
            "initial_severity": severity,
            "current_severity": severity,
            "trend": "stable"
        }
        
        # BROADCAST to Dashboard via WebSockets
        asyncio.create_task(ws_manager.broadcast({
            "type": "DISASTER_DETECTED",
            "data": decision
        }))
        
        return decision
    
    def _calculate_disaster_radius(self, disaster_type: str, severity: float) -> float:
        """Calculate affected radius in kilometers"""
        base_radius = {
            "flood": 5.0,
            "fire": 2.0,
            "earthquake": 10.0,
            "cyclone": 15.0,
            "landslide": 1.0
        }
        radius = base_radius.get(disaster_type, 3.0) * severity
        return round(radius, 2)
    
    def _register_disaster_zone(self, disaster: Dict):
        """Register disaster zone for map display"""
        zone = {
            "id": disaster["id"],
            "type": disaster["type"],
            "severity": disaster["severity"],
            "location": disaster["location"],
            "radius": disaster["radius"] * 1000,  # Convert to meters for map
            "detected_at": disaster["detected_at"]
        }
        satellite_zones.append(zone)
    
    def _run_ai_models(self, disaster: Dict) -> Dict:
        """Run all relevant AI models with deterministic, disaster-aware logic"""
        results = {}
        disaster_type = disaster["type"]
        severity = disaster["severity"]
        
        # Satellite AI - detect anomalies based on disaster type
        if disaster_type in ["fire", "flood", "cyclone", "earthquake"]:
            satellite_result = self._simulate_satellite_detection(disaster)
            results["satellite_ai"] = satellite_result
        
        # Flood Predictor - if flood-related
        if disaster_type == "flood":
            weather = self._simulate_weather_data(disaster)
            flood_pred = flood_predictor.predict_flood_risk(
                disaster["location"],
                weather
            )
            # Enhance with deterministic logic
            flood_pred["flood_risk"] = min(1.0, severity * 1.2)  # Flood risk escalates
            flood_pred["time_to_flood_hours"] = max(1, int(12 / severity))
            results["flood_predictor"] = flood_pred
        
        # Space Weather - check GPS/communication status
        space_weather = space_weather_monitor.check_space_weather()
        
        # Trigger GPS failure if cyclone or earthquake (simulated)
        if disaster_type in ["cyclone", "earthquake"] and severity > 0.7:
            space_weather["gps_status"] = "degraded"
            space_weather["gps_reliability"] = 0.5
            space_weather["solar_storm_active"] = True
        
        results["space_weather"] = space_weather
        
        return results
    
    def _simulate_satellite_detection(self, disaster: Dict) -> Dict:
        """Simulate realistic satellite AI detection"""
        disaster_type = disaster["type"]
        severity = disaster["severity"]
        
        # Deterministic confidence based on severity
        base_confidence = {
            "flood": 0.85,
            "fire": 0.90,
            "earthquake": 0.75,
            "cyclone": 0.80
        }
        
        confidence = base_confidence.get(disaster_type, 0.70) * (0.8 + severity * 0.2)
        confidence = min(0.95, max(0.65, confidence))
        
        # Calculate water surface increase for floods
        water_increase = None
        if disaster_type == "flood":
            water_increase = round(severity * 40, 1)  # 40% base increase
        
        anomaly_type_map = {
            "flood": "flood",
            "fire": "fire",
            "earthquake": "land_change",
            "cyclone": "cloud_anomaly"
        }
        
        return {
            "disaster_type": disaster_type,
            "confidence": round(confidence, 3),
            "severity": round(severity, 3),
            "anomalies": [{
                "type": anomaly_type_map.get(disaster_type, "unknown"),
                "confidence": round(confidence, 3),
                "water_surface_increase_percent": water_increase,
                "detected_at": datetime.now().isoformat()
            }],
            "detected_at": datetime.now().isoformat(),
            "reasoning": f"ViT model detected {disaster_type} with {confidence*100:.1f}% confidence. Satellite imagery shows significant anomaly."
        }
    
    def _simulate_weather_data(self, disaster: Dict) -> Dict:
        """Generate realistic weather data for disaster"""
        disaster_type = disaster["type"]
        severity = disaster["severity"]
        
        if disaster_type == "flood":
            return {
                "precipitation": round(20 + severity * 40, 1),
                "humidity": round(70 + severity * 20, 1),
                "temperature": round(25 - severity * 5, 1),
                "wind_speed": round(5 + severity * 15, 1)
            }
        return {
            "precipitation": 10.0,
            "humidity": 60.0,
            "temperature": 25.0,
            "wind_speed": 10.0
        }
    
    def _generate_action_plan(self,
                             disaster: Dict,
                             ai_results: Dict,
                             cascading_analysis: Dict) -> Dict:
        """Generate intelligent action plan based on analysis"""
        actions = []
        priority = "medium"
        severity = disaster["severity"]
        
        # Determine priority based on severity and cascading risks
        critical_nodes = cascading_analysis.get("critical_nodes", [])
        max_cascade_risk = max([n["risk"] for n in critical_nodes], default=0.0)
        
        if severity >= HIGH_RISK or max_cascade_risk >= HIGH_RISK:
            priority = "critical"
        elif severity >= MEDIUM_RISK or max_cascade_risk >= MEDIUM_RISK:
            priority = "high"
        
        # Infrastructure protection for critical nodes
        if critical_nodes:
            for node in critical_nodes:
                if node["risk"] >= HIGH_RISK:
                    actions.append({
                        "type": "infrastructure_protection",
                        "target": node["id"],
                        "target_name": node["name"],
                        "action": "initiate_protection_protocol",
                        "urgency": "immediate"
                    })
        
        # Deploy reconnaissance drones
        slam_required = space_weather_monitor.should_use_slam()
        actions.append({
            "type": "drone_deployment",
            "location": disaster["location"],
            "action": "deploy_reconnaissance_drone",
            "slam_required": slam_required,
            "count": 2 if priority == "critical" else 1,
            "mission": "assess_damage_and_evacuation_routes"
        })
        
        # Alert distribution
        actions.append({
            "type": "alert",
            "channels": ["dashboard", "esp32", "mobile"],
            "action": "send_alerts",
            "recipients": ["authorities", "emergency_services", "public"]
        })
        
        # Evacuation protocol
        if priority == "critical":
            actions.append({
                "type": "evacuation",
                "location": disaster["location"],
                "action": "initiate_evacuation_protocol",
                "radius_km": disaster["radius"]
            })
        
        # Resource allocation
        if disaster["type"] == "flood":
            actions.append({
                "type": "resource_allocation",
                "resources": ["rescue_boats", "sandbags", "medical_teams"],
                "action": "mobilize_flood_response_teams"
            })
        elif disaster["type"] == "fire":
            actions.append({
                "type": "resource_allocation",
                "resources": ["fire_teams", "helicopters", "water_trucks"],
                "action": "mobilize_fire_response_teams"
            })
        
        return {
            "priority": priority,
            "actions": actions,
            "estimated_response_time": "5-10 minutes" if priority == "critical" else "15-30 minutes",
            "resources_mobilized": len([a for a in actions if a["type"] == "resource_allocation"])
        }
    
    def _execute_actions(self, action_plan: Dict, disaster: Dict):
        """Execute actions like deploying drones"""
        for action in action_plan["actions"]:
            if action["type"] == "drone_deployment":
                count = action.get("count", 1)
                for i in range(count):
                    drone_id = drone_controller.deploy_drone(disaster["location"])
                    if action.get("slam_required", False):
                        drone_controller.enable_slam(drone_id)
                        drone_controller.execute_command(drone_id, "takeoff", {"altitude": 50})
    
    def _generate_alerts(self,
                        disaster: Dict,
                        cascading_analysis: Dict,
                        action_plan: Dict) -> List[Dict]:
        """Generate alerts to send"""
        alerts = []
        
        # Main disaster alert
        alerts.append({
            "id": f"alert_{disaster['id']}_main",
            "type": "disaster_detected",
            "severity": disaster["severity"],
            "disaster_type": disaster["type"],
            "location": disaster["location"],
            "message": f"{disaster['type'].upper()} DETECTED at {disaster['location'].get('name', 'location')}. Severity: {disaster['severity']*100:.0f}%",
            "timestamp": datetime.now().isoformat(),
            "channel": "all"
        })
        
        # Cascading risk alerts
        critical_nodes = cascading_analysis.get("critical_nodes", [])
        for node in critical_nodes:
            alerts.append({
                "id": f"alert_{disaster['id']}_cascade_{node['id']}",
                "type": "cascading_risk",
                "severity": node["risk"],
                "target": node["name"],
                "target_id": node["id"],
                "message": f"CRITICAL: {node['name']} at {node['risk']*100:.0f}% risk due to cascading failure from {disaster['type']}",
                "timestamp": datetime.now().isoformat(),
                "channel": "all"
            })
        
        # GPS failure alert (if applicable)
        if action_plan["actions"] and any(a.get("slam_required") for a in action_plan["actions"]):
            alerts.append({
                "id": f"alert_{disaster['id']}_gps",
                "type": "gps_failure",
                "severity": 0.8,
                "message": "GPS unavailable - All drones switching to V-SLAM navigation mode",
                "timestamp": datetime.now().isoformat(),
                "channel": "dashboard"
            })
        
        # Priority alert
        if action_plan["priority"] == "critical":
            alerts.append({
                "id": f"alert_{disaster['id']}_priority",
                "type": "priority_alert",
                "severity": 1.0,
                "message": "CRITICAL PRIORITY: Immediate response required. Evacuation protocol activated.",
                "timestamp": datetime.now().isoformat(),
                "channel": "all"
            })
        
        return alerts
    
    def get_active_disasters(self) -> List[Dict]:
        """Get list of active disasters"""
        return self.active_disasters
    
    def clear_all(self):
        """Clear all disasters and reset"""
        self.active_disasters = []
        self.decision_history = []
        self.risk_progression = {}
        cascading_risk_analyzer.reset_risks()
        satellite_zones.clear()

# Global instance
decision_engine = DecisionEngine()
