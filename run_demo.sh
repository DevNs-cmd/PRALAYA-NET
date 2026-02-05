#!/bin/bash
echo "============================================================"
echo "🚀 PRALAYA-NET: PRODUCTION COMMAND CENTER (UNIX)"
echo "============================================================"

# 1. Backend + Ingestor
echo "[1/3] Launching Strategic Layer..."
python3 backend/run.py &
BACKEND_PID=$!

# 2. Drone Simulation (Hybrid V-SLAM)
echo "[2/3] Initializing Reconnaissance Drones..."
python3 drone_simulation/visual_slam.py &
DRONE_PID=$!

# 3. Dashboard
echo "[3/3] Deploying Tactical Dashboard..."
cd dashboard && npm run dev

# Cleanup
trap "kill $BACKEND_PID $DRONE_PID" EXIT
