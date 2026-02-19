"""Pipeline component for preprocessing mentions."""
import logging
import re
import time
import numpy as np
from typing import List

from ..logger import get_logger, log_with_context
from ..metrics import worker_preprocessing_time_seconds
from ..domain_types import Chunk, ChunkMetrics, Mention

logger = get_logger(__name__)

CLEAN_URL_RE = re.compile(r"https?://\S+")
CLEAN_WHITESPACE_RE = re.compile(r"\s+")

class PipelinePreprocessor:
    """Handles regex cleaning and deduplication of mentions."""

    def __init__(self, worker_id: str):
        self._worker_id = worker_id

    def preprocess(self, chunk: Chunk, metrics: ChunkMetrics) -> List[Mention]:
        """Clean texts, calculate influence, and deduplicate."""
        start = time.perf_counter()
        dedup: dict[str, Mention] = {}
        
        for mention in chunk.mentions:
            cleaned = self._clean_text(mention.text)
            if not cleaned:
                continue
            if cleaned in dedup:
                continue
                
            # Calculate influence
            meta = mention.metadata or {}
            followers = 0
            try:
                followers = int(meta.get("author_followers", meta.get("followers", 0)))
            except (ValueError, TypeError):
                followers = 0
                
            influence = 0.0
            if followers > 1:
                influence = float(np.log10(followers))
            else:
                # Fallback: Use upvotes/score if available (Reddit, HN, etc.)
                try:
                    upvotes = int(meta.get("score", meta.get("ups", meta.get("upvotes", 0))))
                    if upvotes > 1:
                        influence = float(np.log10(upvotes))
                except (ValueError, TypeError):
                    pass

            dedup[cleaned] = Mention(
                id=mention.id,
                source=meta.get("platform") or meta.get("source") or mention.source, # Fix aggregator source
                text=cleaned,
                author=mention.author or meta.get("author") or "Unknown",  # Extract author
                url=mention.url or meta.get("url"),
                created_at=mention.created_at,
                sentiment=mention.sentiment,
                metadata=mention.metadata,
                author_followers=followers,
                influence_score=influence,
            )
            
        duration = time.perf_counter() - start
        metrics.preprocessing_time_ms = duration * 1000
        worker_preprocessing_time_seconds.labels(self._worker_id, chunk.brand).observe(duration)
        
        log_with_context(
            logger,
            level=logging.INFO,
            message="Preprocessing completed",
            context={
                "worker_id": self._worker_id,
                "brand": chunk.brand,
                "chunk_id": chunk.chunk_id,
                "original_mentions": len(chunk.mentions),
                "clean_mentions": len(dedup),
            },
            metrics={"preprocessing_time_ms": metrics.preprocessing_time_ms},
        )
        return list(dedup.values())

    @staticmethod
    def _clean_text(text: str) -> str:
        text = CLEAN_URL_RE.sub("", text)
        text = CLEAN_WHITESPACE_RE.sub(" ", text)
        text = text.strip().lower()
        return text
