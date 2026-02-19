"""Pipeline component for publishing results."""
import logging
import json
from datetime import datetime, timezone
from typing import List, Any

from ..logger import get_logger
from ..domain_types import Chunk, ChunkResult, ClusterResult
from ..storage import ResultStorage

logger = get_logger(__name__)

class ResultPublisher:
    """Handles persistence and broadcasting of processing results."""

    def __init__(self, worker_id: str, redis_client, storage: ResultStorage):
        self._worker_id = worker_id
        self._redis = redis_client
        self._storage = storage

    async def publish_metrics(self, brand: str, chunk_id: str, cluster_count: int, mention_count: int) -> None:
        """Publish WebSocket event for real-time dashboard updates."""
        try:
            channel = f"events:brand:{brand}"
            event_data = {
                "type": "chunk_processed",
                "brand": brand,
                "chunkId": chunk_id,
                "clusterCount": cluster_count,
                "mentionCount": mention_count,
            }
            await self._redis.publish(channel, json.dumps(event_data))
            logger.info(f"[WS] Published event to {channel}")
        except Exception as e:
            logger.error(f"[WS] Failed to publish event: {e}")

    async def persist_results(self, chunk: Chunk, result: ChunkResult, envelope: dict = None) -> None:
        """Persist analysis results to MongoDB and Redis."""
        if not self._storage or not envelope:
            return

        # 1. MongoDB Save
        await self._storage.save_result(envelope, result.model_dump())

        # 2. Update Brand Summary (Sentiment, Health Score)
        # We need to calculate health score here or pass it?
        # Processor calculated it. Ideally Publisher takes the calculated values.
        # But for now let's assume result contains necessary info or we update usage.
        
        # 3. Push Spike Timeline
        if result.spikeDetected:
            spike_event = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "spikeScore": 1.0, 
                "mentionCount": len(enumerate(result.clusters).__next__()[1].examples) if result.clusters else 0, # Rough approx
                "clusters": [{"id": c.cluster_id, "label": c.summary or ""} for c in result.clusters if c.spike]
            }
            # Fix mentionCount logic: we don't have total mentions in result easily unless valid_mentions passed
            # We will rely on caller to construct spike event or pass data
            pass 

    async def publish_mention_stats(self, brand: str, mentions: List[Any]) -> None:
        """Publish analyzed mentions to the timeline."""
        if mentions and self._storage:
            await self._storage.push_mention_stats(brand, mentions)

    async def publish_leads(self, brand: str, leads: List[Any]) -> None:
        if leads and self._storage:
            await self._storage.push_leads(brand, leads)

    async def publish_crisis(self, brand: str, event: dict, metrics: dict) -> None:
         if self._storage:
             await self._storage.push_crisis_event(brand, event)
             await self._storage.update_crisis_metrics(brand, metrics)

    async def update_brand_summary(self, brand: str, result: ChunkResult, health_score: float) -> None:
        if self._storage:
             await self._storage.update_brand_summary(brand, result, health_score=health_score)

