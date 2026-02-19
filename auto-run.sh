#!/bin/bash

# ============================================
# Market Analysis System - Auto Start Script
# Starts both backend and frontend
# ============================================

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$SCRIPT_DIR"
cd "$BASE_DIR"

set -e  # Exit on error

# ============================================
# CLEANUP TRAP - Kill services on Ctrl+C
# ============================================
cleanup() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  🛑 Caught interrupt signal - Cleaning up..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Run kill-all script
    if [ -f ./kill-all.sh ]; then
        ./kill-all.sh
    else
        # Fallback cleanup
        echo "Stopping services..."
        [ -f .backend.pid ] && kill $(cat .backend.pid) 2>/dev/null && echo "  ✓ Backend stopped"
        [ -f .frontend.pid ] && kill $(cat .frontend.pid) 2>/dev/null && echo "  ✓ Frontend stopped"
        lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "  ✓ Port 8000 cleaned"
        lsof -ti:5173 | xargs kill -9 2>/dev/null && echo "  ✓ Port 5173 cleaned"
    fi
    
    echo ""
    echo "✅ Cleanup complete. Goodbye!"
    exit 0
}

# Register cleanup on script exit, Ctrl+C, or termination
trap cleanup SIGINT SIGTERM EXIT

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 MARKET ANALYSIS SYSTEM - AUTO STARTUP"
echo "  (Press Ctrl+C to stop all services and exit)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track errors
ERRORS=0

# ============================================
# STEP 1: Check Prerequisites
# ============================================
echo -e "${BLUE}[1/9]${NC} Checking prerequisites..."

# Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "  ${GREEN}✓${NC} Python: $PYTHON_VERSION"
else
    echo -e "  ${RED}✗${NC} Python 3 not found"
    ERRORS=$((ERRORS + 1))
fi

# Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "  ${GREEN}✓${NC} Node.js: $NODE_VERSION"
else
    echo -e "  ${RED}✗${NC} Node.js not found"
    ERRORS=$((ERRORS + 1))
fi

# npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "  ${GREEN}✓${NC} npm: $NPM_VERSION"
else
    echo -e "  ${RED}✗${NC} npm not found"
    ERRORS=$((ERRORS + 1))
fi

if [ $ERRORS -gt 0 ]; then
    echo -e "\n${RED}Prerequisites check failed. Please install missing dependencies.${NC}"
    exit 1
fi

echo ""

# ============================================
# STEP 2: Validate Environment
# ============================================
echo -e "${BLUE}[2/9]${NC} Validating environment variables..."

if [ -f .env ]; then
    echo -e "  ${GREEN}✓${NC} .env file found"
    
    # Check required variables
    source .env
    
    if [ -n "$MONGO_URL" ]; then
        echo -e "  ${GREEN}✓${NC} MONGO_URL configured"
    else
        echo -e "  ${YELLOW}⚠${NC} MONGO_URL not set (will use mock data)"
    fi
    
    if [ -n "$REDIS_URL" ]; then
        echo -e "  ${GREEN}✓${NC} REDIS_URL configured"
    else
        echo -e "  ${YELLOW}⚠${NC} REDIS_URL not set (will use mock data)"
    fi
    
    if [ -n "$NVIDIA_API_KEY" ]; then
        echo -e "  ${GREEN}✓${NC} NVIDIA_API_KEY configured"
    else
        echo -e "  ${YELLOW}⚠${NC} NVIDIA_API_KEY not set (LLM features disabled)"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} .env file not found. Creating from template..."
    cp .env.example .env 2>/dev/null || echo "No .env.example found"
fi

echo ""

# ============================================
# STEP 3: Setup Virtual Environment & Install Dependencies
# ============================================
echo -e "${BLUE}[3/9]${NC} Setting up Python virtual environment...\n"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
    echo -e "  ${GREEN}✓${NC} Virtual environment created"
else
    echo -e "  ${GREEN}✓${NC} Virtual environment exists"
fi

# Activate venv
source venv/bin/activate
echo -e "  ${GREEN}✓${NC} Virtual environment activated"

# Install dependencies from worker/requirements.txt
if [ -f worker/requirements.txt ]; then
    # Check if packages are already installed
    if ./venv/bin/python -c "import fastapi, pymongo, redis, yfinance" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Worker packages already installed (skipping)"
    else
        echo "  Installing worker packages (showing progress)..."
        pip install -r worker/requirements.txt
        echo -e "  ${GREEN}✓${NC} Worker dependencies installed"
    fi
fi

# Install main requirements if exists
if [ -f requirements.txt ]; then
    # Check if key packages exist
    if ./venv/bin/python -c "import pandas, numpy" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Main packages already installed (skipping)"
    else
        echo "  Installing main packages (showing progress)..."
        pip install -r requirements.txt
        echo -e "  ${GREEN}✓${NC} Main dependencies installed"
    fi
fi

echo ""

# ============================================
# STEP 4: Install Frontend Dependencies
# ============================================
echo -e "${BLUE}[4/9]${NC} Installing frontend dependencies..."

cd frontend
if [ -f package.json ]; then
    if [ ! -d node_modules ]; then
        echo "  Installing npm packages (this may take a minute)..."
        npm install 2>&1 | grep -E "(added|removed|changed|audited)" || echo "  Installing..."
        echo -e "  ${GREEN}✓${NC} npm packages installed"
    else
        echo -e "  ${GREEN}✓${NC} Frontend dependencies already installed"
    fi
