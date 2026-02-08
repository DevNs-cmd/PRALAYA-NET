# PRALAYA-NET Drone Operations Dashboard - Implementation Plan

## Information Gathered

### Current Architecture
- **Backend**: FastAPI with 40+ API endpoints for disaster management
- **Frontend**: React + Vite with Leaflet maps, 5 command center variants
- **Drone API**: `drone_fleet_api.py` with basic fleet management (12 drones)
- **Geo-Intel**: Weather, NASA POWER, infrastructure endpoints
- **Demo Mode**: Enabled by default with simulated data fallbacks

### Critical Components Analyzed
- `backend/main.py` - Main FastAPI app with CORS and API endpoints
- `backend/api/drone_fleet_api.py` - Drone fleet management (needs enhancement)
- `dashboard/src/App.jsx` - Main router with navigation
- `dashboard/src/pages/Dashboard.jsx` - Main dashboard with MapView
- `dashboard/src/components/MapView.jsx` - Leaflet map with click handler
- `dashboard/src/components/RiskPopup.jsx` - Geo-intel popup (needs safe drone count)
- `dashboard/src/services/api.js` - API service layer
- `dashboard/src/services/geoIntelligenceService.js` - Geo-intel with fallback data

## Implementation Plan

### Phase 1: Backend Enhancements (Drone Fleet & APIs)
1. **Enhance `backend/api/drone_fleet_api.py`**:
   - Add safe drone count calculation with weather-based limits
   - Integrate OpenWeather API for real-time weather data
   - Add GPS fallback using satellite/weather estimation
   - Implement prediction module with confidence scoring

2. **Update `backend/main.py`**:
   - Add safe-drone-count endpoint with weather integration
   - Add prediction/risk estimation endpoint with ≥90% confidence simulation
   - Connect NASA and Data.gov datasets

### Phase 2: Frontend Services Update
1. **Update `dashboard/src/services/api.js`**:
   - Add `getSafeDroneCount()` function
   - Add `fetchPrediction()` function
   - Add `fetchDroneCameraFeed()` placeholder

2. **Update `dashboard/src/services/geoIntelligenceService.js`**:
   - Add safe drone count fetching
   - Add prediction module integration
   - Enhance fallback data generation

### Phase 3: Interactive Map Enhancements
1. **Enhance `dashboard/src/components/MapView.jsx`**:
   - Pass API URL properly
   - Add live weather/risk display on click

2. **Enhance `dashboard/src/components/RiskPopup.jsx`**:
   - Fetch and display safe drone count
   - Display real-time weather conditions
   - Show risk level with recommendations

### Phase 4: Drone View Simulation (12-Panel Camera Feed)
1. **Create `dashboard/src/components/DroneView.jsx`**:
   - 12-panel grid for simulated drone camera feeds
   - WebRTC/MediaStream for device camera access
   - Real-time feed replication across all panels
   - "Launch Drone View" button integration

2. **Update `dashboard/src/App.jsx`**:
   - Add `/drone-view` route
   - Add "Launch Drone View" button to navbar
   - Beautify navbar with Tailwind CSS

### Phase 5: UI/UX Improvements
1. **Beautify Navigation**:
   - Add Tailwind styling to navbar
   - Add mode indicators (Live/Simulation)
   - Add backend status indicator

2. **Fix Routing Issues**:
   - Ensure all routes load correctly
   - Add error boundaries
   - Improve responsive design

### Phase 6: Deployment Readiness
1. **Backend Configuration**:
   - Update `backend/requirements.txt`
   - Update `backend/render.yaml` for Python 3.12
   - Ensure proper CORS for production

2. **Frontend Configuration**:
   - Update `dashboard/vite.config.js` with environment variables
   - Update `dashboard/netlify.toml` and `vercel.json`
   - Add production API URL configuration

## Files to Create/Modify

### New Files
- `dashboard/src/components/DroneView.jsx` - 12-panel camera feed

### Modified Files
1. `backend/api/drone_fleet_api.py` - Enhanced drone fleet management
2. `backend/main.py` - New endpoints for drone operations
3. `dashboard/src/services/api.js` - New API functions
4. `dashboard/src/services/geoIntelligenceService.js` - Enhanced geo-intel
5. `dashboard/src/components/MapView.jsx` - Enhanced map interactions
6. `dashboard/src/components/RiskPopup.jsx` - Safe drone count display
7. `dashboard/src/App.jsx` - New route and navbar improvements
8. `dashboard/src/index.css` - Enhanced Tailwind styles

## Success Criteria
- ✅ Click map → Get live weather, risk level, AND safe drone count
- ✅ Launch Drone View → 12-panel camera feed with device camera
- ✅ Safe drone count based on real-time weather/wind/risk
- ✅ ≥90% predictive confidence scoring (simulated)
- ✅ Beautiful responsive Tailwind UI
- ✅ Deployment-ready for Render/Netlify

## Follow-up Steps
1. Install backend dependencies: `cd backend && pip install -r requirements.txt`
2. Install frontend dependencies: `cd dashboard && npm install`
3. Start backend: `cd backend && python main.py`
4. Start frontend: `cd dashboard && npm run dev`
5. Test click-to-fetch functionality
6. Test drone view simulation

