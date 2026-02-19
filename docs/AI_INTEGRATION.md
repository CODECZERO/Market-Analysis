# AI Integration Guide

## Provider Selection

### Worker Providers (Background Processing)

| Provider | Use Case | Cost | Accuracy | Latency |
|----------|----------|------|----------|---------|
| **Gemini 2.5 Flash** | Primary (Workers) | $0.075/1M tokens | High | ~400ms |
| **OpenAI GPT-4o-mini** | Fallback (Worker) | $0.15/1M tokens | High | ~500ms |
| **Mock LLM** | Development | Free | Low | ~10ms |

The Python worker supports multiple providers via `LLM_PROVIDER` env var:

```python
# worker/src/worker/llm_adapter.py

LLM_PROVIDER="gemini"    # Uses Gemini as primary
LLM_PROVIDER="openai"    # Uses OpenAI as primary
LLM_PROVIDER="mock"      # Uses mock for testing
```

### API Gateway Providers (Real-Time Features)

For fast AI responses without Worker roundtrip (Money Mode, Sales Pitch):

| Provider | Model | Use Case | Cost |
|----------|-------|----------|------|
| **Groq** | llama-3.3-70b-versatile | Sales Pitch, Chat | Free tier available |
| **NVIDIA NIM** | llama-3.1-nemotron-70b | Sales Pitch, Chat | API credits |
| **OpenRouter** | meta-llama/llama-3.1-70b | Fallback | Pay-per-use |

```typescript
// api-gateway/src/services/llm.service.ts
// Priority: GROQ_API_KEY > NVIDIA_API_KEY > OPENROUTER_API_KEY
```

### Sales Pitch Prompt Template

```
You are a veteran Sales Director with 50+ years of experience. You are helping {brand} convert a high-potential lead.

Your style is:
- Authoritative yet deeply empathetic
- Concise and direct (no fluff)
- Focused entirely on solving the user's specific pain point

Draft a response that:
1. Acknowledges their specific situation immediately.
2. Positions {brand} as the obvious solution without being "salesy".
3. Ends with a clear, low-friction Call to Action.
4. Is strictly under 4 sentences.
```

---

## Enhanced Analysis Prompts

### Sentiment + Emotion + Topics (Combined Prompt)

```
You are a sentiment analysis assistant analyzing brand mentions. For each text:

1. SENTIMENT: Rate from -1.0 (very negative) to +1.0 (very positive)
2. EMOTIONS: Rate each 0.0-1.0: joy, anger, fear, sadness, surprise, disgust
3. SARCASM: Is the text sarcastic? (true/false)
4. URGENCY: Classify as "high", "medium", or "low"
5. TOPICS: Tag with relevant categories from: product, support, pricing, feature, bug, competitor, praise, complaint

Return JSON:
{
  "sentiment": 0.75,
  "emotions": {
    "joy": 0.8,
    "anger": 0.0,
    "fear": 0.0,
    "sadness": 0.0,
    "surprise": 0.1,
    "disgust": 0.0
  },
  "isSarcastic": false,
  "urgency": "low",
  "topics": ["product", "praise"]
}

Texts:
{texts}
```

### Crisis Keywords Detection

High-urgency keywords that trigger immediate alerts:

```python
CRISIS_KEYWORDS = [
    "scam", "fraud", "lawsuit", "breach", "hack", 
    "data leak", "security", "outage", "down",
    "lawsuit", "sued", "class action", "recall",
    "investigation", "regulators", "SEC", "FTC"
]
```

---

## Language Detection

Using `langdetect` library before LLM processing:

```python
from langdetect import detect

def detect_language(text: str) -> str:
    try:
        return detect(text)  # Returns ISO 639-1 code
    except:
        return "en"  # Default to English
```

---

## Brand Health Score Calculation

