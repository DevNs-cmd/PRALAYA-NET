#!/bin/bash

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "🚀 PRALAYA-NET: RELIABLE STARTUP SCRIPT"
echo "═════════════════════════════════════════════════════════════════════════"
echo ""

echo "🔍 CHECKING SYSTEM REQUIREMENTS..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "💡 Please install Python 3.9+"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "💡 Please install Node.js 16+"
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

echo ""
echo "📁 CHANGING TO PROJECT DIRECTORY..."
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ $? -ne 0 ]; then
    echo "❌ Failed to change to project directory"
    exit 1
fi
echo "✅ Project directory: $SCRIPT_DIR"

echo ""
echo "🐍 STARTING BACKEND SERVER..."
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating default .env file..."
    cat > .env << EOF
DEMO_MODE=true
DATA_GOV_KEY=demo_key
PORT=8000
EOF
    echo "✅ .env file created"
fi

# Start backend in background
echo "🚀 Starting backend server..."
cd backend
python3 run.py &
BACKEND_PID=$!
cd ..

echo "⏳ Waiting for backend to start..."
sleep 15

echo ""
echo "🌐 STARTING FRONTEND SERVER..."
echo ""

# Check if node_modules exists
if [ ! -d "dashboard/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd dashboard
    npm install
    cd ..
    echo "✅ Dependencies installed"
fi

# Start frontend
echo "🎯 Starting frontend server..."
cd dashboard
npm run dev &
FRONTEND_PID=$!
cd ..

echo "⏳ Waiting for frontend to start..."
sleep 10

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "🎉 PRALAYA-NET SYSTEM STARTUP COMPLETE"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "📍 ACCESS POINTS:"
echo "   Backend API:        http://127.0.0.1:8000"
echo "   Frontend UI:        http://localhost:5173"
echo "   Enhanced Command:   http://localhost:5173/enhanced-command-center"
echo "   API Documentation:  http://127.0.0.1:8000/docs"
echo "   Health Check:       http://127.0.0.1:8000/api/health"
echo ""
echo "🎯 NEXT STEPS:"
echo "   1. Open Enhanced Command Center in your browser"
echo "   2. Wait for connection to establish"
echo "   3. Click 'Simulate Disaster' to test autonomous response"
echo "   4. Watch real-time updates in all panels"
echo ""
echo "🌟 SYSTEM READY FOR DEMONSTRATION"
echo ""

# Open browser automatically
sleep 3
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5173/enhanced-command-center
elif command -v open > /dev/null; then
    open http://localhost:5173/enhanced-command-center
else
    echo "Please manually open: http://localhost:5173/enhanced-command-center"
fi

echo ""
echo "💡 Press Ctrl+C to stop all services..."
echo ""

# Wait for user interrupt
trap 'echo ""; echo "🛑 STOPPING ALL SERVICES..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo "✅ All services stopped"; echo ""; echo "🎯 Thank you for using PRALAYA-NET!"; echo ""; exit 0' INT

# Keep script running
while true; do
    sleep 1
done
