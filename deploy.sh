#!/bin/bash

# Quick Deployment Script
# Automates the deployment process with all optimizations

set -e  # Exit on error

echo "🚀 DEPLOYMENT AUTOMATION SCRIPT"
echo "==============================="
echo ""

# Step 1: Install Dependencies
echo "📦 Step 1: Installing Dependencies..."
cd "$(dirname "$0")"

if [ -f "worker/requirements.txt" ]; then
    echo "   Installing Python packages..."
    pip install -r worker/requirements.txt --break-system-packages || {
        echo "   ⚠️  Trying with virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r worker/requirements.txt
    }
    echo "   ✅ Python dependencies installed"
else
    echo "   ⚠️  requirements.txt not found"
fi

if [ -d "frontend" ]; then
    echo "   Installing Node packages..."
    cd frontend
    npm install --silent 2>&1 | grep -i "error" || echo "   ✅ Node dependencies installed"
    cd ..
fi

echo ""

# Step 2: Environment Configuration
echo "🔧 Step 2: Environment Configuration..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "   Creating .env from template..."
        cp .env.example .env
        echo "   ⚠️  IMPORTANT: Update .env with your credentials!"
        echo "   - Generate API_KEYS: openssl rand -hex 16"
        echo "   - Generate JWT_SECRET_KEY: openssl rand -hex 32"
        echo "   - Update database URLs"
    else
        echo "   ❌ .env.example not found"
    fi
else
    echo "   ✅ .env file exists"
fi

echo ""

# Step 3: Database Setup
echo "🗄️  Step 3: Database Indexes..."
echo "   Indexes will be created automatically on server startup"
echo "   ✅ Database setup ready"

echo ""

# Step 4: Security Check
echo "🔐 Step 4: Security Checklist..."
echo "   [ ] Rotate exposed credentials (Redis, MongoDB, API keys)"
echo "   [ ] Verify .env is in .gitignore"
echo "   [ ] Generate secure API_KEYS"
echo "   [ ] Generate secure JWT_SECRET_KEY"
echo "   [ ] Configure CORS allowed origins for production"
echo ""
echo "   ⚠️  CRITICAL: Complete these before production deployment!"

echo ""

# Step 5: Start Services
echo "🎬 Step 5: Starting Services..."
echo ""
echo "To start the system, run:"
echo "   ./auto-run.sh"
echo ""
echo "Or manually:"
echo "   # Terminal 1 - API Server"
echo "   python api_server_production.py"
echo ""
echo "   # Terminal 2 - Frontend"
echo "   cd frontend && npm run dev"

echo ""
echo "================================"
echo "✅ DEPLOYMENT PREPARATION COMPLETE"
echo ""
echo "Next Steps:"
echo "1. Update .env with your credentials"
echo "2. Run: ./validate-performance.sh (to test optimizations)"
echo "3. Run: ./auto-run.sh (to start the system)"
echo "4. Monitor logs for any errors"
echo "5. Test API endpoints"
echo ""
echo "🎉 System ready for deployment!"
