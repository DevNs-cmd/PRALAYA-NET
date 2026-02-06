import cv2
import time
import os
import threading
import requests
import json
from concurrent.futures import ThreadPoolExecutor


class DroneFeedSimulator:
    """Simulate N drone camera feeds using the local laptop webcam.

    - Captures frames from `cv2.VideoCapture(0)`
    - Publishes the same frame (JPEG) to each drone's upload endpoint
    - Periodically posts telemetry metadata for each drone
    """

    def __init__(self, backend_url=None, num_drones=12, fps=6, telemetry_interval=2.0):
        self.backend_url = backend_url or os.getenv("BACKEND_URL") or "http://127.0.0.1:8000"
        self.num_drones = int(os.getenv("SIMULATED_DRONES", num_drones))
        self.fps = float(os.getenv("SIMULATOR_FPS", fps))
        self.telemetry_interval = float(os.getenv("SIMULATOR_TELEMETRY_INTERVAL", telemetry_interval))
        self.running = False
        self.session = requests.Session()
        self.executor = ThreadPoolExecutor(max_workers=min(16, max(4, self.num_drones)))
        self.registered_drone_ids = []

    def _drone_ids(self):
        # Prefer registered backend drone ids if available
        if self.registered_drone_ids:
            return self.registered_drone_ids
        return [f"drone_{i+1}" for i in range(self.num_drones)]

    def register_drones_with_backend(self):
        """Register virtual drones in the backend so the UI will list them."""
        url = f"{self.backend_url}/api/drones/deploy"
        ids = []
        for i in range(self.num_drones):
            try:
                resp = self.session.post(url, json={"lat": 0.0, "lon": 0.0}, timeout=2.0)
                if resp.ok:
                    data = resp.json()
                    drone_id = data.get("drone_id") or data.get("id")
                    if drone_id:
                        ids.append(drone_id)
            except Exception:
                # ignore errors and continue
                pass

        if ids:
            self.registered_drone_ids = ids
            print(f"[Simulator] Registered {len(ids)} virtual drones with backend")

    def _encode_frame(self, frame):
        # Resize for transmission efficiency
        try:
            frame_small = cv2.resize(frame, (320, 240))
        except Exception:
            frame_small = frame
        _, img_encoded = cv2.imencode('.jpg', frame_small, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return img_encoded.tobytes()

    def _create_synthetic_frame(self):
        """Generate a test pattern frame when camera is unavailable."""
        import numpy as np
        # Create a dark frame
        frame = np.ones((240, 320, 3), dtype=np.uint8) * 20
        # Add some colored rectangles
        cv2.rectangle(frame, (10, 10), (100, 50), (0, 255, 0), 2)
        cv2.rectangle(frame, (150, 100), (300, 200), (255, 0, 0), 2)
        cv2.putText(frame, "SYNTHETIC FEED", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.putText(frame, f"T: {time.time():.1f}", (10, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        return frame

    def _post_frame(self, drone_id, frame_bytes):
        url = f"{self.backend_url}/api/drones/slam/{drone_id}/frame"
        try:
            # Send as multipart/form-data so FastAPI's File(...) parameter parses it correctly
            files = {"file": ("frame.jpg", frame_bytes, "image/jpeg")}
            self.session.post(url, files=files, timeout=1.5)
        except Exception:
            # best-effort; ignore failures so simulator stays alive
            pass

    def _post_telemetry(self, drone_id):
        url = f"{self.backend_url}/api/drones/slam/{drone_id}/telemetry"
        payload = {
            "drone_id": drone_id,
            "timestamp": time.time(),
            "gps": {"lat": 0.0, "lon": 0.0},
            "battery": 100,
            "tactical_swarm": True
        }
        try:
            self.session.post(url, json=payload, timeout=1.5)
        except Exception:
            pass

    def run(self):
        # Attempt to register virtual drones so frontend lists them
        try:
            self.register_drones_with_backend()
        except Exception:
            pass

        # Try multiple camera indices to be more robust on different systems
        cap = None
        for idx in range(0, 4):
            try:
                c = cv2.VideoCapture(idx)
                if c is not None and c.isOpened():
                    cap = c
                    print(f"[Simulator] Opened webcam at index {idx}")
                    break
                else:
                    try:
                        c.release()
                    except Exception:
                        pass
            except Exception:
                pass

        if cap is None or not cap.isOpened():
            print("[Simulator] Warning: Could not open any webcam (tried indices 0-3). Simulator disabled.")
            return

        print(f"[Simulator] Starting Drone Feed Simulator -> {self.num_drones} virtual drones @ {self.backend_url}")
        self.running = True
        drone_ids = self._drone_ids()
        last_telemetry = 0.0
        frame_interval = 1.0 / max(1.0, self.fps)

        try:
            while self.running:
                t0 = time.time()
                ret, frame = cap.read()
                if not ret or frame is None:
                    # Fallback to synthetic frames when camera read fails
                    frame = self._create_synthetic_frame()
                    if frame is None:
                        time.sleep(0.1)
                        continue

                frame_bytes = self._encode_frame(frame)

                # Post frames concurrently to backend per drone
                for d in drone_ids:
                    self.executor.submit(self._post_frame, d, frame_bytes)

                # Periodic telemetry (less frequent)
                if time.time() - last_telemetry > self.telemetry_interval:
                    for d in drone_ids:
                        self.executor.submit(self._post_telemetry, d)
                    last_telemetry = time.time()

                # Maintain target FPS
                elapsed = time.time() - t0
                to_sleep = frame_interval - elapsed
                if to_sleep > 0:
                    time.sleep(to_sleep)

        finally:
            cap.release()
            self.executor.shutdown(wait=False)
            print("[Simulator] Stopped Drone Feed Simulator")


def start_simulator_in_thread(backend_url=None, num_drones=12, fps=6):
    sim = DroneFeedSimulator(backend_url=backend_url, num_drones=num_drones, fps=fps)
    t = threading.Thread(target=sim.run, daemon=True)
    t.start()
    return sim
