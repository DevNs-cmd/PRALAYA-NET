"""
GPS Failure Autonomous Navigation System
Implements Visual SLAM fallback with optical flow and terrain matching
"""
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import threading
import logging
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NavigationMode(Enum):
    GPS_ACTIVE = "gps_active"
    VISUAL_SLAM = "visual_slam"
    OPTICAL_FLOW = "optical_flow"
    TERRAIN_MATCHING = "terrain_matching"
    EMERGENCY_RETURN = "emergency_return"

class NavigationState(Enum):
    NORMAL = "normal"
    GPS_LOSS_DETECTED = "gps_loss_detected"
    SLAM_ACTIVATING = "slam_activating"
    EMERGENCY_MODE = "emergency_mode"
    RETURN_TO_BASE = "return_to_base"

@dataclass
class Position:
    x: float
    y: float
    z: float
    accuracy: float  # meters

@dataclass
class Velocity:
    vx: float  # m/s
    vy: float  # m/s
    vz: float  # m/s

@dataclass
class Orientation:
    roll: float   # radians
    pitch: float  # radians
    yaw: float    # radians

class VisualSLAMProcessor:
    """Visual SLAM implementation using ORB features"""
    
    def __init__(self):
        self.orb = cv2.ORB_create(nfeatures=1000)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.keyframes = []
        self.map_points = []
        self.pose_graph = []
        
    def process_frame(self, frame: np.ndarray, prev_frame: Optional[np.ndarray] = None) -> Tuple[Position, List]:
        """Process frame and estimate motion using Visual SLAM"""
        if prev_frame is None:
            # First frame - extract features
            kp, des = self.orb.detectAndCompute(frame, None)
            return Position(0, 0, 0, 5.0), kp if kp else []
        
        # Extract features from current frame
        kp1, des1 = self.orb.detectAndCompute(prev_frame, None)
        kp2, des2 = self.orb.detectAndCompute(frame, None)
        
        if des1 is None or des2 is None or len(des1) < 10 or len(des2) < 10:
            return Position(0, 0, 0, 10.0), []
        
        # Match features
        matches = self.matcher.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Filter good matches
        good_matches = [m for m in matches if m.distance < 50]
        
        if len(good_matches) < 10:
            return Position(0, 0, 0, 10.0), kp2
        
        # Estimate motion using essential matrix
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
        try:
            E, mask = cv2.findEssentialMat(src_pts, dst_pts, focal=500, pp=(320, 240))
            if E is not None:
                _, R, t, mask = cv2.recoverPose(E, src_pts, dst_pts, focal=500, pp=(320, 240))
                
                # Convert to position change (simplified)
                translation = t.flatten()
                scale_factor = 0.1  # Scale factor for realistic movement
                
                position_change = Position(
                    translation[0] * scale_factor,
                    translation[1] * scale_factor,
                    translation[2] * scale_factor,
                    2.0  # Good accuracy when enough matches
                )
                
                return position_change, kp2
        except Exception as e:
            logger.warning(f"SLAM processing error: {e}")
        
        return Position(0, 0, 0, 10.0), kp2

