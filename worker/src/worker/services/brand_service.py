"""Brand-specific Redis services."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from ..redis_client import RedisClient
from ..config import get_settings

logger = logging.getLogger(__name__)

class BrandService:
    """Service for interacting with brand data in Redis."""

    def __init__(self, redis_client: RedisClient) -> None:
        self._redis = redis_client
        self._settings = get_settings()
        self._lock = asyncio.Lock()

    async def scan_brand_queues(self) -> list[str]:
        """Scan for brand-related queues."""
        # Scan for BOTH:
        # - data:brand:*:mentions: Live mentions that need sentiment/business analysis
        # - queue:brand:*:chunks: Batch chunks for clustering and deep analysis
        patterns = ["data:brand:*:mentions", "queue:brand:*:chunks"]
        results: list[str] = []
        
        try:
            for pattern in patterns:
                cursor = 0
                while True:
                    # Access inner client for scan
                    cursor, chunk = await self._redis.client.scan(cursor=cursor, match=pattern, count=100)
                    results.extend(chunk)
                    if cursor == 0:
                        break
            
            unique_results = sorted(set(results))
            if unique_results:
                logger.info(f"Found {len(unique_results)} brand queues: {unique_results[:5]}...")
            else:
                logger.debug(f"No brand queues found matching patterns: {', '.join(patterns)}")
            return unique_results
        except Exception as exc:
            logger.error("Scanning brand queues failed", extra={"context_error": str(exc)})
            return []

    async def get_brand_metadata(self, brand: str) -> dict[str, Any]:
        """Fetch brand metadata (including keywords) from Redis."""
        key = f"brand:{brand}:meta"
        try:
            data = await self._redis.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.error(f"Failed to fetch metadata for {brand}: {e}")
        return {}

    async def get_spike_history(self, brand: str, cluster_id: int) -> list[int]:
        """Get spike detection history for a cluster."""
        key = self._spike_key(brand, cluster_id)
        try:
            history = await self._redis.client.lrange(key, 0, -1)
            return [int(item) for item in history]
        except Exception as exc:
            logger.warning("Fetching spike history failed", extra={"context_error": str(exc)})
            return []

    async def append_spike_history(self, brand: str, cluster_id: int, value: int) -> None:
        """Append a value to the spike detection history."""
        key = self._spike_key(brand, cluster_id)
        try:
            async with self._lock:
                pipe = self._redis.client.pipeline()
                pipe.lpush(key, value)
                pipe.ltrim(key, 0, 99)
                pipe.expire(key, self._settings.spike_history_ttl_sec)
                await pipe.execute()
        except Exception as exc:
            logger.warning("Updating spike history failed", extra={"context_error": str(exc)})

    def _spike_key(self, brand: str, cluster_id: int) -> str:
        return f"{self._settings.redis_spike_prefix}{brand}:{cluster_id}"
