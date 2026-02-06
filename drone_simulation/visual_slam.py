import cv2
import numpy as np
import json
import requests
import time
import threading
from pathlib import Path
import random
import os
from datetime import datetime
import queue
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from multi_drone_camera import multi_drone_camera, DroneCamera

BACKEND_URL = "http://127.0.0.1:8000"

# Ensure directories exist
os.makedirs("data/recordings", exist_ok=True)

# Setup session with retries
def create_session():
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

class VideoRecorder:
    def __init__(self, drone_id):
        self.drone_id = drone_id
        self.recording = False
        self.frames = []
        self.last_save = time.time()
        self.save_interval = 30 # Seconds
        self.clip_duration = 10 # Seconds

    def process(self, frame):
        now = time.time()
        
        # Start recording if interval passed
        if not self.recording and (now - self.last_save > self.save_interval):
            self.recording = True
            self.frames = []
            
        if self.recording:
            self.frames.append(frame.copy())
            # Stop if duration reached (assuming ~10 FPS, so 100 frames)
            if len(self.frames) >= 100:
                self.save_clip()
                self.recording = False
                self.last_save = now

    def save_clip(self):
        if not self.frames: return
        try:
            filename = f"data/recordings/{self.drone_id}_{int(time.time())}.mp4"
            height, width, _ = self.frames[0].shape
            out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), 10, (width, height))
            for f in self.frames:
                out.write(f)
            out.release()
            print(f"🎥 CLIP SAVED: {filename}")
        except Exception as e:
            print(f"❌ RECORD ERROR: {e}")

