# Stock Analysis API Specification

## Base URL
```
http://localhost:3000/api/stocks
```

## Authentication
All endpoints require authentication via Bearer token:
```
Authorization: Bearer <jwt_token>
```

---

## Endpoints

### 1. Get Watchlist
Get user's stock watchlist.

**GET** `/watchlist`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "user1_RELIANCE_NSE",
      "userId": "user1",
      "symbol": "RELIANCE",
      "exchange": "NSE",
      "addedAt": "2026-01-31T08:30:00Z",
      "lastAnalyzedAt": "2026-01-31T09:15:00Z",
      "analysisStatus": "completed"
    }
  ],
  "count": 1
}
```

---

### 2. Add to Watchlist
Add a stock to user's watchlist.

**POST** `/watchlist`

**Body:**
```json
{
  "symbol": "RELIANCE",
  "exchange": "NSE"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user1_RELIANCE_NSE",
    "userId": "user1",
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "addedAt": "2026-01-31T08:30:00Z",
    "lastAnalyzedAt": null,
    "analysisStatus": "pending"
  }
}
```

---

### 3. Remove from Watchlist
Remove a stock from watchlist.

**DELETE** `/watchlist/:symbol?exchange=NSE`

**Response:**
```json
{
  "success": true,
  "message": "Stock removed from watchlist"
}
```

---

### 4. Trigger Stock Analysis
Start a comprehensive stock analysis.

**POST** `/analyze`

**Body:**
```json
{
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "refresh": false
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "data": {
    "analysisId": "RELIANCE_NSE_1738492800000",
    "userId": "user1",
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "status": "processing",
    "startedAt": "2026-01-31T08:30:00Z",
    "completedAt": null,
    "progress": {
      "phase": "data_fetch",
      "percentage": 10,
      "message": "Fetching stock data..."
    }
  },
  "message": "Analysis started. Use analysisId to check progress."
}
```

---

### 5. Get Analysis Results
Retrieve analysis results or check progress.

**GET** `/analyze/:analysisId`

**Response (Processing):**
```json
{
  "success": true,
  "data": {
    "analysisId": "RELIANCE_NSE_1738492800000",
    "status": "processing",
    "progress": {
      "phase": "llm_phase2",
      "percentage": 65,
      "message": "Running LLM Phase 2..."
    }
  }
}
```

**Response (Complete):**
```json
{
  "success": true,
  "data": {
    "analysisId": "RELIANCE_NSE_1738492800000",
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "status": "completed",
    "timestamp": "2026-01-31T08:35:00Z",
    "current_price": 2456.75,
    "currency": "INR",
    
    "fundamentals": {
      "market_cap_cr": 166250.5,
      "pe_ratio": 28.4,
      "pb_ratio": 2.1,
      "roe": 8.9,
      "debt_to_equity": 0.45
    },
    
    "technical_indicators": {
      "rsi_14": 38.2,
      "macd_bullish": true,
      "price_vs_sma50": 2.34,
      "adx_14": 28.5,
      "trend_strength": "strong"
    },
    
    "quant_signals": {
      "momentum": {
        "signal": "LONG",
        "percentile_rank": 72.5
      },
      "mean_reversion": {
        "signal": "BUY",
        "zscore": -1.8
      },
      "regime": {
        "regime": "BULL",
        "probability": 0.82
      }
    },
    
    "ml_predictions": {
      "lstm": {
        "1d": 2468.30,
        "7d": 2510.50,
        "30d": 2620.00,
        "90d": 2780.00,
        "confidence": 0.78
      },
      "xgboost": {
        "signal": "BUY",
        "probability": 0.78
      }
    },
    
    "sentiment": {
      "fused_sentiment": 0.35,
      "signal": "POSITIVE"
    },
    
    "phase1_what_why": {
      "what": "Reliance consolidating after Q3 earnings",
      "why": "Refining margin expansion and strong petrochemical demand",
      "primary_cause": "FUNDAMENTALS_SHIFT",
      "confidence": 78
    },
    
    "phase2_when_where": {
      "entry_window": "Next 5-7 trading days",
      "entry_trigger": "Price dips to ₹2440-2470 with RSI below 40",
      "horizon": "MEDIUM_TERM",
      "horizon_days": 90,
      "segment": "LARGE_CAP_STABILITY"
    },
    
    "phase3_recommendation": {
      "rating": "BUY",
      "entry_price_range": {"min": 2440, "max": 2470},
      "stop_loss": 2380,
      "targets": {
        "t1_1week": 2550,
        "t2_30day": 2650,
        "t3_90day": 2800
      },
      "position_size_pct": 3.5,
      "risk_reward_ratio": 3.2,
      "reasoning": "Strong fundamentals combined with oversold technical position...",
      "markdown_report": "# Investment Recommendation: RELIANCE\n\n## 📈 **BUY**\n..."
    },
    
    "decision": {
      "recommendation": "BUY",
      "composite_score": 62.5,
      "confidence": 78.2
    }
  }
}
```

---

### 6. Get Stock Quote
Get current stock quote.

**GET** `/quotes/:symbol?exchange=NSE`

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "price": 2456.75,
    "change": 23.50,
    "changePercent": 0.96,
    "volume": 5234567,
    "dayHigh": 2478.00,
    "dayLow": 2445.30,
    "timestamp": "2026-01-31T08:30:00Z"
  }
}
```

---

### 7. Search Stocks
Search for stocks by symbol or name.

**GET** `/search?q=reliance&exchange=NSE&limit=10`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "RELIANCE",
      "name": "Reliance Industries Ltd",
      "exchange": "NSE",
      "sector": "Oil & Gas"
    }
  ],
  "count": 1
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Error message description"
}
```

**Status Codes:**
- `200` - Success
- `201` - Created
- `202` - Accepted (async operation started)
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `409` - Conflict (duplicate entry)
- `500` - Internal Server Error

---

## Analysis Status Flow

```
     POST /analyze
          ↓
    202 Accepted
          ↓
  ┌──────────────┐
  │  processing  │     GET /analyze/:id
  └──────┬───────┘          ↓
         │           Progress updates:
         │           - data_fetch (10%)
         │           - technical (25%)
         │           - quant (40%)
         │           - ml (55%)
         │           - llm_phase1 (65%)
         │           - llm_phase2 (75%)
         │           - llm_phase3 (90%)
         ↓
  ┌──────────────┐
  │  completed   │
  └──────────────┘
         │
   Full results
```

---

## Rate Limits

- **Watchlist**: 100 stocks per user
- **Analysis**: 10 concurrent analyses per user
- **Quote**: 60 requests/minute
- **Search**: 20 requests/minute

---

## WebSocket (Future)

Real-time stock updates via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:3000/ws/stocks');

ws.on('message', (data) => {
  // { type: 'quote_update', symbol: 'RELIANCE', price: 2456.75 }
  // { type: 'analysis_progress', analysisId: '...', progress: 65 }
  // { type: 'analysis_complete', analysisId: '...' }
});
```
