# Python Worker Service Documentation

## Overview

The Python Worker handles **AI/ML-intensive processing** including sentiment analysis, LLM inference, embeddings, and crisis detection. It serves as a fallback when the Rust worker is unavailable.

| Property | Value |
|----------|-------|
| Port | 8000 |
| Framework | FastAPI |
| RAM Usage | ~500MB |
| Language | Python 3.11+ |

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | FastAPI, Uvicorn |
| Queue | Redis (hiredis) |
| Database | MongoDB (motor, pymongo) |
| HTTP | aiohttp, httpx, requests |
| LLM | LangChain (Gemini, OpenAI, Groq, Ollama, NVIDIA) |
| ML | scikit-learn, numpy |
| NLP | vaderSentiment, tiktoken |
| Web Scraping | BeautifulSoup4 |
| Metrics | prometheus-client |

---

## Directory Structure

```
worker/src/worker/
├── app.py                # FastAPI entry point
├── config.py             # Environment configuration
├── processor.py          # Main task processor (44KB)
├── analyzer.py           # 3-Tier Intelligence Engine
├── llm_adapter.py        # Multi-provider LLM adapter (35KB)
├── llm_executor.py       # LLM execution layer
├── embeddings.py         # Vector embeddings
├── clustering.py         # K-Means clustering
├── storage.py            # MongoDB persistence (31KB)
├── redis_client.py       # Redis operations
├── queue_worker.py       # Queue consumer
├── queue_consumer.py     # Task polling
├── batch_processor.py    # Batch processing
├── crisis_detector.py    # Crisis thermometer
├── spike_detector.py     # Volume spike detection
├── health_score.py       # Brand health calculation
├── competitor_discovery.py # AI competitor detection
├── fallback_analysis.py  # Heuristic fallback (22KB)
├── janitor.py            # Smart GC / data cleanup
├── web_scraper.py        # Web content extraction
├── bluesky_scraper.py    # Bluesky integration
├── handlers/             # Task handlers
├── llm/                  # LLM provider implementations
├── pipeline/             # Processing pipelines
└── services/             # Business services
```

---

## LLM Providers

| Provider | Package | Model |
|----------|---------|-------|
| Google Gemini | langchain-google-genai | gemini-2.5-flash |
| OpenAI | langchain-openai | gpt-4o-mini |
| Groq | langchain-groq | llama-3.3-70b |
| NVIDIA | langchain-nvidia-ai-endpoints | nemotron-70b |
| Ollama | langchain-ollama | Local models |

Priority order configurable via `LLM_PROVIDER` env var.

---

## Core Components

### Processor (`processor.py`)
- Main task routing (44KB, handles all task types)
- Content deduplication
- Priority queue management

### Analyzer (`analyzer.py`)
- 3-Tier Intelligence Engine implementation
- Regex-based fast filtering (90% cost reduction)
- Intent classification

### LLM Adapter (`llm_adapter.py`)
- Multi-provider abstraction
- Fallback chain
- Retry logic with exponential backoff

### Storage (`storage.py`)
- MongoDB operations
- Processed chunk persistence
- Historical data management

### Crisis Detector
- Velocity tracking
- Sentiment intensity monitoring
- Trigger reason analysis

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `REDIS_URL` | Redis connection |
| `MONGODB_URI` | MongoDB connection |
| `LLM_PROVIDER` | Primary provider (gemini/openai/groq) |
| `GEMINI_API_KEY` | Google Gemini API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `GROQ_API_KEY` | Groq API key |
| `NVIDIA_API_KEY` | NVIDIA API key |
| `LOG_LEVEL` | Logging level |

---

## Running

```bash
# Setup virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the worker
python -m src.worker.app
```

---

## Janitor (Scheduled Cleanup)

```bash
# Run via Docker Compose
docker-compose run --rm janitor

# Or directly
python -m src.worker.janitor
```

The janitor performs:
- Smart GC (AI-powered compression before eviction)
- Redis memory management
- Historical data archiving
