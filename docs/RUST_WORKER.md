# Rust Worker Service Documentation

## Overview

The Rust Worker is the **primary high-performance processing engine** designed for minimal memory footprint, enabling free-tier cloud deployment. It handles 99% of the workload.

| Property | Value |
|----------|-------|
| Port | 3000 |
| Framework | Axum + Tokio |
| RAM Usage | ~50MB |
| Package Name | `argos-worker` |

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Runtime | Tokio (async) |
| HTTP | Axum |
| Queue | Redis |
| Database | MongoDB |
| ML | smartcore (K-Means) |
| HTTP Client | reqwest |
| Regex | regex |
| Web Scraping | scraper |
| Hashing | sha2, hex |
| Metrics | prometheus |
| Tracing | tracing, tracing-subscriber |

---

## Directory Structure

```
rust-worker/src/
├── main.rs              # Entry point, task supervision
├── processor.rs         # Main task router (892 lines)
├── analyzer.rs          # 3-Tier Intelligence Engine (1009 lines)
├── llm.rs               # LLM adapter (680 lines)
├── regex_sentiment.rs   # Regex-based sentiment (277 lines)
├── clustering.rs        # K-Means clustering
├── spike_detector.rs    # Volume spike detection
├── gc.rs                # Smart garbage collection
├── web_scraper.rs       # Enhanced web scraping (347 lines)
├── envelope.rs          # Message envelope types
├── metrics.rs           # Prometheus metrics
│
├── # NEW: Feature Parity Modules
├── fallback_analysis.rs # Regex fallback (539 lines)
├── storage.rs           # MongoDB persistence (484 lines)
├── prompts.rs           # LLM prompts (376 lines)
├── crisis_detector.rs   # Crisis detection (349 lines)
├── batch_processor.rs   # Mention batching (342 lines)
├── competitor_discovery.rs # Market Gap (340 lines)
├── domain_types.rs      # Type definitions (340 lines)
├── config.rs            # Configuration (252 lines)
├── health_score.rs      # Health scoring (247 lines)
│
└── tasks/               # Task handlers
    ├── mod.rs
    ├── cluster_handler.rs
    ├── competitor_handler.rs
    ├── crisis_handler.rs
    ├── lead_handler.rs
    └── web_handler.rs
```

**Total: 7,246 lines of Rust code across 26 files**


---

## Core Components

### Processor (`processor.rs` - 38KB)
- Main task routing and dispatch
- MongoDB persistence
- Priority queue management
- Content fingerprinting (SHA256)

### Analyzer (`analyzer.rs` - 36KB)
- **3-Tier Intelligence Engine** implementation
- Layer 1: Regex gatekeeper (90% noise filter)
- Layer 2: Gemini AI disambiguation
- Layer 3: Priority assignment

### LLM (`llm.rs` - 17KB)
- Gemini API integration
- Prompt construction
- Response parsing
- Error handling with retries

### Regex Sentiment (`regex_sentiment.rs` - 9KB)
Pre-compiled regex patterns for fast filtering:
- LEAD patterns: "switching to", "alternative", "recommend"
- PAIN patterns: "hate", "broken", "scam", "crash"
- PURCHASE patterns: "buy", "pricing", "demo"
- LAUNCH patterns: "announcing", "v2.0", "now available"

### Clustering (`clustering.rs`)
- K-Means clustering via smartcore
- TF-IDF vectorization
- Topic grouping

### Smart GC (`gc.rs`)
- Redis memory monitoring
- AI-powered compression before eviction
- Historical archive to MongoDB

### Spike Detector
```rust
let threshold = f64::max(10.0, historical_average * 2.0);
let is_spike = (current_count as f64) > threshold;
```

---

## Task Handlers

| Handler | Purpose |
|---------|---------|
| `cluster_handler.rs` | Topic clustering |
| `competitor_handler.rs` | Competitor analysis |
| `crisis_handler.rs` | Crisis detection |
| `lead_handler.rs` | Lead qualification (Money Mode) |
| `web_handler.rs` | Web scraping tasks |

