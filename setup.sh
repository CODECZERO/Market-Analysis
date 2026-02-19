#!/bin/bash
# Quick Setup Script for Market Analysis System
# Automates the entire setup process

set -e  # Exit on error

echo "=================================================="
echo "  Market Analysis System - Quick Setup"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose installed${NC}"

echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp .env.example .env
    
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: You need to add your API keys to .env${NC}"
    echo ""
    echo "Please edit .env and add at least ONE of these API keys:"
    echo "  - GROQ_API_KEY (recommended - free tier available)"
    echo "  - NVIDIA_API_KEY"
    echo "  - OPENROUTER_API_KEY"
    echo ""
    read -p "Press ENTER after you've added your API key to .env..."
    
    # Validate that at least one key is set
    if ! grep -q "GROQ_API_KEY=.*[^=]" .env && \
       ! grep -q "NVIDIA_API_KEY=.*[^=]" .env && \
       ! grep -q "OPENROUTER_API_KEY=.*[^=]" .env; then
        echo -e "${RED}✗ No LLM API key found in .env${NC}"
        echo "Please add at least one API key and run this script again."
        exit 1
    fi
    echo -e "${GREEN}✓ API key configured${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo ""
echo "Building Docker images (this may take a few minutes)..."
docker-compose build

echo ""
echo "Starting all services..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check MongoDB
echo -n "Checking MongoDB... "
if docker-compose exec -T mongodb mongosh --quiet --eval "db.runCommand({ ping: 1 })" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ (may take longer to start)${NC}"
fi

# Check Redis
echo -n "Checking Redis... "
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ (may take longer to start)${NC}"
fi

# Check API Gateway
echo -n "Checking API Gateway... "
sleep 5
if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ (starting up...)${NC}"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "Access your application:"
echo "  Frontend: http://localhost"
echo "  API:      http://localhost:3000"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart:          docker-compose restart"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost in your browser"
echo "  2. Add stocks to your watchlist (e.g., RELIANCE, TCS, INFY)"
echo "  3. Click 'Analyze' to get AI-powered recommendations"
echo ""
echo "For detailed documentation, see:"
echo "  - README.md - Project overview"
echo "  - DEPLOYMENT.md - Deployment guide"
echo "  - API_SPEC.md - API documentation"
echo ""
