"""Resilience patterns for LLM execution: Rate Limiting, Circuit Breakers, Concurrency."""
import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from ..redis_client import RedisClient
from ..logger import get_logger, log_with_context

logger = get_logger(__name__)

class GlobalRateLimiter:
    """Redis-backed global rate limiter for distributed workers."""
    
    def __init__(self, limit_rpm: int):
        self.limit_rpm = limit_rpm
        self.redis = RedisClient()
        self._local_lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire a token from the global bucket."""
        while True:
            try:
                # Fixed window logic (1 minute)
                current_minute = int(time.time() // 60)
                key = f"rate_limit:global:{current_minute}"
                
                # We access the raw client for atomic pipeline operations
                client = self.redis.client
                async with client.pipeline(transaction=True) as pipe:
                    pipe.incr(key)
                    pipe.expire(key, 60)
                    results = await pipe.execute()
                    
                count = results[0]
                
                # Check for "Soft Limit" (38 RPM)
                if count >= 38:
                    logger.warning(f"Approaching rate limit ({count}/40). Sleeping for 2 minutes to cool down...")
                    await asyncio.sleep(120)
                    # After sleeping, the window has passed. We can assume safe to proceed (or re-acquire?)
                    # Ideally we loop back, but 120s is > 60s, so key is expired.
                    # We accept this token as "delayed" but valid.
                    return

                if count <= self.limit_rpm:
                    return
                
                # Limit reached (Hard Limit 40)
                wait_time = 60 - (time.time() % 60)
                log_with_context(
                    logger,
                    level=logging.WARNING,
                    message=f"Global rate limit reached ({count}/{self.limit_rpm}), waiting {wait_time:.1f}s",
                    context={"minute": current_minute},
                )
                await asyncio.sleep(min(wait_time, 5)) # Check again soon or wait full time
                
            except Exception as e:
                logger.error(f"Rate limiter error: {e}")
                # Fail open if Redis is down, but sleep slightly to be safe
                await asyncio.sleep(1)
                return


class CircuitBreaker:
    """Circuit breaker to prevent cascade failures."""
    
    def __init__(self, threshold: int = 5, cooldown_secs: int = 30):
        self.threshold = threshold
        self.cooldown_secs = cooldown_secs
        self.failure_count = 0
        self.last_failure: float | None = None
        self._lock = asyncio.Lock()
    
    async def is_open(self) -> bool:
        """Check if circuit is open (too many failures)."""
        async with self._lock:
            if self.failure_count < self.threshold:
                return False
            if self.last_failure and (time.time() - self.last_failure) >= self.cooldown_secs:
                self.failure_count = 0
                return False
            return True
    
    async def record_failure(self) -> None:
        async with self._lock:
            self.failure_count += 1
            self.last_failure = time.time()
    
    async def record_success(self) -> None:
        async with self._lock:
            self.failure_count = 0


class ConcurrencyTracker:
    """Tracks concurrency slots to give human-readable 'Thread IDs' (1-N)."""
    
    def __init__(self, max_concurrency: int):
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.slots = set(range(1, max_concurrency + 1))
        self.lock = asyncio.Lock()

    @asynccontextmanager
    async def acquire_slot(self):
        """Acquire a semaphore and a unique slot ID."""
        async with self.semaphore:
            async with self.lock:
                slot = min(self.slots) # Always grab the lowest available number
                self.slots.remove(slot)
            try:
                yield slot
            finally:
                async with self.lock:
                    self.slots.add(slot)
