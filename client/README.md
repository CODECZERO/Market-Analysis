# API Client Examples

This directory contains client libraries and examples for interacting with the Market Analysis API.

## 📦 Python Client

### Installation

```bash
pip install requests
```

### Quick Start

```python
from client.python.market_analysis_client import MarketAnalysisClient

# Initialize client
client = MarketAnalysisClient(api_url="http://localhost:3000")

# Add stock to watchlist
client.add_to_watchlist("RELIANCE", "NSE")

# Trigger analysis
result = client.analyze_stock("RELIANCE", "NSE", wait_for_completion=True)

# Get quote
quote = client.get_quote("RELIANCE", "NSE")
print(f"Price: ₹{quote['data']['price']:,.2f}")
```

### API Reference

#### Watchlist Operations

```python
# Get watchlist
watchlist = client.get_watchlist()

# Add stock
client.add_to_watchlist(symbol="TCS", exchange="NSE")

# Remove stock
client.remove_from_watchlist(symbol="TCS", exchange="NSE")
```

#### Stock Analysis

```python
# Trigger analysis (async)
result = client.analyze_stock("INFY", "NSE")
analysis_id = result['data']['analysisId']

# Wait for completion
result = client.analyze_stock(
    "INFY",
    "NSE",
    wait_for_completion=True,
    max_wait=300
)

# Check progress
progress = client.get_analysis_progress(analysis_id)
```

#### Stock Data

```python
# Get current quote
quote = client.get_quote("HDFCBANK", "NSE")

# Search stocks
results = client.search_stocks("Reliance", limit=10)
```

#### Batch Operations

```python
# Analyze entire watchlist
results = client.analyze_watchlist(batch_size=2, delay=10)

# Or use convenience function
from client.python.market_analysis_client import bulk_analyze

results = bulk_analyze(
    ["RELIANCE", "TCS", "INFY"],
    exchange="NSE"
)
```

## 🔧 Tools

### Performance Benchmark

```bash
cd tools
python benchmark.py
```

Output:
```
=== Benchmarking Single Analysis (RELIANCE) ===
Runs: 3
Run 1/3... ✓ 45.2s
Run 2/3... ✓ 43.8s
Run 3/3... ✓ 44.5s

=== Summary ===
Single Analysis: 44.5s avg
get_watchlist: 125.3ms avg
search: 89.7ms avg
get_quote: 156.2ms avg
```

### System Monitor

```bash
./monitor.sh
```

Shows real-time:
- Service health
- Resource usage (CPU, Memory)
- GPU status
- Recent activity

Press `Ctrl+C` to exit.

## 📝 Examples

### Example 1: Analyze Top 5 Stocks

```python
from client.python.market_analysis_client import MarketAnalysisClient

client = MarketAnalysisClient()

# Top 5 Nifty stocks
stocks = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK"]

for stock in stocks:
    print(f"Analyzing {stock}...")
    client.add_to_watchlist(stock, "NSE")
    client.analyze_stock(stock, "NSE")

print("✓ All analyses triggered!")
```

### Example 2: Get Recommendations

```python
from client.python.market_analysis_client import MarketAnalysisClient

client = MarketAnalysisClient()

# Analyze and wait
result = client.analyze_stock(
    "RELIANCE",
    "NSE",
    wait_for_completion=True
)

# Extract recommendation
analysis = result['data']
print(f"Symbol: {analysis['symbol']}")
print(f"Rating: {analysis['recommendation']}")
print(f"Entry: ₹{analysis['entry_price']}")
print(f"Target: ₹{analysis['target_1']}")
print(f"Stop Loss: ₹{analysis['stop_loss']}")
```

### Example 3: Portfolio Analysis

```python
from client.python.market_analysis_client import MarketAnalysisClient
import pandas as pd

client = MarketAnalysisClient()

# Your portfolio
portfolio = [
    {"symbol": "RELIANCE", "qty": 10},
    {"symbol": "TCS", "qty": 5},
    {"symbol": "INFY", "qty": 15}
]

# Get current prices
data = []
for holding in portfolio:
    quote = client.get_quote(holding['symbol'], "NSE")
    price = quote['data']['price']
    data.append({
        'symbol': holding['symbol'],
        'qty': holding['qty'],
        'price': price,
        'value': price * holding['qty']
    })

# Create DataFrame
df = pd.DataFrame(data)
print(df)
print(f"\nTotal Portfolio Value: ₹{df['value'].sum():,.2f}")
```

### Example 4: Scheduled Analysis

```python
import schedule
import time
from client.python.market_analysis_client import MarketAnalysisClient

client = MarketAnalysisClient()

def daily_analysis():
    """Run daily analysis at market close"""
    print("Running daily watchlist analysis...")
    results = client.analyze_watchlist(batch_size=2, delay=10)
    
    successful = sum(1 for r in results if r['success'])
    print(f"Completed: {successful}/{len(results)}")

# Schedule for 4 PM IST (market close)
schedule.every().day.at("16:00").do(daily_analysis)

print("Scheduler started. Press Ctrl+C to exit.")
while True:
    schedule.run_pending()
    time.sleep(60)
```

## 🔒 Authentication

If the API requires authentication:

```python
client = MarketAnalysisClient(
    api_url="http://localhost:3000",
    api_key="your_api_key_here"
)
```

## ⚡ Performance Tips

1. **Use batch operations** for multiple stocks
2. **Set reasonable timeouts** for slow networks
3. **Cache results** when possible
4. **Limit concurrent requests** to 2-3 for low-memory systems
5. **Add delays** between batch requests (5-10 seconds)

## 🐛 Error Handling

```python
from client.python.market_analysis_client import MarketAnalysisClient
import requests

client = MarketAnalysisClient(timeout=30)

try:
    result = client.analyze_stock("RELIANCE", "NSE")
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.ConnectionError:
    print("Could not connect to API")
except Exception as e:
    print(f"Error: {e}")
```

## 📚 Additional Resources

- **API Documentation**: See [API_SPEC.md](../API_SPEC.md)
- **Deployment Guide**: See [DEPLOYMENT.md](../DEPLOYMENT.md)
- **Optimization Guide**: See [OPTIMIZATION.md](../OPTIMIZATION.md)

---

**Happy Trading!** 📈
