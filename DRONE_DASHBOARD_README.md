# PRALAYA-NET Autonomous Drone Operations Dashboard

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.12+ for backend
- Node.js 18+ for frontend
- npm or yarn package manager

### Installation

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Backend will start at: `http://127.0.0.1:8000`

#### Frontend Setup
```bash
cd dashboard
npm install
npm run dev
```
Frontend will start at: `http://localhost:5173`

## 🎯 Features Implemented

### 1. Drone Simulation Layer
- ✅ Virtual drone fleet manager (12 drones)
- ✅ Safe drone count calculation based on:
  - Weather conditions (wind speed, precipitation, temperature)
  - Risk score assessment
  - Visibility factors
- ✅ GPS fallback using satellite/weather estimation
- ✅ OpenWeather API integration (with demo fallback)

### 2. Interactive Map
- ✅ Leaflet-based interactive map
- ✅ Click anywhere to fetch:
  - Real-time weather conditions
  - AI risk level assessment
  - Safe drone count
  - NASA environmental data
- ✅ Disaster zone visualization
- ✅ Infrastructure markers with risk color coding

### 3. Live Drone View Simulation
- ✅ 12-panel camera feed grid
- ✅ WebRTC/MediaStream camera access
- ✅ Real-time feed replication across all panels
- ✅ Simulated telemetry display (altitude, speed, heading)
- ✅ Drone fleet status sidebar

### 4. Backend APIs
- `GET /api/drones/fleet-status` - Complete fleet status
- `GET /api/drones/safe-count` - Safe deployment calculation
- `POST /api/drones/safe-count` - With full weather data
- `POST /api/drones/deploy` - Deploy drone to target
- `POST /api/drones/recall` - Recall drone to base
- `POST /api/drones/position-estimate` - GPS fallback estimation
- `POST /api/drones/prediction` - AI prediction with ≥90% confidence
- `GET /api/drones/conditions/{lat}/{lon}` - Comprehensive conditions

### 5. UI/UX Enhancements
- ✅ Beautiful navbar with Tailwind-inspired styling
- ✅ Backend status indicator (online/offline)
- ✅ Mode indicator (Live/Simulation)
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Dark theme throughout

## 📡 API Integration

### OpenWeather API
Set `OPENWEATHER_API_KEY` environment variable for live weather data.

### NASA POWER API
Integrated for climate data and environmental monitoring.

### Data.gov Datasets
Used for risk historical data and prediction.

## 🎮 Demo Mode

The system runs in demo mode by default with simulated data:
- Weather conditions based on location coordinates
- Risk scores calculated from coordinate-based simulation
- Safe drone counts with weather factors

Set `DEMO_MODE=false` for production use.

## 🖥️ Pages

| Route | Description |
|-------|-------------|
| `/` | Main Dashboard with map and intel feed |
| `/command-center` | Original command center |
| `/enhanced-command-center` | Enhanced command interface |
| `/demo-command-center` | Demo command center |
| `/drone-view` | **NEW** - 12-panel drone camera view |

## 🚁 Drone View Features

1. **12-Panel Grid Display**
   - Real-time camera feed from your device
   - All panels mirror the same feed
   - Individual drone selection

2. **Telemetry Dashboard**
   - Live altitude, speed, heading
   - Battery and signal strength
   - GPS status

3. **Safe Drone Count**
   - Real-time zone status
   - Weather-based deployment limits

4. **AI Prediction**
   - 94% confidence scoring
   - Risk trend analysis

## 🔧 Configuration

### Environment Variables
```
VITE_API_URL=http://127.0.0.1:8000  # Frontend API URL
DEMO_MODE=true                        # Use simulated data
OPENWEATHER_API_KEY=your_key         # Live weather
NASA_API_KEY=your_key                # NASA data
```

### Deployment

#### Render (Backend)
```yaml
# backend/render.yaml
runtime: python312
buildCommand: pip install -r requirements.txt
startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
```

#### Netlify/Vercel (Frontend)
Configure API redirects in `netlify.toml` or `vercel.json`

## 📊 Risk Calculation

The AI risk score (0-100) is calculated from:

| Factor | Weight | Conditions |
|--------|--------|------------|
| Wind Speed | 40 pts | >14 m/s = max, <4 m/s = min |
| Rainfall | 30 pts | >10mm/hr = max, <2mm/hr = min |
| Temperature | 15 pts | >40°C or <-5°C = max |
| Conditions | 15 pts | Thunderstorms, cyclones, etc. |
| NASA Precip | 20 pts | Precipitation anomaly |

## 🎯 Safe Drone Count Formula

```
safe_count = TOTAL_DRONES × risk_factor × wind_factor × 
             precip_factor × temp_factor × visibility_factor
```

## 📈 Prediction Module

- Confidence: ≥90%
- Trend analysis: Stable/Escalating/Fluctuating
- 24-hour forecast with hourly predictions
- Action recommendations based on risk level

## 🔗 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | System health check |
| `/api/drones/fleet-status` | GET | Fleet overview |
| `/api/drones/safe-count` | GET/POST | Safe drone count |
| `/api/drones/conditions/{lat}/{lon}` | GET | Full conditions |
| `/rediction` | POST | AIapi/drones/p prediction |
| `/api/geo-intel` | GET | Geo-intelligence |
| `/api/weather` | GET | Weather data |

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/drone-enhancement`
3. Commit changes: `git commit -am 'Add drone feature'`
4. Push to branch: `git push origin feature/drone-enhancement`
5. Create Pull Request

## 📞 Support

- GitHub Issues for bug reports
- Wiki for detailed documentation
- Discord community for discussions

---

**Built with ❤️ for autonomous disaster response and national infrastructure resilience**

