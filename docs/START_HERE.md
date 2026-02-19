# 🚀 START HERE

## One-Command Startup

```bash
./run-all.sh
```

Press **Ctrl+C** to stop everything.

---

## What Just Happened?

The script:
1. ✅ Checked dependencies
2. ✅ Started MongoDB + Redis (Docker)
3. ✅ Started Python Worker
4. ✅ Began monitoring services

---

## Test It

```bash
# In a new terminal
python examples/complete_integration_demo.py
```

You'll see:
- Stock data fetched
- Technical indicators calculated
- ML predictions made
- Final recommendation: BUY/HOLD/SELL

---

## What This System Does

**Input:** Stock symbol (e.g., RELIANCE, TCS)

**Process:**
1. Fetch OHLCV data (YFinance)
2. Calculate 20+ technical indicators
3. Run 6 quantitative strategies
4. Generate ML predictions (LSTM)
5. Fuse all signals → Recommendation

**Output:**
- Rating: BUY/HOLD/SELL
- Confidence: 0-100%
- Entry price, Stop loss, Targets

---

## Quick Commands

```bash
# Start everything
./run-all.sh

# Test dependencies
./test-system.sh

# Run demo analysis
python examples/complete_integration_demo.py

# Monitor services
./monitor.sh

# View logs
tail -f logs/worker.log
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| **run-all.sh** | Start everything |
| **USAGE.md** | Detailed usage guide |
| **WHAT_WORKS_NOW.md** | What you can use today |
| **INTEGRATION_GUIDE.md** | How to connect pieces |
| **STATUS_REPORT.md** | Honest completion (70%) |
| **OPTIMIZATION.md** | RTX 2050 tuning |

---

## 🎯 Current Status: 70% Complete

### ✅ Working:
- Core analysis engine
- All algorithms (20+ indicators, 6 quant strategies)
- ML predictions (LSTM)
- RTX 2050 optimization
- Docker infrastructure
- **Standalone usage (works today!)**

### ⚠️ Needs Integration:
- API Gateway ↔ Worker
- Frontend ↔ Backend
- LLM API calls
- News/social scrapers

---

## 💡 What You Can Do Now

### Option 1: Use as Python Library

```python
import asyncio
import sys
sys.path.append('worker/src')

from app import StockAnalysisWorker

async def analyze():
    worker = StockAnalysisWorker()
    result = await worker.analyze_stock("RELIANCE", "NSE")
    
    rec = result['recommendation']
    print(f"{rec['rating']}: ₹{rec['entry_price']:,.2f}")

asyncio.run(analyze())
```

### Option 2: Batch Analyze Watchlist

```python
my_stocks = ["RELIANCE", "TCS", "INFY", "HDFCBANK"]

for symbol in my_stocks:
    result = await worker.analyze_stock(symbol, "NSE")
    print(f"{symbol}: {result['recommendation']['rating']}")
```

### Option 3: Build Web App

Follow **INTEGRATION_GUIDE.md** for step-by-step tasks (8-12 hours total).

---

## 🐛 Troubleshooting

### "Worker crashed"
```bash
cat logs/worker.log
```

Missing dependencies? 
```bash
pip install -r worker/requirements.txt
```

### "Port already in use"
```bash
docker-compose down
lsof -i :27017   # MongoDB
lsof -i :6379    # Redis
```

### "Ctrl+C doesn't work"
```bash
pkill -9 -f "python.*app.py"
docker-compose down
```

---

## 📚 Next Steps

1. **Try the demo:** `python examples/complete_integration_demo.py`
2. **Analyze your stocks:** Edit and run examples
3. **Read INTEGRATION_GUIDE.md:** Connect all pieces
4. **Add LLM:** Implement AI analysis (Task 4)

---

**Questions? Check:**
- USAGE.md - How to use run-all.sh
- WHAT_WORKS_NOW.md - Current features
- INTEGRATION_GUIDE.md - Complete the system
- STATUS_REPORT.md - Realistic assessment

---

**The core engine works! Start analyzing stocks now!** 📊🚀
