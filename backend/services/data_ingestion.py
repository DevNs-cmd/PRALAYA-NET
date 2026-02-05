import httpx
import os
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
from config import NASA_FIRMS_URL, USGS_EARTHQUAKE_URL, OPENWEATHER_ALERTS_URL, INGESTION_INTERVAL_SEC
from orchestration.decision_engine import decision_engine

class LiveDataIngestor:
    """
    Background worker service to fetch real disaster data from production APIs
    """
    def __init__(self):
        self.active_workers = False
        self.last_fetch = {}
        self.api_key_nasa = os.getenv("NASA_API_KEY")
        self.api_key_weather = os.getenv("OPENWEATHER_API_KEY")

    async def start_monitoring(self):
        """Starts the infinite monitoring loop"""
        self.active_workers = True
        print("🌍 LIVE DATA INGESTOR: INITIALIZED")
        
        while self.active_workers:
            try:
                print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Polling global disaster APIs...")
                await asyncio.gather(
                    self.fetch_usgs_earthquakes(),
                    self.fetch_nasa_firms(),
                    self.fetch_weather_alerts()
                )
            except Exception as e:
                print(f"⚠️ Ingestion error: {e}")
            
            await asyncio.sleep(INGESTION_INTERVAL_SEC)

    async def fetch_usgs_earthquakes(self):
        """Fetch real-time earthquake data from USGS"""
        params = {
            "format": "geojson",
            "starttime": (datetime.now() - timedelta(hours=1)).isoformat(),
            "minmagnitude": 4.5
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(USGS_EARTHQUAKE_URL, params=params)
                if response.status_code == 200:
                    data = response.json()
                    for feature in data.get("features", []):
                        props = feature["properties"]
                        coords = feature["geometry"]["coordinates"]
                        # Inject into decision engine if not processed
                        event_id = feature["id"]
                        if event_id not in self.last_fetch:
                            print(f"📢 USGS DETECTED: Mag {props['mag']} Earthquake at {props['place']}")
                            decision_engine.process_disaster(
                                disaster_type="earthquake",
                                severity=min(props['mag'] / 10.0, 1.0),
                                location={"lat": coords[1], "lon": coords[0], "name": props['place']},
                                metadata={"usgs_id": event_id, "source": "USGS_LIVE"}
                            )
                            self.last_fetch[event_id] = True
            except Exception as e:
                print(f"❌ USGS Fetch Failed: {e}")

    async def fetch_nasa_firms(self):
        """Fetch wildfire data from NASA FIRMS"""
        if not self.api_key_nasa: return
        # FIRMS API often requires an area bounding box or key
        # Skipping implementation for now as it needs a specific MAP_KEY
        pass

    async def fetch_weather_alerts(self):
        """Fetch extreme weather from OpenWeather"""
        if not self.api_key_weather: return
        # Implementation for OpenWeather One Call API
        pass

# Global instance
data_ingestor = LiveDataIngestor()
