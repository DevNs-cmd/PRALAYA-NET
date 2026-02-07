import requests
import cv2
import numpy as np

# Test backend connectivity
try:
    response = requests.get("http://127.0.0.1:8000/api/drones/status")
    print("Backend Status:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", e)

# Test frame upload
try:
    # Create a test frame
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    cv2.putText(frame, "TEST FRAME", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Encode as JPEG
    _, img_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    frame_bytes = img_encoded.tobytes()
    
    # Upload using multipart/form-data
    files = {"file": ("test_frame.jpg", frame_bytes, "image/jpeg")}
    response = requests.post(
        "http://127.0.0.1:8000/api/drones/slam/drone_1/frame",
        files=files,
        timeout=5.0
    )
    
    print("\nFrame Upload Test:")
    print("Status:", response.status_code)
    if response.status_code == 200:
        print("SUCCESS:", response.json())
    else:
        print("ERROR:", response.text)
        
except Exception as e:
    print("Frame Upload Error:", e)