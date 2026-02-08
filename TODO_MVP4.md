# PRALAYA-NET MVP4 Implementation Plan

## Overview
Implement all upgrades for a hackathon-ready autonomous drone operations dashboard with:
- Real-time safe drone count
- Live weather/wind/risk integration  
- 12-panel drone camera feed
- Enhanced UI with Tailwind CSS
- Full deployment readiness

---

## Phase 1: Backend Enhancements

### 1.1 Enhanced drone_fleet_api.py
- [ ] Implement real-time safe drone count calculation with live weather data
- [ ] Integrate OpenWeather API for wind/weather conditions
- [ ] Add risk prediction module with confidence scoring (≥90%)
- [ ] Create live weather endpoint with wind speed/direction
- [ ] Add drone fleet status streaming endpoint

**New Endpoints:**
- `GET /api/drones/live-weather?lat=&lon=` - Live weather data
- `GET /api/drones/safe-count` - Already exists, enhance with live data
- `GET /api/drones/prediction` - Risk prediction with confidence score

---

## Phase 2: Frontend Services

### 2.1 Enhanced api.js
- [ ] Add `fetchLiveWeather(lat, lon)` - Weather with wind
- [ ] Add `fetchSafeDroneCount(lat, lon, riskScore)` - Safe count calculation
- [ ] Add `fetchDroneFleetStatus()` - Fleet overview
- [ ] Add `fetchRiskPrediction(lat, lon)` - Prediction with confidence

---

## Phase 3: Interactive Map & Risk Popup

### 3.1 Enhanced MapView.jsx
- [ ] Keep interactive map clicks working
- [ ] Show live weather overlay on map
- [ ] Display safe drone count indicator
- [ ] Add drone fleet markers with status
- [ ] Real-time weather visualization

### 3.2 Enhanced RiskPopup.jsx
- [ ] Show live weather conditions (temp, wind, humidity)
- [ ] Display calculated safe drone count
- [ ] Show risk prediction with confidence percentage
- [ ] Add drone recommendations
- [ ] Live data refresh every 5 seconds

---

## Phase 4: Drone View - 12 Panel Camera Feed

### 4.1 Create DroneView.jsx
- [ ] 12-panel grid layout using CSS Grid
- [ ] WebRTC/MediaStream integration for live camera
- [ ] Device camera access (user's webcam)
- [ ] Individual panel controls (mute, fullscreen)
- [ ] Panel labels and status indicators
- [ ] Responsive design for mobile

**Layout:**
```
┌────┬────┬────┐
│ 1  │ 2  │ 3  │
├────┼────┼────┤
│ 4  │ 5  │ 6  │
├────┼────┼────┤
│ 7  │ 8  │ 9  │
├────┼────┼────┤
│ 10 │ 11 │ 12 │
└────┴────┴────┘
```

---

## Phase 5: UI Enhancements

### 5.1 Enhanced App.jsx Navigation
- [ ] Add Drone View to nav menu
- [ ] Add live status indicators
- [ ] Improve responsive navbar design

### 5.2 Enhanced Dashboard.jsx
- [ ] Add safe drone count card
- [ ] Show live weather widget
- [ ] Add prediction confidence display
- [ ] Real-time status badges

---

## Phase 6: Deployment Configuration

### 6.1 Backend (Render)
- [ ] Verify render.yaml configuration
- [ ] Test startup script (render-start.sh)
- [ ] Verify requirements.txt

### 6.2 Frontend (Netlify/Vercel)
- [ ] Verify netlify.toml / vercel.json
- [ ] Test API URL environment variables
- [ ] Verify build configuration

---

## Implementation Order

1. **Backend Services** - Core APIs first
2. **Frontend Services** - API layer
3. **Map & Popup** - Visual components
4. **DroneView** - New feature
5. **UI Polish** - Navigation & Dashboard
6. **Deployment** - Final configuration

---

## Success Criteria

- ✅ Backend runs on Render
- ✅ Frontend runs on Netlify/Vercel
- ✅ Interactive map with live weather
- ✅ Safe drone count calculation with 90%+ confidence
- ✅ 12-panel camera feed working
- ✅ Modern responsive UI
- ✅ All components work together seamlessly

---

## Files to Modify/Create

### Modify:
- `backend/api/drone_fleet_api.py`
- `dashboard/src/services/api.js`
- `dashboard/src/components/MapView.jsx`
- `dashboard/src/components/RiskPopup.jsx`
- `dashboard/src/App.jsx`
- `dashboard/src/pages/Dashboard.jsx`

### Create:
- `dashboard/src/components/DroneView.jsx`

---

## Estimated Time
2-3 hours for full implementation

---

## Testing Checklist

- [ ] Backend health check passes
- [ ] Weather API returns data
- [ ] Safe drone count calculates correctly
- [ ] Map clicks show popup with data
- [ ] Drone camera feed opens
- [ ] Responsive design works
- [ ] No console errors
- [ ] Demo mode fallback works

