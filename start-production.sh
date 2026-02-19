#!/bin/bash

# Production Deployment Script
# Starts all services with production configurations

set -e

echo "🚀 Starting Market Analysis System (Production Mode)"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")"

# Check .env
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "   Please copy .env.example to .env and configure it"
    exit 1
fi

# Load environment
set -a
source .env
set +a

echo -e "${BLUE}1/6 Checking database connections...${NC}"

# Test MongoDB
if [ -n "$MONGO_URL" ]; then
    echo "   Testing MongoDB connection..."
    python3 -c "
from pymongo import MongoClient
import sys
try:
    client = MongoClient('$MONGO_URL', serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print('   ✅ MongoDB connected')
except Exception as e:
    print(f'   ⚠️  MongoDB connection failed: {e}')
    sys.exit(1)
" || exit 1
else
    echo "   ⚠️  MONGO_URL not set in .env"
fi

# Test Redis
if [ -n "$REDIS_URL" ]; then
    echo "   Testing Redis connection..."
    python3 -c "
import redis
import sys
try:
    r = redis.from_url('$REDIS_URL')
    r.ping()
    print('   ✅ Redis connected')
except Exception as e:
    print(f'   ⚠️  Redis connection failed: {e}')
    sys.exit(1)
" || exit 1
else
    echo "   ⚠️  REDIS_URL not set in .env"
fi

echo ""
echo -e "${BLUE}2/6 Checking API keys...${NC}"

if [ -n "$NVIDIA_API_KEY" ]; then
    echo "   ✅ NVIDIA API key configured"
elif [ -n "$GROQ_API_KEY" ]; then
    echo "   ✅ Groq API key configured"
else
    echo "   ⚠️  No LLM API keys configured (will use mock responses)"
fi

echo ""
echo -e "${BLUE}3/6 Setting up Python environment...${NC}"

if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "   ✅ Virtual environment activated"

echo ""
echo -e "${BLUE}4/6 Installing dependencies...${NC}"

pip install -q -r worker/requirements.txt 2>&1 | tail -5
echo "   ✅ Dependencies installed"

echo ""
echo -e "${BLUE}5/6 Starting API server (production)...${NC}"

# Kill any existing server
pkill -f "api_server_production.py" 2>/dev/null || true

# Start production server
python3 api_server_production.py > api_server.log 2>&1 &
API_PID=$!

echo "   ✅ API server started (PID: $API_PID)"
echo "   📋 Logs: tail -f api_server.log"

# Wait for server to be ready
sleep 3

# Health check
echo ""
echo -e "${BLUE}6/6 Health check...${NC}"

for i in {1..10}; do
    if curl -s http://localhost:${API_PORT:-8000}/api/health > /dev/null 2>&1; then
        echo "   ✅ API server healthy"
        break
    fi
    sleep 1
done

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   System Started Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📡 API Server: http://localhost:${API_PORT:-8000}"
echo "📊 Health: http://localhost:${API_PORT:-8000}/api/health"
echo "📖 Docs: http://localhost:${API_PORT:-8000}/docs"
echo ""
echo "🧪 Test analysis:"
echo "   curl -X POST http://localhost:${API_PORT:-8000}/api/stocks/analyze \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"symbol\":\"RELIANCE.NS\"}'"
echo ""
echo "📋 View logs: tail -f api_server.log"
echo "🛑 Stop server: kill $API_PID"
echo ""
