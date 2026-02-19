#!/bin/bash
# Master Script - Run All Services
# Starts entire Market Analysis System including FastAPI server

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Track PIDs for cleanup
PIDS=()
DOCKER_STARTED=false

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}============================================${NC}"
    echo -e "${YELLOW}  Shutting down gracefully...${NC}"
    echo -e "${YELLOW}============================================${NC}"
    echo ""
    
    # Kill background processes
    if [ ${#PIDS[@]} -gt 0 ]; then
        echo -e "${BLUE}Stopping background processes...${NC}"
        for PID in "${PIDS[@]}"; do
            if ps -p $PID > /dev/null 2>&1; then
                echo "  Killing PID $PID"
                kill -TERM $PID 2>/dev/null || true
            fi
        done
        
        # Wait for processes to die
        sleep 2
        
        # Force kill if still alive
        for PID in "${PIDS[@]}"; do
            if ps -p $PID > /dev/null 2>&1; then
                echo "  Force killing PID $PID"
                kill -9 $PID 2>/dev/null || true
            fi
        done
    fi
    
    # Stop Docker containers
    if [ "$DOCKER_STARTED" = true ]; then
        echo -e "${BLUE}Stopping Docker containers...${NC}"
        docker-compose down 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✓ All services stopped${NC}"
    echo ""
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM EXIT

echo "============================================"
echo "  Market Analysis System - Master Launcher"
echo "============================================"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Step 1: Check prerequisites
echo -e "${BLUE}[1/7] Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker not found${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose not found${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites OK${NC}"
echo ""

# Step 2: Setup Virtual Environment
echo -e "${BLUE}[2/7] Setting up Python environment...${NC}"

VENV_DIR="venv"

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$VENV_DIR" || {
        echo -e "${RED}✗ Failed to create virtual environment${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate venv
source "$VENV_DIR/bin/activate" || {
    echo -e "${RED}✗ Failed to activate virtual environment${NC}"
    exit 1
}

echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Step 3: Check .env file
echo -e "${BLUE}[3/7] Checking environment config...${NC}"

if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env from .env.low_memory...${NC}"
    cp .env.low_memory .env
fi

echo -e "${GREEN}✓ Environment configured${NC}"
echo ""

# Step 4: Install Python dependencies
echo -e "${BLUE}[4/7] Installing Python dependencies...${NC}"

# Install worker dependencies
if [ -f "worker/requirements.txt" ]; then
    echo "  Installing worker dependencies..."
    pip install -q -r worker/requirements.txt 2>&1 | grep -E "ERROR|Successfully" || true
fi

# Install API dependencies
if [ -f "api_requirements.txt" ]; then
    echo "  Installing API dependencies..."
    pip install -q -r api_requirements.txt 2>&1 | grep -E "ERROR|Successfully" || true
fi

# Verify critical packages
MISSING_PACKAGES=()

if ! python -c "import fastapi" 2>/dev/null; then
    MISSING_PACKAGES+=("fastapi")
fi

if ! python -c "import pandas" 2>/dev/null; then
    MISSING_PACKAGES+=("pandas")
fi

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠ Some packages missing: ${MISSING_PACKAGES[*]}${NC}"
    echo "  Attempting to install..."
    pip install -q ${MISSING_PACKAGES[*]} || {
        echo -e "${RED}✗ Failed to install packages${NC}"
        echo "  Try manually: pip install ${MISSING_PACKAGES[*]}"
    }
fi

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 5: Create logs directory
echo -e "${BLUE}[5/7] Setting up directories...${NC}"
mkdir -p logs logs/tests
echo -e "${GREEN}✓ Directories ready${NC}"
echo ""

# Step 6: Start Docker services
echo -e "${BLUE}[6/7] Starting Docker services...${NC}"

docker-compose up -d mongodb redis 2>&1 | grep -v "Creating\|Starting" || true
DOCKER_STARTED=true

# Wait for services to be ready
echo "  Waiting for MongoDB (5s)..."
sleep 5

echo "  Waiting for Redis (2s)..."
sleep 2

echo -e "${GREEN}✓ Docker services running${NC}"
echo ""

# Step 7: Start FastAPI Server  
echo -e "${BLUE}[7/8] Starting FastAPI Server...${NC}"

python api_server.py > logs/api_server.log 2>&1 &
API_PID=$!
PIDS+=($API_PID)

# Wait a bit to see if it starts
sleep 3

if ps -p $API_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ FastAPI Server started (PID: $API_PID)${NC}"
else
    echo -e "${YELLOW}⚠ FastAPI Server may have issues (check logs/api_server.log)${NC}"
fi

echo ""

# Step 8: Start Python Worker
echo -e "${BLUE}[8/8] Starting Python Worker...${NC}"

cd worker/src
python app.py > ../../logs/worker.log 2>&1 &
WORKER_PID=$!
PIDS+=($WORKER_PID)
cd ../..

sleep 2

if ps -p $WORKER_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Worker started (PID: $WORKER_PID)${NC}"
else
    echo -e "${YELLOW}⚠ Worker may have issues (check logs/worker.log)${NC}"
fi

echo ""

# Show status
echo "============================================"
echo -e "${GREEN}  All Services Started!${NC}"
echo "============================================"
echo ""

# Docker services
echo "Docker Services:"
docker-compose ps 2>/dev/null | grep -E "mongodb|redis" || echo "  (checking...)"
echo ""

# Python services
echo "Python Services:"
if ps -p $API_PID > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} FastAPI Server: http://localhost:8000 (PID: $API_PID)"
    echo "    API Docs: http://localhost:8000/docs"
else
    echo -e "  ${RED}✗${NC} FastAPI Server: Not running"
fi

if ps -p $WORKER_PID > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} Worker: Running (PID: $WORKER_PID)"
else
    echo -e "  ${RED}✗${NC} Worker: Not running"
