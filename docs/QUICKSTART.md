# Quick Start Guide

## 🚀 Get Started in 3 Steps

# Quick Start Guide 🚀

Get the Market Analysis System running in **under 5 minutes**.

---

## 🎯 The Fastest Way (Single Command!)

```bash
cd market_analysis
./run-all.sh
```

**That's it!** This starts:
- ✅ MongoDB & Redis (Docker)
- ✅ Python Worker
- ✅ Auto-monitoring
- ✅ Auto-restart on crash
- ✅ Graceful shutdown (Ctrl+C)

Then test it:
```bash
# In a new terminal
python examples/complete_integration_demo.py
```

See [USAGE.md](./USAGE.md) for details.

---

## 📋 Prerequisites

### Required
- **Docker** & **Docker Compose**
- **Python 3.9+**
- **4GB RAM minimum** (8GB recommended)
- **Internet connection** (for stock data)

### For RTX 2050 (4GB VRAM)
The system is automatically optimized for low-memory GPUs! See [OPTIMIZATION.md](./OPTIMIZATION.md) for details.

Key optimizations:
- 3GB GPU memory limit (1GB for system)
- Batch size: 8 (inference), 16 (training)
- Max 2 concurrent analyses
- CPU fallback for XGBoost
- Mixed precision (FP16)

### Step 3: Access the App

Open http://localhost in your browser!

---

## 📊 Usage

### Add Stocks to Watchlist

1. Click **"Add Stock"** button
2. Search for stock (e.g., "RELIANCE", "TCS", "INFY")
3.Select NSE or BSE exchange
4. Click the stock to add

### Analyze a Stock

1. Click on a stock in your watchlist
2. Click the **Play** button (▶️)
3. Wait ~30-60 seconds for complete analysis
4. View results in 4 tabs:
   - **Overview**: Investment thesis, entry strategy, targets
   - **Technical**: RSI, MACD, ADX indicators
   - **AI Analysis**: 3-phase LLM reasoning
   - **ML Predictions**: LSTM forecasts, XGBoost signals

### Interpreting Results

**Rating Colors**:
- 🟢 **BUY** / **STRONG_BUY** - Positive signals, good entry opportunity
- 🟡 **HOLD** - Mixed signals, wait for better entry
- 🔴 **SELL** / **STRONG_SELL** - Negative signals, avoid or exit

**Key Metrics**:
- **Entry Range**: Recommended buy price range
- **Stop Loss**: Exit if price falls below this
- **Targets**: Price goals for 1 week, 30 days, 90 days
- **Risk/Reward**: Higher is better (e.g., 1:3.2 means 3.2x reward vs risk)
- **Position Size**: % of portfolio to allocate

---

## 🧪 Testing

### Health Check

```bash
./health-check.sh
```

Validates:
- All Docker containers running
- MongoDB and Redis connectivity
- API endpoints responding
- Frontend serving

### Integration Tests

```bash
cd tests
python integration_test.py
```

Tests:
- API health
- Stock search
- Watchlist operations
- Quote fetching
- (Note: Full analysis requires LLM API key)

### Demo Analysis

```bash
python demo_analysis.py
```

Runs complete analysis for RELIANCE.NS with mock LLM responses.

---

## 🔧 Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-gateway
docker-compose logs -f worker
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api-gateway
```

### Stop Everything

```bash
docker-compose down
```

### Clean Restart

```bash
docker-compose down -v  # ⚠️ Deletes all data!
./setup.sh
```

---

## 📱 Sample Stocks to Try

### Large Cap (Stable)
- **RELIANCE** - Reliance Industries (Oil & Gas)
- **TCS** - Tata Consultancy Services (IT)
- **HDFCBANK** - HDFC Bank (Banking)
- **INFY** - Infosys (IT)
- **ICICIBANK** - ICICI Bank (Banking)

### Mid Cap (Growth)
- **BAJAJFINSV** - Bajaj Finserv
- **ADANIPORTS** - Adani Ports
- **TITAN** - Titan Company

### Indices
- **^NSEI** - Nifty 50
- **^BSESN** - Sensex

---

## ❓ Troubleshooting

### "No LLM provider configured"

**Solution**: Add an API key to `.env`:
```bash
GROQ_API_KEY=gsk_your_key_here
```

Then restart:
```bash
docker-compose restart api-gateway
```

### "Connection refused" errors

**Solution**: Services may still be starting. Wait 30 seconds, then:
```bash
./health-check.sh
```

### MongoDB authentication errors

**Solution**: Reset the database:
```bash
docker-compose down -v
./setup.sh
```

### Analysis takes too long

**Reason**: LLM APIs can be slow. Normal wait time is 30-90 seconds.

**Solution**: Check logs for rate limiting:
```bash
docker-compose logs api-gateway | grep "429"
```

---

## 📖 Learn More

- **[README.md](./README.md)** - Project overview and architecture
- **[API_SPEC.md](./API_SPEC.md)** - REST API documentation
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production deployment guide
- **[FRONTEND_SETUP.md](./FRONTEND_SETUP.md)** - UI component guide

---

## 🎯 What This System Does

### Input
- Stock symbol (e.g., RELIANCE, TCS)
- 5 years of price data
- Recent news and social sentiment
- Company fundamentals

### Analysis Pipeline
1. **Technical Indicators** - RSI, MACD, Bollinger Bands, etc.
2. **Quantitative Strategies** - Momentum, mean reversion, regime detection
3. **ML Predictions** - LSTM price forecasts, XGBoost signals
4. **Sentiment Analysis** - News + social media fusion
5. **LLM Phase 1** - What's happening? Why?
6. **LLM Phase 2** - When to enter? Where?
7. **LLM Phase 3** - How to execute?
8. **Decision Engine** - Fuse all signals → Final recommendation

### Output
- **Rating**: BUY / HOLD / SELL
- **Entry price range**
- **Stop loss**
- **3 price targets** (short/medium/long term)
- **Position size** recommendation
- **Risk/reward ratio**
- **Complete reasoning** from AI

---

**Built for Indian Stock Market (NSE/BSE) | Powered by AI**

*Ready to make better investment decisions!* 🚀
