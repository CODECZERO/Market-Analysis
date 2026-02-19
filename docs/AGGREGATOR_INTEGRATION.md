# Using Existing Aggregator for Stock Data

## 🎯 Overview

Instead of rewriting scrapers, we reuse the **existing, working aggregator service** that already has providers for:

- ✅ Reddit
- ✅ X/Twitter
- ✅ Bluesky
- ✅ News API
- ✅ Hacker News
- ✅ Google Search
- ✅ DuckDuckGo
- ✅ YouTube
- ✅ RSS feeds

## 🔧 How It Works

The `aggregator_adapter.py` acts as a bridge:

1. **Treats stocks as "brands"** - The aggregator is designed to track brand mentions, so we create temporary "brands" for stock symbols
2. **Leverages all providers** - Gets mentions from all enabled platforms
3. **Adds sentiment analysis** - Processes each mention with our FinBERT/VADER pipeline
4. **Returns structured data** - Groups by platform with sentiment scores

## 🚀 Setup

### Step 1: Start Aggregator Service

```bash
cd aggregator
npm install
npm start
```

Aggregator runs on port **4001** by default.

### Step 2: Configure Environment

In `market_analysis/.env`:
```bash
AGGREGATOR_URL=http://localhost:4001
```

### Step 3: (Optional) Enable More Platforms

Configure API keys in `aggregator/.env`:

```bash
# X/Twitter API (optional)
X_API_KEY=your_twitter_bearer_token

# News API (optional, 100 requests/day free)
NEWS_API_KEY=your_newsapi_key

# Google (optional, for Search + YouTube)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX=your_custom_search_engine_id
```

**Without keys:** Reddit, Bluesky, HN, DuckDuckGo still work!

## 📊 Usage

### Python Code

```python
from scrapers.aggregator_adapter import AggregatorAdapter

adapter = AggregatorAdapter()

# Fetch mentions for a stock
mentions = adapter.fetch_mentions(
    symbol="RELIANCE",
    company_name="Reliance Industries"  # optional
)

# mentions is a dict: {platform: [list of mentions]}
print(f"Reddit: {len(mentions['reddit'])} mentions")
print(f"X/Twitter: {len(mentions['x'])} mentions")
print(f"News: {len(mentions['news'])} mentions")

# Get combined sentiment
sentiment = adapter.get_combined_sentiment(mentions)
print(f"Overall: {sentiment['label']} ({sentiment['score']:.2f})")
print(f"Total: {sentiment['count']} mentions")
```

### Enhanced Orchestrator

The `orchestrator_enhanced.py` can now use the aggregator:

```python
from scrapers.aggregator_adapter import AggregatorAdapter

orchestrator = StockAnalysisOrchestrator()
orchestrator.aggregator = AggregatorAdapter()

# In the analysis pipeline:
if orchestrator.aggregator:
    mentions = orchestrator.aggregator.fetch_mentions(symbol)
    sentiment = orchestrator.aggregator.get_combined_sentiment(mentions)
```

## 🎁 Benefits

### 1. **Reuse Working Code**
- No need to rewrite 9 different providers
- Aggregator already tested and working
- Reduces code duplication

### 2. **More Data Sources**
- **9 platforms** vs 2-3 custom scrapers
- Better coverage of market sentiment
- Includes niche sources (HN, Bluesky, etc.)

### 3. **Centralized Configuration**
- API keys managed in one place (aggregator)
- Easy to enable/disable sources
- No changes to market analysis code

### 4. **Better Rate Limiting**
- Aggregator has built-in rate limiting
- Prevents IP bans
- Respects platform limits

## 📋 Data Flow

```
Stock Symbol → AggregatorAdapter
                     ↓
         Create "Brand" for stock
                     ↓
         Call Aggregator API
                     ↓
   Aggregator fetches from all platforms:
   - Reddit (/r/IndianStockMarket, etc.)
   - X/Twitter ($SYMBOL, #SYMBOL)
   - Bluesky (stock mentions)
   - News (MoneyControl, ET, etc.)
   - Hacker News (stock discussions)
   - DuckDuckGo (web search)
                     ↓
         Return all mentions
                     ↓
      Add Sentiment Analysis
                     ↓
   Group by platform + sentiment
```

## 🔍 Example Output

```python
{
    'reddit': [
        {
            'text': 'RELIANCE looking bullish!',
            'author': 'trader123',
            'score': 42,
            'sentiment': {'score': 0.8, 'label': 'POSITIVE'},
            'platform': 'reddit'
        },
        # ... more reddit mentions
    ],
    'x': [
        {
            'text': '$RELIANCE breaking out',
            'author': '@analyst',
            'score': 15,
            'sentiment': {'score': 0.7, 'label': 'POSITIVE'},
            'platform': 'x'
        },
        # ... more X mentions
    ],
    'news': [...],
    'bluesky': [...],
    'hn': [...]
}
```

## 🚨 Fallback Behavior

If aggregator is not running:
- Adapter returns empty data for all platforms
- Analysis continues with other components (technical, ML)
- No crash, just warning message

## ⚡ Performance

- **First request:** ~5-10 seconds (aggregator fetches from all platforms)
- **Cached requests:** ~1-2 seconds (Redis cache in aggregator)
- **Parallel fetching:** Aggregator fetches from platforms concurrently

## 🎯 Integration Checklist

- [ ] Start aggregator service (`cd aggregator && npm start`)
- [ ] Add `AGGREGATOR_URL` to `market_analysis/.env`
- [ ] Update `orchestrator_enhanced.py` to use adapter
- [ ] Test with: `python worker/src/scrapers/aggregator_adapter.py`
- [ ] (Optional) Configure API keys in `aggregator/.env`

## 📚 See Also

- `aggregator/README.md` - Aggregator documentation
- `aggregator/src/modules/aggregator/providers/` - All provider implementations
- `orchestrator_enhanced.py` - Main analysis pipeline

---

**This is the smartest approach - reuse what works!** 🧠