```python
def calculate_health_score(brand_id: str) -> float:
    # 40% - Average sentiment (7 days)
    sentiment_avg = get_avg_sentiment(brand_id, days=7)
    sentiment_score = (sentiment_avg + 1) / 2 * 100  # Normalize to 0-100
    
    # 25% - Volume growth vs baseline
    current_volume = get_mention_count(brand_id, days=7)
    baseline_volume = get_mention_count(brand_id, days=30) / 4
    growth_ratio = current_volume / baseline_volume if baseline_volume > 0 else 1
    volume_score = min(growth_ratio * 50, 100)  # Cap at 100
    
    # 20% - Engagement rate
    engagement = get_engagement_rate(brand_id, days=7)
    engagement_score = min(engagement * 100, 100)
    
    # 15% - Crisis deduction
    crisis_count = get_crisis_count(brand_id, days=7)
    crisis_deduction = min(crisis_count * 10, 100)
    crisis_score = 100 - crisis_deduction
    
    # Weighted average
    health = (
        sentiment_score * 0.40 +
        volume_score * 0.25 +
        engagement_score * 0.20 +
        crisis_score * 0.15
    )
    
    return round(health, 1)
```

---

## Rate Limiting & Costs

### OpenAI Limits
- RPM: 500 (Tier 1)
- TPM: 200,000 (Tier 1)

### Gemini Limits
- RPM: 1,500 (Free tier)
- TPD: 1.5M tokens (Free tier)

### Cost Estimation

For 10,000 mentions/day:
- Average tokens per mention: ~200
- Daily tokens: 2M tokens

| Provider | Daily Cost | Monthly Cost |
|----------|------------|--------------|
| GPT-4o-mini | $0.30 | $9.00 |
| Gemini Flash | $0.15 | $4.50 |
| Mixed (80/20) | $0.27 | $8.10 |

---

## Fallback Strategy

```python
async def analyze_with_fallback(text: str):
    try:
        return await primary_llm.analyze(text)
    except Exception as e:
        logger.warning(f"Primary LLM failed: {e}")
        try:
            return await fallback_llm.analyze(text)
        except Exception as e2:
            logger.error(f"Fallback LLM failed: {e2}")
            return heuristic_analysis(text)
```

---

## Environment Variables

```env
# Primary LLM
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-2.5-flash

# Fallback LLM
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini

# Processing
LLM_TIMEOUT_SEC=30
LLM_MAX_CONCURRENCY=4
LLM_SUMMARY_MAX_TOKENS=256
EMBEDDINGS_BATCH_SIZE=32
```

---

## Rust Worker AI Integration

The Rust Worker now has **full LLM feature parity** with the Python Worker:

### LLM Methods Available (`llm.rs`)

| Method | Purpose |
|--------|---------|
| `summarize()` | Summarize brand mentions |
| `sentiment()` | Basic sentiment analysis |
| `analyze_enhanced()` | Full analysis (sentiment, emotions, topics, entities) |
| `analyze_lead_intent()` | Money Mode lead scoring |
| `analyze_risk()` | Crisis detection |
| `analyze_competitor_complaints()` | Market Gap analysis |
| `analyze_commercial_intent()` | Commercial/purchase intent |
| `generate_response_suggestion()` | Customer service responses |
| `analyze_web_content()` | Web intelligence |
| `generate_insights()` | Deep scan reports |
| `detect_launch_potential()` | The Oracle predictions |
| `analyze_crisis_severity()` | Detailed crisis assessment |
| `categorize_complaint()` | Competitor weakness analysis |
| `batch_analyze()` | Efficient batch processing |

### Fallback Analysis (`fallback_analysis.rs`)

When LLM is unavailable, Rust uses regex-based fallback:

```rust
// 40+ positive/negative word lists
// Intent patterns: HOT_LEAD, CHURN_RISK, BUG_REPORT, FEATURE_REQUEST
// Emotion detection: joy, anger, fear, sadness, surprise, disgust
// Lead score calculation (0-100)
// Sarcasm detection
```

### Health Score (`health_score.rs`)

```rust
// 40% - Sentiment average (7 days)
// 25% - Volume trend
// 20% - Engagement rate
// 15% - Crisis deduction
let health_score = sentiment * 0.40 + volume * 0.25 + engagement * 0.20 + crisis * 0.15;
```

### Organized Prompts (`prompts.rs`)

All LLM prompts are centralized in `prompts.rs`:
- `BRAND_ANALYSIS_PROMPT`
- `STRATEGIC_INTELLIGENCE_PROMPT`
- `COMMERCIAL_INTENT_PROMPT`
- `SALES_PITCH_PROMPT`
- `CRISIS_SEVERITY_PROMPT`
- `COMPETITOR_COMPLAINT_PROMPT`
- `LAUNCH_PREDICTION_PROMPT`

