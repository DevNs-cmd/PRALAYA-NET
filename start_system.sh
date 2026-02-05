#!/bin/bash
echo "============================================================"
echo "🚀 PRALAYA-NET: END-TO-END SYSTEM INITIATION (UNIX)"
echo "============================================================"

# Step 1: Start Backend
echo "[1/4] Starting Strategic Layer (Backend)..."
python3 backend/run.py &
BACKEND_PID=$!

# Step 2: Wait for Health Check
echo "[2/4] Waiting for Protected API to stabilize..."
until curl -s http://127.0.0.1:8000/api/health > /dev/null; do
  sleep 2
done
echo "✅ Backend Strategic Layer is ONLINE."

# Step 3: Inject Initiation Disaster (Demo Mode)
echo "[3/4] Injecting Initiation Disaster Zone..."
curl -X POST http://127.0.0.1:8000/api/trigger/disaster \
     -H "Content-Type: application/json" \
     -d '{"disaster_type": "flood", "severity": 0.4, "location": {"lat": 28.6139, "lon": 77.2090}}' > /dev/null
echo "✅ Demonstration scenario injected successfully."

# Step 4: Start Frontend
echo "[4/4] Launching Tactical Dashboard..."
cd dashboard && npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
