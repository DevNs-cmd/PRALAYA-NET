"""
Real-Time Multi-Drone Camera Stream Multiplexer
Generates 12 independent logical drone feeds from a single webcam source
"""
import cv2
import threading
import time
import numpy as np
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class CameraStreamMultiplexer:
    def __init__(self):
        self.camera = None
        self.is_capturing = False
        self.frame_buffer = {}
        self.drone_feeds = {}
        self.capture_thread = None
        self.fps_counter = {}
        self.last_frame_time = {}
        self.camera_lock = threading.Lock()
        
        # Initialize 12 drone feeds
        self.drone_count = 12
        for i in range(1, self.drone_count + 1):
            drone_id = f"drone_{i}"
            self.drone_feeds[drone_id] = {
                "active": True,
                "frame_count": 0,
                "last_update": time.time(),
                "fps": 0,
                "latency_ms": 0
            }
            self.fps_counter[drone_id] = {"count": 0, "start_time": time.time()}
            self.last_frame_time[drone_id] = time.time()
    
    def initialize_camera(self) -> bool:
        """Initialize the webcam camera"""
        with self.camera_lock:
            if self.camera is not None:
                return True
                
            try:
                # Try different camera indices
                for camera_index in [0, 1, 2]:
                    self.camera = cv2.VideoCapture(camera_index)
                    if self.camera.isOpened():
                        # Set camera properties for better performance
                        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        self.camera.set(cv2.CAP_PROP_FPS, 30)
                        logger.info(f"✅ Camera initialized successfully on index {camera_index}")
                        return True
                    self.camera.release()
                    self.camera = None
                
                # If no physical camera, create synthetic feed
                logger.warning("⚠️ No physical camera found, using synthetic feed")
                self.camera = None
                return True
                
            except Exception as e:
                logger.error(f"❌ Camera initialization failed: {e}")
                self.camera = None
                return False
    
    def generate_synthetic_frame(self, drone_id: str) -> np.ndarray:
        """Generate a synthetic frame for testing"""
        # Create base frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add gradient background
        for i in range(480):
            color_intensity = int(50 + 100 * (i / 480))
            frame[i, :, :] = [color_intensity, color_intensity // 2, 200]
        
        # Add drone-specific patterns
        drone_num = int(drone_id.split('_')[1])
        
        # Moving elements
        t = time.time()
        x_offset = int(320 + 200 * np.sin(t + drone_num))
        y_offset = int(240 + 150 * np.cos(t + drone_num * 0.7))
        
        # Draw drone identifier
        cv2.putText(frame, f"DRONE {drone_num}", (20, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Draw moving circles
        for i in range(3):
            x = (x_offset + i * 100) % 640
            y = (y_offset + i * 80) % 480
            color = ((i * 60) % 255, (i * 120) % 255, (i * 180) % 255)
            cv2.circle(frame, (x, y), 30, color, -1)
        
        return frame
    
    def add_telemetry_overlay(self, frame: np.ndarray, drone_id: str) -> np.ndarray:
        """Add telemetry overlay to frame"""
        frame_copy = frame.copy()
        
        # Get telemetry data
        telemetry = self.drone_feeds[drone_id]
        fps = telemetry["fps"]
        frame_count = telemetry["frame_count"]
        latency = telemetry["latency_ms"]
        
        # Add overlays
        overlay_height = 100
        overlay = np.zeros((overlay_height, frame.shape[1], 3), dtype=np.uint8)
        overlay[:] = (0, 0, 0)
        
        # Telemetry text
        texts = [
            f"DRONE ID: {drone_id.upper()}",
            f"FPS: {fps:.1f}",
            f"FRAMES: {frame_count}",
            f"LATENCY: {latency:.1f}ms"
        ]
        
        for i, text in enumerate(texts):
            y_pos = 20 + i * 20
            color = (0, 255, 0) if i == 0 else (255, 255, 255)
            cv2.putText(overlay, text, (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
        
        # Add connection health indicator
        health_color = (0, 255, 0) if latency < 100 else (0, 255, 255) if latency < 300 else (0, 0, 255)
        cv2.circle(overlay, (frame.shape[1] - 30, 30), 10, health_color, -1)
        cv2.putText(overlay, "LIVE", (frame.shape[1] - 60, 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, health_color, 1)
        
        # Combine frame with overlay
        result = np.vstack([overlay, frame_copy])
        return result
    
    def capture_loop(self):
        """Main capture loop for generating frames"""
        logger.info("📹 Camera capture loop started")
        
        while self.is_capturing:
            try:
                current_time = time.time()
                
                # Capture or generate frame
                if self.camera and self.camera.isOpened():
                    ret, raw_frame = self.camera.read()
                    if not ret:
                        logger.warning("⚠️ Camera frame capture failed, switching to synthetic")
                        self.camera = None
                        raw_frame = self.generate_synthetic_frame("drone_1")
                else:
                    # Generate synthetic frame
                    raw_frame = self.generate_synthetic_frame("drone_1")
                
                # Distribute frame to all drone feeds with unique modifications
                for drone_id in self.drone_feeds:
                    if self.drone_feeds[drone_id]["active"]:
                        # Add drone-specific modifications
                        modified_frame = raw_frame.copy()
                        
                        # Add drone-specific overlay
                        drone_num = int(drone_id.split('_')[1])
                        
                        # Add unique pattern for each drone
                        pattern_offset = drone_num * 20
                        cv2.rectangle(modified_frame, 
                                    (pattern_offset, pattern_offset), 
                                    (pattern_offset + 50, pattern_offset + 50), 
                                    (255, 255, 0), 2)
                        
                        # Add telemetry overlay
                        final_frame = self.add_telemetry_overlay(modified_frame, drone_id)
                        
                        # Convert to JPEG
                        _, buffer = cv2.imencode('.jpg', final_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                        frame_bytes = buffer.tobytes()
                        
                        # Update frame buffer
                        self.frame_buffer[drone_id] = {
                            "data": frame_bytes,
                            "timestamp": current_time,
                            "size": len(frame_bytes)
                        }
                        
                        # Update metrics
                        self.drone_feeds[drone_id]["frame_count"] += 1
                        self.drone_feeds[drone_id]["last_update"] = current_time
                        
                        # Update FPS calculation
                        self.fps_counter[drone_id]["count"] += 1
                        elapsed = current_time - self.fps_counter[drone_id]["start_time"]
                        if elapsed >= 1.0:  # Update FPS every second
                            self.drone_feeds[drone_id]["fps"] = self.fps_counter[drone_id]["count"] / elapsed
                            self.fps_counter[drone_id]["count"] = 0
                            self.fps_counter[drone_id]["start_time"] = current_time
                        
                        # Update latency
                        self.drone_feeds[drone_id]["latency_ms"] = (current_time - self.last_frame_time[drone_id]) * 1000
                        self.last_frame_time[drone_id] = current_time
                
                time.sleep(1/30)  # ~30 FPS
                
            except Exception as e:
                logger.error(f"❌ Capture loop error: {e}")
                time.sleep(0.1)
    
    def start_capture(self):
        """Start the camera capture process"""
        if self.is_capturing:
            return True
            
        if not self.initialize_camera():
            return False
            
        self.is_capturing = True
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()
        logger.info("✅ Camera stream multiplexer started")
        return True
    
    def stop_capture(self):
        """Stop the camera capture process"""
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        
        with self.camera_lock:
            if self.camera:
                self.camera.release()
                self.camera = None
        
        logger.info("⏹️ Camera stream multiplexer stopped")
    
    def get_drone_feed(self, drone_id: str) -> Optional[bytes]:
        """Get the latest frame for a specific drone"""
        if drone_id in self.frame_buffer:
            return self.frame_buffer[drone_id]["data"]
        return None
    
    def get_system_status(self) -> dict:
        """Get system status and metrics"""
        active_drones = [drone_id for drone_id, feed in self.drone_feeds.items() if feed["active"]]
        
        return {
            "system_status": "running" if self.is_capturing else "stopped",
            "active_drones": len(active_drones),
            "total_drones": self.drone_count,
            "camera_status": "physical" if self.camera else "synthetic",
            "drone_feeds": {
                drone_id: {
                    "active": feed["active"],
                    "fps": round(feed["fps"], 2),
                    "frame_count": feed["frame_count"],
                    "latency_ms": round(feed["latency_ms"], 2),
                    "last_update": feed["last_update"]
                }
                for drone_id, feed in self.drone_feeds.items()
            }
        }

# Global instance
multiplexer = CameraStreamMultiplexer()

# API Routes
@router.on_event("startup")
async def startup_event():
    """Initialize camera multiplexer on startup"""
    multiplexer.start_capture()

@router.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    multiplexer.stop_capture()

@router.get("/status")
async def get_camera_status():
    """Get camera multiplexer status"""
    return multiplexer.get_system_status()

@router.get("/drone/{drone_id}/stream")
async def stream_drone_feed(drone_id: str):
    """Stream live video feed for a specific drone"""
    if not drone_id in [f"drone_{i}" for i in range(1, 13)]:
        raise HTTPException(status_code=404, detail="Drone ID must be drone_1 through drone_12")
    
    async def frame_generator():
        while True:
            frame_data = multiplexer.get_drone_feed(drone_id)
            if frame_data:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
            await asyncio.sleep(1/30)  # ~30 FPS
    
    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.get("/drone/{drone_id}/snapshot")
async def get_drone_snapshot(drone_id: str):
    """Get single frame snapshot for a drone"""
    if not drone_id in [f"drone_{i}" for i in range(1, 13)]:
        raise HTTPException(status_code=404, detail="Drone ID must be drone_1 through drone_12")
    
    frame_data = multiplexer.get_drone_feed(drone_id)
    if not frame_data:
        raise HTTPException(status_code=404, detail="Frame not available")
    
    return Response(content=frame_data, media_type="image/jpeg")

@router.post("/drone/{drone_id}/control")
async def control_drone_feed(drone_id: str, action: str):
    """Control drone feed (start/stop)"""
    if not drone_id in [f"drone_{i}" for i in range(1, 13)]:
        raise HTTPException(status_code=404, detail="Drone ID must be drone_1 through drone_12")
    
    if action == "start":
        multiplexer.drone_feeds[drone_id]["active"] = True
        return {"status": "started", "drone_id": drone_id}
    elif action == "stop":
        multiplexer.drone_feeds[drone_id]["active"] = False
        return {"status": "stopped", "drone_id": drone_id}
    else:
        raise HTTPException(status_code=400, detail="Action must be 'start' or 'stop'")

@router.get("/metrics")
async def get_streaming_metrics():
    """Get real-time streaming metrics"""
    status = multiplexer.get_system_status()
    metrics = {
        "timestamp": time.time(),
        "system_uptime": status["system_status"],
        "total_bandwidth_mbps": sum(
            feed["fps"] * (feed.get("frame_size", 50000) / 1024 / 1024) 
            for feed in status["drone_feeds"].values()
        ),
        "average_latency_ms": round(
            sum(feed["latency_ms"] for feed in status["drone_feeds"].values()) / 
            len(status["drone_feeds"]), 2
        ),
        "active_streams": status["active_drones"]
    }
    return metrics