"""
Risk Alert API - Endpoint for ESP32 hardware alerts with caching
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import time
import requests
from datetime import datetime, timedelta
import os
import json

from orchestration.alert_manager import alert_manager
from orchestration.decision_engine import decision_engine
from config import HIGH_RISK, MEDIUM_RISK, LOW_RISK

router = APIRouter()

# Simple in-memory cache for API results
class RiskAlertCache:
    def __init__(self, ttl: int = 30):
        self.cache = None
        self.last_update = None
        self.ttl = ttl
    
    def get(self):
        """Get cached data if fresh"""
        if self.cache and self.last_update:
            age = time.time() - self.last_update
            if age < self.ttl:
                return self.cache
        return None
    
    def set(self, data):
        """Cache new data"""
        self.cache = data
        self.last_update = time.time()
    
    def is_stale(self):
        """Check if cache is stale"""
        return self.get() is None

risk_cache = RiskAlertCache(ttl=30)

@router.post("/api/risk-alert")
async def get_risk_alert(x_api_key: Optional[str] = Header(None)):
    """
    GET risk alert status and hardware trigger signal
    
    Returns JSON with:
    - risk_score: float (0.0-1.0)
    - risk_level: string (safe, low, medium, high, critical)
    - hardware_action: string (none, alert, alarm)
    - hardware_trigger: dict with LED/buzzer signals
    - timestamp: ISO format timestamp
    - message: Human-readable message
    """
    try:
        # Check cache first (for performance)
        cached = risk_cache.get()
        if cached:
            cached["source"] = "cache"
            return cached
        
        # Calculate current risk from active disasters
        risk_score = _calculate_current_risk()
        risk_level = _get_risk_level(risk_score)
        hardware_action = _get_hardware_action(risk_score)
        
        # Generate hardware trigger signals
        hardware_trigger = {
            "buzzer": risk_score >= HIGH_RISK,
            "red_led": risk_score >= MEDIUM_RISK,
            "green_led": risk_score < MEDIUM_RISK,
            "pulse": risk_score >= HIGH_RISK,
            "intensity": min(int(risk_score * 255), 255)
        }
        
        # Get latest alert details
        recent_alerts = alert_manager.get_alert_history(limit=1)
        alert_message = recent_alerts[0].get("message", "") if recent_alerts else "No active alerts"
        
        response = {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "hardware_action": hardware_action,
            "hardware_trigger": hardware_trigger,
            "timestamp": datetime.now().isoformat(),
            "message": alert_message,
            "active_disasters": len(decision_engine.active_disasters),
            "source": "live"
        }
        
        # Cache the result
        risk_cache.set(response)
        
        return response
    
    except Exception as e:
        print(f"❌ RISK ALERT ERROR: {str(e)}")
        # Return a safe fallback instead of 500
        return {
            "risk_score": 0.0,
            "risk_level": "safe",
            "hardware_action": "none",
            "hardware_trigger": {
                "buzzer": False,
                "red_led": False,
                "green_led": True,
                "pulse": False,
                "intensity": 0
            },
            "timestamp": datetime.now().isoformat(),
            "message": "System check in progress",
            "active_disasters": 0,
            "source": "fallback"
        }

@router.get("/api/risk-alert")
async def get_risk_alert_get():
    """
    GET risk alert status (for ESP32 polling)
    Same as POST endpoint for backward compatibility
    """
    try:
        cached = risk_cache.get()
        if cached:
            cached["source"] = "cache"
            return cached
        
        risk_score = _calculate_current_risk()
        risk_level = _get_risk_level(risk_score)
        hardware_action = _get_hardware_action(risk_score)
        
        hardware_trigger = {
            "buzzer": risk_score >= HIGH_RISK,
            "red_led": risk_score >= MEDIUM_RISK,
            "green_led": risk_score < MEDIUM_RISK,
            "pulse": risk_score >= HIGH_RISK,
            "intensity": min(int(risk_score * 255), 255)
        }
        
        recent_alerts = alert_manager.get_alert_history(limit=1)
        alert_message = recent_alerts[0].get("message", "") if recent_alerts else "System nominal"
        
        response = {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "hardware_action": hardware_action,
            "hardware_trigger": hardware_trigger,
            "timestamp": datetime.now().isoformat(),
            "message": alert_message,
            "active_disasters": len(decision_engine.active_disasters),
            "source": "live"
        }
        
        risk_cache.set(response)
        return response
    
    except Exception as e:
        print(f"❌ RISK ALERT ERROR (GET): {str(e)}")
        return {
            "risk_score": 0.0,
            "risk_level": "safe",
            "hardware_action": "none",
            "hardware_trigger": {
                "buzzer": False,
                "red_led": False,
                "green_led": True,
                "pulse": False,
                "intensity": 0
            },
            "timestamp": datetime.now().isoformat(),
            "message": "System check in progress",
            "active_disasters": 0,
            "source": "fallback"
        }

@router.get("/api/risk-alert/history")
async def get_risk_alert_history(limit: int = 20):
    """
    Get historical risk alert data
    
    Query parameters:
    - limit: number of recent alerts to return (default: 20)
    """
    try:
        history = alert_manager.get_alert_history(limit=limit)
        return {
            "total": len(history),
            "alerts": history,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/risk-alert/trigger-test")
async def trigger_test_alert():
    """
    Test endpoint to trigger hardware without real disaster
    (Useful for testing ESP32 hardware)
    """
    try:
        test_alert = {
            "type": "test",
            "severity": HIGH_RISK + 0.05,
            "message": "TEST ALERT - Hardware activation test",
            "timestamp": datetime.now().isoformat(),
            "channel": "esp32"
        }
        
        alert_manager.dispatch_alerts([test_alert])
        
        return {
            "status": "test_triggered",
            "message": "Hardware test alert sent to ESP32",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _calculate_current_risk() -> float:
    """
    Calculate current system risk from active disasters
    Returns float between 0.0 and 1.0
    """
    if not decision_engine.active_disasters:
        return 0.0
    
    # Get highest severity from active disasters
    max_severity = max([d.get("severity", 0.0) for d in decision_engine.active_disasters])
    
    # Apply cascading multiplier (could be higher with cascading failures)
    cascading_factor = 1.0 + (len(decision_engine.active_disasters) * 0.1)
    
    risk = min(max_severity * cascading_factor, 1.0)
    return risk

def _get_risk_level(risk_score: float) -> str:
    """
    Categorize risk score into levels
    """
    if risk_score >= 0.95:
        return "critical"
    elif risk_score >= HIGH_RISK:
        return "high"
    elif risk_score >= MEDIUM_RISK:
        return "medium"
    elif risk_score >= 0.3:
        return "low"
    else:
        return "safe"

def _get_hardware_action(risk_score: float) -> str:
    """
    Determine hardware action based on risk
    """
    if risk_score >= HIGH_RISK:
        return "alarm"
    elif risk_score >= MEDIUM_RISK:
        return "alert"
    else:
        return "none"

def _fetch_gov_data(api_key: str = None) -> dict:
    """
    Fetch data from Government/NASA open data APIs
    Uses API key from environment variables
    """
    if not api_key:
        api_key = os.getenv("DATA_GOV_KEY")
    
    if not api_key:
        raise ValueError("DATA_GOV_KEY not configured in environment variables")
    
    # Example: NASA EONET API (Events, Coordinates, Geometry API)
    # This is a placeholder - replace with actual API calls
    try:
        response = requests.get(
            "https://eonet.gsfc.nasa.gov/api/v3/events",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch government data: {str(e)}")