fi

echo ""
echo "Endpoints:"
echo "  • MongoDB: localhost:27017"
echo "  • Redis: localhost:6379"
echo "  • API: http://localhost:8000"
echo "  • API Docs: http://localhost:8000/docs"
echo ""
echo "Logs:"
echo "  • API Server: tail -f logs/api_server.log"
echo "  • Worker: tail -f logs/worker.log"
echo "  • Docker: docker-compose logs -f"
echo ""
echo "Test it:"
echo -e "  ${YELLOW}# Quick analysis:${NC}"
echo "  python examples/complete_integration_demo.py"
echo ""
echo -e "  ${YELLOW}# API test:${NC}"
echo "  curl http://localhost:8000/api/health"
echo ""
echo -e "  ${YELLOW}# Run tests:${NC}"
echo "  ./run-tests.sh"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Monitor services
while true; do
    # Check API server
    if ! ps -p $API_PID > /dev/null 2>&1; then
        echo -e "${RED}✗ API Server crashed! Check logs/api_server.log${NC}"
        
        # Restart
        echo -e "${YELLOW}Restarting API Server...${NC}"
        python api_server.py > logs/api_server.log 2>&1 &
        API_PID=$!
        PIDS+=($API_PID)
        
        sleep 2
        if ps -p $API_PID > /dev/null 2>&1; then
            echo -e "${GREEN}✓ API Server restarted (PID: $API_PID)${NC}"
        fi
    fi
    
    # Check worker
    if ! ps -p $WORKER_PID > /dev/null 2>&1; then
        echo -e "${RED}✗ Worker crashed! Check logs/worker.log${NC}"
        
        # Restart
        echo -e "${YELLOW}Restarting worker...${NC}"
        cd worker/src
        python app.py > ../../logs/worker.log 2>&1 &
        WORKER_PID=$!
        PIDS+=($WORKER_PID)
        cd ../..
        
        sleep 2
        if ps -p $WORKER_PID > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Worker restarted (PID: $WORKER_PID)${NC}"
        fi
    fi
    
    sleep 5
done

