# 🎥 Independent Multi-Camera Quick Start

## What You Now Have

✅ **Each drone has its own independent camera**  
✅ **All drones can switch to tactical swarm broadcast simultaneously**  
✅ **One-click mode switching between independent and broadcast**  
✅ **Visual indicators showing which mode each drone is in**

---

## 3 Simple Commands to Start

### Terminal 1: Backend
```bash
cd backend
python app.py
```

### Terminal 2: VSLAM with Multi-Camera System
```bash
cd drone_simulation
python visual_slam.py
```
You'll see:
```
📷 INITIALIZING INDEPENDENT CAMERA NETWORK
📷 drone_1: synthetic fallback
📷 drone_2: synthetic fallback
... (12 drones)
✅ 12 drone cameras initialized

🟢 INDEPENDENT CAMERA NETWORK ESTABLISHED
Each drone displays its own camera feed
Ready to switch to tactical swarm mode on command
```

### Terminal 3: Dashboard
```bash
cd dashboard
npm run dev
```

---

## What You'll See

### Independent Mode (Default)
- **Green borders** on all drone screens
- **"📷 OWN FEED"** label in top-right
- **Each drone shows unique colored pattern**
- **"LIVE" badge** (polling mode)
- **All screens look different** (12 unique feeds)

### Switch to Tactical Swarm
1. Find **"📷 Independent Cameras"** control panel
2. Click **"🛰️ ACTIVATE TACTICAL SWARM"**
3. Watch all screens instantly:
   - Turn **Cyan (blue)** borders
   - Show **"🛰️ BROADCAST"** label
   - Become **identical** (all same feed)
   - Get **"STREAM" badge** (MJPEG 10 FPS)

---

## Quick Visual Guide

```
INDEPENDENT MODE              TACTICAL SWARM MODE
═════════════════            ════════════════════
Green Borders                  Cyan Borders
📷 OWN FEED                   🛰️ BROADCAST
Different on each             Same on all
LIVE badge                    STREAM badge
2 FPS polling                10 FPS MJPEG
```

---

## Control Panel

### Toggle Button Changes Based on Mode

**When in Independent Mode:**
```
🛰️ ACTIVATE TACTICAL SWARM
(Green button)
```

**When in Tactical Swarm Mode:**
```
📷 SWITCH TO INDEPENDENT CAMERAS
(Red button)
```

### Status Indicators

```
Independent Mode:        Tactical Swarm Mode:
Drones: 12              Drones: 12
All Feeds: ✅ ACTIVE    Broadcast: 📡 LIVE
```

---

## Features

### Independent Mode
- ✅ Each drone = unique camera feed
- ✅ Unique colored synthetic pattern per drone
- ✅ Individual SLAM processing
- ✅ Green border indicators
- ✅ Perfect for reconnaissance

### Tactical Swarm Mode
- ✅ All drones = synchronized broadcast
- ✅ Unified vision system
- ✅ Cyan border indicators  
- ✅ Higher frame rate (10 FPS)
- ✅ Perfect for coordination

---

## Keyboard Tips

No special commands needed - just use the control panel button!

```
Click Button:  Switches between modes
Takes ~1-2 seconds for all 12 drones to switch
No page refresh required
No system restart needed
```

---

## Troubleshooting

### No video on drone screens?
```bash
# Make sure VSLAM is running and shows:
# 🟢 INDEPENDENT CAMERA NETWORK ESTABLISHED
```

### Mode won't switch?
```bash
# Refresh the dashboard page
# Check browser console (F12) for errors
```

### All screens look same in independent mode?
```bash
# Normal at startup - wait 3-5 seconds
# Each drone's camera initializes sequentially
```

### Want real cameras instead of synthetic?
```bash
# Connect USB webcams to your computer
# Modify drone_simulation/multi_drone_camera.py
# Change: camera_index = idx % 2 (cycles through available)
```

---

## What's Different from Last Version

| Feature | Before | Now |
|---------|--------|-----|
| **Per-Drone Feeds** | All same | Independent unique feed each |
| **Camera Assignment** | Single master | One per drone |
| **Mode Switching** | Broadcast only | Toggle between 2 modes |
| **Visual Indicators** | Blue/Cyan only | Green (independent) + Cyan (broadcast) |
| **Default State** | Broadcast | Independent |

---

## Next Steps

1. ✅ **Start 3 terminals** (Backend, VSLAM, Dashboard)
2. ✅ **View independent feeds** (green borders, all different)
3. ✅ **Click control panel button** to switch to tactical
4. ✅ **Watch all screens sync** (cyan borders, all identical)
5. ✅ **Toggle back and forth** to test modes
6. ✅ **Trigger disasters** to test with real scenarios

---

## Drones in Independent Mode Pattern

Each drone's unique synthetic camera shows:
- **Drone #1** → Orange (unique pattern)
- **Drone #2** → Yellow (unique pattern)
- **Drone #3** → Green (unique pattern)
- **Drone #4** → Cyan (unique pattern)
- **Drone #5** → Blue (unique pattern)
- ... (colors rotate)

Each has its own moving circle and frame counter!

---

**🎯 You now have a production-ready multi-camera drone system!**

For detailed info: See [INDEPENDENT_MULTI_CAMERA_GUIDE.md](INDEPENDENT_MULTI_CAMERA_GUIDE.md)

Happy flying! 🚁🎥
