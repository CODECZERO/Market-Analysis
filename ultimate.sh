#!/bin/bash
# 🚀 LAUNCH NEW API-POWERED CLI
# This is the NEW version that uses the backend API

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 ULTIMATE CLI - API-POWERED VERSION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if backend is running
echo "Checking backend status..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ Backend API is running"
    
    # Show backend status
    echo ""
    echo "Backend Components:"
    curl -s http://localhost:8000/api/health | python3 -c "import sys, json; data=json.load(sys.stdin); print('  Version:', data['version']); [print(f'  {k}: {'✅' if v else '❌'}') for k,v in data['components'].items()]"
    echo ""
else
    echo "⚠️  Backend not running. Starting it now..."
    echo ""
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Start backend
    ./venv/bin/python api_server_production.py > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "   Backend started (PID: $BACKEND_PID)"
    echo "   Waiting for startup..."
    
    # Wait for backend
    for i in {1..10}; do
        sleep 1
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            echo "   ✅ Backend ready!"
            break
        fi
        echo -n "."
    done
    echo ""
fi

# 🆕 Check & Start Aggregator Service (Port 4001)
echo "Checking Aggregator Service..."
if curl -s http://localhost:4001/health > /dev/null 2>&1; then
    echo "✅ Aggregator Service is running (Port 4001)"
else
    echo "⚠️  Aggregator not running. Starting it now..."
    echo ""
    
    # Start aggregator (Node.js) - Use 'npm run dev' to avoid build reqs
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    if [ -d "$SCRIPT_DIR/../aggregator" ]; then
        cd "$SCRIPT_DIR/../aggregator" && npm run dev > "$SCRIPT_DIR/logs/aggregator.log" 2>&1 &
        AGG_PID=$!
        cd "$SCRIPT_DIR"
    elif [ -d "$SCRIPT_DIR/aggregator" ]; then
        cd "$SCRIPT_DIR/aggregator" && npm run dev > "$SCRIPT_DIR/logs/aggregator.log" 2>&1 &
        AGG_PID=$!
        cd "$SCRIPT_DIR"
    fi
    
    echo "   Aggregator started (PID: $AGG_PID)"
    echo "   Waiting for startup..."
    
    # Wait for aggregator
    for i in {1..20}; do
        sleep 1
        if curl -s http://localhost:4001/health > /dev/null 2>&1; then
            echo "   ✅ Aggregator ready!"
            break
        fi
        echo -n "."
    done
    echo ""
fi

echo ""
echo "Launching API-Powered CLI..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Prompt for Stock Symbol (User Wish)
echo ""
echo "👉 ENTER STOCK SYMBOL (e.g., TATASTEEL.NS)"
echo "   OR Press [ENTER] to view Top 10 Stocks Menu"
read -t 15 -p "Selection: " USER_SYMBOL

echo ""
echo "Launching API-Powered CLI..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -z "$USER_SYMBOL" ]; then
    # Interactive Menu Mode (No args)
    ./venv/bin/python ultimate_cli.py
else
    # Direct Launch Mode
    ./venv/bin/python ultimate_cli.py "$USER_SYMBOL"
fi

# Cleanup message
echo ""
echo "✅ CLI closed"
