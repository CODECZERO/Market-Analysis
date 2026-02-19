# Integration Guide

## 🎯 How to Connect All the Pieces

This guide shows you how to integrate the completed components into a working system.

---

## ✅ What's Already Working

### Core Analysis Engine (100% Complete)
The worker can analyze stocks standalone:

```bash
cd market_analysis/worker/src
python app.py
```

This will:
- Fetch stock data for RELIANCE
- Calculate 20+ technical indicators
- Run quant strategies
- Make ML predictions
- Generate BUY/HOLD/SELL recommendation

**Try the demo:**
```bash
cd market_analysis
python examples/complete_integration_demo.py
```

---

## 🔧 Integration Tasks (To Connect Everything)

### Task 1: Worker Queue Integration (2-3 hours)

**Goal**: Make worker process jobs from Redis queue

**Steps**:

1. **Create worker daemon** (`worker/src/daemon.py`):
```python
import asyncio
from utils.redis_queue import RedisQueueManager
from app import StockAnalysisWorker

async def process_jobs():
    manager = RedisQueueManager()
    worker = StockAnalysisWorker()
    
    while True:
        # Dequeue task
        task = manager.dequeue_task('queue_market_data_fetch', timeout=5)
        
        if task:
            symbol = task['data']['symbol']
            exchange = task['data']['exchange']
            
            # Process
            result = await worker.analyze_stock(symbol, exchange)
            
            # Save result
            manager.cache_set(
                f"analysis_result:{task['id']}",
                result,
                ttl=3600
            )

if __name__ == "__main__":
    asyncio.run(process_jobs())
```

2. **Update Docker Compose** to run daemon:
```yaml
worker:
  command: python src/daemon.py  # Instead of app.py
```

---

### Task 2: API Gateway Integration (2 hours)

**Goal**: Connect API endpoints to Redis queue

The TypeScript file has syntax errors. Here's a working approach:

**Option A: Use Express.js Directly**

Create `api-gateway/src/simple-server.js`:
```javascript
const express = require('express');
const Redis = require('ioredis');
const { v4: uuidv4 } = require('uuid');

const app = express();
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

app.use(express.json());

// Trigger analysis
app.post('/api/stocks/analyze', async (req, res) => {
  const { symbol, exchange = 'NSE' } = req.body;
  
  const analysisId = uuidv4();
  
  // Enqueue job
  const task = {
    id: analysisId,
    data: { symbol, exchange, type: 'full_analysis' },
    queue: 'queue_market_data_fetch'
  };
  
  await redis.lpush('queue_market_data_fetch', JSON.stringify(task));
  
  res.json({
    success: true,
    data: { analysisId, symbol, exchange, status: 'queued' }
  });
});

// Get result
app.get('/api/stocks/analyze/:analysisId', async (req, res) => {
  const { analysisId } = req.params;
  
  const result = await redis.get(`analysis_result:${analysisId}`);
  
  if (result) {
    res.json({ success: true, data: JSON.parse(result) });
  } else {
    res.status(404).json({ success: false, error: 'Not found' });
  }
});

app.listen(3000, () => console.log('API running on port 3000'));
```

Run: `node api-gateway/src/simple-server.js`

---

### Task 3: Frontend Connection (1-2 hours)

**Goal**: Connect React frontend to API

Update `frontend/src/config.ts`:
```typescript
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000';
```

Update `StockDashboard.tsx` to call real API:
```typescript
const analyzeStock = async (symbol: string, exchange: string) => {
  const response = await fetch(`${API_BASE_URL}/api/stocks/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, exchange })
  });
  
  const data = await response.json();
  return data.data.analysisId;
};
```

---

### Task 4: LLM Integration (3-4 hours)

**Goal**: Add actual AI analysis

Update `worker/src/app.py` to call LLM:

```python
async def _run_llm_analysis(self, stock_data: Dict, technical: Dict, quant: Dict, ml: Dict) -> Dict:
    """Run 3-phase LLM analysis"""
    try:
        import os
        import requests
        
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            return {'phase1': 'No API key', 'phase2': '', 'phase3': ''}
        
        # Phase 1: What/Why
        prompt = f"""
        Analyze {stock_data['symbol']}:
        Price: ₹{stock_data['current_price']}
        RSI: {technical['rsi']:.2f}
        Trend: {'Bullish' if technical['sma_50'] > technical['sma_200'] else 'Bearish'}
        
        Explain WHAT is happening and WHY in 2-3 sentences.
        """
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={'Authorization': f'Bearer {api_key}'},
            json={
                'model': 'llama-3.1-8b-instant',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 200
            }
        )
        
        phase1 = response.json()['choices'][0]['message']['content']
        
        return {
            'phase1': phase1,
            'phase2': 'Entry analysis...',
            'phase3': 'Execution plan...'
        }
        
    except Exception as e:
        logger.warning(f"LLM analysis failed: {e}")
        return {'phase1': '', 'phase2': '', 'phase3': ''}
```

---

## 🚀 Quick Start (Minimal Working System)

### Step 1: Start Infrastructure
```bash
docker-compose up -d mongodb redis
```

### Step 2: Run Worker Daemon
```bash
cd worker/src
python daemon.py  # (Create this file per Task 1)
```

### Step 3: Run API Server
```bash
cd api-gateway/src
node simple-server.js  # (Create this file per Task 2)
```

### Step 4: Test It!
```bash
curl -X POST http://localhost:3000/api/stocks/analyze \
  -H "Content-Type:application/json" \
  -d '{"symbol": "RELIANCE", "exchange": "NSE"}'
```

Wait 30-60 seconds, then:
```bash
curl http://localhost:3000/api/stocks/analyze/<analysisId>
```

---

## 📊 Integration Checklist

- [ ] **Task 1**: Worker queue processing (daemon.py)
- [ ] **Task 2**: API Gateway endpoints (simple-server.js)
- [ ] **Task 3**: Frontend API calls
- [ ] **Task 4**: LLM integration
- [ ] **Task 5**: MongoDB persistence
- [ ] **Task 6**: WebSocket real-time updates
- [ ] **Task 7**: News/social scrapers

**Minimum to work**: Tasks 1-2 (4-5 hours)
**Full system**: All tasks (12-15 hours)

---

## 🐛 Troubleshooting

### Worker not processing jobs
```bash
# Check Redis queue
docker exec -it market_analysis_redis redis-cli
> LLEN queue_market_data_fetch
```

### API not connecting to Redis
```bash
# Test Redis connection
docker exec -it market_analysis_redis redis-cli ping
```

### MongoDB not storing data
```bash
# Check MongoDB
docker exec -it market_analysis_mongo mongosh market_analysis
> db.analysis_results.find().limit(1)
```

---

## 💡 Simpler Alternative: Python FastAPI

If TypeScript is problematic, use FastAPI for API:

```python
# api-gateway/main.py
from fastapi import FastAPI
from utils.redis_queue import enqueue_analysis, get_queue_manager

app = FastAPI()
manager = get_queue_manager()

@app.post("/api/stocks/analyze")
async def analyze(symbol: str, exchange: str = "NSE"):
    task_id = enqueue_analysis(symbol, exchange)
    return {"success": True, "analysisId": task_id}

@app.get("/api/stocks/analyze/{analysis_id}")
async def get_result(analysis_id: str):
    result = manager.cache_get(f"analysis_result:{analysis_id}")
    if result:
        return {"success": True, "data": result}
    return {"success": False, "error": "Not found"}
```

Run: `uvicorn main:app --host 0.0.0.0 --port 3000`

---

**The core engine works! Integration is just glue code.** 🎉
