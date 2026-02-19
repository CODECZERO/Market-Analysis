# Deployment Guide - Market Analysis System

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Docker & Docker Compose installed
- At least one LLM API key (Groq/NVIDIA/OpenRouter)

### Steps

1. **Clone and navigate**:
```bash
cd market_analysis
```

2. **Create `.env` file**:
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (or NVIDIA_API_KEY)
```

3. **Start all services**:
```bash
docker-compose up -d
```

4. **Verify services**:
```bash
docker-compose ps
# All 6 services should show as "Up"
```

5. **Access the application**:
- Frontend: http://localhost
- API: http://localhost:3000
- MongoDB: localhost:27017
- Redis: localhost:6379

---

## 📦 Manual Setup (Without Docker)

### 1. Install Dependencies

**MongoDB 6.0+**:
```bash
# Ubuntu/Debian
sudo apt-get install -y mongodb-org

# macOS
brew install mongodb-community@6.0
```

**Redis 7.0+**:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis
```

**Python 3.10+**:
```bash
# Install Python dependencies
cd worker
pip install -r requirements.txt
```

**Node.js 18+**:
```bash
# API Gateway
cd api-gateway
npm install

# Aggregator
cd ../aggregator
npm install

# Frontend
cd ../frontend
npm install
```

### 2. Initialize Database

```bash
# Start MongoDB
mongod

# In another terminal, initialize collections
mongo < scripts/mongo-init.js
```

### 3. Start Services

**Terminal 1 - MongoDB**:
```bash
mongod
```

**Terminal 2 - Redis**:
```bash
redis-server
```

**Terminal 3 - Python Worker**:
```bash
cd worker
python src/app.py
```

**Terminal 4 - API Gateway**:
```bash
cd api-gateway
npm run dev
```

**Terminal 5 - Aggregator**:
```bash
cd aggregator
npm run dev
```

**Terminal 6 - Frontend**:
```bash
cd frontend
npm start
```

---

## 🔑 API Keys Setup

### Required (Choose One)

**Option 1: Groq (Recommended - Free Tier)**
```bash
# Get key from: https://console.groq.com
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
```

**Option 2: NVIDIA NIM**
```bash
# Get key from: https://build.nvidia.com
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxx
```

**Option 3: OpenRouter**
```bash
# Get key from: https://openrouter.ai
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxxxxxxx
```

### Optional (Enhanced Features)

**Finnhub (Fundamentals & Earnings)**:
```bash
# Free tier: https://finnhub.io
FINNHUB_API_KEY=your_finnhub_key
```

**Reddit (Social Sentiment)**:
```bash
# Create app: https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=MarketAnalysis/1.0
```

---

## 🧪 Testing

### 1. Test Data Providers

```bash
cd market_analysis
python demo_analysis.py
```

Expected output: Complete analysis for RELIANCE.NS with all phases.

### 2. Test API Endpoints

**Add stock to watchlist**:
```bash
curl -X POST http://localhost:3000/api/stocks/watchlist \
  -H "Content-Type: application/json" \
  -d '{"symbol": "RELIANCE", "exchange": "NSE"}'
```

**Trigger analysis**:
```bash
curl -X POST http://localhost:3000/api/stocks/analyze \
  -H "Content-Type: application/json" \
  -d '{"symbol": "RELIANCE", "exchange": "NSE"}'
```

**Get quote**:
```bash
curl http://localhost:3000/api/stocks/quotes/RELIANCE?exchange=NSE
```

### 3. Verify Database

```bash
# MongoDB
mongo market_analysis
db.watchlists.find().pretty()
db.analysis_results.find().limit(1).pretty()

# Redis
redis-cli
KEYS stock:*
```

---

##配置 Production Deployment

### Environment Variables

**Security** (CRITICAL):
```bash
# Generate secure keys
JWT_SECRET=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)
MONGO_PASSWORD=$(openssl rand -base64 16)
```

**Performance**:
```bash
NODE_ENV=production
WORKER_CONCURRENCY=8
MAX_CONCURRENT_ANALYSES=10
```

**Monitoring**:
```bash
LOG_LEVEL=info
LOG_FORMAT=json
```

### Resource Limits

Update `docker-compose.yml`:

```yaml
worker:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
      reservations:
        memory: 2G

api-gateway:
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 1G
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:80;
    }

    # API
    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## 🔧 Troubleshooting

### MongoDB Connection Failed

**Error**: `MongoServerError: Authentication failed`

**Solution**:
```bash
# Check credentials in .env
MONGODB_URI=mongodb://admin:admin123@localhost:27017/market_analysis?authSource=admin

# Verify MongoDB is running
docker-compose ps mongodb
```

### Redis Connection Refused

**Error**: `Error: connect ECONNREFUSED 127.0.0.1:6379`

**Solution**:
```bash
# Start Redis
docker-compose up -d redis

# Or manually
redis-server
```

### LLM API Errors

**Error**: `No LLM provider configured`

**Solution**:
```bash
# Ensure at least one key is set
echo $GROQ_API_KEY  # Should not be empty
```

**Error**: `HTTP 429 - Rate limit exceeded`

**Solution**: Built-in retry logic handles this. Wait 30-60 seconds.

### Worker Python Errors

**Error**: `ModuleNotFoundError: No module named 'talib'`

**Solution**:
```bash
# Install TA-Lib system library first
# Ubuntu/Debian
sudo apt-get install libta-lib0-dev

# macOS
brew install ta-lib

# Then reinstall Python package
pip install TA-Lib
```

### Frontend Build Errors

**Error**: `Module not found: Can't resolve 'lucide-react'`

**Solution**:
```bash
cd frontend
npm install lucide-react recharts
```

---

## 📊 Monitoring

### Health Checks

```bash
# API Gateway
curl http://localhost:3000/health

# MongoDB
mongo market_analysis --eval "db.stats()"

# Redis
redis-cli PING
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-gateway
docker-compose logs -f worker

# Last 100 lines
docker-compose logs --tail=100 api-gateway
```

### Performance Metrics

```bash
# MongoDB performance
mongo market_analysis --eval "db.currentOp()"

# Redis memory usage
redis-cli INFO memory

# Worker processes
docker stats market_analysis_worker
```

---

## 🧹 Cleanup

### Stop Services

```bash
# Stop all containers
docker-compose down

# Stop and remove volumes (DELETES DATA!)
docker-compose down -v
```

### Reset Database

```bash
# Drop and recreate
mongo market_analysis --eval "db.dropDatabase()"
mongo < scripts/mongo-init.js
```

### Clear Redis Cache

```bash
redis-cli FLUSHALL
```

---

## 🔄 Updates

### Update Code

```bash
git pull
docker-compose build
docker-compose up -d
```

### Update Dependencies

```bash
# Python
cd worker
pip install -r requirements.txt --upgrade

# Node.js
cd api-gateway
npm update
```

---

## 📝 Next Steps

1. **Add more stocks** to watchlist via frontend
2. **Trigger analyses** for each stock
3. **Review recommendations** in the Analysis Panel
4. **Monitor performance** with `docker stats`
5. **Set up cron jobs** for daily analysis automation

---

## 🆘 Support

- **Documentation**: See README.md and API_SPEC.md
- **Demo**: Run `python demo_analysis.py`
- **Logs**: Check `docker-compose logs`

---

**Built for Indian Stock Market (NSE/BSE) | Powered by AI**
