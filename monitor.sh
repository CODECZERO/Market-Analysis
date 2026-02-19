#!/bin/bash

# ============================================
# MONITOR.SH - System Monitoring Dashboard
# ============================================

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📊 MARKET ANALYSIS SYSTEM - MONITORING DASHBOARD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Backend
echo -e "${BLUE}[BACKEND]${NC}"
if ps -p $(cat .backend.pid 2>/dev/null) > /dev/null 2>&1; then
    PID=$(cat .backend.pid)
    echo -e "  Status:  ${GREEN}● RUNNING${NC} (PID: $PID)"
    
    # Check health
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        HEALTH=$(curl -s http://localhost:8000/api/health)
        echo "  Health:  ${GREEN}✓ Healthy${NC}"
        echo "  URL:     http://localhost:8000"
    else
        echo -e "  Health:  ${RED}✗ Not responding${NC}"
    fi
else
    echo -e "  Status:  ${RED}● STOPPED${NC}"
fi
echo ""

# Check Frontend
echo -e "${BLUE}[FRONTEND]${NC}"
if ps -p $(cat .frontend.pid 2>/dev/null) > /dev/null 2>&1; then
    PID=$(cat .frontend.pid)
    echo -e "  Status:  ${GREEN}● RUNNING${NC} (PID: $PID)"
    
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo "  Health:  ${GREEN}✓ Accessible${NC}"
        echo "  URL:     http://localhost:5173"
    else
        echo -e "  Health:  ${YELLOW}⚠ Starting...${NC}"
    fi
else
    echo -e "  Status:  ${RED}● STOPPED${NC}"
fi
echo ""

# Database Status
echo -e "${BLUE}[DATABASES]${NC}"
python3 - <<'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB
mongo_url = os.getenv('MONGO_URL')
if mongo_url:
    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        print("  MongoDB:   \033[0;32m● CONNECTED\033[0m")
        client.close()
    except:
        print("  MongoDB:   \033[0;31m● DISCONNECTED\033[0m")
else:
    print("  MongoDB:   \033[1;33m● NOT CONFIGURED\033[0m")

# Redis
redis_url = os.getenv('REDIS_URL')
if redis_url:
    try:
        import redis
        r = redis.from_url(redis_url, socket_connect_timeout=3)
        r.ping()
        print("  Redis:     \033[0;32m● CONNECTED\033[0m")
        r.close()
    except:
        print("  Redis:     \033[0;31m● DISCONNECTED\033[0m")
else:
    print("  Redis:     \033[1;33m● NOT CONFIGURED\033[0m")
EOF
echo ""

# Resource Usage
echo -e "${BLUE}[RESOURCES]${NC}"
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        CPU=$(ps -p $BACKEND_PID -o %cpu= | tr -d ' ')
        MEM=$(ps -p $BACKEND_PID -o %mem= | tr -d ' ')
        echo "  Backend:   CPU ${CPU}% | MEM ${MEM}%"
    fi
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        CPU=$(ps -p $FRONTEND_PID -o %cpu= | tr -d ' ')
        MEM=$(ps -p $FRONTEND_PID -o %mem= | tr -d ' ')
        echo "  Frontend:  CPU ${CPU}% | MEM ${MEM}%"
    fi
fi
echo ""

# Recent Logs
echo -e "${BLUE}[RECENT LOGS]${NC}"
echo "  Backend (last 5 lines):"
if [ -f logs/backend.log ]; then
    tail -5 logs/backend.log | sed 's/^/    /'
else
    echo "    No logs found"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Commands:"
echo "    View backend logs:  tail -f logs/backend.log"
echo "    View frontend logs: tail -f logs/frontend.log"
echo "    Run tests:          ./test-all.sh"
echo "    Stop all:           kill \$(cat .backend.pid .frontend.pid)"
echo ""
