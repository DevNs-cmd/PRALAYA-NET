"""
Telemetry Generator - Generates fake drone telemetry data
"""

from typing import Dict, Optional
import random
from datetime import datetime
from config import DRONE_MAX_ALTITUDE, DRONE_UPDATE_INTERVAL

class TelemetryGenerator:
    """
    Generates realistic telemetry data for drones
    """
    
    def __init__(self):
        self.telemetry_data = {}
    
    def get_telemetry(self, drone_id: str) -> Optional[Dict]:
        """
        Get current telemetry for a drone
        
        Args:
            drone_id: ID of the drone
        
        Returns:
            Telemetry data dictionary
        """
        if drone_id not in self.telemetry_data:
            # Initialize telemetry
            self.telemetry_data[drone_id] = {
                "drone_id": drone_id,
                "location": {
                    "lat": 28.6139 + random.uniform(-0.1, 0.1),
                    "lon": 77.2090 + random.uniform(-0.1, 0.1)
                },
                "altitude": random.uniform(10, DRONE_MAX_ALTITUDE),
                "speed": random.uniform(5, 15),  # m/s
                "heading": random.uniform(0, 360),  # degrees
                "battery": random.uniform(60, 100),
                "signal_strength": random.uniform(70, 100),
                "gps_status": "active",
                "slam_status": "inactive",
                "slam_points": 0,
                "camera_status": "active",
                "timestamp": datetime.now().isoformat()
            }
        
        # Update telemetry with slight variations
        telemetry = self.telemetry_data[drone_id]
        
        # Simulate movement
        telemetry["location"]["lat"] += random.uniform(-0.001, 0.001)
        telemetry["location"]["lon"] += random.uniform(-0.001, 0.001)
        telemetry["altitude"] += random.uniform(-2, 2)
        telemetry["altitude"] = max(0, min(DRONE_MAX_ALTITUDE, telemetry["altitude"]))
        
        # Update other metrics
        telemetry["speed"] = max(0, telemetry["speed"] + random.uniform(-1, 1))
        telemetry["heading"] = (telemetry["heading"] + random.uniform(-5, 5)) % 360
        telemetry["battery"] = max(0, telemetry["battery"] - random.uniform(0, 0.5))
        telemetry["signal_strength"] = max(0, min(100, telemetry["signal_strength"] + random.uniform(-2, 2)))
        
        telemetry["timestamp"] = datetime.now().isoformat()
        
        return telemetry
    
    def update_telemetry(self, drone_id: str, updates: Dict):
        """Update telemetry data manually"""
        if drone_id not in self.telemetry_data:
            self.telemetry_data[drone_id] = {}
        
        self.telemetry_data[drone_id].update(updates)
        self.telemetry_data[drone_id]["timestamp"] = datetime.now().isoformat()
    
    def set_gps_status(self, drone_id: str, status: str):
        """Set GPS status for a drone"""
        if drone_id in self.telemetry_data:
            self.telemetry_data[drone_id]["gps_status"] = status
    
    def set_slam_status(self, drone_id: str, status: str):
        """Set SLAM status for a drone"""
        if drone_id in self.telemetry_data:
            self.telemetry_data[drone_id]["slam_status"] = status

# Global instance
telemetry_gen = TelemetryGenerator()

