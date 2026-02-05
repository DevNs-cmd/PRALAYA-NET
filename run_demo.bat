@echo off
TITLE PRALAYA-NET PRODUCTION DEMO
echo ============================================================
echo 🚀 PRALAYA-NET: PRODUCTION COMMAND CENTER
echo ============================================================

:: 1. Backend + Ingestor
echo [1/3] Launching Strategic Layer (Backend + Ingestors)...
cd backend
start "PRALAYA-NET Backend" cmd /c "venv\Scripts\python.exe run.py"
cd ..

:: 2. Drone Simulation (Hybrid V-SLAM)
echo [2/3] Initializing Reconnaissance Drones (V-SLAM)...
cd drone_simulation
start "PRALAYA-NET Drone Feed" cmd /c "..\backend\venv\Scripts\python.exe visual_slam.py"
cd ..

:: 3. Dashboard
echo [3/3] Deploying Tactical Dashboard...
cd dashboard
npm run dev

echo ============================================================
echo 🛑 SYSTEM ACTIVE. Close windows to terminate.
echo ============================================================
