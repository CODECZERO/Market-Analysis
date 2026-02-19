from __future__ import annotations
import logging
import json
import time
import html
import re
import uuid
from datetime import datetime, timezone
from typing import Any, List, Optional, Dict

from .domain_types import Chunk, Mention
from .utils import safe_json_loads
from .logger import get_logger

logger = get_logger(__name__)

from .services.brand_service import BrandService

class BatchProcessor:
    """Handles the extraction, normalization, and batching of raw queue items."""

    def __init__(self, redis_client, brand_service: BrandService):
        self._redis = redis_client
        self._brand_service = brand_service

    async def process_batch(self, brand_hint: str, payloads: List[str]) -> Optional[Chunk]:
        """
        Processes a list of raw payloads into a single Chunk object.
        Handles JSON parsing, deduplication, and normalization.
        """
        batched_mentions: List[Dict[str, Any]] = []
        batch_chunk_id = f"{brand_hint}-batch-{int(time.time()*1000)}"

        for i, payload in enumerate(payloads):
            try:
                raw_data = safe_json_loads(payload)
            except ValueError as exc:
                logger.error(f"Invalid JSON in batch for {brand_hint}: {exc}", extra={"payload": payload})
                continue

            # Case A: Indivdual Mention (Standard)
            if "text" in raw_data and "timestamp" in raw_data and "source" in raw_data:
                # Deduplication
                mention_id = raw_data.get("id")
                if mention_id:
                    dedup_key = f"processed:brand:{brand_hint}:ids"
                    already_processed = await self._redis.client.sismember(dedup_key, mention_id)
                    if already_processed:
                        continue
                    await self._redis.client.sadd(dedup_key, mention_id)
                    await self._redis.client.expire(dedup_key, 86400 * 7)

                batched_mentions.append(self._normalize_mention(raw_data))

            # Case B: Envelope (Aggregator Bundle)
            elif "envelope_id" in raw_data and "task" in raw_data:
                task_data = raw_data["task"]
                mentions_input = task_data.get("mentions", [])
                
                for item in mentions_input:
                    batched_mentions.append(self._normalize_envelope_item(item))

        if not batched_mentions:
            return None

        # Fetch brand metadata
        brand_metadata = await self._brand_service.get_brand_metadata(brand_hint)
        keywords = brand_metadata.get("keywords", [])

        # Create ONE chunk with ALL mentions
        chunk_data = {
            "chunkId": batch_chunk_id,
            "brand": brand_hint,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "mentions": batched_mentions,
            "meta": {
                "totalChunks": 1,
                "chunkIndex": 0,
                "keywords": keywords,
                "batchSize": len(payloads)
            }
        }

        logger.info(f"Created Batch Chunk {batch_chunk_id} with {len(batched_mentions)} mentions")
        
        try:
            return Chunk.model_validate(chunk_data)
        except Exception as exc:
            logger.error(f"Batch validation failed for {brand_hint}: {exc}")
            return None

    def _normalize_mention(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a standard mention payload."""
        return {
            "id": raw_data.get("id", str(uuid.uuid4())),
            "source": raw_data.get("source", "unknown"),
            "text": raw_data.get("text", ""),
            "author": raw_data.get("author"),
            "url": raw_data.get("url"),
            "created_at": self._parse_timestamp(raw_data.get("timestamp")),
            "metadata": raw_data.get("metadata", {})
        }

    def _normalize_envelope_item(self, item: Any) -> Dict[str, Any]:
        """Normalize an item from an aggregator envelope."""
        if isinstance(item, str):
            clean_item = html.unescape(re.sub(r'<[^>]+>', '', item)).strip()
            return {
                "id": str(uuid.uuid4()),
                "source": "aggregator",
                "text": clean_item,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        elif isinstance(item, dict):
            m_id = item.get("id") or str(uuid.uuid4())
            raw_src = item.get("source", "aggregator")
            
            created_at = item.get("publishedAt") or item.get("createdAt")
            if not created_at:
                 created_at = datetime.now(timezone.utc).isoformat()

            return {
                "id": m_id,
                "source": raw_src,
                "text": html.unescape(re.sub(r'<[^>]+>', '', item.get("text", ""))).strip(),
                "author": item.get("author"),
                "url": item.get("url"),
                "created_at": created_at,
                "author_followers": item.get("authorFollowers", 0),
                "influence_score": item.get("influenceScore", 0.0),
                "metadata": item.get("metadata", {})
            }
        return {} # Should not happen based on types

    def _parse_timestamp(self, ts: Any) -> str:
        if not ts:
            return datetime.now(timezone.utc).isoformat()
        try:
             # Assume ms timestamp
             return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat()
        except Exception:
             return datetime.now(timezone.utc).isoformat()
