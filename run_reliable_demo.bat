@echo off
echo.
echo ════════════════════════════════════════════════════════════════════════
echo 🚀 PRALAYA-NET: RELIABLE STARTUP SCRIPT
echo ════════════════════════════════════════════════════════════════════════
echo.

echo 🔍 CHECKING SYSTEM REQUIREMENTS...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo 💡 Please install Python 3.9+ and add to PATH
    pause
    exit /b 1
)
echo ✅ Python found

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo 💡 Please install Node.js 16+ and add to PATH
    pause
    exit /b 1
)
echo ✅ Node.js found

echo.
echo 📁 CHANGING TO PROJECT DIRECTORY...
cd /d "%~dp0"
if %errorlevel% neq 0 (
    echo ❌ Failed to change to project directory
    pause
    exit /b 1
)
echo ✅ Project directory: %CD%

echo.
echo 🐍 STARTING BACKEND SERVER...
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating default .env file...
    (
        echo DEMO_MODE=true
        echo DATA_GOV_KEY=demo_key
        echo PORT=8000
    ) > .env
    echo ✅ .env file created
)

REM Start backend in background
start "PRALAYA-NET Backend" cmd /c "cd /d %CD%\backend && echo 🚀 Starting backend server... && python run.py"

echo ⏳ Waiting for backend to start...
timeout /t 15 /nobreak >nul

echo.
echo 🌐 STARTING FRONTEND SERVER...
echo.

REM Check if node_modules exists
if not exist "dashboard\node_modules" (
    echo 📦 Installing frontend dependencies...
    cd dashboard
    call npm install
    cd ..
    echo ✅ Dependencies installed
)

REM Start frontend
start "PRALAYA-NET Frontend" cmd /c "cd /d %CD%\dashboard && echo 🎯 Starting frontend server... && npm run dev"

echo ⏳ Waiting for frontend to start...
timeout /t 10 /nobreak >nul

echo.
echo ════════════════════════════════════════════════════════════════════════
echo 🎉 PRALAYA-NET SYSTEM STARTUP COMPLETE
echo ════════════════════════════════════════════════════════════════════════
echo.
echo 📍 ACCESS POINTS:
echo    Backend API:        http://127.0.0.1:8000
echo    Frontend UI:        http://localhost:5173
echo    Enhanced Command:   http://localhost:5173/enhanced-command-center
echo    API Documentation:  http://127.0.0.1:8000/docs
echo    Health Check:       http://127.0.0.1:8000/api/health
echo.
echo 🎯 NEXT STEPS:
echo    1. Open Enhanced Command Center in your browser
echo    2. Wait for connection to establish
echo    3. Click "Simulate Disaster" to test autonomous response
echo    4. Watch real-time updates in all panels
echo.
echo 🌟 SYSTEM READY FOR DEMONSTRATION
echo.

REM Open browser automatically
timeout /t 3 /nobreak >nul
start http://localhost:5173/enhanced-command-center

echo.
echo 💡 Press any key to stop all services...
pause >nul

echo.
echo 🛑 STOPPING ALL SERVICES...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo ✅ All services stopped
echo.

echo 🎯 Thank you for using PRALAYA-NET!
echo.
pause
