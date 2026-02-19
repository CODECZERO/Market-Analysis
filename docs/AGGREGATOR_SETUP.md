# 🎯 Starting Aggregator Service for Real Sentiment Data

## What is the Aggregator?

The aggregator service collects real-time mentions from multiple platforms:
- **Reddit**: Discussions about stocks
- **Twitter/X**: Tweets with stock symbols/hashtags
- **News APIs**: Financial news articles
- **Bluesky**: Social media mentions
- **Hacker News**: Tech/business discussions

## How to Start the Aggregator

### Option 1: Using Docker (Recommended)
```bash
cd ../aggregator
docker-compose up -d
```

### Option 2: Manual Start
```bash
cd ../aggregator
npm install
npm start
```

The aggregator will start on **http://localhost:4001**

## After Starting Aggregator

Once the aggregator is running, the Ultimate CLI will automatically:
1. Connect to the aggregator
2. Create temporary "brands" for stock symbols
3. Fetch real mentions from all platforms
4. Analyze sentiment using VADER (social) and FinBERT (news)
5. Display LIVE sentiment data with actual mention counts

## CLI Behavior

**With Aggregator Running:**
- Shows `[LIVE DATA]` badge
- Real mention counts from each platform
- Accurate sentiment based on actual discussions
- Total mentions displayed

**Without Aggregator:**
- Shows `[BASELINE]` badge
- Uses estimated/simulated sentiment
- Still works, but data is not real-time

## Testing

```bash
# Start aggregator
cd ../aggregator && npm start

# In another terminal, run CLI
cd market_analysis
./ultimate.sh

# Select any stock to see LIVE sentiment!
```

## Environment Variables (Optional)

Set these in `.env` for better data:

```bash
#Twitter API (for more data)
TWITTER_BEARER_TOKEN=your_token_here

# News API
NEWS_API_KEY=your_key_here

# Reddit (optional, works without)
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
```

Without these, the aggregator still works using free methods (Nitter for Twitter, web scraping for Reddit, etc.)

## Verification

The CLI will show in the sentiment section:
```
Data source: Aggregator service (Reddit, X/Twitter, News APIs)
```

vs

```
Data source: Baseline estimate (start aggregator for live data)
```

---

**Ready to see real sentiment data?** Start the aggregator and launch `./ultimate.sh`! 🚀
