"""Queue consumer responsible for fetching tasks from Redis."""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional

from .config import get_settings
from .logger import get_logger, log_with_context
from .metrics import worker_io_time_seconds, worker_waiting_seconds
from .redis_client import RedisClient
from .utils import timer

logger = get_logger(__name__)


from .services.brand_service import BrandService

class QueueConsumer:
    """Continuously polls Redis queues using BLPOP."""

    def __init__(self, redis_client: RedisClient, brand_service: BrandService, worker_id: str) -> None:
        self._redis = redis_client
        self._brand_service = brand_service
        self._settings = get_settings()
        self._worker_id = worker_id
        self._waiting_since: Optional[float] = None
        self._last_wait_log: float = 0.0
        # Initialize with random offset so workers don't all start at Brand A (Thundering Herd)
        import random
        self._search_iteration: int = random.randint(0, 100)

    async def fetch(self) -> tuple[str, str, float] | None:
        queue_keys = await self._brand_service.scan_brand_queues()
        
        # "OS Algorithm": Strict Round Robin Scheduling
        # Sort queues for deterministic order, then rotate based on counter
        queue_keys.sort()
        if queue_keys:
            # Rotate list: move first N items to end
            rotation = self._search_iteration % len(queue_keys)
            queue_keys = queue_keys[rotation:] + queue_keys[:rotation]
            self._search_iteration += 1
        
        # Parity: Poll priority queue + brand-specific queues + competitor detection queue
        all_queues = ["tasks:priority", "tasks:web_scan", "queue:competitor_detection"] + queue_keys

        if not all_queues:
            await asyncio.sleep(self._settings.blpop_timeout_sec)
            self._update_waiting([])
            return None

        # Logic: BLPOP for the first item (blocking wait)
        with timer() as timing:
            result = await self._redis.blpop(all_queues, timeout=self._settings.blpop_timeout_sec)
        
        if result is None:
            self._update_waiting(all_queues)
            worker_io_time_seconds.labels(self._worker_id, "unknown", "fetch").observe(
                timing["elapsed_ms"] / 1000
            )
            return None

        # We got the first item
        queue_key, first_payload = result
        payloads = [first_payload]
        fetch_time_ms = timing["elapsed_ms"]

        # BATCH OPTIMIZATION: Try to fetch more items immediately from the SAME queue
        # This reduces RTT and allows batch processing (e.g. 1 LLM call for 30 mentions)
        try:
            # Try to pop up to 29 more items (Total batch size target: 30)
            # Use LPOP with count (Redis 6.2+)
            # If standard redis-py or older Redis, loop. 
            # Assuming recent Redis/library support for lpop(key, count).
            # If not supported, we can loop lpop or use pipeline.
            # Using pipeline for compatibility and atomicity on connection use
            
            client = self._redis.client
            # Verify if client supports lpop with count (redis-py >= 4.something)
            # Safe bet: use pipeline with multiple lpop? No, lpop(count) is atomic.
            
            # Let's try lpop(count) if available, otherwise fallback.
            # Actually, standard redis-py `lpop` accepts count.
            
            # Use a safe batch size
            BATCH_SIZE = 30
            remaining = BATCH_SIZE - 1
            
            if remaining > 0:
                # We could use lpop(count)
                # Note: redis-py lpop returns List if count provided, else single.
                # await client.lpop(queue_key, count=remaining)
                
                # However, to be safe with unknown library version/server version compatibility:
                # We will use a simple loop with pipeline (or just lpop count if confident).
                # User config implies modern stack. Let's use lpop(count).
                
                more_items = await client.lpop(queue_key, count=remaining)
                if more_items:
                    # redis-py might return None if empty, or list.
                    if isinstance(more_items, list):
                        payloads.extend(more_items)
                    elif isinstance(more_items, str) or isinstance(more_items, bytes):
                        payloads.append(more_items)
                        
        except Exception as e:
            logger.warning(f"Batch fetch warning: {e}")
            # Continue with just the first item

        self._clear_waiting()
        worker_io_time_seconds.labels(self._worker_id, extract_brand_from_queue(queue_key), "fetch").observe(
            fetch_time_ms / 1000
        )
        log_with_context(
            logger,
            level=logging.INFO,
            message=f"Fetched batch from Redis (size={len(payloads)})",
            context={
                "worker_id": self._worker_id,
                "queue": queue_key,
                "batch_size": len(payloads)
            },
            metrics={"fetch_time_ms": fetch_time_ms, "batch_size": len(payloads)},
        )
        return queue_key, payloads, fetch_time_ms

    def _update_waiting(self, queues: list[str]) -> None:
        now = time.perf_counter()
        if self._waiting_since is None:
            self._waiting_since = now
        elapsed = now - self._waiting_since
        worker_waiting_seconds.labels(self._worker_id).set(elapsed)
        if now - self._last_wait_log >= self._settings.metrics_wait_log_interval_sec:
            # Show top 5 queues to avoid huge logs
            display_queues = queues[:5]
            if len(queues) > 5:
                display_queues.append(f"...and {len(queues) - 5} more")
            
            queue_names = ", ".join(display_queues or ["<none>"])
            log_with_context(
                logger,
                level=logging.INFO,
                message="Waiting for new tasks",
                context={"worker_id": self._worker_id, "queues": queue_names},
                metrics={"waiting_seconds": elapsed},
            )
            self._last_wait_log = now

    def _clear_waiting(self) -> None:
        self._waiting_since = None
        worker_waiting_seconds.labels(self._worker_id).set(0)

    async def retry_failed(self, brand: str) -> int:
        """
        Retry failed tasks for a specific brand by moving them from
        failed:brand:{brand} back to queue:brand:{brand}:chunks.
        """
        # Note: failure keys are recorded as `failed:brand:{brand}`
        # Work queues are `queue:brand:{brand}:chunks`
        failed_key = f"{self._settings.redis_failed_prefix}{brand}"
        work_key = f"{self._settings.redis_queue_prefix}{brand}:chunks"
        
        count = 0
        while True:
            # Atomic move: safe against crashes
            item = await self._redis.rpoplpush(failed_key, work_key)
            if not item:
                break
            count += 1
            
        if count > 0:
            log_with_context(
                logger,
                level=logging.INFO,
                message="Retried failed tasks",
                context={"brand": brand, "count": count, "worker_id": self._worker_id}
            )
        return count


def extract_brand_from_queue(queue_key: str) -> str:
    parts = queue_key.split(":")
    return parts[2] if len(parts) >= 3 else "unknown"
