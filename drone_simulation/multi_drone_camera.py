"""
Multi-Drone Independent Camera System
Each drone has its own camera source with individual feed processing
"""

import cv2
import numpy as np
import time
from typing import Dict, Optional

class DroneCamera:
    """Individual camera for each drone with fallback to synthetic"""
    
    def __init__(self, drone_id: str, camera_index: int = 0):
        self.drone_id = drone_id
        self.camera_index = camera_index
        self.cap = None
        self.current_frame = None
        self.frame_count = 0
        self.is_active = False
        self.init_camera()
    
    def init_camera(self):
        """Initialize camera for this drone (fallback to synthetic)"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if self.cap and self.cap.isOpened():
                self.is_active = True
                print(f"📷 {self.drone_id}: Real camera initialized (index {self.camera_index})")
                return True
        except Exception as e:
            print(f"⚠️ {self.drone_id}: Real camera failed - {e}")
        
        self.cap = None
        self.is_active = False
        print(f"🎬 {self.drone_id}: Using synthetic fallback")
        return False
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get current frame from camera or synthetic source"""
        try:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.frame_count += 1
                    self.current_frame = frame.copy()
                    return frame
        except Exception as e:
            print(f"⚠️ {self.drone_id}: Camera read error - {e}")
        
        # Synthetic fallback: generate unique per-drone pattern
        return self.generate_synthetic_frame()
    
    def generate_synthetic_frame(self) -> np.ndarray:
        """Generate unique synthetic frame per drone"""
        w, h = 640, 480
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Create noise base
        cv2.randn(frame, (80, 80, 80), (30, 30, 30))
        
        # Get drone number from ID (e.g., "drone_1" -> 1)
        try:
            drone_num = int(self.drone_id.split('_')[1])
        except:
            drone_num = 1
        
        # Unique color per drone (HSV space mapped to RGB)
        hue = (drone_num * 30) % 180
        saturation = 255
        value = 200
        unique_color = cv2.cvtColor(
            np.uint8([[[hue, saturation, value]]]),
            cv2.COLOR_HSV2BGR
        )[0][0]
        unique_color = tuple(int(x) for x in unique_color)
        
        # Draw moving pattern unique to drone
        t = time.time()
        x = int(w/2 + 150*np.sin(t + drone_num))
        y = int(h/2 + 150*np.cos(t + drone_num*2))
        cv2.circle(frame, (x, y), 40, unique_color, -1)
        
        # Draw drone identifier
        cv2.putText(frame, f"CAMERA: {self.drone_id}", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, unique_color, 2)
        cv2.putText(frame, f"Frames: {self.frame_count}", (20, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        
        self.frame_count += 1
        return frame
    
    def release(self):
        """Release camera resources"""
        if self.cap:
            self.cap.release()
            self.cap = None
        self.is_active = False


class MultiDroneCamera:
    """Manages multiple independent camera feeds for all drones"""
    
    def __init__(self, num_drones: int = 12):
        self.num_drones = num_drones
        self.drone_cameras: Dict[str, DroneCamera] = {}
        self.tactical_swarm_mode = False
        self.master_broadcast_frame = None
    
    def initialize_drone_cameras(self, drone_ids: list):
        """Initialize independent camera for each drone"""
        print("\n" + "═"*60)
        print("📷 INITIALIZING INDEPENDENT CAMERA NETWORK")
        print("═"*60)
        
        for idx, drone_id in enumerate(drone_ids):
            # Assign camera index (cycling through available cameras)
            # In real scenario: camera_index would be drone-specific
            camera_index = idx % 2  # Cycle between webcam 0 and 1
            
            drone_cam = DroneCamera(drone_id, camera_index)
            self.drone_cameras[drone_id] = drone_cam
        
        print(f"✅ {len(self.drone_cameras)} drone cameras initialized\n")
    
    def get_drone_frame(self, drone_id: str) -> Optional[np.ndarray]:
        """Get individual frame for specific drone"""
        if drone_id in self.drone_cameras:
            return self.drone_cameras[drone_id].get_frame()
        return None
    
    def get_broadcast_frame(self) -> Optional[np.ndarray]:
        """Get current broadcast frame (tactical swarm)"""
        return self.master_broadcast_frame
    
    def set_broadcast_frame(self, frame: np.ndarray):
        """Set broadcast frame (from tactical swarm)"""
        self.master_broadcast_frame = frame.copy() if frame is not None else None
    
    def get_frame_for_display(self, drone_id: str, use_broadcast: bool = False) -> Optional[np.ndarray]:
        """
        Get appropriate frame for display
        
        Args:
            drone_id: ID of the drone
            use_broadcast: If True, use broadcast frame; if False, use drone's own camera
        
        Returns:
            Frame to display
        """
        if use_broadcast and self.master_broadcast_frame is not None:
            return self.master_broadcast_frame.copy()
        else:
            return self.get_drone_frame(drone_id)
    
    def set_tactical_swarm_mode(self, enabled: bool):
        """Enable/disable tactical swarm mode"""
        self.tactical_swarm_mode = enabled
    
    def release_all(self):
        """Release all camera resources"""
        for drone_cam in self.drone_cameras.values():
            drone_cam.release()
        self.drone_cameras.clear()


# Global instance
multi_drone_camera = MultiDroneCamera()
