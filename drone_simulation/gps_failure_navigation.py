"""
Autonomous GPS Failure Navigation System
Vision-based SLAM fallback with return-to-base capability
"""
import cv2
import numpy as np
import time
import json
from typing import Dict, Optional, Tuple
from collections import deque
import threading

class VisualSLAMNavigator:
    """Core Visual SLAM Navigation System"""
    
    def __init__(self, drone_id: str):
        self.drone_id = drone_id
        
        # SLAM Components
        self.orb = cv2.ORB_create(nfeatures=500)
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        # Position tracking
        self.position = np.array([0.0, 0.0, 0.0])  # x, y, z in meters
        self.orientation = np.array([0.0, 0.0, 0.0])  # roll, pitch, yaw
        self.keyframe_history = deque(maxlen=50)
        self.landmark_map = {}  # visual landmarks for position estimation
        
        # Navigation state
        self.is_lost = False
        self.lost_timestamp = None
        self.last_known_gps = None
        self.return_waypoints = []
        self.navigation_mode = "normal"  # normal, recovery, return_home
        
        # Performance metrics
        self.feature_matches = 0
        self.position_accuracy = 1.0  # meters
        self.tracking_quality = 1.0  # 0.0 to 1.0
        
        # Emergency protocols
        self.base_position = np.array([0.0, 0.0, 0.0])  # launch position
        self.battery_critical = 0.15  # 15% battery threshold
        self.max_search_distance = 5000  # meters
        
        # Optical flow tracking
        self.previous_gray = None
        self.feature_points = None
        self.motion_vectors = []
        
        print(f"🧭 Visual SLAM Navigator initialized for {drone_id}")
    
    def update_gps_status(self, gps_available: bool, gps_coords: Optional[Tuple[float, float]] = None):
        """Update GPS status and handle failures"""
        if not gps_available and not self.is_lost:
            print(f"⚠️  GPS LOST for {self.drone_id} - Activating Visual SLAM")
            self.activate_gps_failure_protocol(gps_coords)
        elif gps_available and self.is_lost:
            print(f"✅ GPS RESTORED for {self.drone_id} - Resuming normal navigation")
            self.resume_normal_navigation()
    
    def activate_gps_failure_protocol(self, last_gps_coords: Optional[Tuple[float, float]] = None):
        """Activate emergency navigation protocol"""
        self.is_lost = True
        self.lost_timestamp = time.time()
        self.navigation_mode = "recovery"
        
        if last_gps_coords:
            self.last_known_gps = np.array([last_gps_coords[0], last_gps_coords[1], 0.0])
            self.position = self.last_known_gps.copy()
        
        # Generate return path
        self.generate_return_path()
        
        # Notify command center
        self.notify_command_center()
        
        print(f"🚨 EMERGENCY: {self.drone_id} entering autonomous recovery mode")
        print(f"   Last known position: {self.last_known_gps}")
        print(f"   Return waypoints: {len(self.return_waypoints)}")
    
    def resume_normal_navigation(self):
        """Resume normal GPS-based navigation"""
        self.is_lost = False
        self.lost_timestamp = None
        self.navigation_mode = "normal"
        self.return_waypoints = []
        
        print(f"✅ {self.drone_id} resumed normal GPS navigation")
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """Process frame for SLAM and navigation"""
        if frame is None:
            return self.get_navigation_status()
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Feature detection and matching
        keypoints, descriptors = self.orb.detectAndCompute(gray, None)
        
        if descriptors is not None and len(keypoints) > 10:
            # Match with previous frame/keyframes
            matches = self.match_features(descriptors)
            self.feature_matches = len(matches)
            
            # Update position based on feature tracking
            if len(matches) > 20:
                self.update_position_from_matches(matches, keypoints)
                self.tracking_quality = min(1.0, len(matches) / 100.0)
            else:
                self.tracking_quality *= 0.95  # Gradual quality degradation
            
            # Optical flow tracking
            self.track_optical_flow(gray, keypoints)
            
            # Update landmark map
            self.update_landmark_map(keypoints, descriptors)
        
        # Update previous frame
        self.previous_gray = gray.copy()
        
        # Return navigation status
        return self.get_navigation_status()
    
    def match_features(self, descriptors):
        """Match current features with reference features"""
        matches = []
        try:
            if len(self.keyframe_history) > 0:
                # Match with latest keyframe
                ref_descriptors = self.keyframe_history[-1]['descriptors']
                if ref_descriptors is not None:
                    matches = self.matcher.match(descriptors, ref_descriptors)
                    matches = sorted(matches, key=lambda x: x.distance)[:50]
        except Exception as e:
            print(f"Feature matching error: {e}")
        return matches
    
    def update_position_from_matches(self, matches, keypoints):
        """Update position estimate from feature matches"""
        try:
            if len(matches) < 4:
                return
            
            # Extract matched points
            src_pts = np.float32([keypoints[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([self.keyframe_history[-1]['keypoints'][m.trainIdx].pt 
                                for m in matches]).reshape(-1, 1, 2)
            
            # Calculate essential matrix
            E, mask = cv2.findEssentialMat(src_pts, dst_pts, focal=500, pp=(320, 240))
            
            if E is not None:
                # Recover pose
                _, R, t, mask = cv2.recoverPose(E, src_pts, dst_pts, focal=500, pp=(320, 240))
                
                # Update position (simple integration - in real system would be more sophisticated)
                movement = t.flatten() * 0.1  # Scale factor
                self.position += movement
                self.position_accuracy = max(0.5, self.position_accuracy + 0.01)
                
                # Add to keyframe history if significant movement
                if np.linalg.norm(movement) > 0.5:
                    self.add_keyframe(keypoints, None)  # descriptors handled separately
                    
        except Exception as e:
            print(f"Position update error: {e}")
    
    def track_optical_flow(self, gray, keypoints):
        """Track motion using optical flow"""
        if self.previous_gray is not None and self.feature_points is not None:
            try:
                # Calculate optical flow
                new_points, status, err = cv2.calcOpticalFlowPyrLK(
                    self.previous_gray, gray, self.feature_points, None
                )
                
                # Filter good points
                good_new = new_points[status == 1]
                good_old = self.feature_points[status == 1]
                
                if len(good_new) > 10:
                    # Calculate motion vectors
                    motion = np.mean(good_new - good_old, axis=0)
                    self.motion_vectors.append(motion)
                    
                    # Update position estimate
                    self.position[0] += motion[0] * 0.01  # x movement
                    self.position[1] += motion[1] * 0.01  # y movement
                    
                    # Keep only recent motion vectors
                    if len(self.motion_vectors) > 10:
                        self.motion_vectors.pop(0)
                
                # Update feature points for next iteration
                self.feature_points = good_new.reshape(-1, 1, 2)
                
            except Exception as e:
                print(f"Optical flow error: {e}")
        
        # Initialize feature points if needed
        if self.feature_points is None and len(keypoints) > 0:
            points = np.float32([kp.pt for kp in keypoints[:50]]).reshape(-1, 1, 2)
            self.feature_points = points
    
    def update_landmark_map(self, keypoints, descriptors):
        """Update visual landmark map for consistent positioning"""
        try:
            for i, kp in enumerate(keypoints[:20]):  # Process first 20 keypoints
                landmark_id = f"landmark_{int(kp.pt[0])}_{int(kp.pt[1])}"
                if landmark_id not in self.landmark_map:
                    self.landmark_map[landmark_id] = {
                        'position': self.position.copy(),
                        'descriptor': descriptors[i] if descriptors is not None else None,
                        'first_seen': time.time(),
                        'observations': 1
                    }
                else:
                    self.landmark_map[landmark_id]['observations'] += 1
                    # Update position estimate based on landmark consistency
                    pos_diff = np.linalg.norm(self.position - self.landmark_map[landmark_id]['position'])
                    if pos_diff > 5.0:  # If position drifts too much
                        self.landmark_map[landmark_id]['position'] = self.position.copy()
        except Exception as e:
            print(f"Landmark update error: {e}")
    
    def add_keyframe(self, keypoints, descriptors):
        """Add keyframe to history for loop closure"""
        keyframe = {
            'timestamp': time.time(),
            'position': self.position.copy(),
            'keypoints': keypoints,
            'descriptors': descriptors,
            'landmarks': len(self.landmark_map)
        }
        self.keyframe_history.append(keyframe)
    
    def generate_return_path(self):
        """Generate path back to base position"""
        if self.last_known_gps is not None:
            # Simple straight-line return (in real system would use path planning)
            current_pos = self.position
            base_pos = self.base_position
            
            # Generate intermediate waypoints
            distance = np.linalg.norm(base_pos - current_pos)
            num_waypoints = min(10, max(3, int(distance / 100)))  # Waypoint every 100m
            
            self.return_waypoints = []
            for i in range(1, num_waypoints + 1):
                ratio = i / (num_waypoints + 1)
                waypoint = current_pos + ratio * (base_pos - current_pos)
                self.return_waypoints.append({
                    'position': waypoint,
                    'sequence': i,
                    'distance_to_base': np.linalg.norm(waypoint - base_pos)
                })
            
            print(f"🗺️  Generated {len(self.return_waypoints)} return waypoints")
    
    def get_next_waypoint(self):
        """Get next navigation waypoint"""
        if self.navigation_mode == "return_home" and self.return_waypoints:
            return self.return_waypoints[0]
        elif self.navigation_mode == "recovery":
            # Stay in current area, search for GPS signal
            return {
                'position': self.position.copy(),
                'search_pattern': 'spiral',
                'radius': 50  # meters
            }
        else:
            return None
    
    def notify_command_center(self):
        """Send emergency notification to command center"""
        emergency_data = {
            'drone_id': self.drone_id,
            'timestamp': time.time(),
            'status': 'GPS_LOST',
            'position': self.position.tolist(),
            'last_known_gps': self.last_known_gps.tolist() if self.last_known_gps is not None else None,
            'navigation_mode': self.navigation_mode,
            'return_waypoints': len(self.return_waypoints),
            'battery_level': self.get_battery_level(),
            'tracking_quality': self.tracking_quality
        }
        
        # In real implementation, this would send to backend
        print(f"🚨 EMERGENCY NOTIFICATION: {json.dumps(emergency_data, indent=2)}")
    
    def get_battery_level(self):
        """Simulate battery level (in real system would read from drone)"""
        # Simple battery simulation - decreases over time
        elapsed = time.time() - (self.lost_timestamp or time.time())
        battery = max(0.1, 1.0 - (elapsed / 3600))  # 1 hour mission
        return battery
    
    def get_navigation_status(self):
        """Get current navigation status"""
        return {
            'drone_id': self.drone_id,
            'position': self.position.tolist(),
            'orientation': self.orientation.tolist(),
            'is_lost': self.is_lost,
            'navigation_mode': self.navigation_mode,
            'tracking_quality': self.tracking_quality,
            'position_accuracy': self.position_accuracy,
            'feature_matches': self.feature_matches,
            'landmarks_tracked': len(self.landmark_map),
            'return_waypoints_remaining': len(self.return_waypoints),
            'battery_level': self.get_battery_level(),
            'emergency_status': 'ACTIVE' if self.is_lost else 'NORMAL'
        }

class FleetSLAMManager:
    """Manage SLAM navigation for entire drone fleet"""
    
    def __init__(self):
        self.drones: Dict[str, VisualSLAMNavigator] = {}
        self.fleet_status = "normal"
        self.active_missions = []
        
    def register_drone(self, drone_id: str):
        """Register a new drone with SLAM capabilities"""
        if drone_id not in self.drones:
            self.drones[drone_id] = VisualSLAMNavigator(drone_id)
            print(f"✅ Registered {drone_id} with Visual SLAM")
    
    def update_drone_status(self, drone_id: str, gps_available: bool, 
                          gps_coords: Optional[Tuple[float, float]] = None):
        """Update drone GPS status"""
        if drone_id in self.drones:
            self.drones[drone_id].update_gps_status(gps_available, gps_coords)
            self.update_fleet_status()
    
    def process_drone_frame(self, drone_id: str, frame: np.ndarray):
        """Process frame for SLAM navigation"""
        if drone_id in self.drones:
            return self.drones[drone_id].process_frame(frame)
        return None
    
    def update_fleet_status(self):
        """Update overall fleet status"""
        lost_drones = [drone_id for drone_id, nav in self.drones.items() if nav.is_lost]
        
        if len(lost_drones) == 0:
            self.fleet_status = "normal"
        elif len(lost_drones) < len(self.drones) * 0.5:
            self.fleet_status = "partial_failure"
        else:
            self.fleet_status = "critical_failure"
    
    def get_fleet_summary(self):
        """Get fleet-wide navigation summary"""
        lost_count = sum(1 for nav in self.drones.values() if nav.is_lost)
        total_tracking_quality = sum(nav.tracking_quality for nav in self.drones.values())
        avg_quality = total_tracking_quality / len(self.drones) if self.drones else 0
        
        return {
            'total_drones': len(self.drones),
            'lost_drones': lost_count,
            'operational_drones': len(self.drones) - lost_count,
            'fleet_status': self.fleet_status,
            'average_tracking_quality': round(avg_quality, 3),
            'emergency_drones': [drone_id for drone_id, nav in self.drones.items() if nav.is_lost]
        }

# Global instance
slam_manager = FleetSLAMManager()

def initialize_gps_failure_system(drone_ids: list):
    """Initialize GPS failure system for all drones"""
    print("\n" + "="*60)
    print("🧭 INITIALIZING GPS FAILURE AUTONOMOUS NAVIGATION")
    print("="*60)
    
    for drone_id in drone_ids:
        slam_manager.register_drone(drone_id)
    
    print(f"✅ GPS Failure Navigation System ready for {len(drone_ids)} drones")
    print("🎯 Features: Visual SLAM, Return-to-Base, Emergency Protocols")
    
    return slam_manager

if __name__ == "__main__":
    # Test the system
    drone_ids = [f"drone_{i}" for i in range(1, 4)]
    manager = initialize_gps_failure_system(drone_ids)
    
    # Simulate GPS failure
    manager.update_drone_status("drone_1", False, (28.6139, 77.2090))
    
    # Process some frames
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    for i in range(10):
        result = manager.process_drone_frame("drone_1", test_frame)
        if result:
            print(f"Frame {i}: Position {result['position']}, Quality {result['tracking_quality']:.2f}")
        time.sleep(0.1)
    
    print("\n📊 Fleet Summary:")
    print(json.dumps(manager.get_fleet_summary(), indent=2))