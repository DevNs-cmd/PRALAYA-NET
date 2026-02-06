# 🛰️ Tactical Swarm Real-Time Camera Network

## Overview
Your PRALAYA-NET system now features **Tactical Swarm Mode**, a unified OpenCV-powered real-time camera network that connects all drone screens to a synchronized broadcast feed. When activated, all drones receive and display real-time camera feeds simultaneously, creating a unified visual intelligence system.

## Features

### ✅ What Tactical Swarm Mode Does

1. **Real-Time Frame Broadcasting**
   - All drone screens connected to a single OpenCV network
   - Synchronized frame delivery across all units
   - MJPEG streaming for low-latency video feeds

2. **Unified Camera Feed**
   - Master camera source distributed to all drones
   - Individual drone processing maintains SLAM functionality
   - Live keypoint detection and feature mapping visible on all screens

3. **Visual Synchronization**
   - All screens display identical baseline, then process individually
   - Blue border highlight with "TACTICAL SWARM" indicator appears on active screens
   - Stream status badge shows live broadcast connection

4. **Performance Optimizations**
   - Efficient JPEG encoding/decoding
   - 10 FPS streaming capability
   - Non-blocking frame updates to backend
   - Connection pooling for simultaneous drone streams

## How to Use

### Activating Tactical Swarm Mode

1. **Open Dashboard**
   - Navigate to the main PRALAYA-NET dashboard

2. **Locate Control Panel**
   - Find the "🛰️ Tactical Swarm Control" section at the top of the Control Panel

3. **Activate**
   - Click the green **"🟢 ACTIVATE TACTICAL SWARM"** button

4. **Observe Changes**
   - All drone camera feeds will synchronize
   - Blue borders appear on all drone screen panels
   - "TACTICAL SWARM" indicator displays in top-right of each feed
   - "📡 LIVE" status badge shows broadcast is active

### Monitoring Tactical Swarm Status

Watch the Control Panel for:
- **Drones Connected**: Count of actively streaming drones
- **Broadcast Status**: Shows "📡 LIVE" when frames are broadcasting
- **System Message**: Green confirmation when mode is activated

### Deactivating Tactical Swarm Mode

1. Click the red **"🔴 DEACTIVATE TACTICAL SWARM"** button
2. Drones return to independent operation mode
3. Blue borders disappear, individual frame polling resumes

## Architecture

### Backend Components

**[drone_api.py](backend/api/drone_api.py)**
- `/api/drones/tactical-swarm/enable` - Activate swarm mode
- `/api/drones/tactical-swarm/disable` - Deactivate swarm mode
- `/api/drones/tactical-swarm/status` - Get current status
- Frame broadcasting via `shared_broadcast_frame` global

**[visual_slam.py](drone_simulation/visual_slam.py)**
- `DroneAgent` enhanced with `tactical_swarm` parameter
- `DroneSwarmManager` broadcasts frames to all connected drones
- OpenCV frame processing with SLAM keypoint detection
- Binary frame upload to backend

### Frontend Components

**[VSLAMCameraFeed.jsx](dashboard/src/components/VSLAMCameraFeed.jsx)**
- Detects tactical swarm mode status
- Switches between polling (independent) and MJPEG streaming (tactical)
- Visual indicators for mode status
- Automatic stream connection management

**[TacticalSwarmControl.jsx](dashboard/src/components/TacticalSwarmControl.jsx)**
- Main control interface for tactical swarm activation
- Real-time status polling (2-second updates)
- Visual feedback with pulsing status indicator
- Connected drone count and broadcast status display

## Technical Details

### Frame Flow in Tactical Swarm Mode

```
Master Camera (Webcam/Synthetic)
    ↓
DroneSwarmManager.get_master_frame()
    ↓
Broadcast to all DroneAgent instances (parallel)
    ↓
Each drone processes frame with SLAM
    ↓
drone_frames[drone_id] = processed_frame
    ↓
shared_broadcast_frame = processed_frame (for tactical sync)
    ↓
Backend: /api/drones/slam/{drone_id}/frame
    ↓
VSLAMCameraFeed receives MJPEG stream
    ↓
All screens display synchronized feed
```

### OpenCV Processing Pipeline

1. **Frame Capture** (12 FPS master capture)
2. **Resize** (320x240 for bandwidth optimization)
3. **Feature Detection** (ORB detector, 200 features)
4. **Keypoint Filtering** (minimum 5 points threshold)
5. **SLAM Visualization** (draw green keypoints)
6. **Telemetry Sync** (10 FPS to backend)
7. **JPEG Encoding** (85% quality)
8. **MJPEG Stream** (multipart/x-mixed-replace)

