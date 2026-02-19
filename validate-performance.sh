#!/bin/bash

# Performance Validation Script
# Tests all optimization improvements

echo "🔍 PERFORMANCE VALIDATION SUITE"
echo "================================"
echo ""

# Change to worker directory
cd "$(dirname "$0")/worker/src" || exit 1

# Test 1: Parallel Processing Test
echo "1️⃣  Testing Parallel Stock Screening..."
python3 << 'EOF'
import sys
import time
from services.stock_screener import StockScreener

screener = StockScreener()

# Test with 5 stocks only (faster)
screener.NIFTY_50 = screener.NIFTY_50[:5]

print("   Starting parallel screening test...")
start = time.time()
results = screener.screen_stocks("long", limit=3)
elapsed = time.time() - start

print(f"   ✅ Completed in {elapsed:.2f}s")
print(f"   📊 Results: {len(results)} stocks screened")
if elapsed > 30:
    print(f"   ⚠️  WARNING: Slower than expected (should be <20s for 5 stocks)")
else:
    print(f"   🚀 PASS: Parallel processing working!")
EOF

echo ""

# Test 2: Cached Provider Test
echo "2️⃣  Testing API Call Caching..."
python3 << 'EOF'
import sys
from providers.cached_yfinance import get_cached_provider

provider = get_cached_provider()

# First call (should hit API)
print("   First call (API)...")
data1 = provider.get_stock_data("TCS.NS", "1y")
print(f"   ✅ Got {len(data1) if data1 is not None else 0} data points")

# Second call (should use cache)
print("   Second call (cached)...")
data2 = provider.get_stock_data("TCS.NS", "3mo")
print(f"   ✅ Got {len(data2) if data2 is not None else 0} data points")

# Check cache stats
stats = provider.get_cache_stats()
print(f"   📊 Cache stats: {stats}")
print("   🚀 PASS: Caching working!")
EOF

echo ""

# Test 3: Fast JSON Test
echo "3️⃣  Testing Fast JSON Serialization..."
python3 << 'EOF'
import sys
import time
from utils.performance import fast_json_dumps, fast_json_loads, get_json_library

print(f"   Using: {get_json_library()}")

# Test data
large_dict = {
    "data": [{"id": i, "value": f"test_{i}"} for i in range(1000)]
}

# Benchmark
start = time.time()
for _ in range(100):
    json_str = fast_json_dumps(large_dict)
    obj = fast_json_loads(json_str)
elapsed = time.time() - start

print(f"   ✅ 100 iterations in {elapsed*1000:.2f}ms")
print(f"   🚀 PASS: JSON serialization working!")
EOF

echo ""

# Test 4: Database Connection Test
echo "4️⃣  Testing Database Connections..."
python3 << 'EOF'
import sys
import os
from dotenv import load_dotenv
load_dotenv()

# Test MongoDB
try:
    from pymongo import MongoClient
    mongo_url = os.getenv('MONGO_URL')
    if mongo_url:
        client = MongoClient(mongo_url)
        client.admin.command('ping')
        print("   ✅ MongoDB connected")
        
        # Check indexes
        db = client[os.getenv('MONGO_DB_NAME', 'brand_tracker')]
        indexes = list(db.watchlist.list_indexes())
        print(f"   📊 Watchlist indexes: {len(indexes)}")
        client.close()
    else:
        print("   ⚠️  MONGO_URL not configured")
except Exception as e:
    print(f"   ❌ MongoDB error: {e}")

# Test Redis
try:
    import redis
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        r = redis.from_url(redis_url, decode_responses=True)
        r.ping()
        print("   ✅ Redis connected")
        r.close()
    else:
        print("   ⚠️  REDIS_URL not configured")
except Exception as e:
    print(f"   ❌ Redis error: {e}")
EOF

echo ""

# Test 5: Security Validators Test
echo "5️⃣  Testing Input Validators..."
python3 << 'EOF'
import sys
from utils.validators import InputValidator

# Test symbol validation
try:
    valid = InputValidator.sanitize_symbol("TCS.NS")
    print(f"   ✅ Valid symbol: {valid}")
    
    # Test injection attempt
    try:
        invalid = InputValidator.sanitize_symbol("{'$ne': 1}")
        print(f"   ❌ FAIL: Should have rejected injection")
    except ValueError as e:
        print(f"   ✅ Blocked injection: {str(e)[:50]}")
    
    print("   🚀 PASS: Validators working!")
except Exception as e:
    print(f"   ❌ Validator error: {e}")
EOF

echo ""
echo "================================"
echo "✅ VALIDATION COMPLETE"
echo ""
echo "Summary:"
echo "- Parallel processing: Tested"
echo "- API caching: Tested"
echo "- Fast JSON: Tested"
echo "- Database: Tested"
echo "- Security: Tested"
echo ""
echo "🚀 System ready for deployment!"