else
    echo -e "  ${RED}✗${NC} package.json not found"
    ERRORS=$((ERRORS + 1))
fi
cd ..

echo ""

# ============================================
# STEP 5: Verify Database Connections
# ============================================
echo -e "${BLUE}[5/9]${NC} Verifying database connections...\n"

# Use venv python
./venv/bin/python - <<EOF
import os
from dotenv import load_dotenv

# Explicitly load .env file (fixes Python 3.13 issue)
load_dotenv('.env')

# Test MongoDB
mongo_url = os.getenv('MONGO_URL')
if mongo_url:
    print("  ✓ MongoDB URL configured")
    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("  \033[0;32m✓\033[0m MongoDB: Connected")
        client.close()
    except Exception as e:
        print(f"  \033[1;33m⚠\033[0m MongoDB: {str(e)[:50]}")
else:
    print("  \033[1;33m⚠\033[0m MongoDB: Not configured")

# Test Redis
redis_url = os.getenv('REDIS_URL')
if redis_url:
    try:
        import redis
        r = redis.from_url(redis_url, socket_connect_timeout=5)
        r.ping()
        print("  \033[0;32m✓\033[0m Redis: Connected")
        r.close()
    except Exception as e:
        print(f"  \033[1;33m⚠\033[0m Redis: {str(e)[:50]}")
else:
    print("  \033[1;33m⚠\033[0m Redis: Not configured")
EOF

echo ""

# ============================================
# STEP 6: Start Backend (FastAPI)
# ============================================
echo -e "${CYAN}[6/9] Starting backend server (FastAPI on :8000)...${NC}"
cd "$BASE_DIR"
export PYTHONPATH="${BASE_DIR}/worker/src:${PYTHONPATH}"

# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Use the SIMPLE, WORKING backend
nohup "$VENV_PYTHON" -m uvicorn api_server_simple:app \
  --host 0.0.0.0 \
  --port 8000 \
  --log-level info > "$BACKEND_LOG" 2>&1 &

BACKEND_PID=$!
echo $BACKEND_PID > "$BACKEND_PID_FILE"
sleep 3

# Check if backend started
if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
  echo -e "${RED}  ✗ Backend failed to start${NC}"
  echo -e "  Check logs/backend.log for errors:"
  tail -20 "$BACKEND_LOG" | sed 's/^/  /'
  exit 1
fi

# Wait for backend to be ready
MAX_WAIT=15
WAIT_COUNT=0
while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
  if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ Backend running (PID: $BACKEND_PID)${NC}"
    echo -e "  ${GREEN}✓${NC} API: http://localhost:8000"
    echo -e "  ${GREEN}✓${NC} Docs: http://localhost:8000/docs"
    break
  fi
  sleep 1
  ((WAIT_COUNT++))
done

if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
  echo -e "${YELLOW}  ⚠ Backend started but health check timeout${NC}"
  echo "  Check logs/backend.log for errors:"
  tail -20 logs/backend.log
  ERRORS=$((ERRORS + 1))
fi

echo ""

# ============================================
# STEP 7: Start Frontend Server
# ============================================
echo -e "${BLUE}[7/9]${NC} Starting frontend dev server..."

# Kill any existing process on port 5173
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

cd frontend
# Start frontend in background
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "  Frontend PID: $FRONTEND_PID"
echo "  Waiting for dev server..."
sleep 8

# Check if frontend is running
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Frontend server running on http://localhost:5173"
else
    echo -e "  ${YELLOW}⚠${NC} Frontend server may still be starting"
    echo "  Check logs/frontend.log for details"
fi

echo ""

# ============================================
# STEP 8: Run Health Checks
# ============================================
echo -e "${BLUE}[8/9]${NC} Running health checks..."

# Backend health
BACKEND_HEALTH=$(curl -s http://localhost:8000/api/health | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"{data.get('status', 'unknown')} - MongoDB: {data.get('mongodb', 'unknown')}, Redis: {data.get('redis', 'unknown')}\")" 2>/dev/null || echo "failed")
echo "  Backend: $BACKEND_HEALTH"

# Frontend connectivity
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Frontend: Accessible"
else
    echo -e "  ${YELLOW}⚠${NC} Frontend: Not yet accessible"
fi

echo ""

# ============================================
# STEP 9: Display Summary & Open Browser
# ============================================
echo -e "${BLUE}[9/9]${NC} System startup complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  ${GREEN}✨ MARKET ANALYSIS SYSTEM READY ✨${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  🌐 Frontend:  http://localhost:5173"
echo "  🔌 Backend:   http://localhost:8000"
echo "  📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "  📊 Process IDs:"
echo "     Backend:  $BACKEND_PID"
echo "     Frontend: $FRONTEND_PID"
echo ""
echo "  📝 Logs:"
echo "     Backend:  tail -f logs/backend.log"
echo "     Frontend: tail -f logs/frontend.log"
echo ""
echo "  🛑 To stop:"
echo "     kill $BACKEND_PID $FRONTEND_PID"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save PIDs for later
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# Open browser (optional)
if command -v xdg-open &> /dev/null; then
    echo "  Opening browser..."
    sleep 2
    xdg-open http://localhost:5173 &
fi

echo ""
echo -e "${GREEN}✅ System is running!${NC}"
echo ""
