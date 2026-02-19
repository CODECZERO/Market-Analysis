#!/bin/bash

# Fast Install Script - Install dependencies with progress indicators
# This shows what's being installed and skips already installed packages

set -e

echo "🚀 Fast Dependency Installation"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")"

# Activate venv if exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓ Using virtual environment${NC}"
else
    echo -e "${YELLOW}⚠️  No venv found, using system Python${NC}"
fi

# Core dependencies (fast)
echo ""
echo -e "${BLUE}1/4 Installing core dependencies...${NC}"
pip install -q numpy pandas yfinance ta-lib-bin 2>&1 | grep -E "(Installing|Requirement already)" || true
echo -e "${GREEN}✓ Core installed${NC}"

# Network dependencies (medium)
echo ""
echo -e "${BLUE}2/4 Installing network & scraping...${NC}"
pip install -q requests beautifulsoup4 lxml praw 2>&1 | grep -E "(Installing|Requirement already)" || true
echo -e "${GREEN}✓ Network installed${NC}"

# Database dependencies (fast)
echo ""
echo -e "${BLUE}3/4 Installing database clients...${NC}"
pip install -q redis pymongo 2>&1 | grep -E "(Installing|Requirement already)" || true
echo -e "${GREEN}✓ Database installed${NC}"

# ML dependencies (SLOW - this is the bottleneck!)
echo ""
echo -e "${BLUE}4/4 Installing ML libraries (this may take 2-3 minutes)...${NC}"
echo -e "${YELLOW}   ⏳ Installing TensorFlow (large package)...${NC}"
pip install tensorflow==2.15.0 2>&1 | tail -5 &
TF_PID=$!

# Show spinner while TensorFlow installs
spinner() {
    local pid=$1
    local delay=0.5
    local spinstr='|/-\'
    while ps -p $pid > /dev/null 2>&1; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

spinner $TF_PID
wait $TF_PID

echo -e "${GREEN}   ✓ TensorFlow installed${NC}"

echo -e "${YELLOW}   Installing XGBoost & scikit-learn...${NC}"
pip install -q xgboost scikit-learn 2>&1 | grep -E "(Installing|Requirement already)" || true
echo -e "${GREEN}   ✓ ML libraries installed${NC}"

# Transformers (for sentiment)
echo ""
echo -e "${BLUE}Installing transformers (sentiment analysis)...${NC}"
pip install -q transformers torch 2>&1 | tail -3
echo -e "${GREEN}✓ Transformers installed${NC}"

# API server dependencies
echo ""
echo -e "${BLUE}Installing API server dependencies...${NC}"
pip install -q fastapi uvicorn python-multipart pydantic 2>&1 | grep -E "(Installing|Requirement already)" || true
echo -e "${GREEN}✓ API server ready${NC}"

echo ""
echo -e "${GREEN}✅ All dependencies installed!${NC}"
echo ""
echo "Next: ./run-all.sh"
