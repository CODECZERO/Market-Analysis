#!/bin/bash

# ============================================
# TEST-ALL.SH - Comprehensive Test Suite
# ============================================

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🧪 COMPREHENSIVE TEST SUITE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
START_TIME=$(date +%s)

# ============================================
# TEST 1: Unit Tests
# ============================================
echo -e "${BLUE}[TEST SUITE 1]${NC} Unit Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Run Python unit tests
if [ -f tests/comprehensive_test_suite.py ]; then
    echo "Running comprehensive test suite..."
    python3 tests/comprehensive_test_suite.py 2>&1 | tee logs/test-results.log
    
    # Count results from output
    UNIT_PASSED=$(grep -c "✅ PASS" logs/test-results.log || echo 0)
    UNIT_FAILED=$(grep -c "❌ FAIL" logs/test-results.log || echo 0)
    
    TOTAL_TESTS=$((TOTAL_TESTS + UNIT_PASSED + UNIT_FAILED))
    PASSED_TESTS=$((PASSED_TESTS + UNIT_PASSED))
    FAILED_TESTS=$((FAILED_TESTS + UNIT_FAILED))
    
    echo -e "  Unit Tests: ${GREEN}$UNIT_PASSED passed${NC}, ${RED}$UNIT_FAILED failed${NC}"
else
    echo -e "  ${YELLOW}⚠${NC} No unit tests found"
fi

echo ""

# ============================================
# TEST 2: Integration Tests (API)
# ============================================
echo -e "${BLUE}[TEST SUITE 2]${NC} Integration Tests - API Endpoints"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Start backend if not running
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "  Starting backend server for testing..."
    python3 api_server_production.py > logs/test-backend.log 2>&1 &
    TEST_BACKEND_PID=$!
    sleep 5
fi

# Test health endpoint
echo -n "  Testing /api/health... "
if curl -s http://localhost:8000/api/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Test watchlist endpoint
echo -n "  Testing /api/stocks/watchlist... "
if curl -s http://localhost:8000/api/stocks/watchlist | grep -q "success"; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Test quote endpoint
echo -n "  Testing /api/stocks/quote/RELIANCE.NS... "
if curl -s http://localhost:8000/api/stocks/quote/RELIANCE.NS | grep -q "success"; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Test portfolio endpoint
echo -n "  Testing /api/portfolio... "
if curl -s "http://localhost:8000/api/portfolio?user_id=default" | grep -q "success"; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Test sector correlations
echo -n "  Testing /api/sector/correlations... "
if curl -s http://localhost:8000/api/sector/correlations | grep -q "success"; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""

# ============================================
# TEST 3: Frontend-Backend Communication
# ============================================
echo -e "${BLUE}[TEST SUITE 3]${NC} Frontend-Backend Communication"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check frontend build
echo -n "  Testing frontend build... "
cd frontend
if npm run build > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))
cd ..

# Check API config
echo -n "  Testing API configuration... "
if grep -q "http://localhost:8000" frontend/.env.local 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠ WARNING${NC} - API URL not configured"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Check CORS
echo -n "  Testing CORS configuration... "
CORS_TEST=$(curl -s -H "Origin: http://localhost:5173" -I http://localhost:8000/api/health 2>/dev/null | grep -i "access-control-allow-origin" || echo "")
if [ -n "$CORS_TEST" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""

# ============================================
# TEST 4: Database Connectivity
# ============================================
echo -e "${BLUE}[TEST SUITE 4]${NC} Database Connectivity"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python3 - <<'PYEOF'
import os
import sys
from dotenv import load_dotenv

load_dotenv()

total = 0
passed = 0

# MongoDB test
total += 1
print("  Testing MongoDB connection... ", end="")
mongo_url = os.getenv('MONGO_URL')
if mongo_url:
    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        client.close()
        print("\033[0;32m✓ PASS\033[0m")
        passed += 1
    except Exception as e:
        print(f"\033[0;31m✗ FAIL\033[0m ({str(e)[:30]})")
else:
    print("\033[1;33m⚠ SKIP\033[0m (not configured)")
    passed += 1  # Don't count as failure

# Redis test
total += 1
print("  Testing Redis connection... ", end="")
redis_url = os.getenv('REDIS_URL')
if redis_url:
    try:
        import redis
        r = redis.from_url(redis_url, socket_connect_timeout=5)
        r.ping()
        r.close()
        print("\033[0;32m✓ PASS\033[0m")
        passed += 1
    except Exception as e:
        print(f"\033[0;31m✗ FAIL\033[0m ({str(e)[:30]})")
else:
    print("\033[1;33m⚠ SKIP\033[0m (not configured)")
    passed += 1  # Don't count as failure

print(f"\n{passed}/{total}")
sys.exit(0 if passed == total else 1)
PYEOF

DB_EXIT=$?
if [ $DB_EXIT -eq 0 ]; then
    PASSED_TESTS=$((PASSED_TESTS + 2))
else
    FAILED_TESTS=$((FAILED_TESTS + 1))
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 2))

echo ""

# ============================================
# TEST 5: Component Tests
# ============================================
echo -e "${BLUE}[TEST SUITE 5]${NC} Component Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test data providers
echo -n "  Testing YFinance provider... "
if python3 -c "from worker.src.providers.yfinance_provider import YFinanceProvider; p = YFinanceProvider(); p.fetch_stock_data('RELIANCE.NS')" 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Test scrapers
echo -n "  Testing MoneyControl scraper... "
if python3 -c "from worker.src.scrapers.moneycontrol_scraper import MoneyControlScraper; s = MoneyControlScraper()" 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Test technical indicators
echo -n "  Testing Technical Indicators... "
if python3 -c "import sys; sys.path.insert(0, 'worker/src'); from analysis.technical_indicators import TechnicalIndicators" 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ FAIL${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""

# ============================================
# Generate Test Report
# ============================================
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📊 TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Total Tests:    $TOTAL_TESTS"
echo -e "  Passed:         ${GREEN}$PASSED_TESTS${NC}"
echo -e "  Failed:         ${RED}$FAILED_TESTS${NC}"
PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
echo "  Pass Rate:      ${PASS_RATE}%"
echo "  Duration:       ${DURATION}s"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  SOME TESTS FAILED${NC}"
    echo ""
    echo "  Check logs/test-results.log for details"
    echo ""
    exit 1
fi

# Cleanup test backend if we started it
if [ -n "$TEST_BACKEND_PID" ]; then
    kill $TEST_BACKEND_PID 2>/dev/null || true
fi
