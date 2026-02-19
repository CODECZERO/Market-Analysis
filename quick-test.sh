#!/bin/bash

# ============================================
# QUICK-TEST.SH - Fast Smoke Test (< 30s)
# ============================================

echo "🔥 Running quick smoke test..."
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PASSED=0
FAILED=0

# Test 1: Python imports
echo -n "1. Python imports... "
if python3 -c "import yfinance, pandas, numpy" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 2: Environment
echo -n "2. Environment file... "
if [ -f .env ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 3: Backend can start
echo -n "3. Backend imports... "
if python3 -c "import sys; sys.path.insert(0, 'worker/src'); from orchestrator_enhanced import StockAnalysisOrchestrator" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 4: Frontend dependencies
echo -n "4. Frontend setup... "
if [ -d frontend/node_modules ]; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 5: Stock data fetch
echo -n "5. Data fetching... "
if python3 -c "import yfinance as yf; ticker = yf.Ticker('RELIANCE.NS'); data = ticker.history(period='5d'); assert len(data) > 0" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗${NC}"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "Passed: $PASSED/5"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some checks failed${NC}"
    exit 1
fi
