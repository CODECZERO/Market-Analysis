"""Crisis detector that monitors sentiment and mention patterns for crisis conditions."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from .config import get_settings
from .logger import get_logger, log_with_context
from .domain_types import EnhancedAnalysis

logger = get_logger(__name__)


class CrisisDetector:
    """
    Detect crisis conditions based on:
    - Rapid sentiment decline
    - High urgency mentions
    - Spike in negative mentions
    - Keyword triggers
    """

    CRISIS_KEYWORDS = [
        "breach", "hack", "lawsuit", "boycott", "scandal", "outage",
        "fraud", "recall", "safety", "injury", "death", "crash",
        "leak", "exposed", "investigation", "charged", "arrested",
    ]

    def __init__(self, redis_client, worker_id: str) -> None:
        self._redis = redis_client
        self._worker_id = worker_id
        self._settings = get_settings()

    async def check_for_crisis(
        self,
        brand: str,
        current_analysis: list[EnhancedAnalysis],
        mention_texts: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Check current analysis results for crisis conditions.
        
        Returns:
            Dict with crisis detection results:
            - is_crisis: bool
            - severity: "critical" | "warning" | "normal"
            - reasons: list of triggered conditions
            - recommended_action: str
        """
        result = {
            "is_crisis": False,
            "severity": "normal",
            "reasons": [],
            "recommended_action": "No action required",
            "metrics": {},
        }

        if not current_analysis:
            return result

        # Calculate metrics
        avg_sentiment = sum(a.sentiment_score for a in current_analysis) / len(current_analysis)
        high_urgency_count = sum(1 for a in current_analysis if a.urgency == "high")
        high_urgency_ratio = high_urgency_count / len(current_analysis)
        negative_count = sum(1 for a in current_analysis if a.sentiment_label == "negative")
        negative_ratio = negative_count / len(current_analysis)

        result["metrics"] = {
            "avg_sentiment": avg_sentiment,
            "high_urgency_ratio": high_urgency_ratio,
            "negative_ratio": negative_ratio,
            "mention_count": len(current_analysis),
        }

        # Check historical sentiment for rapid decline
        prev_sentiment = await self._get_previous_sentiment(brand)
        if prev_sentiment is not None:
            sentiment_drop = prev_sentiment - avg_sentiment
            if sentiment_drop >= 0.5:  # 50% decline on -1 to 1 scale
                result["reasons"].append(f"Rapid sentiment decline: {sentiment_drop:.2f} points")
                result["is_crisis"] = True
                result["severity"] = "critical"

        # Check high urgency ratio
        if high_urgency_ratio >= 0.5:
            result["reasons"].append(f"High urgency ratio: {high_urgency_ratio:.1%}")
            result["is_crisis"] = True
            if result["severity"] != "critical":
                result["severity"] = "warning"

        # Check negative sentiment ratio
        if negative_ratio >= 0.7 and len(current_analysis) >= 5:
            result["reasons"].append(f"High negative sentiment ratio: {negative_ratio:.1%}")
            result["is_crisis"] = True
            if result["severity"] != "critical":
                result["severity"] = "warning"

        # Check for crisis keywords
        if mention_texts:
            triggered_keywords = self._check_keywords(mention_texts)
            if triggered_keywords:
                result["reasons"].append(f"Crisis keywords detected: {', '.join(triggered_keywords)}")
                result["is_crisis"] = True
                result["severity"] = "critical"

        # Check for extreme negative sentiment
        if avg_sentiment < -0.7:
            result["reasons"].append(f"Extremely negative average sentiment: {avg_sentiment:.2f}")
            result["is_crisis"] = True
            result["severity"] = "critical"

        # Set recommended action
        if result["severity"] == "critical":
            result["recommended_action"] = "Immediate response required. Escalate to crisis management team."
        elif result["severity"] == "warning":
            result["recommended_action"] = "Monitor closely. Prepare response if situation escalates."

        # Store current sentiment for future comparison
        await self._store_sentiment(brand, avg_sentiment)

        if result["is_crisis"]:
            log_with_context(
                logger,
                level=logging.WARNING,
                message="Crisis detected",
                context={
                    "worker_id": self._worker_id,
                    "brand": brand,
                    "severity": result["severity"],
                    "reasons": result["reasons"],
                },
                metrics=result["metrics"],
            )

        return result

    def _check_keywords(self, texts: list[str]) -> list[str]:
        """Check for crisis keywords in mention texts."""
        triggered = set()
        combined_text = " ".join(texts).lower()
        
        for keyword in self.CRISIS_KEYWORDS:
            if keyword in combined_text:
                triggered.add(keyword)
        
        return list(triggered)

    async def _get_previous_sentiment(self, brand: str) -> float | None:
        """Get previous sentiment score from Redis."""
        key = f"crisis:sentiment:{brand}"
        try:
            value = await self._redis.get(key)
            if value:
                return float(value)
        except Exception as e:
            logger.warning(f"Failed to get previous sentiment: {e}")
        return None

    async def _store_sentiment(self, brand: str, sentiment: float) -> None:
        """Store current sentiment for future comparison."""
        key = f"crisis:sentiment:{brand}"
        try:
            await self._redis.set(key, str(sentiment), ex=3600)  # 1 hour TTL
        except Exception as e:
            logger.warning(f"Failed to store sentiment: {e}")


async def check_crisis_conditions(
    brand: str,
    analysis_results: list[dict[str, Any]],
    mention_texts: list[str] | None = None,
) -> dict[str, Any]:
    """
    Synchronous helper to check for crisis without Redis.
    For simple integrations.
    """
    result = {
        "is_crisis": False,
        "severity": "normal",
        "reasons": [],
    }

    if not analysis_results:
        return result

    # Calculate metrics
    avg_sentiment = sum(r.get("sentiment_score", 0) for r in analysis_results) / len(analysis_results)
    high_urgency = sum(1 for r in analysis_results if r.get("urgency") == "high")
    high_urgency_ratio = high_urgency / len(analysis_results)

    # Check crisis conditions
    if avg_sentiment < -0.5 and high_urgency_ratio >= 0.3:
        result["is_crisis"] = True
        result["severity"] = "warning"
        result["reasons"].append("Negative sentiment with high urgency mentions")

    if avg_sentiment < -0.7:
        result["is_crisis"] = True
        result["severity"] = "critical"
        result["reasons"].append("Critically negative sentiment")

    if high_urgency_ratio >= 0.5:
        result["is_crisis"] = True
        result["severity"] = "warning" if result["severity"] != "critical" else "critical"
        result["reasons"].append("Majority high urgency mentions")

    # Check keywords
    if mention_texts:
        crisis_words = ["breach", "hack", "lawsuit", "boycott", "scandal", "outage"]
        combined = " ".join(mention_texts).lower()
        found = [w for w in crisis_words if w in combined]
        if found:
            result["is_crisis"] = True
            result["severity"] = "critical"
            result["reasons"].append(f"Keywords: {', '.join(found)}")

    return result
