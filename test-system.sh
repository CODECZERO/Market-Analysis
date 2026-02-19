#!/bin/bash
# Quick Test - Verify system is working without starting services

echo "============================================"
echo "  Market Analysis - Quick Test"
echo "============================================"
echo ""

# Test Python dependencies
echo "[1/3] Testing Python dependencies..."
cd worker
python3 -c "
import sys
try:
    import pandas
    import numpy
    import yfinance
    print('✓ Core dependencies OK')
except ImportError as e:
    print(f'✗ Missing dependency: {e}')
    sys.exit(1)
" 2>/dev/null
cd ..
echo ""

# Test worker can import
echo "[2/3] Testing worker modules..."
cd worker/src
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from technical_indicators import TechnicalIndicators
    from decision_engine import DecisionEngine
    print('✓ Worker modules OK')
except Exception as e:
    print(f'✗ Import failed: {e}')
    sys.exit(1)
" 2>/dev/null
cd ../..
echo ""

# Test Docker
echo "[3/3] Testing Docker..."
if docker ps > /dev/null 2>&1; then
    echo "✓ Docker is running"
else
    echo "✗ Docker is not running"
    echo "  Start with: sudo systemctl start docker"
fi
echo ""

echo "============================================"
echo "  Test Complete!"
echo "============================================"
echo ""
echo "Ready to run:"
echo "  ./run-all.sh"
echo ""
