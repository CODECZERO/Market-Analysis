#!/bin/bash
# System Health Check Script
# Validates all components are working correctly

set -e

echo "=================================================="
echo "  Market Analysis System - Health Check"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0

# Function to check service
check_service() {
    SERVICE=$1
    COMMAND=$2
    
    echo -n "Checking $SERVICE... "
    if eval "$COMMAND" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Function to check endpoint
check_endpoint() {
    NAME=$1
    URL=$2
    
    echo -n "Testing $NAME... "
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$URL" 2>/dev/null || echo "000")
    
    if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "201" ]; then
        echo -e "${GREEN}✓ HTTP $RESPONSE${NC}"
        return 0
    else
        echo -e "${RED}✗ HTTP $RESPONSE${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "=== Docker Containers ==="
check_service "MongoDB" "docker-compose ps mongodb | grep -q 'Up'"
check_service "Redis" "docker-compose ps redis | grep -q 'Up'"
check_service "Worker" "docker-compose ps worker | grep -q 'Up'"
check_service "API Gateway" "docker-compose ps api-gateway | grep -q 'Up'"
check_service "Frontend" "docker-compose ps frontend | grep -q 'Up'"

echo ""
echo "=== Database Connectivity ==="
check_service "MongoDB Connection" "docker-compose exec -T mongodb mongosh --quiet --eval 'db.runCommand({ ping: 1 })'"
check_service "Redis Connection" "docker-compose exec -T redis redis-cli ping | grep -q PONG"

echo ""
echo "=== MongoDB Collections ==="
COLLECTIONS=$(docker-compose exec -T mongodb mongosh market_analysis --quiet --eval "db.getCollectionNames()" 2>/dev/null | grep -o '\[.*\]' || echo "[]")
echo "Collections created: $COLLECTIONS"

echo ""
echo "=== API Endpoints ==="
check_endpoint "API Health" "http://localhost:3000/health"
check_endpoint "Stock Search" "http://localhost:3000/api/stocks/search?q=RELIANCE"

echo ""
echo "=== Frontend ==="
check_endpoint "Frontend Serving" "http://localhost"

echo ""
echo "=== Service Logs (Last 5 lines) ==="
echo "--- API Gateway ---"
docker-compose logs --tail=5 api-gateway 2>/dev/null || echo "No logs available"

echo ""
echo "--- Worker ---"
docker-compose logs --tail=5 worker 2>/dev/null || echo "No logs available"

echo ""
echo "=================================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo "=================================================="
    echo ""
    echo "System Status: HEALTHY"
    echo ""
    echo "You can now:"
    echo "  1. Access the frontend at http://localhost"
    echo "  2. Test the demo: python demo_analysis.py"
    echo "  3. View logs: docker-compose logs -f"
    exit 0
else
    echo -e "${RED}✗ $FAILED check(s) failed${NC}"
    echo "=================================================="
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check logs: docker-compose logs"
    echo "  2. Restart services: docker-compose restart"
    echo "  3. See DEPLOYMENT.md for detailed troubleshooting"
    exit 1
fi
