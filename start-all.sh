#!/bin/bash

# ============================================
# START-ALL.SH - Start All Services
# Improved version with better npm handling
# ============================================

set -e

# Cleanup on interrupt
cleanup() {
    echo ""
    echo "🛑 Caught interrupt - stopping services..."
    [ -f ./kill-all.sh ] && ./kill-all.sh || {
        [ -f .backend.pid ] && kill $(cat .backend.pid) 2>/dev/null
        [ -f .frontend.pid ] && kill $(cat .frontend.pid) 2>/dev/null
        lsof -ti:8000 | xargs kill -9 2>/dev/null
        lsof -ti:5173 | xargs kill -9 2>/dev/null
    }
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 STARTING ALL SERVICES"
echo "  (Press Ctrl+C to stop and exit)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ============================================
# Step 1: Kill existing services
# ============================================
echo -e "${BLUE}[1/5]${NC} Stopping existing services..."

# Kill existing processes
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "  ✓ Killed port 8000" || echo "  ⊘ Port 8000 free"
lsof -ti:5173 | xargs kill -9 2>/dev/null && echo "  ✓ Killed port 5173" || echo "  ⊘ Port 5173 free"

# Clean up old PID files
rm -f .backend.pid .frontend.pid

sleep 2
echo ""

# ============================================
# Step 2: Check and install npm dependencies
# ============================================
echo -e "${BLUE}[2/5]${NC} Checking frontend dependencies..."

cd frontend
if [ ! -d node_modules ]; then
    echo "  📦 npm packages not found. Installing..."
    npm install 2>&1 | grep -E "(added|removed|changed|audited|up to date)" || echo "  Installing..."
    echo -e "  ${GREEN}✓${NC} npm packages installed"
elif [ ! -f node_modules/.package-lock.json ]; then
    echo "  📦 Dependencies may be outdated. Updating..."
    npm install 2>&1 | grep -E "(added|removed|changed|audited|up to date)" || echo "  Updating..."
    echo -e "  ${GREEN}✓${NC} npm packages updated"
else
    echo -e "  ${GREEN}✓${NC} npm packages already installed"
fi
cd ..

echo ""

# ============================================
# Step 3: Create logs directory
# ============================================
echo -e "${BLUE}[3/5]${NC} Preparing environment..."

mkdir -p logs
> logs/backend.log
> logs/frontend.log

echo -e "  ${GREEN}✓${NC} Logs directory ready"
echo ""

# ============================================
# Step 4: Start Backend Server
# ============================================
echo -e "${BLUE}[4/5]${NC} Starting backend server..."

# Start in background
nohup python3 api_server_production.py > logs/backend.log 2>&1 &
BACKEND_PID=$!

echo "  Started backend (PID: $BACKEND_PID)"
echo $BACKEND_PID > .backend.pid

# Wait for backend to be ready
echo "  Waiting for backend to start..."
for i in {1..15}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Backend ready at http://localhost:8000"
        break
    fi
    
    if [ $i -eq 15 ]; then
        echo -e "  ${RED}✗${NC} Backend failed to start in 15 seconds"
        echo "  Check logs/backend.log for errors"
        tail -20 logs/backend.log
        exit 1
    fi
    
    sleep 1
done

echo ""

# ============================================
# Step 5: Start Frontend Server
# ============================================
echo -e "${BLUE}[5/5]${NC} Starting frontend server..."

cd frontend

# Start in background
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

echo "  Started frontend (PID: $FRONTEND_PID)"
echo $FRONTEND_PID > .frontend.pid

# Wait for frontend to be ready
echo "  Waiting for frontend to start..."
for i in {1..20}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Frontend ready at http://localhost:5173"
        break
    fi
    
    if [ $i -eq 20 ]; then
        echo -e "  ${YELLOW}⚠${NC} Frontend may still be starting..."
        echo "  Check logs/frontend.log if needed"
    fi
    
    sleep 1
done

echo ""

# ============================================
# Summary
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${GREEN}✨ ALL SERVICES RUNNING ✨${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🌐 Frontend:    http://localhost:5173"
echo "  🔌 Backend:     http://localhost:8000"
echo "  📚 API Docs:    http://localhost:8000/docs"
echo ""
echo "  📊 Process IDs:"
echo "     Backend:     $BACKEND_PID (saved to .backend.pid)"
echo "     Frontend:    $FRONTEND_PID (saved to .frontend.pid)"
echo ""
echo "  📝 View Logs:"
echo "     Backend:     tail -f logs/backend.log"
echo "     Frontend:    tail -f logs/frontend.log"
echo ""
echo "  🛑 Stop Services:"
echo "     ./kill-all.sh"
echo ""
echo "  📊 Monitor:"
echo "     ./monitor.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Open browser (optional)
if command -v xdg-open &> /dev/null; then
    echo "  Opening browser in 3 seconds..."
    sleep 3
    xdg-open http://localhost:5173 > /dev/null 2>&1 &
fi

echo -e "${GREEN}✅ System is running in background!${NC}"
echo ""
