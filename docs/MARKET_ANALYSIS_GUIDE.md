# Market Analysis Guide

## 📊 Introduction

This guide explains how our AI-powered market analysis system works end-to-end.

---

## 🔄 Analysis Pipeline

The system follows a **7-step pipeline**:

```
1. Data Fetch → 2. Technical Analysis → 3. Quant Strategies → 
4. ML Predictions → 5. Sentiment Analysis → 6. Correlation Analysis → 
7. Decision Fusion
```

### Step 1: Data Fetch
- Fetches 1-year OHLCV data from NSE/BSE
- Uses YFinance for Indian stocks
- Validates data quality
- Handles missing/invalid data

### Step 2: Technical Analysis
- Calculates 20+ indicators
- Identifies support/resistance
- Detects chart patterns
- Generates technical signals

**Key Outputs:**
- RSI, MACD, Bollinger Bands
- Moving averages (SMA 50/200)
- Volume indicators (OBV, MFI)
- Volatility measures (ATR, BB width)

### Step 3: Quantitative Strategies
- Runs 6 Wall Street algorithms
- Signal fusion with weighted scores
- Risk-adjusted metrics

**Strategies:**
1. Momentum (STRONG_BUY to STRONG_SELL)
2. Mean Reversion (z-score based)
3. Pairs Trading (Kalman filter)
4. HMM Regime Detection (BULL/BEAR/FLAT)
5. Fama-French 3-Factor
6. Cross-Sectional Momentum

### Step 4: ML Predictions
- LSTM model for price prediction
- XGBoost for directional signals
- Confidence intervals via MC Dropout

**Outputs:**
- 1d, 7d, 30d, 90d predictions
- Confidence scores
- SHAP feature importance

### Step 5: Sentiment Analysis
- News sentiment (FinBERT)
- Social media sentiment (VADER)
- Volatility-scaled fusion

**Currently:** Framework ready, scrapers not implemented

### Step 6: Correlation Analysis
- Price-to-price correlations
- Sentiment-to-price lag analysis
- Volume-to-price relationships

### Step 7: Decision Fusion
- Combines all signals
- Weighted scoring system
- Final recommendation

---

## 💡 How Recommendations Are Made

### Scoring System

Each component contributes to the final score:

| Component | Weight | Range |
|-----------|--------|-------|
| Technical Indicators | 30% | -1 to +1 |
| Quant Strategies | 30% | -1 to +1 |
| ML Predictions | 25% | -1 to +1 |
| Sentiment | 15% | -1 to +1 |

**Final Score = Weighted Average**

### Rating Thresholds

| Score Range | Rating |
|-------------|--------|
| > 0.6 | STRONG_BUY |
| 0.3 to 0.6 | BUY |
| -0.3 to 0.3 | HOLD |
| -0.6 to -0.3 | SELL |
| < -0.6 | STRONG_SELL |

### Confidence Calculation

```
Confidence = (Signal Alignment * ML Confidence * Data Quality) ^ 0.5
```

Where:
- **Signal Alignment:** How many signals agree
- **ML Confidence:** Model uncertainty
- **Data Quality:** Completeness & freshness

---

## 🎯 Price Targets

### Entry Price
```
Entry = Current Price ± (ATR * 0.5)
```
Allows for normal market volatility.

### Stop Loss
```
Stop Loss = Entry - (ATR * 2.0)
```
Based on Average True Range (ATR) for volatility-adjusted risk.

### Target Prices

**Target 1 (Conservative):**
```
T1 = Entry + (Risk * 2.0)
```
Risk-reward ratio: 2:1

**Target 2 (Moderate):**
```
T2 = Entry + (Risk * 3.5)
```
Risk-reward ratio: 3.5:1

**Target 3 (Aggressive):**
```
T3 = Entry + (Risk * 5.0)
```
Risk-reward ratio: 5:1

---

## 📈 Position Sizing

### Risk-Based Position Sizing

```
Position Size = (Account Size * Risk%) / (Entry - Stop Loss)
```

**Example:**
- Account: ₹1,00,000
- Risk: 2% = ₹2,000
- Stock: RELIANCE @ ₹2,450
- Stop Loss: ₹2,380
- Risk per share: ₹70

**Shares = ₹2,000 / ₹70 = 28 shares**

---

## 🔍 Interpreting Results

### Recommendation Card

```json
{
  "rating": "BUY",
  "confidence": 0.72,
  "entry_price": 2445.00,
  "stop_loss": 2380.00,
  "target_1": 2575.00,
  "target_2": 2675.00,
  "target_3": 2770.00
}
```

**What it means:**
- **72% confidence** that this is a good BUY
- Enter around **₹2,445**
- Exit immediately if drops to **₹2,380** (2.7% loss)
- Take profits at **₹2,575** (5.3% gain), **₹2,675** (9.4%), or **₹2,770** (13.3%)

### Technical Analysis

- **RSI > 70:** Overbought, potential pullback
- **RSI < 30:** Oversold, potential bounce
- **MACD > 0:** Bullish momentum
- **Price > SMA 200:** Long-term uptrend

### Quant Signals

- **Momentum = BUY:** Price trending up
- **Z-Score < -2:** Undervalued (mean reversion signal)
- **Regime = BULL:** Market in bullish phase

### ML Predictions

- **1d prediction > current:** Short-term bullish
- **Confidence > 60%:** Reliable prediction
- **SHAP values:** Shows why model predicted this

---

## ⚠️ Risk Management

### Never Trade Without:
1. **Stop Loss:** Always set before entry
2. **Position Sizing:** Never risk >2% per trade
3. **Diversification:** Max 20% in any one stock
4. **Validation:** Check multiple timeframes

### Red Flags:
- ⚠️ Confidence < 40%: Skip trade
- ⚠️ Conflicting signals: Wait for clarity
- ⚠️ Low volume: Poor liquidity
- ⚠️ News events: High uncertainty

---

## 📊 Best Practices

### 1. Use Multiple Timeframes
- Daily chart for entries
- Weekly chart for trend
- Monthly chart for context

### 2. Confirm Signals
Wait for:
- Technical + Quant agreement
- ML confidence > 60%
- No negative sentiment spikes

### 3. Scale In/Out
- Buy 50% at entry
- Buy 25% if dips to support
- Sell 50% at T1
- Sell 25% at T2
- Trail stop for rest

### 4. Keep a Trading Journal
Log:
- Entry/exit prices
- Reasoning
- Emotions
- Results

---

## 🎓 Learning Resources

### Technical Analysis
- "Technical Analysis of the Financial Markets" - John Murphy
- "Encyclopedia of Chart Patterns" - Thomas Bulkowski

### Quantitative Finance
- "Quantitative Trading" - Ernest Chan
- "Advances in Financial Machine Learning" - Marcos López de Prado

### Risk Management
- "The New Trading for a Living" - Alexander Elder
- "Trade Your Way to Financial Freedom" - Van K. Tharp

---

## 🤖 System Limitations

### What the System CAN'T Do:
1. **Predict black swan events** (COVID, war, etc.)
2. **Account for insider trading**
3. **React to breaking news instantly**
4. **Guarantee profits** (no system can!)

### Current Gaps:
- News scraping not implemented
- Social media analysis not done
- Real-time data limited
- LLM API calls not connected

### Use Responsibly:
- This is a **decision support tool**, not a crystal ball
- Always do your own research
- Never invest more than you can afford to lose
- Past performance ≠ future results

---

**Remember: The best traders combine AI insights with human judgment!** 🧠💻
