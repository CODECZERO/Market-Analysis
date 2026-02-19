#!/bin/bash

# ============================================
# COMPLETE STARTUP - Backend + Frontend + Live Monitor
# ============================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SYMBOL=${1:-TCS.NS}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 MARKET ANALYSIS - COMPLETE SYSTEM STARTUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo""
echo "Symbol to monitor: $SYMBOL"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    [ -f .backend.pid ] && kill $(cat .backend.pid) 2>/dev/null
    [ -f .frontend.pid ] && kill $(cat .frontend.pid) 2>/dev/null
    [ -f .monitor.pid ] && kill $(cat .monitor.pid) 2>/dev/null
    pkill -f "analyze_cli.py" 2>/dev/null
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    lsof -ti:5173 | xargs kill -9 2>/dev/null
    rm -f .backend.pid .frontend.pid .monitor.pid
    echo "✅ Cleanup complete"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Activate venv
source ./venv/bin/activate

# Start Backend
echo -e "${BLUE}[1/3]${NC} Starting Backend API..."
export PYTHONPATH="${PWD}/worker/src:${PYTHONPATH}"
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
./venv/bin/uvicorn api_server_production:app --host 0.0.0.0 --port 8000 --log-level info > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid
echo -e "  ${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"
sleep 3

# Start Frontend
echo -e "${BLUE}[2/3]${NC} Starting Frontend..."
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
cd frontend
python3 -m http.server 5173 --bind 127.0.0.1 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo $FRONTEND_PID > .frontend.pid
echo -e "  ${GREEN}✓${NC} Frontend started (PID: $FRONTEND_PID)"
sleep 2

# Start Live Monitor
echo -e "${BLUE}[3/3]${NC} Starting Live Monitor..."
(
    sleep 3
    while true; do
        clear
        echo "════════════════════════════════════════════════════════════════════════════════"
        echo "                    🔴 LIVE MARKET ANALYSIS - AUTO-REFRESH"
        echo "           Monitoring: $SYMBOL | Updates every 120s | Ctrl+C to stop"
        echo "════════════════════════════════════════════════════════════════════════════════"
        echo ""
        
        ./venv/bin/python analyze_cli.py $SYMBOL 2>/dev/null || echo "⚠️  Analysis temporarily unavailable"
        
        echo ""
        echo "════════════════════════════════════════════════════════════════════════════════"
        echo "⏰ Next update in 120 seconds..."
        echo "Web: http://localhost:5173 | API: http://localhost:8000"
        echo "════════════════════════════════════════════════════════════════════════════════"
        
        sleep 120
    done
) &
MONITOR_PID=$!
echo $MONITOR_PID > .monitor.pid
echo -e "  ${GREEN}✓${NC} Live monitor started (PID: $MONITOR_PID)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${GREEN}✅ ALL SYSTEMS OPERATIONAL${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🌐 Web Dashboard:  http://localhost:5173"
echo "  🔌 API Backend:    http://localhost:8000"
echo "  📊 Live Monitor:   Running (updating every 2 min)"
echo ""
echo "  💡 Monitoring: $SYMBOL"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Keep running
wait
