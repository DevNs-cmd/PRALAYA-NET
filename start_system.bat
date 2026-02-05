@echo off
TITLE PRALAYA-NET System Orchestrator
echo ============================================================
echo 🚀 PRALAYA-NET: END-TO-END SYSTEM INITIATION
echo ============================================================

:: Step 1: Start Backend
echo [1/4] Starting Strategic Layer (Backend)...
cd backend
start "PRALAYA-NET Backend" cmd /c "python run.py"
cd ..

:: Step 2: Wait for Health Check
echo [2/4] Waiting for Protected API to stabilize...
:wait_loop
curl -s http://127.0.0.1:8000/api/health > nul
if %errorlevel% neq 0 (
    timeout /t 2 /nobreak > nul
    goto wait_loop
)
echo ✅ Backend Strategic Layer is ONLINE.

:: Step 3: Inject Initiation Disaster (Demo Mode)
echo [3/4] Injecting Initiation Disaster Zone...
curl -X POST http://127.0.0.1:8000/api/trigger/disaster -H "Content-Type: application/json" -d "{\"disaster_type\": \"flood\", \"severity\": 0.4, \"location\": {\"lat\": 28.6139, \"lon\": 77.2090}}" > nul
echo ✅ Demonstration scenario injected successfully.

:: Step 4: Start Frontend
echo [4/4] Launching Tactical Dashboard...
cd dashboard
npm run dev
cd ..

echo ============================================================
echo 🛑 SYSTEM SHUTDOWN: Close all terminal windows to terminate.
echo ============================================================
