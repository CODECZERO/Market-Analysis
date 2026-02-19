# Database Schema Documentation

## MongoDB Collections

### 1. `watchlists`
Stores user stock watchlists

**Schema:**
```javascript
{
  _id: ObjectId,
  userId: String,          // User identifier
  symbol: String,          // Stock symbol (e.g., "RELIANCE")
  exchange: String,        // Exchange (NSE/BSE)
  addedAt: ISODate,        // When added
  lastAnalyzedAt: ISODate  // Last analysis timestamp
}
```

**Indexes:**
- `{userId: 1, symbol: 1, exchange: 1}` (unique)
- `{userId: 1}`

**Example:**
```javascript
{
  userId: "user123",
  symbol: "RELIANCE",
  exchange: "NSE",
  addedAt: ISODate("2026-01-31T10:00:00Z"),
  lastAnalyzedAt: ISODate("2026-01-31T14:30:00Z")
}
```

---

### 2. `analysis_results`
Stores completed analysis results

**Schema:**
```javascript
{
  _id: ObjectId,
  analysisId: String,      // Unique analysis ID
  symbol: String,
  exchange: String,
  timestamp: ISODate,
  result: {
    // Complete analysis result
    symbol: String,
    current_price: Number,
    technical: Object,     // Technical indicators
    quant_signals: Object, // Quant strategy signals
    ml_predictions: Object,// ML model predictions
    sentiment: Object,     // Sentiment analysis
    correlations: Object,  // Correlation data
    recommendation: {
      rating: String,      // BUY/HOLD/SELL
      confidence: Number,  // 0-1
      entry_price: Number,
      stop_loss: Number,
      target_1: Number,
      target_2: Number
    }
  }
}
```

**Indexes:**
- `{analysisId: 1}` (unique)
- `{symbol: 1, timestamp: -1}`

**Example:**
```javascript
{
  analysisId: "abc123",
  symbol: "RELIANCE",
  exchange: "NSE",
  timestamp: ISODate("2026-01-31T14:30:00Z"),
  result: {
    symbol: "RELIANCE",
    current_price: 2456.75,
    technical: {
      rsi: 65.23,
      macd: 12.45,
      sma_50: 2420.30
    },
    recommendation: {
      rating: "BUY",
      confidence: 0.72,
      entry_price: 2445.00,
      stop_loss: 2380.00,
      target_1: 2545.00,
      target_2: 2620.00
    }
  }
}
```

---

### 3. `user_portfolios`
User portfolio tracking

**Schema:**
```javascript
{
  _id: ObjectId,
  userId: String,
  stocks: [{
    symbol: String,
    exchange: String,
    quantity: Number,
    buyPrice: Number,
    buyDate: ISODate
  }],
  totalValue: Number,
  lastUpdated: ISODate
}
```

**Indexes:**
- `{userId: 1}` (unique)

---

### 4-6. TimeSeries Collections (Planned)

#### `stock_prices_daily`
Daily OHLCV data

```javascript
{
  symbol: String,
  exchange: String,
  timestamp: ISODate,
  open: Number,
  high: Number,
  low: Number,
  close: Number,
  volume: Number
}
```

#### `technical_indicators_daily`
Pre-computed technical indicators

```javascript
{
  symbol: String,
  exchange: String,
  timestamp: ISODate,
  rsi: Number,
  macd: Number,
  bb_upper: Number,
  bb_lower: Number,
  // ... other indicators
}
```

#### `sentiment_timeline`
Sentiment scores over time

```javascript
{
  symbol: String,
  timestamp: ISODate,
  news_sentiment: Number,
  social_sentiment: Number,
  overall_score: Number,
  sources_count: Number
}
```

---

## Redis Data Structures

### Queues (Lists)

All queues store JSON task envelopes:
```javascript
{
  id: "task_123",
  data: {
    symbol: "RELIANCE",
    exchange: "NSE",
    type: "full_analysis"
  },
  queue: "queue_market_data_fetch",
  priority: "medium",
  timeout: 180
}
```

**Queue Names:**
1. `queue_market_data_fetch` - Data fetching jobs
2. `queue_sentiment_scrape` - Sentiment scraping
3. `queue_llm_phase1_what_why` - LLM Phase 1
4. `queue_technical_indicators` - Technical analysis
5. `queue_quant_strategies` - Quant computations
6. `queue_llm_phase2_when_where` - LLM Phase 2
7. `queue_ml_prediction` - ML inference
8. `queue_llm_phase3_how` - LLM Phase 3
9. `queue_report_generation` - Final report

---

### Cache Keys (Strings)

#### Analysis Results
- **Key:** `analysis_result:{analysisId}`
- **TTL:** 3600s (1 hour)
- **Value:** JSON analysis result

#### Analysis Progress
- **Key:** `analysis_progress:{analysisId}`
- **TTL:** 3600s
- **Value:** JSON progress object
```javascript
{
  analysisId: "abc123",
  symbol: "RELIANCE",
  status: "processing",  // queued/processing/completed/failed
  progress: 45,          // 0-100
  currentStep: "Running ML predictions"
}
```

#### Stock Quote Cache
- **Key:** `stock_quote:{exchange}:{symbol}`
- **TTL:** 300s (5 minutes)
- **Value:** JSON quote data

---

## Data Flow

```
1. API Request
   ↓
2. Redis Queue (enqueue job)
   ↓
3. Worker (dequeue job)
   ↓
4. Analysis Pipeline
   ├─ Fetch Data
   ├─ Technical Analysis
   ├─ Quant Strategies
   ├─ ML Predictions
   └─ Decision Fusion
   ↓
5. Result Storage
   ├─ Redis Cache (1 hour)
   └─ MongoDB (permanent)
   ↓
6. API Response
```

---

## Storage Estimates

### Per Stock Analysis:
- MongoDB: ~50-100 KB per analysis
- Redis Cache: ~50 KB, 1 hour TTL

### For 100 stocks/day:
- MongoDB: ~5-10 MB/day
- Redis: ~5 MB peak (with TTL)

### Annual Projection:
- MongoDB: ~3.5 GB/year
- TimeSeries Data: ~10-20 GB/year (daily OHLCV)

---

## Backup Strategy

### MongoDB
```bash
# Daily backup
mongodump --db market_analysis --out /backup/$(date +%Y%m%d)

# Restore
mongorestore --db market_analysis /backup/20260131
```

### Redis
```bash
# Save snapshot
redis-cli SAVE

# Backup RDB file
cp /var/lib/redis/dump.rdb /backup/redis_$(date +%Y%m%d).rdb
```

---

## Migration Scripts

### Initialize Collections
```javascript
// Run in mongosh
db.createCollection("watchlists");
db.watchlists.createIndex({userId: 1, symbol: 1, exchange: 1}, {unique: true});

db.createCollection("analysis_results");
db.analysis_results.createIndex({analysisId: 1}, {unique: true});
db.analysis_results.createIndex({symbol: 1, timestamp: -1});

db.createCollection("user_portfolios");
db.user_portfolios.createIndex({userId: 1}, {unique: true});
```

See `scripts/mongo-init.js` for full initialization script.
