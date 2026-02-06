# 🚁 Multi-Camera System - Quick Reference Card

## START THE SYSTEM (3 Commands)

```powershell
# Terminal 1 - Backend
cd backend && python app.py

# Terminal 2 - VSLAM Cameras  
cd drone_simulation && python visual_slam.py

# Terminal 3 - Dashboard
cd dashboard && npm run dev
```

---

## VISUAL INDICATORS

### 🟢 INDEPENDENT MODE (Default)
```
Border:  GREEN #00ff66
Label:   📷 OWN FEED
Updates: 2 sec polling
Badge:   LIVE
Frame:   Unique per drone
```

### 🔵 TACTICAL SWARM MODE
```
Border:  CYAN #00d4ff
Label:   🛰️ BROADCAST
Updates: 10 FPS MJPEG
Badge:   STREAM
Frame:   Identical all drones
```

---

## CONTROL BUTTON

**Independent → Tactical:**
```
Click: "🛰️ ACTIVATE TACTICAL SWARM"
Drones: 12
All Feeds: ✅ ACTIVE
(Changes to Broadcast: 📡 LIVE)
```

**Tactical → Independent:**
```
Click: "📷 SWITCH TO INDEPENDENT CAMERAS"
All Feeds: ✅ ACTIVE (switches back)
```

---

## ALL 12 DRONES

| ID | Independent | Tactical |
|----|------------|----------|
| 1-12 | Unique feed | Sync feed |
| Border | 🟢 Green | 🔵 Cyan |
| Label | 📷 | 🛰️ |
| Color | Rotating hue | White/gray |

---

## KEY FEATURES

✅ Click toggles all 12 drones instantly  
✅ No page refresh needed  
✅ No system restart needed  
✅ Both modes available anytime  
✅ Visual feedback always shows current mode  

---

## TROUBLESHOOTING

| Issue | Fix |
|-------|-----|
| No video | Check VSLAM terminal shows "ESTABLISHED" |
| Won't switch | Refresh page (F5) |
| All look same | Wait 3-5 sec, refresh page |
| Weird colors | Normal - synthetic pattern rotation |

---

## COMMAND REFERENCE

```python
# Enable Tactical Swarm
POST /api/drones/tactical-swarm/enable
→ All drones use broadcast frame

# Disable Tactical Swarm  
POST /api/drones/tactical-swarm/disable
→ All drones use own camera

# Check Status
GET /api/drones/tactical-swarm/status
→ Returns: tactical_swarm_enabled, independent_feeds
```

---

## FILES MODIFIED

- ✅ `drone_simulation/multi_drone_camera.py` (NEW)
- ✅ `drone_simulation/visual_slam.py` (enhanced)
- ✅ `backend/api/drone_api.py` (enhanced)
- ✅ `dashboard/src/components/VSLAMCameraFeed.jsx` (redesigned)
- ✅ `dashboard/src/components/TacticalSwarmControl.jsx` (redesigned)

---

## MODE SWITCHING LOGIC

```
User clicks button
    ↓
Frontend calls /enable or /disable
    ↓
Backend sets tactical_swarm_enabled flag
    ↓
Each DroneAgent's set_broadcast_mode() called
    ↓
Drones switch frame source:
  - Independent: use own camera
  - Tactical: use shared broadcast frame
    ↓
Frontend polls status, updates colors
    ↓
All screens instantly reflect new mode
```

---

## PERFORMANCE

**Independent Mode:**
- 2 FPS polling (frontend refresh rate)
- Lower bandwidth
- 12 unique parallel feeds
- Perfect for individual reconnaissance

**Tactical Swarm Mode:**
- 10 FPS MJPEG streaming
- Synchronized across all drones
- Single broadcast source
- Perfect for coordinated operations

---

## CUSTOMIZE

### Change Camera Index
`drone_simulation/multi_drone_camera.py`
```python
# Line ~45
camera_index = idx % 2  # Cycles 0,1,0,1... for 2 cameras
```

### Change Polling Rate  
`dashboard/src/components/VSLAMCameraFeed.jsx`
```javascript
// Line ~30
}, 2000);  // Change 2000ms to desired interval
```

### Change Frame Rate
`backend/api/drone_api.py`
```python
# Line ~120  
time.sleep(0.1)  # 10 FPS - change for different rate
```

---

**🎯 Ready to fly! Start those 3 terminals above.**

📖 Full docs: [INDEPENDENT_MULTI_CAMERA_GUIDE.md](INDEPENDENT_MULTI_CAMERA_GUIDE.md)
