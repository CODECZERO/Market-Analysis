# 📈 Advanced Stock Analysis Dashboard

## 🎯 Features

### 1. **Multi-Stock Portfolio View**
View multiple stocks in a single compact table:
- Current prices and day changes
- BUY/SELL/HOLD recommendations
- Hold duration (e.g., "14-30 days", "Exit now")
- Target prices and stop-loss levels
- Clear reasoning for each recommendation

### 2. **Top 5 Stock Screener**
AI-powered screener that analyzes top 20 Indian stocks and ranks them:
- Scores based on RSI, momentum, and trend strength
- Shows only the best 5 opportunities
- Real-time market sentiment (Bullish/Bearish/Neutral)
- Detailed reasoning for each pick

### 3. **Interactive Search**
Search and analyze any stock:
- Detailed technical analysis
- Precise entry/exit recommendations
- Risk management (stop-loss levels)
- Hold timing guidance

### 4. **Smart Recommendations**
Each stock gets personalized advice:
- **Action**: BUY/SELL/HOLD
- **Hold Duration**: How long to stay invested
- **Target Price**: When to book profits
- **Stop Loss**: When to cut losses
- **Reason**: Why this recommendation

## 🚀 Quick Start

### Run Interactive Dashboard:
```bash
cd market_analysis
./dashboard.sh
```

### Direct Modes:

**Top 5 Stock Picks (Screener):**
```bash
./venv/bin/python advanced_cli.py --mode screener
```

**Portfolio View (Multiple Stocks):**
```bash
./venv/bin/python advanced_cli.py --mode portfolio
```

**Search Specific Stock:**
```bash
./venv/bin/python advanced_cli.py --mode search --symbol TCS.NS
```

**Interactive Menu:**
```bash
./venv/bin/python advanced_cli.py
```

## 📊 System Modes

### Full System Launch:
```bash
./start-enhanced.sh
```

Choose from:
1. **Full System** - Backend + Frontend + Auto-refreshing Dashboard
2. **Dashboard Only** - Just the CLI analysis
3. **Backend + Frontend** - Web interface only

## 💡 Understanding the Recommendations

### Hold Duration Examples:
- **"14-30 days"** = Good uptrend, hold for medium term
- **"30-60 days"** = Oversold stock, value opportunity
- **"7-14 days"** = Neutral, wait for clearer signal
- **"Exit now"** = Take profit or cut losses immediately

### Actions:
- **🟢 BUY** = Strong uptrend, good entry point
- **🔴 SELL** = Downtrend or overbought, exit position
- **🟡 HOLD** = Wait for clearer trend direction

### Technical Signals:
- **RSI > 70** = Overbought (consider selling)
- **RSI < 30** = Oversold (consider buying)
- **RSI 30-70** = Neutral territory

## 📋 Stock Symbols

Use NSE stock codes:
- TCS.NS - Tata Consultancy Services
- RELIANCE.NS - Reliance Industries
- INFY.NS - Infosys
- HDFCBANK.NS - HDFC Bank
- ICICIBANK.NS - ICICI Bank

## 🎨 Sample Output

```
🏆 TOP 5 STOCK PICKS
┌──────┬─────────────┬───────────┬────────┬────────────────┬──────────┬─────────────────────┐
│ Rank │ Symbol      │ Price ₹   │ Action │ Hold Duration  │ Target ₹ │ Why?                │
├──────┼─────────────┼───────────┼────────┼────────────────┼──────────┼─────────────────────┤
│ #1   │ INFY        │ 1,450.00  │ 🟢 BUY │ 30-60 days     │ 1,566.00 │ Oversold - value    │
│ #2   │ HDFCBANK    │ 1,650.00  │ 🟢 BUY │ 14-30 days     │ 1,732.50 │ Strong uptrend      │
└──────┴─────────────┴───────────┴────────┴────────────────┴──────────┴─────────────────────┘

Market Sentiment: Bullish 📈
```

## ⚙️ Requirements

- Python 3.8+
- Dependencies: `yfinance`, `pandas`, `numpy`, `rich`
- Internet connection (for real-time data)

## 📅 Market Hours

Indian Stock Markets (NSE/BSE):
- **Trading Days**: Monday - Friday
- **Trading Hours**: 9:15 AM - 3:30 PM IST
- **Closed**: Weekends and holidays

*Note: During non-market hours, the dashboard shows the last available data with a timestamp.*

## 🔄 Auto-Refresh

The dashboard can auto-refresh to show updated data:
- Default interval: 5 minutes
- Press Ctrl+C to stop

## 📝 Tips

1. **Check market hours** - Best accuracy during trading hours
2. **Use stop-loss** - Always protect your capital
3. **Follow hold duration** - Don't exit too early or hold too long
4. **Diversify** - Don't invest everything in one stock
5. **Paper trade first** - Test strategies before real money

## 🛠️ Troubleshooting

**No data shown?**
- Check internet connection
- Verify stock symbol is correct (must end with .NS)
- Markets may be closed

**Slow performance?**
- Normal - analyzing 20 stocks takes ~30 seconds
- Backend API provides faster cached results

## 📞 Support

For issues or questions, check the logs:
- Backend: `logs/backend.log`
- Frontend: `logs/frontend.log`
