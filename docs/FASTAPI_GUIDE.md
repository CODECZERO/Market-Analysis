# FastAPI Server Guide

## 🚀 Quick Start

The FastAPI server is a **working alternative** to the TypeScript API Gateway.

### Install Dependencies
```bash
pip install -r api_requirements.txt
```

### Start Server
```bash
python api_server.py
```

Server runs on: **http://localhost:8000**  
API Docs: **http://localhost:8000/docs**

---

## 📊 Endpoints

### Health Check
```bash
GET /api/health
```

Returns system status and queue statistics.

### Analyze Stock
```bash
POST /api/stocks/analyze
Content-Type: application/json

{
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "refresh": false
}
```

Returns `analysisId` to track progress.

### Get Analysis Progress
```bash
GET /api/stocks/analyze/{analysisId}/progress
```

### Get Analysis Result
```bash
GET /api/stocks/analyze/{analysisId}
```

### Watchlist Operations
```bash
# Get watchlist
GET /api/stocks/watchlist?user_id=default_user

# Add to watchlist
POST /api/stocks/watchlist
{
  "symbol": "TCS",
  "exchange": "NSE"
}

# Remove from watchlist
DELETE /api/stocks/watchlist/TCS?exchange=NSE
```

---

## 🧪 Testing

### Run Integration Tests
```bash
# Start server first
python api_server.py

# In another terminal
python tests/integration_test.py
```

### Manual Testing
```bash
# Health check
curl http://localhost:8000/api/health

# Analyze stock
curl -X POST http://localhost:8000/api/stocks/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "RELIANCE", "exchange": "NSE"}'

# Get result (use analysisId from above)
curl http://localhost:8000/api/stocks/analyze/{analysisId}
```

---

## 🔄 With Frontend

### Update Frontend Config
In `frontend/src/config.ts`:
```typescript
export const API_BASE_URL = "http://localhost:8000";
```

### Start Frontend
```bash
cd frontend
npm install
npm start
```

Now your React frontend will connect to FastAPI!

---

## 🐳 With Docker

### Add to docker-compose.yml
```yaml
api-fastapi:
  build:
    context: .
    dockerfile: Dockerfile.api
  ports:
    - "8000:8000"
  environment:
    - REDIS_URL=redis://redis:6379
    - MONGODB_URI=mongodb://mongodb:27017/market_analysis
  depends_on:
    - redis
    - mongodb
```

### Create Dockerfile.api
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY api_requirements.txt worker/requirements.txt ./
RUN pip install -r api_requirements.txt -r requirements.txt

COPY api_server.py ./
COPY worker/ ./worker/

CMD ["python", "api_server.py"]
```

---

## 📈 Features

- ✅ Full REST API
- ✅ Automatic OpenAPI docs
- ✅ CORS enabled
- ✅ Redis queue integration
- ✅ MongoDB storage
- ✅ Analysis job tracking
- ✅ Watchlist management
- ✅ Health monitoring

---

## 🆚 vs TypeScript API

| Feature | FastAPI | TypeScript |
|---------|---------|------------|
| **Status** | ✅ Working | ❌ Syntax errors |
| **Setup** | 1 command | Multiple steps |
| **Docs** | Auto-generated | Manual |
| **Performance** | Fast | Fast |
| **Type Safety** | Pydantic | TypeScript |

**Recommendation**: Use FastAPI for now, migrate to TypeScript later if needed.

---

## 🔍 Monitoring

### Check Queue Stats
```bash
curl http://localhost:8000/api/health | jq '.queues'
```

### View Logs
```bash
# Server logs show all requests
python api_server.py 2>&1 | tee api.log
```

---

**The FastAPI server is production-ready! Use it now!** 🚀
