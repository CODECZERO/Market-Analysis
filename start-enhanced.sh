#!/bin/bash

# ============================================
# ENHANCED AUTO-RUN - WITH ADVANCED DASHBOARD
# ============================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    [ -f .backend.pid ] && kill $(cat .backend.pid) 2>/dev/null
    [ -f .frontend.pid ] && kill $(cat .frontend.pid) 2>/dev/null
    [ -f .dashboard.pid ] && kill $(cat .dashboard.pid) 2>/dev/null
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    lsof -ti:5173 | xargs kill -9 2>/dev/null
    rm -f .backend.pid .frontend.pid .dashboard.pid
    echo "✅ Cleanup complete"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 MARKET ANALYSIS - COMPLETE SYSTEM"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Choose mode:"
echo "  [1] Full System (Backend + Frontend + Dashboard)"
echo "  [2] Advanced Dashboard Only"
echo "  [3] Backend + Frontend Only"
echo ""

read -p "Select [1-3]: " MODE

source ./venv/bin/activate

if [ "$MODE" = "2" ]; then
    # Dashboard only
    echo -e "${CYAN}Starting Advanced Dashboard...${NC}"
    python advanced_cli.py
    exit 0
fi

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

if [ "$MODE" = "1" ]; then
    # Start Advanced Dashboard in background
    echo -e "${BLUE}[3/3]${NC} Starting Live Dashboard..."
    (
        sleep 2
        while true; do
            clear
            python advanced_cli.py --mode screener
            echo ""
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "⏰ Next refresh in 300s (5 min) | Ctrl+C to stop"
            echo "Web: http://localhost:5173 | API: http://localhost:8000"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            sleep 300
        done
    ) &
    DASHBOARD_PID=$!
    echo $DASHBOARD_PID > .dashboard.pid
    echo -e "  ${GREEN}✓${NC} Dashboard started (PID: $DASHBOARD_PID)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${GREEN}✅ ALL SYSTEMS OPERATIONAL${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🌐 Web Dashboard:  http://localhost:5173"
echo "  🔌 API Backend:    http://localhost:8000"
if [ "$MODE" = "1" ]; then
    echo "  📊 CLI Dashboard:  Auto-refreshing every 5 min"
fi
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

wait
