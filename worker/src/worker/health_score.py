"""Brand health score calculator based on mentions and sentiment data."""
from __future__ import annotations

import logging
import json
from datetime import datetime, timezone
from typing import Any, List

from .logger import get_logger, log_with_context
from .domain_types import EnhancedAnalysis

logger = get_logger(__name__)


class HealthScoreCalculator:
    """
    Calculate brand health score (0-100) based on:
    - 40% Sentiment average (7 days)
    - 25% Volume trend
    - 20% Engagement rate
    - 15% Crisis deduction
    """

    def __init__(self, redis_client, worker_id: str) -> None:
        self._redis = redis_client
        self._worker_id = worker_id

    async def calculate(self, brand: str, analysis_results: List[EnhancedAnalysis]) -> float:
        """
        Calculate health score from recent analysis results.
        
        Args:
            brand: Brand identifier
            analysis_results: List of enhanced analysis results from recent processing
            
        Returns:
            Health score from 0 to 100
        """
        if not analysis_results:
            # Try to fetch last known score or return default
            last_score = await self.get_score(brand)
            return last_score if last_score is not None else 50.0
        
        # 40% - Sentiment Score (average of sentiment_score, normalized to 0-100)
        sentiment_scores = [a.sentiment_score for a in analysis_results]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        # Convert from [-1, 1] to [0, 100]
        sentiment_component = ((avg_sentiment + 1) / 2) * 100

        # 25% - Volume Score (based on number of mentions)
        # More mentions = more visibility (capped at 100)
        # Assuming this is a chunk, we might want to scale this differently or rely on aggregation
        volume_score = min(len(analysis_results) * 5, 100)

        # 20% - Engagement Score (based on variety of topics)
        all_topics = []
        for a in analysis_results:
            all_topics.extend(a.topics)
        unique_topics = len(set(all_topics))
        engagement_score = min(unique_topics * 10, 100)

        # 15% - Crisis Deduction (high urgency = bad)
        high_urgency_count = sum(1 for a in analysis_results if a.urgency == "high")
        crisis_ratio = high_urgency_count / len(analysis_results) if analysis_results else 0
        crisis_deduction = crisis_ratio * 100
        crisis_score = max(0, 100 - crisis_deduction)

        # Weighted average
        health_score = (
            sentiment_component * 0.40 +
            volume_score * 0.25 +
            engagement_score * 0.20 +
            crisis_score * 0.15
        )

        # Clamp to 0-100
        health_score = max(0.0, min(100.0, health_score))

        log_with_context(
            logger,
            level=logging.INFO,
            message="Health score calculated",
            context={
                "worker_id": self._worker_id,
                "brand": brand,
                "mentions_count": len(analysis_results),
                "avg_sentiment": avg_sentiment,
            },
            metrics={
                "health_score": health_score,
                "sentiment_component": sentiment_component,
                "volume_score": volume_score,
                "engagement_score": engagement_score,
                "crisis_score": crisis_score,
            },
        )

        final_score = round(health_score, 1)
        
        # Store it immediately for persistence across chunks
        await self.store_score(brand, final_score)
        
        return final_score

    async def store_score(self, brand: str, score: float) -> None:
        """Store health score in Redis for API access."""
        key = f"health:brand:{brand}"
        data = {
            "score": score,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        # Store for 24 hours
        await self._redis.set(key, json.dumps(data), ex=86400)

    async def get_score(self, brand: str) -> float | None:
        """Retrieve stored health score."""
        key = f"health:brand:{brand}"
        result = await self._redis.get(key)
        if result:
            try:
                data = json.loads(result)
                return float(data.get("score", 50.0))
            except (JSONDecodeError, ValueError):
                return None
        return None

def calculate_simple_health_score(analysis_results: List[dict[str, Any]]) -> float:
    """
    Simple synchronous health score calculation for use outside async context.
    
    Args:
        analysis_results: List of analysis result dicts
        
    Returns:
        Health score from 0 to 100
    """
    if not analysis_results:
        return 50.0
    
    sentiment_scores = [
        r.get("sentiment_score", 0.0) for r in analysis_results
    ]
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
    
    # Simple calculation
    sentiment_component = ((avg_sentiment + 1) / 2) * 100
    
    high_urgency = sum(1 for r in analysis_results if r.get("urgency") == "high")
    crisis_deduction = (high_urgency / len(analysis_results)) * 30 if analysis_results else 0
    
    health = sentiment_component - crisis_deduction
    return max(0.0, min(100.0, round(health, 1)))
