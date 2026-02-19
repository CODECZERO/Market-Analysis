# 🎯 Multi-Source Data Strategy

## Overview

The market analysis system now uses **MULTIPLE data sources** for maximum coverage and reliability:

## 📊 Data Sources (In Order)

### 1. **Aggregator Service** (Primary - Best Coverage)
**9 Platforms:**
- Reddit
- X/Twitter
- Bluesky
- News API
- Hacker News
- Google Search
- DuckDuckGo
- YouTube
- RSS feeds

**Pros:**
- ✅ Most comprehensive
- ✅ Proven, tested code
- ✅ Built-in rate limiting
- ✅ Redis caching
- ✅ Parallel fetching

**Cons:**
- ⚠️ Requires aggregator service running
- ⚠️ Extra dependency

**Setup:**
```bash
cd aggregator
npm start  # Port 4001
```

---

### 2. **Direct Scrapers** (Supplement/Fallback)

Individual scrapers that work independently:

#### MoneyControl News
- Indian stock news
- No API key needed
- Sentiment analysis built-in

#### Economic Times News
- Indian stock news
- No API key needed
- Sentiment analysis built-in

#### Reddit Direct (PRAW)
- r/IndianStockMarket, r/investing, etc.
- Optional API key for better limits
- Weighted sentiment by upvotes

#### Twitter Direct (Nitter)
- Free via Nitter instances
- Optional Twitter API v2
- Weighted sentiment by engagement

**Pros:**
- ✅ No external dependencies
- ✅ Works immediately
- ✅ Fine-grained control
- ✅ Individual fallback

**Cons:**
- ⚠️ Less coverage than aggregator
- ⚠️ Slower (sequential fetching)
- ⚠️ More rate limit management

---

## 🔄 How They Work Together

### Strategy: **Best of Both Worlds**

```python
# 1. Try aggregator first (most data)
aggregator_mentions = aggregator.fetch_mentions("RELIANCE")
# Returns: Reddit, X, Bluesky, News, HN, Google, etc.

# 2. Supplement with direct scrapers
moneycontrol_articles = moneycontrol_scraper.scrape_news("RELIANCE")
reddit_posts = reddit_scraper.scrape_discussions("RELIANCE")

# 3. Combine results
if aggregator_data:
    primary_sentiment = aggregator_data
    # Use direct scrapers to fill gaps or as validation
else:
    # Fallback to direct scrapers only
    primary_sentiment = combine_direct_scrapers()
```

### Orchestrator Logic

The `orchestrator_enhanced.py` automatically:

1. **Tries aggregator** - Best coverage, 9 platforms
2. **Runs direct scrapers** - MoneyControl + Reddit as supplement
3. **Combines intelligently**:
   - If aggregator works: Use it as primary + add direct scraper counts
   - If aggregator fails: Use direct scrapers only
   - If both work: Maximum data coverage!

---

## 📈 Coverage Comparison

| Source | Platforms | API Keys | Setup |
|--------|-----------|----------|-------|
| **Aggregator** | 9 | Optional | Need service running |
| **Direct Scrapers** | 4 | Optional | Built-in, ready |
| **Combined** | 9 (unique) | Optional | Best of both! |

---

## 🚀 Quick Start

### Option 1: Full Power (Aggregator + Direct)

```bash
# Terminal 1: Start aggregator
cd aggregator
npm start

# Terminal 2: Start market analysis
cd market_analysis
./run-all.sh

# Analyze stock
python quick_analyze.py RELIANCE
# Uses: Aggregator (9 sources) + Direct scrapers (validation)
```

**Result:** Maximum data coverage! 📊

---

### Option 2: Direct Scrapers Only

```bash
# Just start market analysis
cd market_analysis
./run-all.sh

python quick_analyze.py RELIANCE
# Uses: MoneyControl + Reddit only
```

**Result:** Works immediately, good coverage! ✅

---

