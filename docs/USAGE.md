# Usage Guide

## 🚀 Quick Start (One Command!)

```bash
./run-all.sh
```

This single command:
- ✅ Starts MongoDB & Redis (Docker)
- ✅ Starts Python Worker
- ✅ Monitors all services
- ✅ Auto-restarts crashed processes
- ✅ Gracefully shuts down on Ctrl+C

---

## 📊 What Happens

When you run `./run-all.sh`:

```
============================================
  Market Analysis System - Master Launcher
============================================

[1/5] Checking prerequisites...
✓ Prerequisites OK

[2/5] Checking environment...
✓ Environment configured

[3/5] Starting Docker services...
  Waiting for MongoDB...
  Waiting for Redis...
✓ Docker services running

[4/5] Starting Python Worker...
✓ Worker started (PID: 12345)

[5/5] System Status

Docker Services:
  mongodb    Up    27017/tcp
  redis      Up    6379/tcp

✓ Worker: Running (PID: 12345)

============================================
  All Services Started!
============================================

Services running:
  • MongoDB: localhost:27017
  • Redis: localhost:6379
  • Worker: Running analysis engine

Logs:
  • Worker: logs/worker.log
  • Docker: docker-compose logs

Test it:
  python examples/complete_integration_demo.py

Press Ctrl+C to stop all services
```

The script then **monitors** the worker and auto-restarts if it crashes.

---

## 🛑 Stopping Everything

**Just press Ctrl+C!**

The script will:
1. Catch the signal
2. Stop Python worker (graceful SIGTERM)
3. Stop Docker containers
4. Clean up all processes
5. Exit cleanly

```
============================================
  Shutting down gracefully...
============================================

Stopping background processes...
  Killing PID 12345
Stopping Docker containers...
✓ All services stopped
```

---

## 📝 Logs

### View Worker Logs
```bash
tail -f logs/worker.log
```

### View Docker Logs
```bash
docker-compose logs -f mongodb
docker-compose logs -f redis
```

### View All Logs
```bash
# In separate terminal
tail -f logs/worker.log &
docker-compose logs -f
```

---

## 🧪 Testing

While `run-all.sh` is running, open a new terminal:

### Test 1: Run Demo Analysis
```bash
cd market_analysis
python examples/complete_integration_demo.py
```

### Test 2: Analyze Your Stocks
```bash
python examples/quick_analysis.py RELIANCE TCS INFY
```

### Test 3: Check Services
```bash
# MongoDB
docker exec -it market_analysis_mongo mongosh market_analysis

# Redis
docker exec -it market_analysis_redis redis-cli ping
```

---

## 🔧 Advanced Usage

### Run in Background
```bash
nohup ./run-all.sh > system.log 2>&1 &

# Check status
tail -f system.log

# Stop it
pkill -f run-all.sh
```

### Run Specific Services Only

**Just Docker:**
```bash
docker-compose up -d mongodb redis
```

**Just Worker:**
```bash
cd worker/src
python app.py
```

**Just Monitor:**
```bash
./monitor.sh
```

---

## 🐛 Troubleshooting

### Worker keeps crashing

Check logs:
```bash
cat logs/worker.log
```

Common issues:
- Missing dependencies: `pip install -r worker/requirements.txt`
- MongoDB not ready: Increase wait time in run-all.sh
- Redis connection failed: Check docker-compose ps

### Ports already in use

```bash
# Find what's using ports
lsof -i :27017   # MongoDB
lsof -i :6379    # Redis

# Kill or change ports in docker-compose.yml
```

### Ctrl+C doesn't stop everything

```bash
# Force stop
pkill -9 -f "python.*app.py"
docker-compose down
```

---

## 📈 What You Can Do Now

With `run-all.sh` running:

1. **Analyze stocks** using Python
2. **Monitor** services with `./monitor.sh`
3. **Benchmark** with `python tools/benchmark.py`
4. **Batch analyze** your watchlist

---

## 🎯 Next Steps

The system is now running! To add more features:

1. **Add LLM integration** - See INTEGRATION_GUIDE.md Task 4
2. **Create API endpoint** - See INTEGRATION_GUIDE.md Task 2
3. **Connect frontend** - See INTEGRATION_GUIDE.md Task 3

---

**Happy Analyzing!** 📊🚀
