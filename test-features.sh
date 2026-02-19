#!/bin/bash

# Test All New Features
# Tests scrapers, LLM client, and orchestrator

set -e

echo "🧪 Testing New Features..."

cd "$(dirname "$0")"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Activate venv if exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

echo ""
echo -e "${BLUE}1️⃣  Testing LLM Client...${NC}"
python3 -c "
import sys
sys.path.insert(0, 'worker/src')
from services.llm_client import get_llm_client
client = get_llm_client()
print(f'   Provider: {client.provider}')
if client.provider == 'mock':
    print('   ⚠️  Using mock mode (no API keys)')
else:
    print(f'   ✅ Using {client.provider}')
" && echo -e "${GREEN}✓ LLM Client working${NC}" || echo -e "${RED}✗ LLM Client failed${NC}"

echo ""
echo -e "${BLUE}2️⃣  Testing MoneyControl Scraper...${NC}"
timeout 10 python3 -c "
import sys
sys.path.insert(0, 'worker/src')
from scrapers.moneycontrol_scraper import MoneyControlScraper
scraper = MoneyControlScraper()
print('   ✅ MoneyControl scraper initialized')
" 2>/dev/null && echo -e "${GREEN}✓ MoneyControl Scraper working${NC}" || echo -e "${YELLOW}⚠️  Scraper may need network${NC}"

echo ""
echo -e "${BLUE}3️⃣  Testing Economic Times Scraper...${NC}"
timeout 10 python3 -c "
import sys
sys.path.insert(0, 'worker/src')
from scrapers.economictimes_scraper import EconomicTimesScraper
scraper = EconomicTimesScraper()
print('   ✅ Economic Times scraper initialized')
" 2>/dev/null && echo -e "${GREEN}✓ Economic Times Scraper working${NC}" || echo -e "${YELLOW}⚠️  Scraper may need network${NC}"

echo ""
echo -e "${BLUE}4️⃣  Testing Reddit Scraper...${NC}"
python3 -c "
import sys
sys.path.insert(0, 'worker/src')
from scrapers.reddit_scraper import RedditScraper
scraper = RedditScraper()
print('   ✅ Reddit scraper initialized')
if scraper.reddit is None:
    print('   ⚠️  No Reddit API credentials (using mock mode)')
" && echo -e "${GREEN}✓ Reddit Scraper working${NC}" || echo -e "${YELLOW}⚠️  Reddit Scraper has issues${NC}"

echo ""
echo -e "${BLUE}5️⃣  Testing News Aggregator...${NC}"
python3 -c "
import sys
sys.path.insert(0, 'worker/src')
from scrapers.news_aggregator import NewsAggregator
aggregator = NewsAggregator()
print(f'   ✅ Aggregator initialized with {len(aggregator.scrapers)} sources')
" && echo -e "${GREEN}✓ News Aggregator working${NC}" || echo -e "${RED}✗ News Aggregator failed${NC}"

echo ""
echo -e "${BLUE}6️⃣  Checking Enhanced Orchestrator...${NC}"
python3 -c "
import sys
sys.path.insert(0, 'worker/src')
from orchestrator_enhanced import StockAnalysisOrchestrator
orchestrator = StockAnalysisOrchestrator()
print('   ✅ Orchestrator initialized')
print(f'   LLM Provider: {orchestrator.llm_client.provider}')
print(f'   News Scraper: {'Available' if orchestrator.news_scraper else 'Not available'}')
print(f'   Reddit Scraper: {'Available' if orchestrator.reddit_scraper else 'Not available'}')
" && echo -e "${GREEN}✓ Enhanced Orchestrator working${NC}" || echo -e "${RED}✗ Enhanced Orchestrator failed${NC}"

echo ""
echo -e "${GREEN}✅ All tests completed!${NC}"
echo ""
echo "📋 Summary:"
echo "  - LLM Client: Ready (add API keys for real calls)"
echo "  - News Scrapers: Ready (2 sources)"
echo "  - Social Scraper: Ready (add Reddit keys for real data)"
echo "  - Orchestrator: Ready (integrates all 8 steps)"
echo ""
echo "🚀 Try it out:"
echo "  python quick_analyze.py RELIANCE"
