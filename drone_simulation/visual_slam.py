"""
Visual SLAM Demo - Demonstrates GPS-denied navigation
Uses laptop camera or video feed for SLAM simulation
"""

import cv2
import numpy as np
import json
from pathlib import Path

class VisualSLAMDemo:
    """
    Visual SLAM demonstration using OpenCV
    Simulates feature detection and mapping for GPS-denied navigation
    """
    
    def __init__(self, config_path="config.json", source=None):
        self._config_path = config_path
        self.config = self._load_config(config_path)
        self.cap = None
        self.slam_enabled = False
        self.map_points = []
        self.keyframes = []
        self.source = source or self.config.get("simulation", {}).get("video_source", 0)

    def _load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {
                "drone": {"max_altitude": 120},
                "simulation": {"update_interval_ms": 2000, "video_source": 0}
            }

    def initialize_camera(self, source=None):
        """Initialize camera or video source with robust fallback"""
        src = source if source is not None else self.source
        print(f"📡 INITIALIZING VIDEO SOURCE: {src}")
        
        self.cap = cv2.VideoCapture(src)
        
        if not self.cap.isOpened():
            # Try video file fallback if webcam fails
            fallback_video = Path("data/simulated/drone_recon.mp4")
            if src == 0 and fallback_video.exists():
                print(f"⚠️ Webcam failed. Using fallback video: {fallback_video}")
                self.cap = cv2.VideoCapture(str(fallback_video))
            else:
                return False
        return self.cap.isOpened()
    
    def enable_slam(self):
        """Enable Visual SLAM"""
        self.slam_enabled = True
        self.map_points = []
        self.keyframes = []
        print("V-SLAM enabled - GPS-denied navigation active")
    
    def disable_slam(self):
        """Disable Visual SLAM"""
        self.slam_enabled = False
        print("V-SLAM disabled - GPS navigation active")
    
    def detect_features(self, frame):
        """
        Detect features in frame using ORB detector
        
        Args:
            frame: Input image frame
        
        Returns:
            Keypoints and descriptors
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # ORB feature detector
        orb = cv2.ORB_create(nfeatures=500)
        keypoints, descriptors = orb.detectAndCompute(gray, None)
        
        return keypoints, descriptors
    
    def process_frame(self, frame):
        """
        Process a frame for SLAM
        
        Args:
            frame: Input image frame
        
        Returns:
            Processed frame with features visualized
        """
        if not self.slam_enabled:
            return frame
        
        # Detect features
        keypoints, descriptors = self.detect_features(frame)
        
        # Add to map if significant features found
        if len(keypoints) > 50:
            self.map_points.append({
                "keypoints": len(keypoints),
                "timestamp": cv2.getTickCount()
            })
            
            # Store keyframe
            if len(self.keyframes) == 0 or len(keypoints) > self.keyframes[-1]["keypoints"]:
                self.keyframes.append({
                    "keypoints": len(keypoints),
                    "frame_id": len(self.keyframes)
                })
        
        # Draw keypoints on frame
        frame_with_features = cv2.drawKeypoints(
            frame, keypoints, None, color=(0, 255, 0), flags=0
        )
        
        # Add SLAM status overlay
        cv2.putText(
            frame_with_features,
            f"V-SLAM: ACTIVE | Map Points: {len(self.map_points)} | Keyframes: {len(self.keyframes)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        return frame_with_features
    
    def run_demo(self):
        """Run the SLAM demo with robust camera/synthetic fallback"""
        print("\n" + "═"*50)
        print("🚁 DRONE MODULE READY: PRALAYA-NET V-SLAM")
        print("═"*50)
        print("Controls: Press 's' to toggle SLAM, 'q' to exit")
        
        # Check for camera
        if not self.initialize_camera():
            print("⚠️  WEBCAM NOT DETECTED! Entering SYNTHETIC IMAGE MODE.")
            self._run_synthetic_demo()
            return
        
        self._run_main_loop()

    def _run_main_loop(self):
        """Main camera loop"""
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            frame = self.process_frame(frame) if self.slam_enabled else self._draw_inactive_overlay(frame)
            cv2.imshow("PRALAYA-NET V-SLAM Demo", frame)
            
            if not self._handle_keys():
                break
        
        self.cap.release()
        cv2.destroyAllWindows()

    def _run_synthetic_demo(self):
        """Generates a moving synthetic pattern if NO camera is available"""
        self.enable_slam()
        width, height = 640, 480
        t = 0
        
        while True:
            # Create a synthetic "disaster zone" pattern
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            # Add some moving "features" (geometric shapes)
            for i in range(15):
                pos = (
                    int(width/2 + 200 * np.sin(t + i)),
                    int(height/2 + 150 * np.cos(t * 0.5 + i))
                )
                cv2.circle(frame, pos, 20, (50, 50, 150 + i*5), -1)
                cv2.rectangle(frame, (pos[0]-10, pos[1]-10), (pos[0]+10, pos[1]+10), (0, 255, 0), 1)

            t += 0.05
            frame = self.process_frame(frame)
            
            cv2.putText(frame, "SYNTHETIC DRONE FEED (DEMO)", (10, height - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow("PRALAYA-NET V-SLAM Demo (SYNTHETIC)", frame)
            if not self._handle_keys():
                break
        cv2.destroyAllWindows()

    def _draw_inactive_overlay(self, frame):
        cv2.putText(frame, "V-SLAM: INACTIVE (Press 's' to enable)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame

    def _handle_keys(self):
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): return False
        if key == ord('s'):
            self.slam_enabled = not self.slam_enabled
            if self.slam_enabled: self.enable_slam()
            else: self.disable_slam()
        return True

if __name__ == "__main__":
    try:
        demo = VisualSLAMDemo()
        demo.run_demo()
    except Exception as e:
        print(f"CRITICAL ERROR in SLAM module: {e}")