### Option 3: Aggregator Only

Set in code:
```python
# In orchestrator
use_direct_scrapers = False  # Skip individual scrapers
use_aggregator = True
```

**Result:** 9 platforms, centralized! 🎯

---

## 🎮 Configuration

### Enable/Disable Sources

In `orchestrator_enhanced.py`:

```python
async def analyze_stock(
    symbol: str,
    use_llm: bool = True,
    use_scrapers: bool = True,  # All sources
    use_aggregator: bool = True,  # Try aggregator
    use_direct: bool = True  # Use direct scrapers
):
    # ...
```

### Environment Variables

**For Aggregator:**
```bash
# market_analysis/.env
AGGREGATOR_URL=http://localhost:4001
```

**For Direct Scrapers:**
```bash
# market_analysis/.env
REDDIT_CLIENT_ID=your_id  # Optional
REDDIT_CLIENT_SECRET=your_secret  # Optional
TWITTER_BEARER_TOKEN=your_token  # Optional
```

**Aggregator API Keys:**
```bash
# aggregator/.env
X_API_KEY=twitter_bearer_token
NEWS_API_KEY=newsapi_key
GOOGLE_API_KEY=google_key
```

---

## 💡 Best Practices

### 1. **For Development**
Use direct scrapers only:
- No extra services needed
- Fast iteration
- Good enough coverage

### 2. **For Production**
Use both:
- Maximum data coverage
- Redundancy if one fails
- Best sentiment accuracy

### 3. **For Testing**
Mock mode works with both:
- No API keys needed
- No network calls
- Fast testing

---

## 🔍 Data Quality

### Aggregator Advantages
- **More platforms** = better market sentiment picture
- **Reddit + X + Bluesky** = social media coverage
- **News + Google + DDG** = news coverage
- **HN + YouTube** = niche but valuable

### Direct Scraper Advantages
- **MoneyControl** = India-specific stock news
- **Economic Times** = India business focus
- **Reddit direct** = Fine-tuned for stock subreddits
- **No dependencies** = Always works

### Combined
- **Best sentiment accuracy** from multiple sources
- **Validation** - cross-check aggregator with direct
- **Redundancy** - if one fails, others work

---

## 📊 Example Output

### With Both Sources:

```
5️⃣  Fetching news & social sentiment...
   📡 Using aggregator service (9 platforms)...
   ✅ Aggregator: 156 mentions, POSITIVE
   📰 MoneyControl scraper...
   ✅ MoneyControl: 5 articles
   💬 Reddit scraper...
   ✅ Reddit: 23 posts

Combined Sentiment:
- Aggregator: POSITIVE (0.62) from 156 mentions
  - Reddit: 45 posts
  - X/Twitter: 67 tweets
  - News: 23 articles
  - Bluesky: 12 posts
  - HN: 9 discussions
- Direct Scrapers: 28 additional items
- Total Coverage: 184 data points
```

### With Direct Only:

```
5️⃣  Fetching news & social sentiment...
   ⚠️  Aggregator unavailable
   📰 MoneyControl scraper...
   ✅ MoneyControl: 5 articles
   💬 Reddit scraper...
   ✅ Reddit: 23 posts

Combined Sentiment:
- News: POSITIVE (0.65) from 5 articles
- Social: POSITIVE (0.58) from 23 posts
- Total Coverage: 28 data points
```

---

## 🎯 Recommendation

**Use BOTH for best results!**

1. Start aggregator in background
2. Configure any API keys you have
3. Let orchestrator use both sources
4. Get maximum market sentiment coverage

**If aggregator is down:** Direct scrapers provide solid fallback!

---

## 📚 See Also

- `AGGREGATOR_INTEGRATION.md` - Detailed aggregator guide
- `orchestrator_enhanced.py` - Implementation
- `aggregator/README.md` - Aggregator documentation

**Now you have the best of both worlds!** 🌍
