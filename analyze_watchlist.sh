#!/bin/bash
# Analyze Watchlist in Batches
# Safe batch processing for low-memory systems

set -e

echo "=================================================="
echo "  Batch Watchlist Analysis (Low-Memory Mode)"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
API_URL=${API_URL:-http://localhost:3000/api}
BATCH_SIZE=${BATCH_SIZE:-2}
DELAY=${DELAY:-10}

echo "Configuration:"
echo "  API URL: $API_URL"
echo "  Batch Size: $BATCH_SIZE stocks"
echo "  Delay: $DELAY seconds between batches"
echo ""

# Get watchlist
echo "Fetching watchlist..."
WATCHLIST=$(curl -s "$API_URL/stocks/watchlist" | jq -r '.data[].symbol' 2>/dev/null)

if [ -z "$WATCHLIST" ]; then
    echo -e "${YELLOW}No stocks in watchlist${NC}"
    exit 0
fi

# Count stocks
TOTAL=$(echo "$WATCHLIST" | wc -l)
echo -e "${GREEN}Found $TOTAL stocks in watchlist${NC}"
echo ""

# Process in batches
PROCESSED=0
BATCH_NUM=0

echo "$WATCHLIST" | while IFS= read -r SYMBOL; do
    BATCH_NUM=$((BATCH_NUM + 1))
    
    echo -e "${GREEN}[$BATCH_NUM/$TOTAL] Analyzing $SYMBOL...${NC}"
    
    # Trigger analysis
    curl -s -X POST "$API_URL/stocks/analyze" \
        -H "Content-Type: application/json" \
        -d "{\"symbol\": \"$SYMBOL\", \"exchange\": \"NSE\", \"refresh\": true}" \
        > /dev/null
    
    PROCESSED=$((PROCESSED + 1))
    
    # Delay after each batch
    if [ $((PROCESSED % BATCH_SIZE)) -eq 0 ] && [ $PROCESSED -lt $TOTAL ]; then
        echo -e "${YELLOW}Batch complete. Waiting ${DELAY}s for memory cleanup...${NC}"
        sleep $DELAY
        echo ""
    fi
done

echo ""
echo "=================================================="
echo -e "${GREEN}Batch analysis complete!${NC}"
echo "  Total stocks: $TOTAL"
echo "  Processed: $PROCESSED"
echo "=================================================="
echo ""
echo "Check results in the dashboard: http://localhost"
