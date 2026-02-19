# Quick Reference - All Commands

## 🚀 Starting Services

### Start Everything (Recommended)
```bash
./run-all.sh
```

This starts:
- MongoDB & Redis (Docker)
- FastAPI Server (http://localhost:8000)
- Python Worker (analysis engine)
- Auto-monitoring & restart

**Stop:** Press `Ctrl+C`

---

## 🧪 Running Tests

### Run All Tests
```bash
./run-tests.sh
```

Interactive - asks before running online tests.

### Run Specific Tests
```bash
# Offline (fast, synthetic data)
python tests/test_offline.py

# Online (slow, real NSE data)
python tests/test_online.py

# Integration (needs API running)
python tests/integration_test.py
```

---

## 📊 Analyzing Stocks

### Quick Analysis (Single Stock)
```bash
python examples/complete_integration_demo.py
```

### Your Watchlist
```bash
# Edit WATCHLIST in analyze_my_stocks.py first
python analyze_my_stocks.py
```

### Via API
```bash
# Start server
python api_server.py

# Trigger analysis
curl -X POST http://localhost:8000/api/stocks/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "RELIANCE", "exchange": "NSE"}'
```

---

## 🔧 Utilities

### Health Check
```bash
./health-check.sh
```

### Monitor Services
```bash
./monitor.sh
```

### View Logs
```bash
# Worker
tail -f logs/worker.log

# API Server
tail -f logs/api_server.log

# Docker
docker-compose logs -f mongodb
docker-compose logs -f redis
```

---

## 🛠️ Installation

### First Time Setup
```bash
# Install worker dependencies
pip install -r worker/requirements.txt

# Install API dependencies
pip install -r api_requirements.txt

# Start Docker
sudo systemctl start docker

# Run setup
./setup.sh
```

---

## 📁 Project Files

```
market_analysis/
├── run-all.sh ⭐           # Start everything
├── run-tests.sh ⭐         # Run all tests
├── api_server.py ⭐        # FastAPI server
├── analyze_my_stocks.py   # Watchlist analyzer
│
├── worker/                # Analysis engine
│   └── src/
│       ├── app.py                    # Main orchestrator
│       ├── technical_indicators.py   # 20+ indicators
│       ├── decision_engine.py        # Signal fusion
│       └── ml/                       # ML models
│
├── tests/                 # Test suites
│   ├── test_offline.py   # Synthetic data tests
│   ├── test_online.py    # Real market tests
│   └── integration_test.py
│
└── examples/
    └── complete_integration_demo.py
```

---

## 🎯 Common Workflows

### Workflow 1: Test System
```bash
# 1. Run offline tests (fast)
python tests/test_offline.py

# 2. Start services
./run-all.sh

# 3. Run integration tests (new terminal)
python tests/integration_test.py
```

### Workflow 2: Analyze Stocks
```bash
# 1. Start services
./run-all.sh

# 2. Analyze (new terminal)
python examples/complete_integration_demo.py
```

### Workflow 3: Development
```bash
# 1. Start services
./run-all.sh

# 2. Make code changes
# ...

# 3. Run tests
./run-tests.sh

# 4. Check logs
tail -f logs/*.log
```

---

## 🐛 Troubleshooting

### "Port already in use"
```bash
# Kill existing processes
pkill -f "python.*api_server"
pkill -f "python.*app.py"

# Or use different ports in .env
```

### "Docker not running"
```bash
sudo systemctl start docker
```

### "Module not found"
```bash
pip install -r worker/requirements.txt
pip install -r api_requirements.txt
```

### "Tests failing"
```bash
# Check logs
cat logs/tests/*.log

# Verify data fetch
python -c "import yfinance; print(yfinance.download('RELIANCE.NS', period='1d'))"
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| START_HERE.md | Main entry point |
| USAGE.md | run-all.sh guide |
| TESTING_GUIDE.md | Test documentation |
| FASTAPI_GUIDE.md | API usage |
| INTEGRATION_GUIDE.md | Connect components |
| WHAT_WORKS_NOW.md | Current features |
| DATABASE_SCHEMA.md | DB structure |

---

## ⚡ Quick Commands

```bash
# Everything in one go
./run-all.sh

# Tests
./run-tests.sh

# Quick analysis
python examples/complete_integration_demo.py

# API docs
# Open: http://localhost:8000/docs

# Health check
curl http://localhost:8000/api/health

# Stop everything
# Press Ctrl+C on run-all.sh terminal
```

---

**Start here:** `./run-all.sh` 🚀
