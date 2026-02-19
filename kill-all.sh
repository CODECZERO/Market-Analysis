#!/bin/bash

# ============================================
# KILL-ALL.SH - Stop All Background Services
# ============================================

echo "🛑 Stopping all Market Analysis System services..."
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

STOPPED=0

# Kill processes by saved PIDs
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "  ${GREEN}✓${NC} Backend stopped (PID: $BACKEND_PID)"
        STOPPED=$((STOPPED + 1))
    else
        echo -e "  ${YELLOW}⊘${NC} Backend not running"
    fi
    rm .backend.pid
else
    echo -e "  ${YELLOW}⊘${NC} Backend PID file not found"
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "  ${GREEN}✓${NC} Frontend stopped (PID: $FRONTEND_PID)"
        STOPPED=$((STOPPED + 1))
    else
        echo -e "  ${YELLOW}⊘${NC} Frontend not running"
    fi
    rm .frontend.pid
else
    echo -e "  ${YELLOW}⊘${NC} Frontend PID file not found"
fi

# Kill all Python processes on port 8000
echo ""
echo "Cleaning up port 8000..."
BACKEND_PROCS=$(lsof -ti:8000 2>/dev/null)
if [ -n "$BACKEND_PROCS" ]; then
    echo "$BACKEND_PROCS" | xargs kill -9 2>/dev/null
    echo -e "  ${GREEN}✓${NC} Killed processes on port 8000"
    STOPPED=$((STOPPED + 1))
else
    echo -e "  ${YELLOW}⊘${NC} No processes on port 8000"
fi

# Kill all Node processes on port 5173
echo "Cleaning up port 5173..."
FRONTEND_PROCS=$(lsof -ti:5173 2>/dev/null)
if [ -n "$FRONTEND_PROCS" ]; then
    echo "$FRONTEND_PROCS" | xargs kill -9 2>/dev/null
    echo -e "  ${GREEN}✓${NC} Killed processes on port 5173"
    STOPPED=$((STOPPED + 1))
else
    echo -e "  ${YELLOW}⊘${NC} No processes on port 5173"
fi

# Kill any Python API server processes
echo ""
echo "Cleaning up Python API servers..."
API_PROCS=$(ps aux | grep "[a]pi_server_production.py" | awk '{print $2}')
if [ -n "$API_PROCS" ]; then
    echo "$API_PROCS" | xargs kill -9 2>/dev/null
    echo -e "  ${GREEN}✓${NC} Killed API server processes"
    STOPPED=$((STOPPED + 1))
else
    echo -e "  ${YELLOW}⊘${NC} No API server processes found"
fi

# Kill any npm dev server processes
echo "Cleaning up npm dev servers..."
NPM_PROCS=$(ps aux | grep "[n]pm run dev" | awk '{print $2}')
if [ -n "$NPM_PROCS" ]; then
    echo "$NPM_PROCS" | xargs kill -9 2>/dev/null
    echo -e "  ${GREEN}✓${NC} Killed npm dev processes"
    STOPPED=$((STOPPED + 1))
else
    echo -e "  ${YELLOW}⊘${NC} No npm dev processes found"
fi

# Kill any Vite dev servers
echo "Cleaning up Vite servers..."
VITE_PROCS=$(ps aux | grep "[v]ite" | awk '{print $2}')
if [ -n "$VITE_PROCS" ]; then
    echo "$VITE_PROCS" | xargs kill -9 2>/dev/null
    echo -e "  ${GREEN}✓${NC} Killed Vite processes"
    STOPPED=$((STOPPED + 1))
else
    echo -e "  ${YELLOW}⊘${NC} No Vite processes found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $STOPPED -gt 0 ]; then
    echo -e "${GREEN}✅ Stopped $STOPPED service(s)${NC}"
else
    echo -e "${YELLOW}No services were running${NC}"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
