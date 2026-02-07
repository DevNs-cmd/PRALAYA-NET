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
from config import (
    BACKEND_URL, 
    FRAME_ENCODING_FORMAT, 
    FRAME_JPEG_QUALITY,
    FRAME_UPLOAD_FPS,
    FRAME_UPLOAD_TIMEOUT,
    TELEMETRY_UPLOAD_TIMEOUT,
    LOG_FRAME_ERRORS,
    LOG_FRAME_SUCCESS,
    LOG_TELEMETRY_ERRORS
)

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
        """
        Sync frame and telemetry to backend using corrected multipart/form-data format
        
        FIXED: Uses multipart/form-data instead of raw binary
        FIXED: Proper error logging instead of silent failures
        """
        now = time.time()
        if now - self.last_sync_time < (1.0 / FRAME_UPLOAD_FPS):
            return

        try:
            # === FRAME UPLOAD (FIXED FORMAT) ===
            # Encode frame as JPEG bytes
            success, img_encoded = cv2.imencode(FRAME_ENCODING_FORMAT, frame, 
                                               [cv2.IMWRITE_JPEG_QUALITY, FRAME_JPEG_QUALITY])
            
            if not success:
                if LOG_FRAME_ERRORS:
                    print(f"❌ {self.drone_id}: Frame encoding failed")
                return
            
            frame_bytes = img_encoded.tobytes()
            
            # FIXED: Use multipart/form-data instead of application/octet-stream
            # This matches what backend API expects: form.get("file")
            files = {
                "file": (f"frame_{self.drone_id}.jpg", frame_bytes, "image/jpeg")
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/drones/slam/{self.drone_id}/frame",
                files=files,
                timeout=FRAME_UPLOAD_TIMEOUT
            )
            
            if response.status_code == 200:
                if LOG_FRAME_SUCCESS:
                    print(f"✅ {self.drone_id}: Frame uploaded ({len(frame_bytes)} bytes)")
            else:
                if LOG_FRAME_ERRORS:
                    print(f"❌ {self.drone_id}: Frame upload failed with {response.status_code}")
                    try:
                        error_detail = response.json().get("detail", "Unknown error")
                        print(f"   Error: {error_detail}")
                    except:
                        print(f"   Response: {response.text[:100]}")
            
            # === TELEMETRY UPLOAD ===
            payload = {
                "keypoints": len(self.map_points) * 10,
                "keyframes": len(self.keyframes),
                "status": "localized",
                "gps_status": "active" if self.gps_active else "lost",
                "tactical_swarm": self.use_broadcast,
                "camera_mode": mode,
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.session.post(
                f"{BACKEND_URL}/api/drones/slam/{self.drone_id}/telemetry",
                json=payload,
                timeout=TELEMETRY_UPLOAD_TIMEOUT
            )
            
            if response.status_code != 200:
                if LOG_TELEMETRY_ERRORS:
                    print(f"⚠️  {self.drone_id}: Telemetry upload failed with {response.status_code}")
            
            self.last_sync_time = now
            
        except requests.exceptions.Timeout:
            if LOG_FRAME_ERRORS:
                print(f"⏱️  {self.drone_id}: Frame upload timeout")
        except requests.exceptions.ConnectionError as e:
            if LOG_FRAME_ERRORS:
                print(f"🔌 {self.drone_id}: Connection error - {str(e)[:50]}")
        except Exception as e:
            if LOG_FRAME_ERRORS:
                print(f"❌ {self.drone_id}: Unexpected error in sync_backend: {str(e)[:100]}")

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
        """Broadcast frame to all drones via backend with FIXED format"""
        session = create_session()
        try:
            # Encode with proper JPEG quality
            success, img_encoded = cv2.imencode(
                FRAME_ENCODING_FORMAT, 
                frame, 
                [cv2.IMWRITE_JPEG_QUALITY, FRAME_JPEG_QUALITY]
            )
            
            if not success:
                print("❌ Failed to encode broadcast frame")
                return
            
            frame_data = img_encoded.tobytes()
            
            # FIXED: Use multipart/form-data
            files = {
                "file": (f"broadcast_frame.jpg", frame_data, "image/jpeg")
            }
            
            # Send to all active drones
            success_count = 0
            for drone in self.drones:
                try:
                    response = session.post(
                        f"{BACKEND_URL}/api/drones/slam/{drone.drone_id}/frame",
                        files=files,
                        timeout=0.5
                    )
                    if response.status_code == 200:
                        success_count += 1
                except Exception:
                    pass
            
            if success_count > 0:
                print(f"📡 Broadcast frame sent to {success_count}/{len(self.drones)} drones")
        except Exception as e:
            print(f"❌ Broadcast failed: {str(e)[:50]}")

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
