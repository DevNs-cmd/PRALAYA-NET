#!/usr/bin/env python3
"""
PRALAYA-NET Frame Upload Test Suite
Tests frame transmission between drone simulator and backend API on port 8001
"""

import cv2
import numpy as np
import requests
import sys
from pathlib import Path
import json
from datetime import datetime
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    BACKEND_URL, 
    FRAME_ENCODING_FORMAT, 
    FRAME_JPEG_QUALITY,
    FRAME_RESIZE_WIDTH,
    FRAME_RESIZE_HEIGHT
)

class FrameUploadTester:
    def __init__(self, backend_url=BACKEND_URL, verbose=True):
        self.backend_url = backend_url
        self.verbose = verbose
        self.session = requests.Session()
        self.test_results = []
        
    def log(self, message, level="INFO"):
        """Log with timestamp and level"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅ ",
            "ERROR": "❌ ",
            "WARNING": "⚠️ ",
            "TEST": "🧪 "
        }.get(level, "  ")
        
        if self.verbose:
            print(f"[{timestamp}] {prefix} {message}")
    
    def test_backend_health(self):
        """Test 1: Verify backend is running and responding"""
        self.log("Testing backend health check...", "TEST")
        
        try:
            response = self.session.get(f"{self.backend_url}/", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✓ Backend is healthy: {data.get('system', 'Unknown')}", "SUCCESS")
                self.test_results.append(("Backend Health", True, None))
                return True
            else:
                error = f"Backend returned {response.status_code}"
                self.log(error, "ERROR")
                self.test_results.append(("Backend Health", False, error))
                return False
                
        except requests.exceptions.ConnectionError as e:
            error = f"Cannot connect to {self.backend_url} - Is server running?"
            self.log(error, "ERROR")
            self.test_results.append(("Backend Health", False, error))
            return False
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            self.log(error, "ERROR")
            self.test_results.append(("Backend Health", False, error))
            return False
    
    def capture_frame(self, use_synthetic=True):
        """Capture frame from camera or generate synthetic"""
        self.log("Capturing frame...", "TEST")
        
        try:
            cap = cv2.VideoCapture(0)
            
            if cap and cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                
                if ret and frame is not None:
                    self.log(f"✓ Captured real frame: {frame.shape}", "SUCCESS")
                    return frame
                else:
                    self.log("⚠️ Camera opened but frame read failed", "WARNING")
            else:
                self.log("⚠️ Camera not available, using synthetic", "WARNING")
        except Exception as e:
            self.log(f"Camera error: {str(e)}", "WARNING")
        
        if use_synthetic:
            return self.generate_synthetic_frame()
        return None
    
    def generate_synthetic_frame(self):
        """Generate a synthetic test frame"""
        w, h = FRAME_RESIZE_WIDTH, FRAME_RESIZE_HEIGHT
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Gradient background
        for i in range(h):
            frame[i, :] = [int(255 * i / h), int(200 - 100 * i / h), 100]
        
        # Add test pattern
        cv2.circle(frame, (w//2, h//2), 50, (0, 255, 255), -1)
        cv2.rectangle(frame, (20, 20), (w-20, h-20), (255, 0, 0), 2)
        
        # Add text
        cv2.putText(frame, "TEST FRAME", (w//4, h//3), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, datetime.now().strftime("%H:%M:%S"), (w//4, 2*h//3),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        self.log(f"✓ Generated synthetic frame: {frame.shape}", "SUCCESS")
        return frame
    
    def test_frame_upload(self, drone_id="test_drone_1", frame=None):
        """Test 2: Upload frame using CORRECT multipart/form-data format"""
        if frame is None:
            frame = self.capture_frame()
        
        if frame is None:
            self.log("No frame available for upload", "ERROR")
            self.test_results.append(("Frame Upload", False, "No frame"))
            return False
        
        self.log(f"Uploading frame for {drone_id} ({frame.shape})...", "TEST")
        
        try:
            # Resize frame
            frame_resized = cv2.resize(frame, (FRAME_RESIZE_WIDTH, FRAME_RESIZE_HEIGHT))
            
            # Encode as JPEG
            success, img_encoded = cv2.imencode(
                FRAME_ENCODING_FORMAT, 
                frame_resized,
                [cv2.IMWRITE_JPEG_QUALITY, FRAME_JPEG_QUALITY]
            )
            
            if not success:
                error = "JPEG encoding failed"
                self.log(error, "ERROR")
                self.test_results.append(("Frame Upload", False, error))
                return False
            
            frame_bytes = img_encoded.tobytes()
            self.log(f"✓ Encoded to {FRAME_ENCODING_FORMAT}: {len(frame_bytes)} bytes", "SUCCESS")
            
            # CORRECT FORMAT: multipart/form-data
            files = {
                "file": (f"test_frame.jpg", frame_bytes, "image/jpeg")
            }
            
            endpoint = f"{self.backend_url}/api/drones/slam/{drone_id}/frame"
            self.log(f"Posting to: {endpoint}", "INFO")
            
            response = self.session.post(
                endpoint,
                files=files,
                timeout=5
            )
            
            self.log(f"Response: {response.status_code}", "INFO")
            
            if response.status_code == 200:
                self.log(f"✓ Frame uploaded successfully", "SUCCESS")
                self.test_results.append(("Frame Upload", True, None))
                
                try:
                    resp_data = response.json()
                    self.log(f"Backend response: {json.dumps(resp_data, indent=2)}", "INFO")
                except:
                    self.log(f"Response body: {response.text[:100]}", "INFO")
                
                return True
            else:
                error = f"Upload returned {response.status_code}"
                self.log(error, "ERROR")
                
                try:
                    error_detail = response.json()
                    self.log(f"Server error: {json.dumps(error_detail)}", "ERROR")
                    error = json.dumps(error_detail)
                except:
                    self.log(f"Response: {response.text}", "ERROR")
                    error = response.text[:100]
                
                self.test_results.append(("Frame Upload", False, error))
                return False
                
        except requests.exceptions.Timeout:
            error = "Request timeout"
            self.log(error, "ERROR")
            self.test_results.append(("Frame Upload", False, error))
            return False
        except requests.exceptions.ConnectionError as e:
            error = f"Connection failed: {str(e)[:50]}"
            self.log(error, "ERROR")
            self.test_results.append(("Frame Upload", False, error))
            return False
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            self.log(error, "ERROR")
            self.test_results.append(("Frame Upload", False, error))
            return False
    
    def test_telemetry_upload(self, drone_id="test_drone_1"):
        """Test 3: Upload telemetry data"""
        self.log(f"Uploading telemetry for {drone_id}...", "TEST")
        
        try:
            payload = {
                "keypoints": 250,
                "keyframes": 5,
                "status": "localized",
                "gps_status": "active",
                "tactical_swarm": False,
                "camera_mode": "OWN_CAMERA",
                "timestamp": datetime.now().isoformat()
            }
            
            endpoint = f"{self.backend_url}/api/drones/slam/{drone_id}/telemetry"
            
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=5
            )
            
            self.log(f"Response: {response.status_code}", "INFO")
            
            if response.status_code == 200:
                self.log(f"✓ Telemetry uploaded successfully", "SUCCESS")
                self.test_results.append(("Telemetry Upload", True, None))
                return True
            else:
                error = f"Telemetry returned {response.status_code}"
                self.log(error, "ERROR")
                self.test_results.append(("Telemetry Upload", False, error))
                return False
                
        except Exception as e:
            error = f"Telemetry upload failed: {str(e)}"
            self.log(error, "ERROR")
            self.test_results.append(("Telemetry Upload", False, error))
            return False
    
    def test_drone_status(self):
        """Test 4: Fetch drone status from backend"""
        self.log("Fetching drone status...", "TEST")
        
        try:
            endpoint = f"{self.backend_url}/api/drones/status"
            response = self.session.get(endpoint, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                drone_count = len(data.get('drones', []))
                self.log(f"✓ Found {drone_count} drones on backend", "SUCCESS")
                self.test_results.append(("Drone Status", True, None))
                return True
            else:
                error = f"Status returned {response.status_code}"
                self.log(error, "ERROR")
                self.test_results.append(("Drone Status", False, error))
                return False
                
        except Exception as e:
            error = f"Status fetch failed: {str(e)}"
            self.log(error, "ERROR")
            self.test_results.append(("Drone Status", False, error))
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        
        for test_name, passed, error in self.test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            error_msg = f" - {error}" if error else ""
            print(f"{status} | {test_name}{error_msg}")
        
        total = len(self.test_results)
        passed = sum(1 for _, p, _ in self.test_results if p)
        
        print("="*70)
        print(f"Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ All tests PASSED! Frame transmission is working correctly.")
            return True
        else:
            print(f"❌ {total - passed} test(s) FAILED!")
            return False
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*70)
        print("🧪 PRALAYA-NET FRAME UPLOAD TEST SUITE")
        print("="*70)
        print(f"Backend: {self.backend_url}")
        print("="*70 + "\n")
        
        # Test 1: Health
        if not self.test_backend_health():
            print("\n❌ Backend is not running!")
            print(f"Start backend with: cd backend && python -m uvicorn app:app --port 8001")
            self.print_summary()
            return False
        
        print()
        
        # Test 2: Frame Upload
        frame = self.capture_frame(use_synthetic=True)
        if not self.test_frame_upload(frame=frame):
            print("\n❌ Frame upload failed!")
            self.print_summary()
            return False
        
        print()
        
        # Test 3: Telemetry
        self.test_telemetry_upload()
        
        print()
        
        # Test 4: Drone Status
        self.test_drone_status()
        
        # Print summary
        return self.print_summary()

def main():
    parser = argparse.ArgumentParser(description="Test frame uploads to PRALAYA-NET backend")
    parser.add_argument("--backend", default=BACKEND_URL, help=f"Backend URL (default: {BACKEND_URL})")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    tester = FrameUploadTester(backend_url=args.backend, verbose=not args.quiet)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
