#!/bin/bash

# Quick Setup Script for New Features
# Installs scraper dependencies and sets up API keys template

set -e

echo "🚀 Setting up new features..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")"

# Step 1: Install scraper dependencies
echo -e "${BLUE}📦 Installing scraper dependencies...${NC}"
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️  Virtual environment not found, using system Python${NC}"
fi

pip install -q beautifulsoup4 lxml requests praw

echo -e "${GREEN}✓ Scraper dependencies installed${NC}"

# Step 2: Check for API keys
echo -e "${BLUE}🔑 Checking API keys configuration...${NC}"

if [ -f ".env" ]; then
    if grep -q "GROQ_API_KEY" .env && grep -q "REDDIT_CLIENT_ID" .env; then
        echo -e "${GREEN}✓ API keys already configured${NC}"
    else
        echo -e "${YELLOW}⚠️  Some API keys missing in .env${NC}"
        echo "   Add these for full functionality:"
        echo "   - GROQ_API_KEY (get from: https://console.groq.com/keys)"
        echo "   - REDDIT_CLIENT_ID/SECRET (get from: https://www.reddit.com/prefs/apps)"
    fi
else
    echo -e "${YELLOW}⚠️  .env not found${NC}"
    echo "   Copy .env.complete to .env and add your API keys"
fi

# Step 3: Test components
echo -e "${BLUE}🧪 Testing new components...${NC}"

# Test LLM client
python3 -c "
import sys
sys.path.insert(0, 'worker/src')
from services.llm_client import get_llm_client
client = get_llm_client()
print(f'LLM Provider: {client.provider}')
" 2>/dev/null && echo -e "${GREEN}✓ LLM client working${NC}" || echo -e "${YELLOW}⚠️  LLM client needs API keys${NC}"

# Test scraper
python3 -c "
import sys
sys.path.insert(0, 'worker/src')
from scrapers.moneycontrol_scraper import MoneyControlScraper
scraper = MoneyControlScraper()
print('Scraper initialized')
" 2>/dev/null && echo -e "${GREEN}✓ News scraper working${NC}" || echo -e "${YELLOW}⚠️  Scraper needs dependencies${NC}"

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Add API keys to .env (optional but recommended)"
echo "2. Test with: python quick_analyze.py RELIANCE"
echo "3. See FRONTEND_INTEGRATION.md for frontend setup"