class DroneAgent(threading.Thread):
    def __init__(self, drone_id, camera_source=None, tactical_swarm=False):
        threading.Thread.__init__(self)
        self.drone_id = drone_id
        self.running = True
        self.slam_enabled = True
        self.map_points = []
        self.keyframes = []
        self.last_sync_time = 0
        self.gps_active = True
        self.camera_source = camera_source
        self.current_frame = None
        self.recorder = VideoRecorder(drone_id)
        self.session = create_session()
        self.tactical_swarm = tactical_swarm
        self.swarm_mode_active = False
        self.use_broadcast = False  # Whether to use tactical broadcast frame
        
    def update_frame(self, frame):
        """For direct frame injection (deprecated in multi-camera mode)"""
        self.current_frame = frame.copy()

    def set_broadcast_mode(self, enabled: bool):
        """Switch between own camera and broadcast"""
        self.use_broadcast = enabled
        if enabled:
            print(f"  → {self.drone_id}: Switched to TACTICAL BROADCAST")
        else:
            print(f"  → {self.drone_id}: Switched to OWN CAMERA FEED")

    def run(self):
        print(f"🚁 DRONE {self.drone_id}: SYSTEMS ONLINE {'[TACTICAL SWARM]' if self.tactical_swarm else '[INDEPENDENT]'}")
        
        while self.running:
            # Get frame based on mode
            if self.use_broadcast:
                # Use tactical swarm broadcast
                frame = multi_drone_camera.get_broadcast_frame()
                mode_indicator = "BROADCAST"
            else:
                # Use drone's own camera
                frame = multi_drone_camera.get_drone_frame(self.drone_id)
                mode_indicator = "OWN_CAMERA"
            
            if frame is None:
                time.sleep(0.05)
                continue
                
            frame = frame.copy()
            height, width = frame.shape[:2]
            
            # Simulate GPS update
            target_status = "GPS_ACTIVE"
            if random.random() < 0.005: 
                self.gps_active = not self.gps_active
            
            if not self.gps_active:
                target_status = "GPS_LOST"
                
            # Process V-SLAM
            frame = self.process_slam(frame)
            
            # Vision Recorder
            self.recorder.process(frame)
            
            # HUD Overlay (Unique per drone)
            color = (0, 255, 0) if self.gps_active else (0, 0, 255)
            cv2.putText(frame, f"{self.drone_id}", (10, 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            cv2.putText(frame, f"{target_status}", (10, height-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            cv2.putText(frame, f"BAT: {random.randint(20, 100)}%", (width-80, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            # Add tactical swarm indicator
            if self.use_broadcast:
                cv2.rectangle(frame, (2, 2), (width-2, height-2), (0, 200, 255), 2)
                cv2.putText(frame, "TACTICAL BROADCAST", (width-180, 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 200, 255), 1)
            else:
                # Own camera indicator
                cv2.rectangle(frame, (2, 2), (width-2, height-2), (0, 255, 100), 2)
                cv2.putText(frame, "OWN FEED", (width-100, 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 100), 1)

            # Sync to backend
            self.sync_backend(frame, mode_indicator)
            
            self.current_frame = None
            time.sleep(0.01)

    def process_slam(self, frame):
        try:
            # Resize for performance/bandwidth (320x240)
            frame = cv2.resize(frame, (320, 240))
            
            # Feature Detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            orb = cv2.ORB_create(nfeatures=200)
            kp, des = orb.detectAndCompute(gray, None)
            
            # Mapping logic
            if len(kp) > 5:
                 self.map_points = [{"p": 1} for _ in range(len(kp))]
            
            # Draw Keypoints
            frame = cv2.drawKeypoints(frame, kp, None, color=(0, 255, 0), flags=0)
            
            return frame
        except Exception:
            return frame

    def sync_backend(self, frame, mode="OWN_CAMERA"):
        now = time.time()
        if now - self.last_sync_time < 0.1:  # 10 FPS sync
            return

        try:
            # Upload Frame with mode indicator
            _, img_encoded = cv2.imencode('.jpg', frame)
            self.session.post(
                f"{BACKEND_URL}/api/drones/slam/{self.drone_id}/frame", 
                data=img_encoded.tobytes(),
                timeout=2.0,
                headers={"Content-Type": "application/octet-stream"}
            )
            
            # Upload Telemetry
            payload = {
                "keypoints": len(self.map_points) * 10,
                "keyframes": len(self.keyframes),
                "status": "localized",
                "gps_status": "active" if self.gps_active else "lost",
                "tactical_swarm": self.use_broadcast,
                "camera_mode": mode
            }
            self.session.post(
                f"{BACKEND_URL}/api/drones/slam/{self.drone_id}/telemetry", 
                json=payload, 
                timeout=2.0
            )
            self.last_sync_time = now
        except Exception as e:
            pass

class DroneSwarmManager:
    def __init__(self):
        self.drones = []
        self.active_ids = []
        self.tactical_swarm_mode = False
        self.broadcast_running = False

    def init_drone_cameras(self, drone_ids):
        """Initialize independent cameras for all drones"""
        multi_drone_camera.initialize_drone_cameras(drone_ids)
    
    def broadcast_frame_to_backend(self, frame):
        """Broadcast frame to all drones via backend"""
        session = create_session()
        try:
            _, img_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_data = img_encoded.tobytes()
            
            # Send to all active drones
            for drone in self.drones:
                try:
                    session.post(
                        f"{BACKEND_URL}/api/drones/slam/{drone.drone_id}/frame",
                        data=frame_data,
                        timeout=0.5,
                        headers={"Content-Type": "application/octet-stream"}
                    )
                except Exception:
                    pass
        except Exception:
            pass

    def enable_tactical_swarm(self):
        """Enable tactical swarm mode - all drones show broadcast"""
        print("\n⚡ ACTIVATING TACTICAL SWARM MODE")
        print("   Switching all drone screens to broadcast feed...")
        
        self.tactical_swarm_mode = True
        multi_drone_camera.set_tactical_swarm_mode(True)
        
        # Switch all drones to broadcast mode
        for drone in self.drones:
            drone.set_broadcast_mode(True)
        
        print("✅ All drones switched to TACTICAL BROADCAST\n")

    def disable_tactical_swarm(self):
        """Disable tactical swarm mode - each drone shows own camera"""
        print("\n⚡ DEACTIVATING TACTICAL SWARM MODE")
        print("   Switching all drone screens to independent feeds...")
        
        self.tactical_swarm_mode = False
        multi_drone_camera.set_tactical_swarm_mode(False)
        
        # Switch all drones to own camera mode
        for drone in self.drones:
            drone.set_broadcast_mode(False)
        
        print("✅ All drones switched to INDEPENDENT CAMERA FEEDS\n")

    def sync_swarm(self):
        print("\n" + "═"*70)
        print("📡 DRONE SWARM INITIALIZATION: INDEPENDENT MULTI-CAMERA NETWORK")
        print("═"*70)
        
        target_count = 12
        self.active_ids = []
        
        try:
            # 1. Fetch/Deploy Drones
            resp = requests.get(f"{BACKEND_URL}/api/drones/status")
            if resp.status_code == 200:
                data = resp.json()
                self.active_ids = [d['id'] for d in data.get('drones', [])]
            
            missing = target_count - len(self.active_ids)
            if missing > 0:
                print(f"🚀 DEPLOYING {missing} ADDITIONAL UNITS...")
                for _ in range(missing):
                    resp = requests.post(
                        f"{BACKEND_URL}/api/drones/deploy", 
                        json={"lat": 28.61, "lon": 77.20}
                    )
                    if resp.status_code == 200:
                        self.active_ids.append(resp.json()['drone_id'])
                    time.sleep(0.05)
            
            # 2. Initialize independent cameras for all drones
            print(f"\n📷 INITIALIZING INDEPENDENT CAMERA SYSTEM")
            self.init_drone_cameras(self.active_ids)
            
            # 3. Launch Drone Agents with independent camera feeds
            print(f"\n🎬 LAUNCHING {len(self.active_ids)} DRONE AGENTS")
            print("═"*70)
            
            for d_id in self.active_ids:
                drone = DroneAgent(d_id, tactical_swarm=True)
                drone.set_broadcast_mode(False)  # Start with own camera feed
                drone.daemon = True 
                drone.start()
                self.drones.append(drone)
            
            print(f"✅ {len(self.drones)} drones activated with independent cameras")

        except Exception as e:
            print(f"❌ INITIALIZATION FAILED: {e}")
            return

        # Main Loop - Continuous Independent Camera Feed Capture
        print("\n🟢 INDEPENDENT CAMERA NETWORK ESTABLISHED")
        print("   Each drone displays its own camera feed")
        print("   Ready to switch to tactical swarm mode on command\n")
        print("═"*70 + "\n")
        
        frame_count = 0
        last_print = time.time()
        
        while True:
            try:
                # Get broadcast frame from backend (tactical swarm)
                if self.tactical_swarm_mode:
                    try:
                        resp = requests.get(f"{BACKEND_URL}/api/drones/tactical-swarm/status")
                        if resp.status_code == 200:
                            status = resp.json()
                            if status.get("broadcast_active"):
                                # Get the broadcast frame from first available drone
                                resp = requests.get(f"{BACKEND_URL}/api/drones/slam/{self.active_ids[0]}/live?t={time.time()}")
                                if resp.status_code == 200:
                                    nparr = np.frombuffer(resp.content, np.uint8)
                                    broadcast_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                                    if broadcast_frame is not None:
                                        multi_drone_camera.set_broadcast_frame(broadcast_frame)
                    except Exception:
                        pass
                
                frame_count += 1
                now = time.time()
                
                if now - last_print > 5:
                    mode = "TACTICAL BROADCAST" if self.tactical_swarm_mode else "INDEPENDENT FEEDS"
                    print(f"✅ SWARM STATUS: {len(self.drones)} drones | Mode: {mode} | {frame_count} frames processed")
                    last_print = now
                    
                time.sleep(0.08)  # ~12.5 FPS master loop
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Loop error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    swarm = DroneSwarmManager()
    swarm.sync_swarm()
