import requests
import json

# Test a simple JSON POST to see if the issue is with multipart/form-data specifically
try:
    response = requests.post(
        "http://127.0.0.1:8000/api/drones/slam/drone_1/telemetry",
        json={"test": "data"},
        timeout=5.0
    )
    
    print(f"JSON POST Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS:", response.json())
    else:
        print("ERROR:", response.text)
        
except Exception as e:
    print("JSON POST Exception:", e)
    import traceback
    traceback.print_exc()