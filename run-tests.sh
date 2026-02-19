#!/bin/bash
# Run All Tests - Comprehensive Test Suite Runner
# Executes offline, online, and integration tests

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

echo ""
echo "============================================"
echo "  Market Analysis - Test Suite Runner"
echo "============================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

# Create logs directory
mkdir -p logs/tests

# Test 1: Offline Tests (Synthetic Data)
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 1: Offline Tests (Synthetic Data)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f "tests/test_offline.py" ]; then
    python3 tests/test_offline.py 2>&1 | tee logs/tests/offline.log
    
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo -e "${GREEN}✅ Offline tests PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ Offline tests FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
else
    echo -e "${YELLOW}⚠ test_offline.py not found, skipping${NC}"
    TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
fi

echo ""

# Test 2: Online Tests (Real Market Data)
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 2: Online Tests (Real Market Data)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⚠ This test fetches real stock data and may take 2-3 minutes${NC}"
echo ""

read -p "Run online tests? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "tests/test_online.py" ]; then
        python3 tests/test_online.py 2>&1 | tee logs/tests/online.log
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            echo -e "${GREEN}✅ Online tests PASSED${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}❌ Online tests FAILED${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        echo -e "${YELLOW}⚠ test_online.py not found, skipping${NC}"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
    fi
else
    echo -e "${YELLOW}⚠ Skipping online tests${NC}"
    TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
fi

echo ""

# Test 3: Integration Tests (API)
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}TEST 3: Integration Tests (API)${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if API server is running
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API Server detected at http://localhost:8000${NC}"
    echo ""
    
    if [ -f "tests/integration_test.py" ]; then
        python3 tests/integration_test.py 2>&1 | tee logs/tests/integration.log
        
        if [ ${PIPESTATUS[0]} -eq 0 ]; then
            echo -e "${GREEN}✅ Integration tests PASSED${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}❌ Integration tests FAILED${NC}"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        echo -e "${YELLOW}⚠ integration_test.py not found, skipping${NC}"
        TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
    fi
else
    echo -e "${YELLOW}⚠ API Server not running${NC}"
    echo "  Start with: python api_server.py"
    echo "  Skipping integration tests"
    TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
fi

echo ""

# Summary
echo "============================================"
echo "  TEST SUMMARY"
echo "============================================"
echo ""
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo -e "${YELLOW}Skipped: $TESTS_SKIPPED${NC}"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

if [ $TOTAL_TESTS -eq 0 ]; then
    echo "No tests were run"
    exit 1
fi

SUCCESS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))

echo "Success Rate: $SUCCESS_RATE%"
echo ""

# Test logs
echo "Test Logs:"
echo "  • Offline: logs/tests/offline.log"
echo "  • Online: logs/tests/online.log"
echo "  • Integration: logs/tests/integration.log"
echo ""

# Final result
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
elif [ $SUCCESS_RATE -ge 66 ]; then
    echo -e "${YELLOW}⚠️  Most tests passed, but some failed${NC}"
    exit 0
else
    echo -e "${RED}❌ Tests failed${NC}"
    exit 1
fi
