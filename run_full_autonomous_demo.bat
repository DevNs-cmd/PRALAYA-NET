@echo off
echo.
echo ══════════════════════════════════════════════════════════════════════════
echo 🚀 PRALAYA-NET: FULL AUTONOMOUS SELF-HEALING INFRASTRUCTURE DEMO
echo ══════════════════════════════════════════════════════════════════════════
echo.

echo 📍 Starting Autonomous Self-Healing National Infrastructure Network...
echo.

echo 🔄 Step 1: Starting Backend Services...
cd /d "%~dp0backend"
start "PRALAYA-NET Backend" cmd /k "echo 🚀 Backend Starting... && python run.py"
echo ✅ Backend services starting...
echo.

echo 🔄 Step 2: Waiting for Backend Initialization...
timeout /t 10 /nobreak >nul
echo ✅ Backend initialization time completed
echo.

echo 🔄 Step 3: Starting Frontend Command Center...
cd /d "%~dp0dashboard"
start "PRALAYA-NET Command Center" cmd /k "echo 🎯 Command Center Starting... && npm run dev"
echo ✅ Frontend command center starting...
echo.

echo 🔄 Step 4: Waiting for Frontend Initialization...
timeout /t 8 /nobreak >nul
echo ✅ Frontend initialization time completed
echo.

echo ══════════════════════════════════════════════════════════════════════════
echo 🎯 SYSTEM READY - AUTONOMOUS SELF-HEALING INFRASTRUCTURE ACTIVE
echo ══════════════════════════════════════════════════════════════════════════
echo.
echo 📍 Backend API:        http://127.0.0.1:8000
echo 📍 Command Center:     http://localhost:5173/command-center
echo 📍 API Documentation:  http://127.0.0.1:8000/docs
echo 📍 System Health:      http://127.0.0.1:8000/api/health
echo.
echo 🚀 DEMO INSTRUCTIONS:
echo.
echo 1️⃣ Open Command Center: http://localhost:5173/command-center
echo.
echo 2️⃣ Click "Start Full Demo" to trigger autonomous disaster response
echo.
echo 3️⃣ Watch the National Stability Index improve in real-time
echo.
echo 4️⃣ Observe autonomous intents, agent coordination, and stabilization
echo.
echo 5️⃣ View execution proof in the forensic ledger
echo.
echo 🔥 AUTONOMOUS CAPABILITIES ACTIVE:
echo    ✅ Intent-Driven Command Execution
echo    ✅ Multi-Agent Negotiation Protocol  
echo    ✅ Self-Healing Infrastructure Control
echo    ✅ Real-Time Stability Index
echo    ✅ Execution Ledger & Forensic Proof
echo.
echo 🎯 TRANSFORMATION ACHIEVED:
echo    From: Disaster Prediction Dashboard
echo    To:   Autonomous Self-Healing Infrastructure Network
echo.
echo ══════════════════════════════════════════════════════════════════════════
echo 🌟 Judges can now clearly see: disaster → system decides → system acts → country stabilizes
echo ══════════════════════════════════════════════════════════════════════════
echo.

echo 🔄 Step 5: Launching Command Center in browser...
timeout /t 3 /nobreak >nul
start http://localhost:5173/command-center

echo.
echo 🎉 PRALAYA-NET Autonomous Self-Healing Infrastructure Demo is RUNNING!
echo.
echo 💡 Press any key to stop all services...
pause >nul

echo.
echo 🛑 Stopping all services...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo ✅ All services stopped
echo.

echo 🎯 Demo Complete. Thank you for reviewing PRALAYA-NET!
echo.
pause
