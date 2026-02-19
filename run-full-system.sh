#!/bin/bash

# Start Both Services for Maximum Coverage
# Runs aggregator AND market analysis together

echo "🚀 Starting Full System with All Data Sources..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Start aggregator in background
echo -e "${BLUE}1️⃣  Starting Aggregator Service (9 platforms)...${NC}"
cd "$PROJECT_ROOT/aggregator"

if [ ! -d "node_modules" ]; then
    echo "   Installing aggregator dependencies..."
    npm install
fi

# Start aggregator in background
npm start > /tmp/aggregator.log 2>&1 &
AGGREGATOR_PID=$!

echo -e "${GREEN}   ✅ Aggregator started (PID: $AGGREGATOR_PID)${NC}"
echo "   📋 Logs: tail -f /tmp/aggregator.log"
echo ""

# Wait for aggregator to be ready
echo "   ⏳ Waiting for aggregator to start..."
for i in {1..30}; do
    if curl -s http://localhost:4001/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ Aggregator ready!${NC}"
        break
    fi
    sleep 1
done

echo ""

# Start market analysis
echo -e "${BLUE}2️⃣  Starting Market Analysis System...${NC}"
cd "$SCRIPT_DIR"

./run-all.sh &
MARKET_PID=$!

echo ""
echo -e "${GREEN}✅ Both services started!${NC}"
echo ""
echo "="*70
echo "  Services Running:"
echo "="*70
echo "  🔹 Aggregator:      http://localhost:4001  (PID: $AGGREGATOR_PID)"
echo "  🔹 Market Analysis: http://localhost:8000  (PID: $MARKET_PID)"
echo ""
echo "  📊 Data Sources: 9 platforms via aggregator + 4 direct scrapers"
echo ""
echo "  Try: python quick_analyze.py RELIANCE"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "="*70

# Trap Ctrl+C to cleanup
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $AGGREGATOR_PID 2>/dev/null
    kill $MARKET_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

trap cleanup INT TERM

# Wait for both processes
wait
