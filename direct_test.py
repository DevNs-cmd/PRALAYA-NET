import requests
import cv2
import numpy as np

# Create a test frame
frame = np.zeros((240, 320, 3), dtype=np.uint8)
cv2.putText(frame, "TEST FRAME", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

# Encode as JPEG
_, img_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
frame_bytes = img_encoded.tobytes()

print(f"Frame size: {len(frame_bytes)} bytes")

# Upload using multipart/form-data
files = {"file": ("test_frame.jpg", frame_bytes, "image/jpeg")}
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/drones/slam/drone_1/frame",
        files=files,
        timeout=5.0
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS:", response.json())
    else:
        print("ERROR:", response.text)
        print("Headers:", dict(response.headers))
        
except Exception as e:
    print("Exception:", e)
    import traceback
    traceback.print_exc()