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
        print("[INIT] LIVE DATA INGESTOR: INITIALIZED")
        
        while self.active_workers:
            try:
                print(f"[POLL] [{datetime.now().strftime('%H:%M:%S')}] Polling global disaster APIs...")
                await asyncio.gather(
                    self.fetch_usgs_earthquakes(),
                    self.fetch_nasa_firms(),
                    self.fetch_weather_alerts()
                )
            except Exception as e:
                print(f"[WARN] Ingestion error: {e}")
            
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
                            print(f"[USGS] Earthquake detected: Mag {props['mag']} at {props['place']}")
                            decision_engine.process_disaster(
                                disaster_type="earthquake",
                                severity=min(props['mag'] / 10.0, 1.0),
                                location={"lat": coords[1], "lon": coords[0], "name": props['place']},
                                metadata={"usgs_id": event_id, "source": "USGS_LIVE"}
                            )
                            self.last_fetch[event_id] = True
            except Exception as e:
                print(f"[ERROR] USGS Fetch Failed: {e}")

    async def fetch_nasa_firms(self):
        """Fetch wildfire data from NASA FIRMS"""
        if not self.api_key_nasa: return
        
        # Area: Global, Source: VIIRS_SNPP, Range: 1 day
        # Format: URL/[KEY]/[SOURCE]/[AREA]/[RANGE]
        area = "world"
        source = "VIIRS_SNPP_NRT"
        url = f"{NASA_FIRMS_URL}/{self.api_key_nasa}/{source}/{area}/1"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    rows = response.text.strip().split("\n")
                    if len(rows) > 1: # Header + data
                        header = rows[0].split(",")
                        for row in rows[1:10]: # Process top 10 hotspots to avoid noise
                            data = dict(zip(header, row.split(",")))
                            lat, lon = float(data["latitude"]), float(data["longitude"])
                            bright = float(data["bright_ti4"])
                            
                            event_id = f"fire_{lat}_{lon}_{data['acq_date']}"
                            if event_id not in self.last_fetch:
                                print(f"[FIRE] NASA FIRMS detected: Active fire at {lat}, {lon} (Brightness: {bright})")
                                decision_engine.process_disaster(
                                    disaster_type="fire",
                                    severity=min(bright / 400.0, 1.0),
                                    location={"lat": lat, "lon": lon, "name": "Wildfire Hotspot"},
                                    metadata={"satellite": data["satellite"], "source": "NASA_FIRMS_LIVE"}
                                )
                                self.last_fetch[event_id] = True
            except Exception as e:
                print(f"[ERROR] NASA FIRMS Fetch Failed: {e}")

    async def fetch_weather_alerts(self):
        """Fetch extreme weather from OpenWeather"""
        if not self.api_key_weather: return
        
        # Using a default coordinate for global monitoring (example: New Delhi / Central region)
        # In production, this can iterate through multiple strategic hotspots
        lat, lon = 28.6139, 77.2090
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key_weather}&units=metric"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    main_weather = data["weather"][0]["main"].lower()
                    temp = data["main"]["temp"]
                    wind = data["wind"].get("speed", 0)
                    
                    # Automated disaster detection logic
                    alert_type = None
                    severity = 0
                    
                    if temp > 42:
                        alert_type = "heatwave"
                        severity = min((temp - 40) / 10, 1.0)
                    elif wind > 20:
                        alert_type = "cyclone"
                        severity = min(wind / 50, 1.0)
                    elif "rain" in main_weather or "storm" in main_weather:
                        alert_type = "flood"
                        severity = 0.6 # Elevated risk
                        
                    if alert_type:
                        event_id = f"weather_{alert_type}_{lat}_{lon}_{datetime.now().strftime('%Y%m%d%H')}"
                        if event_id not in self.last_fetch:
                            print(f"[WEATHER] Alert: {alert_type.upper()} detected at {data['name']}")
                            decision_engine.process_disaster(
                                disaster_type=alert_type,
                                severity=severity,
                                location={"lat": lat, "lon": lon, "name": data["name"]},
                                metadata={"temp": temp, "wind": wind, "source": "OPENWEATHER_LIVE"}
                            )
                            self.last_fetch[event_id] = True
            except Exception as e:
                print(f"[ERROR] Weather Fetch Failed: {e}")

# Global instance
data_ingestor = LiveDataIngestor()