class OpticalFlowTracker:
    """Optical flow based motion estimation"""
    
    def __init__(self):
        self.lk_params = dict(
            winSize=(15, 15),
            maxLevel=2,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03)
        )
        self.feature_params = dict(
            maxCorners=100,
            qualityLevel=0.3,
            minDistance=7,
            blockSize=7
        )
        self.prev_gray = None
        self.prev_points = None
    
    def track_motion(self, frame: np.ndarray) -> Tuple[Velocity, float]:
        """Track motion using optical flow"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if self.prev_gray is None:
            # Initialize with good features
            self.prev_gray = gray.copy()
            self.prev_points = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            return Velocity(0, 0, 0), 0.0
        
        if self.prev_points is None or len(self.prev_points) < 10:
            # Reinitialize features
            self.prev_points = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            self.prev_gray = gray.copy()
            return Velocity(0, 0, 0), 0.0
        
        # Calculate optical flow
        next_points, status, error = cv2.calcOpticalFlowPyrLK(
            self.prev_gray, gray, self.prev_points, None, **self.lk_params
        )
        
        # Filter good points
        good_new = next_points[status == 1]
        good_old = self.prev_points[status == 1]
        
        if len(good_new) < 5:
            self.prev_points = cv2.goodFeaturesToTrack(gray, mask=None, **self.feature_params)
            self.prev_gray = gray.copy()
            return Velocity(0, 0, 0), 0.0
        
        # Calculate average motion
        motion_vectors = good_new - good_old
        avg_motion = np.mean(motion_vectors, axis=0)
        
        # Convert to velocity (pixels/frame to m/s - simplified)
        velocity = Velocity(
            avg_motion[0] * 0.05,  # Scale factor
            avg_motion[1] * 0.05,
            0.0  # Assume no vertical movement for now
        )
        
        # Calculate confidence based on number of tracked points
        confidence = min(1.0, len(good_new) / 50.0)
        
        # Update for next iteration
        self.prev_points = good_new.reshape(-1, 1, 2)
        self.prev_gray = gray.copy()
        
        return velocity, confidence

class TerrainMatcher:
    """Terrain matching for position estimation"""
    
    def __init__(self):
        self.terrain_database = {}  # In real system, this would be loaded from maps
        self.template_matcher = cv2.TM_CCOEFF_NORMED
    
    def match_terrain(self, frame: np.ndarray, search_radius: float = 100.0) -> Tuple[Position, float]:
        """Match current frame against terrain database"""
        # In a real implementation, this would:
        # 1. Extract terrain features from frame
        # 2. Compare against known terrain database
        # 3. Return position estimate with confidence
        
        # Simplified implementation - return random position with low confidence
        position = Position(
            np.random.uniform(-search_radius, search_radius),
            np.random.uniform(-search_radius, search_radius),
            0.0,
            search_radius  # High uncertainty
        )
        
        confidence = 0.3  # Low confidence for synthetic implementation
        
        return position, confidence

class GPSFailureNavigation:
    """Main GPS failure navigation system"""
    
    def __init__(self, drone_id: str):
        self.drone_id = drone_id
        self.navigation_mode = NavigationMode.GPS_ACTIVE
        self.navigation_state = NavigationState.NORMAL
        self.position = Position(0, 0, 0, 0)
        self.velocity = Velocity(0, 0, 0)
        self.orientation = Orientation(0, 0, 0)
        self.base_position = Position(0, 0, 0, 0)
        
        # Navigation components
        self.slam_processor = VisualSLAMProcessor()
        self.optical_flow = OpticalFlowTracker()
        self.terrain_matcher = TerrainMatcher()
        
        # State tracking
        self.gps_signal_strength = 1.0
        self.last_gps_update = time.time()
        self.gps_loss_threshold = 0.3
        self.emergency_return_path = []
        self.navigation_history = deque(maxlen=1000)
        
        # Performance metrics
        self.position_accuracy_history = deque(maxlen=100)
        self.mode_switch_count = 0
        self.emergency_activations = 0
        
        logger.info(f"🧭 GPS Failure Navigation initialized for {drone_id}")
    
    def update_gps_status(self, signal_strength: float, position: Optional[Position] = None):
        """Update GPS status and handle failures"""
        self.gps_signal_strength = signal_strength
        current_time = time.time()
        
        # Check for GPS loss
        if signal_strength < self.gps_loss_threshold:
            if self.navigation_state == NavigationState.NORMAL:
                self._handle_gps_loss_detection()
        else:
            # GPS signal restored
            if self.navigation_state != NavigationState.NORMAL:
                self._handle_gps_restoration()
            
            # Update position if available
            if position:
                self.position = position
                self.last_gps_update = current_time
    
    def _handle_gps_loss_detection(self):
        """Handle GPS loss detection"""
        logger.warning(f"⚠️ GPS loss detected for {self.drone_id}")
        self.navigation_state = NavigationState.GPS_LOSS_DETECTED
        self.last_gps_update = time.time()
        
        # Start emergency protocols
        self._activate_emergency_navigation()
    
    def _handle_gps_restoration(self):
        """Handle GPS signal restoration"""
        logger.info(f"✅ GPS signal restored for {self.drone_id}")
        self.navigation_state = NavigationState.NORMAL
        self.navigation_mode = NavigationMode.GPS_ACTIVE
        self.mode_switch_count += 1
    
    def _activate_emergency_navigation(self):
        """Activate emergency navigation protocols"""
        self.emergency_activations += 1
        self.navigation_state = NavigationState.EMERGENCY_MODE
        
        # Generate return path to base
        self._generate_return_path()
        
        # Switch to Visual SLAM mode
        self.navigation_mode = NavigationMode.VISUAL_SLAM
        logger.info(f"🧭 Activating Visual SLAM for {self.drone_id}")
    
    def _generate_return_path(self):
        """Generate path back to base position"""
        # Simple straight-line path (in real system would use path planning)
        current_pos = self.position
        base_pos = self.base_position
        
        distance = np.sqrt((base_pos.x - current_pos.x)**2 + (base_pos.y - current_pos.y)**2)
        steps = max(10, int(distance / 10))  # 10m steps
        
        self.emergency_return_path = []
        for i in range(1, steps + 1):
            ratio = i / steps
            intermediate_pos = Position(
                current_pos.x + ratio * (base_pos.x - current_pos.x),
                current_pos.y + ratio * (base_pos.y - current_pos.y),
                current_pos.z + ratio * (base_pos.z - current_pos.z),
                current_pos.accuracy
            )
            self.emergency_return_path.append(intermediate_pos)
        
        logger.info(f"🗺️ Generated return path with {len(self.emergency_return_path)} waypoints")
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """Process frame for navigation updates"""
        if frame is None:
            return self.get_navigation_status()
        
        current_time = time.time()
        
        # Handle GPS loss timeout
        if (self.navigation_state in [NavigationState.GPS_LOSS_DETECTED, NavigationState.EMERGENCY_MODE] and
            current_time - self.last_gps_update > 5.0):  # 5 seconds timeout
            self.navigation_state = NavigationState.RETURN_TO_BASE
            self.navigation_mode = NavigationMode.EMERGENCY_RETURN
        
        # Process based on current mode
        if self.navigation_mode == NavigationMode.VISUAL_SLAM:
            self._process_visual_slam(frame)
        elif self.navigation_mode == NavigationMode.OPTICAL_FLOW:
            self._process_optical_flow(frame)
        elif self.navigation_mode == NavigationMode.TERRAIN_MATCHING:
            self._process_terrain_matching(frame)
        elif self.navigation_mode == NavigationMode.EMERGENCY_RETURN:
            self._process_emergency_return()
        
        # Update navigation history
        self.navigation_history.append({
            'timestamp': current_time,
            'position': self.position,
            'velocity': self.velocity,
            'mode': self.navigation_mode.value,
            'state': self.navigation_state.value
        })
        
        return self.get_navigation_status()
    
    def _process_visual_slam(self, frame: np.ndarray):
        """Process frame using Visual SLAM"""
        # Get previous frame from navigation history
        prev_frame = None
        if len(self.navigation_history) > 0:
            # In real implementation, would retrieve actual previous frame
            pass
        
        position_change, keypoints = self.slam_processor.process_frame(frame, prev_frame)
        
        # Update position
        self.position = Position(
            self.position.x + position_change.x,
            self.position.y + position_change.y,
            self.position.z + position_change.z,
            position_change.accuracy
        )
        
        # Update accuracy history
        self.position_accuracy_history.append(position_change.accuracy)
    
    def _process_optical_flow(self, frame: np.ndarray):
        """Process frame using optical flow"""
        velocity, confidence = self.optical_flow.track_motion(frame)
        
        # Update velocity
        self.velocity = velocity
        
        # Update position based on velocity (integrated over time)
        dt = 0.1  # Assuming 10 FPS processing
        self.position = Position(
            self.position.x + velocity.vx * dt,
            self.position.y + velocity.vy * dt,
            self.position.z + velocity.vz * dt,
            self.position.accuracy + (1.0 - confidence) * 2.0  # Decrease accuracy with low confidence
        )
    
    def _process_terrain_matching(self, frame: np.ndarray):
        """Process frame using terrain matching"""
        position_estimate, confidence = self.terrain_matcher.match_terrain(frame)
        
        # Blend with current position estimate
        blend_factor = confidence
        self.position = Position(
            self.position.x * (1 - blend_factor) + position_estimate.x * blend_factor,
            self.position.y * (1 - blend_factor) + position_estimate.y * blend_factor,
            self.position.z * (1 - blend_factor) + position_estimate.z * blend_factor,
            position_estimate.accuracy
        )
    
    def _process_emergency_return(self):
        """Process emergency return to base"""
        if self.emergency_return_path:
            next_waypoint = self.emergency_return_path.pop(0)
            self.position = next_waypoint
            
            # Check if reached base
            distance_to_base = np.sqrt(
                (self.position.x - self.base_position.x)**2 +
                (self.position.y - self.base_position.y)**2
            )
            
            if distance_to_base < 5.0:  # Within 5 meters of base
                self.navigation_state = NavigationState.NORMAL
                self.navigation_mode = NavigationMode.GPS_ACTIVE
                logger.info(f"🏠 {self.drone_id} returned to base successfully")
    
    def get_navigation_status(self) -> Dict:
        """Get current navigation status"""
        avg_accuracy = np.mean(self.position_accuracy_history) if self.position_accuracy_history else self.position.accuracy
        
        return {
            'drone_id': self.drone_id,
            'navigation_mode': self.navigation_mode.value,
            'navigation_state': self.navigation_state.value,
            'position': {
                'x': round(self.position.x, 2),
                'y': round(self.position.y, 2),
                'z': round(self.position.z, 2),
                'accuracy_meters': round(self.position.accuracy, 2)
            },
            'velocity': {
                'vx': round(self.velocity.vx, 3),
                'vy': round(self.velocity.vy, 3),
                'vz': round(self.velocity.vz, 3)
            },
            'orientation': {
                'roll': round(self.orientation.roll, 3),
                'pitch': round(self.orientation.pitch, 3),
                'yaw': round(self.orientation.yaw, 3)
            },
            'gps_status': {
                'signal_strength': round(self.gps_signal_strength, 3),
                'last_update_seconds': round(time.time() - self.last_gps_update, 1)
            },
            'emergency_status': {
                'active': self.navigation_state in [NavigationState.EMERGENCY_MODE, NavigationState.RETURN_TO_BASE],
                'return_path_remaining': len(self.emergency_return_path),
                'activations': self.emergency_activations
            },
            'performance_metrics': {
                'mode_switches': self.mode_switch_count,
                'average_position_accuracy': round(avg_accuracy, 2),
                'navigation_history_length': len(self.navigation_history)
            }
        }
    
    def set_base_position(self, position: Position):
        """Set the base position for return navigation"""
        self.base_position = position
        logger.info(f"📍 Base position set for {self.drone_id}: ({position.x}, {position.y}, {position.z})")

# Global navigation system manager
class NavigationSystemManager:
    def __init__(self):
        self.drones = {}
        self.system_status = "normal"
    
    def register_drone(self, drone_id: str) -> GPSFailureNavigation:
        """Register a new drone with navigation system"""
        if drone_id not in self.drones:
            self.drones[drone_id] = GPSFailureNavigation(drone_id)
            logger.info(f"✅ Registered drone {drone_id} with navigation system")
        return self.drones[drone_id]
    
    def get_drone_navigation(self, drone_id: str) -> Optional[GPSFailureNavigation]:
        """Get navigation system for a drone"""
        return self.drones.get(drone_id)
    
    def update_all_gps_status(self, signal_data: Dict[str, float]):
        """Update GPS status for all drones"""
        for drone_id, signal_strength in signal_data.items():
            if drone_id in self.drones:
                self.drones[drone_id].update_gps_status(signal_strength)
    
    def process_all_frames(self, frame_data: Dict[str, np.ndarray]) -> Dict[str, Dict]:
        """Process frames for all drones"""
        results = {}
        for drone_id, frame in frame_data.items():
            if drone_id in self.drones:
                results[drone_id] = self.drones[drone_id].process_frame(frame)
        return results
    
    def get_system_overview(self) -> Dict:
        """Get system-wide navigation overview"""
        emergency_drones = [
            drone_id for drone_id, nav in self.drones.items()
            if nav.navigation_state in [NavigationState.EMERGENCY_MODE, NavigationState.RETURN_TO_BASE]
        ]
        
        return {
            'total_drones': len(self.drones),
            'emergency_drones': len(emergency_drones),
            'normal_drones': len(self.drones) - len(emergency_drones),
            'emergency_drone_list': emergency_drones,
            'system_status': 'emergency' if emergency_drones else 'normal',
            'drone_statuses': {
                drone_id: {
                    'mode': nav.navigation_mode.value,
                    'state': nav.navigation_state.value,
                    'accuracy': round(nav.position.accuracy, 2)
                }
                for drone_id, nav in self.drones.items()
            }
        }

# Global instance
navigation_manager = NavigationSystemManager()