### Network Protocols

**Upload Frame (Drone → Backend)**
```
POST /api/drones/slam/{drone_id}/frame
Content-Type: application/octet-stream
Body: JPEG binary data
```

**Get Live Snapshot**
```
GET /api/drones/slam/{drone_id}/live?t={timestamp}
Response: JPEG image
```

**Stream MJPEG**
```
GET /api/drones/slam/{drone_id}/stream
Response: multipart/x-mixed-replace; boundary=frame
```

## Performance Metrics

- **Frame Rate**: 12 FPS master capture → 10 FPS telemetry sync → ~2 FPS polling / continuous MJPEG
- **JPEG Quality**: 85% (balanced quality/bandwidth)
- **Frame Dimensions**: 320x240 pixels (optimized transmission)
- **Feature Detection**: 200 ORB features per frame
- **Connection Pool**: 20 concurrent connections per session
- **Retry Logic**: 3 attempts with exponential backoff

## Troubleshooting

### "NO SIGNAL" on Canvas
- Check if backend is running: `http://127.0.0.1:8000/api/drones/status`
- Verify visual_slam.py is executing drone swarm initialization
- Check browser console for CORS or connection errors

### Tactical Swarm Not Activating
- Ensure all drone agents are deployed (check console for "DRONE X: SYSTEMS ONLINE")
- Verify 12 target drones deployed successfully
- Check `/api/drones/tactical-swarm/status` returns enabled=true

### MJPEG Stream Stops
- Backend may be overloaded (reduce frame broadcast frequency)
- Check browser tab is active (some browsers throttle background tabs)
- Verify network connection stability

### Frames Not Synchronized
- SLAM processing may have variable latency
- This is normal; synchronization is at broadcast level, processing is parallel
- Baseline frame is synchronized; SLAM keypoints added per-drone in real-time

## Starting the System

### Full System Start

1. **Terminal 1 - Backend**
   ```bash
   cd backend
   python -m pip install -r requirements.txt
   python app.py
   ```

2. **Terminal 2 - VSLAM with Tactical Swarm**
   ```bash
   cd drone_simulation
   python visual_slam.py
   ```
   (Automatically initializes tactical swarm on startup)

3. **Terminal 3 - Dashboard**
   ```bash
   cd dashboard
   npm install
   npm run dev
   ```

4. **Activate in Dashboard**
   - Open dashboard UI
   - Click "🟢 ACTIVATE TACTICAL SWARM" button
   - Observe synchronized feeds on all drone screens

## Advanced Configuration

### Adjust Master Capture Rate
In `visual_slam.py`, modify `DroneSwarmManager.sync_swarm()`:
```python
time.sleep(0.08)  # ~12 FPS. Change to 0.05 for ~20 FPS
```

### Adjust JPEG Quality
In `drone_api.py`, modify frame encoding:
```python
_, img_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
# Change 85 to higher (90-95) for better quality, lower (70-80) for less bandwidth
```

### Increase Keypoint Detection
In `visual_slam.py`, modify `DroneAgent.process_slam()`:
```python
orb = cv2.ORB_create(nfeatures=200)  # Increase to 300+ for more features
```

## Concept Diagram

```
┌─────────────────────────────────────────────────────────┐
│            TACTICAL SWARM VISION NETWORK               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Master Camera Source                                   │
│        ↓                                                │
│  OpenCV Processing                                      │
│        ↓                                                │
│  ┌──────────────────────────────────────────┐          │
│  │     Real-Time Frame Broadcast            │          │
│  │   (All Screens Connected & Synced)       │          │
│  └──────────────────────────────────────────┘          │
│   ↙    ↓    ↙    ↓    ↙    ↓    ↙    ↓    ↙           │
│                                                         │
│  Drone Screen 1  Drone Screen 2  ... Drone Screen N   │
│  [SLAM Active]   [SLAM Active]        [SLAM Active]   │
│  TacticalSwarm   TacticalSwarm        TacticalSwarm   │
│        │              │                     │          │
│        └──────────────┴─────────────────────┘          │
│                   ↓                                     │
│             Unified Intelligence Feed                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

**Status**: ✅ Production Ready  
**Last Updated**: February 6, 2026  
**Version**: 1.0 - Tactical Swarm OpenCV Network
