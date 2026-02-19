# Aggregator Service Documentation

## Overview

The Aggregator is a **multi-source data collection service** that polls 10 external data sources, normalizes mentions, and pushes them to Redis for processing.

| Property | Value |
|----------|-------|
| Port | 4001 |
| Framework | Express.js |
| Language | TypeScript (ESM) |
| Package Name | `@rapidquest/aggregator` |

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | Express.js |
| HTTP Client | Axios |
| HTML Parsing | Cheerio |
| Fuzzy Search | Fuse.js |
| String Matching | fastest-levenshtein |
| Database | MongoDB, Redis |
| RSS | rss-parser |
| Scheduler | node-cron |
| Logging | Pino |
| Metrics | prom-client |

---

## Directory Structure

```
aggregator/src/modules/aggregator/
├── controllers/       # HTTP route controllers
├── providers/         # 10 data source providers
│   ├── reddit.provider.ts
│   ├── x.provider.ts
│   ├── hackernews.provider.ts
│   ├── news.provider.ts
│   ├── google.provider.ts
│   ├── bluesky.provider.ts
│   ├── rss.provider.ts
│   ├── duckduckgo.provider.ts
│   ├── youtube-search.provider.ts
│   └── social-web.provider.ts
├── routes/            # Express routes
├── services/          # Business logic
│   ├── aggregator.service.ts
│   ├── deduplication.service.ts
│   ├── normalizer.service.ts
│   ├── redis-writer.service.ts
│   ├── smart-matcher.service.ts
│   └── validator.service.ts
└── types/             # TypeScript types
```

---

## Data Source Providers (10)

| Provider | Source | Method |
|----------|--------|--------|
| Reddit | reddit.com | API + Web scraping |
| X/Twitter | twitter.com | API |
| HackerNews | news.ycombinator.com | Algolia API |
| News | Various news APIs | REST APIs |
| Google | google.com | Search API |
| Bluesky | bsky.app | AT Protocol |
| RSS | Various | rss-parser |
| DuckDuckGo | duckduckgo.com | Search API |
| YouTube | youtube.com | Search API |
| SocialWeb | Generic | Web scraping |

---

## Services

| Service | Purpose |
|---------|---------|
| `aggregator.service.ts` | Orchestrates provider polling |
| `deduplication.service.ts` | SHA256-based content fingerprinting |
| `normalizer.service.ts` | Normalize mentions to common schema |
| `smart-matcher.service.ts` | Fuzzy brand matching |
| `validator.service.ts` | Validate mention structure |
| `redis-writer.service.ts` | Push to Redis queues |

---

## Data Flow

```
1. Cron triggers polling (node-cron)
2. Each provider fetches from its source
3. Raw mentions normalized to common schema
4. Deduplication (content hash)
5. Smart matching (brand detection)
6. Validation
7. Push to Redis queue for worker processing
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PORT` | Server port (default: 4001) |
| `REDIS_URL` | Redis connection |
| `MONGODB_URI` | MongoDB connection |
| `REDDIT_CLIENT_ID` | Reddit API |
| `REDDIT_CLIENT_SECRET` | Reddit API |
| `NEWS_API_KEY` | News API key |
| `GOOGLE_API_KEY` | Google Search API |
| `YOUTUBE_API_KEY` | YouTube Data API |

---

## Scripts

```bash
npm run dev    # Development with tsx watch
npm run build  # Compile TypeScript
npm run start  # Run production build
```
