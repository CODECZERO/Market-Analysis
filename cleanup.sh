#!/bin/bash

# ============================================
# CLEANUP.SH - Clean Build Artifacts & Caches
# ============================================

echo "🧹 Cleaning up build artifacts and caches..."
echo ""

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Stop running servers
echo -e "${BLUE}[1/6]${NC} Stopping running servers..."
if [ -f .backend.pid ]; then
    kill $(cat .backend.pid) 2>/dev/null && echo "  ✓ Backend stopped"
    rm .backend.pid
fi

if [ -f .frontend.pid ]; then
    kill $(cat .frontend.pid) 2>/dev/null && echo "  ✓ Frontend stopped"
    rm .frontend.pid
fi
echo ""

# Python cache
echo -e "${BLUE}[2/6]${NC} Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo "  ✓ Python cache cleaned"
echo ""

# Node modules (optional)
echo -e "${BLUE}[3/6]${NC} Node modules..."
read -p "  Remove node_modules? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf frontend/node_modules
    echo "  ✓ Node modules removed"
else
    echo "  ⊘ Skipped"
fi
echo ""

# Build artifacts
echo -e "${BLUE}[4/6]${NC} Removing build artifacts..."
rm -rf frontend/dist
rm -rf frontend/build
rm -rf .next
rm -rf out
echo "  ✓ Build artifacts removed"
echo ""

# Logs
echo -e "${BLUE}[5/6]${NC} Cleaning logs..."
read -p "  Clear log files? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    > logs/backend.log
    > logs/frontend.log
    > logs/test-results.log
    echo "  ✓ Logs cleared"
else
    echo "  ⊘ Skipped"
fi
echo ""

# Database reset (optional)
echo -e "${BLUE}[6/6]${NC} Database reset..."
echo -e "  ${YELLOW}WARNING:${NC} This will delete all stored data!"
read -p "  Reset databases? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 - <<'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

# Drop MongoDB collections
mongo_url = os.getenv('MONGO_URL')
if mongo_url:
    try:
        from pymongo import MongoClient
        client = MongoClient(mongo_url)
        db = client[os.getenv('MONGO_DB_NAME', 'brand_tracker')]
        
        # Drop collections
        for collection in ['stock_analyses', 'watchlist', 'portfolio', 'alerts']:
            db[collection].drop()
        
        print("  ✓ MongoDB collections reset")
        client.close()
    except Exception as e:
        print(f"  ✗ MongoDB reset failed: {e}")

# Clear Redis
redis_url = os.getenv('REDIS_URL')
if redis_url:
    try:
        import redis
        r = redis.from_url(redis_url)
        r.flushdb()
        print("  ✓ Redis cache cleared")
        r.close()
    except Exception as e:
        print(f"  ✗ Redis clear failed: {e}")
EOF
else
    echo "  ⊘ Skipped"
fi

echo ""
echo -e "${GREEN}✅ Cleanup complete!${NC}"
echo ""
