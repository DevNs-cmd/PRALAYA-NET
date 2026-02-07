# backend/config.py

APP_NAME = "PRALAYA-NET Backend"
VERSION = "0.1.0"

# Server Configuration
HOST = "0.0.0.0"
PORT = 8000
CORS_ORIGINS = [
    "http://localhost:5173", 
    "http://localhost:3000", 
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://0.0.0.0:5173",
    "http://0.0.0.0:3000",
    "https://pralaya-net.vercel.app",
    "*"  # Fallback for production
]

# Risk Thresholds
LOW_RISK = 0.3
MEDIUM_RISK = 0.6
HIGH_RISK = 0.8
CRITICAL_RISK = 0.9

# Critical Infrastructure Locations (for demo)
CRITICAL_INFRA = [
    {"id": "power_grid_1", "name": "Power Grid Station A", "lat": 28.6139, "lon": 77.2090, "type": "power"},
    {"id": "hospital_1", "name": "City Hospital", "lat": 28.7041, "lon": 77.1025, "type": "healthcare"},
    {"id": "water_supply_1", "name": "Water Treatment Plant", "lat": 28.5355, "lon": 77.3910, "type": "water"},
    {"id": "telecom_1", "name": "Telecom Tower", "lat": 28.5562, "lon": 77.1000, "type": "telecom"},
]

# Disaster Types
DISASTER_TYPES = ["flood", "fire", "earthquake", "cyclone", "landslide"]

# AI Model Parameters
SATELLITE_IMAGE_SIZE = (224, 224)
FLOOD_PREDICTION_HORIZON = 24  # hours
GNN_UPDATE_INTERVAL = 5  # seconds

# ESP32 Configuration
ESP32_POLL_INTERVAL = 10  # seconds
ESP32_BASE_URL = "http://192.168.1.100"  # Update with your ESP32 IP

# Drone Configuration
DRONE_UPDATE_INTERVAL = 2  # seconds
DRONE_BATTERY_DECAY = 0.1  # per minute
DRONE_MAX_ALTITUDE = 120  # meters

# Data Paths
DATA_RAW_PATH = "data/raw"
DATA_PROCESSED_PATH = "data/processed"
DATA_SIMULATED_PATH = "data/simulated"

# Real-time Data Sources
NASA_FIRMS_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
USGS_EARTHQUAKE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"
OPENWEATHER_ALERTS_URL = "https://api.openweathermap.org/data/2.5/onecall"

# Ingestion Settings
INGESTION_INTERVAL_SEC = 300  # 5 minutes
CACHE_TTL_SEC = 3600  # 1 hour