---

## New Feature Parity Modules

These modules were added to achieve feature parity with the Python Worker:

### Storage (`storage.rs` - 484 lines)
MongoDB persistence layer for all processed data:
- `ProcessedChunkDoc` - Save analyzed chunks
- `LeadDoc` - Hot leads for Money Mode
- `CrisisEventDoc` - Crisis events
- Buffer flushing for batch writes
- Redis push for real-time dashboard

### Fallback Analysis (`fallback_analysis.rs` - 539 lines)
Regex-based fallback when LLM is unavailable:
- 40+ positive/negative word lists
- Intent patterns: `HOT_LEAD`, `CHURN_RISK`, `BUG_REPORT`, `FEATURE_REQUEST`
- Emotion detection (joy, anger, fear, etc.)
- Lead score calculation (0-100)
- Sarcasm detection

### Health Score (`health_score.rs` - 247 lines)
Brand health calculation:
```rust
// 40% Sentiment + 25% Volume + 20% Engagement + 15% Crisis
let score = sentiment * 0.40 + volume * 0.25 + engagement * 0.20 + crisis * 0.15;
```

### Crisis Detector (`crisis_detector.rs` - 349 lines)
Full crisis detection with:
- 25+ crisis keywords
- Severity levels: Critical, Warning, Normal
- Sentiment decline tracking

### Competitor Discovery (`competitor_discovery.rs` - 340 lines)
Market Gap Analysis:
- Complaint categorization (pricing, support, features, etc.)
- Opportunity scoring
- Competitive intelligence

### Prompts (`prompts.rs` - 376 lines)
Centralized LLM prompt templates for all analysis types.

### Config (`config.rs` - 252 lines)
Structured configuration with environment variable loading.

### Domain Types (`domain_types.rs` - 340 lines)
Core data structures: `Mention`, `Chunk`, `Lead`, `CrisisEvent`, etc.

### Batch Processor (`batch_processor.rs` - 342 lines)
Mention normalization and deduplication.

### LLM Adapter (`llm.rs` - 680 lines)
14 LLM methods including:
- `analyze_commercial_intent()` - Money Mode
- `generate_response_suggestion()` - Customer service
- `detect_launch_potential()` - The Oracle
- `analyze_crisis_severity()` - Crisis assessment

---

## Why Rust?

| Metric | Rust Worker | Python Worker |
|--------|-------------|---------------|
| RAM | ~50MB | ~500MB |
| Free Tier | ✅ Fits Render 512MB | ❌ Too heavy |
| Cold Start | Fast | Slow |
| Concurrency | Excellent (Tokio) | Good (asyncio) |

> The 50MB footprint allows deployment on **Render Free Tier (512MB limit)** where Python ML stacks would fail.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PORT` | Server port (default: 3000) |
| `REDIS_URL` | Redis connection |
| `MONGODB_URI` | MongoDB connection |
| `GEMINI_API_KEY` | Google Gemini API key |
| `LLM_PROVIDER` | Provider (gemini) |
| `LOG_LEVEL` | Logging level |

---

## Building & Running

```bash
# Development
cargo run

# Release build
cargo build --release

# Run tests
cargo test

# Docker
docker build -t rust-worker .
docker run -p 3000:3000 rust-worker
```

---

## Key Algorithms

### Content Deduplication
```rust
pub fn generate_content_hash(source_url: &str, text: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(source_url.as_bytes());
    hasher.update(b"|");
    hasher.update(text.as_bytes());
    hex::encode(hasher.finalize())
}
```

### Priority Assignment
```
P0 CRITICAL → CRITICAL_ALERT or (CHURN_RISK + sentiment < -0.7)
P1 HIGH     → OPPORTUNITY_TO_STEAL or HOT_LEAD or CHURN_RISK
P2 MEDIUM   → BUG_REPORT or FEATURE_REQUEST
P3 LOW      → PRAISE or GENERAL
```
