"""Async Redis client wrapper."""
from __future__ import annotations

import asyncio
from typing import Any, Iterable

from redis import asyncio as redis_asyncio
from redis.exceptions import RedisError

from .config import get_settings
from .logger import get_logger
from .utils import with_retry

logger = get_logger(__name__)


class RedisClient:
    """Encapsulates Redis interactions with retry logic."""

    def __init__(self, url: str | None = None) -> None:
        settings = get_settings()
        self._url = url or settings.redis_url
        self._client = redis_asyncio.Redis.from_url(self._url, decode_responses=True)
        self._settings = settings
        self._lock = asyncio.Lock()

    @property
    def client(self) -> redis_asyncio.Redis:
        return self._client

    async def ensure_connection(self) -> None:
        await with_retry(
            self._client.ping,
            retries=self._settings.max_retries,
            base_delay=self._settings.retry_backoff_base,
            logger=logger,
            operation_name="redis_ping",
        )

    async def blpop(self, keys: list[str], timeout: int) -> tuple[str, str] | None:
        if not keys:
            await asyncio.sleep(timeout)
            return None

        async def _op() -> tuple[str, str] | None:
            # New redis-py API: blpop(keys, timeout) - keys as list, timeout as positional
            return await self._client.blpop(keys, timeout)

        try:
            return await _op()
        except RedisError as exc:
            logger.error("BLPOP failed", extra={"context_error": str(exc)})
            await asyncio.sleep(timeout)
            return None

    async def rpush(self, key: str, value: str) -> None:
        await with_retry(
            lambda: self._client.rpush(key, value),
            retries=self._settings.max_retries,
            base_delay=self._settings.retry_backoff_base,
            logger=logger,
            operation_name="redis_rpush",
        )

    async def set_heartbeat(self, worker_id: str, interval: int) -> None:
        ttl = max(interval * 2, interval + 5)
        try:
            await self._client.set(f"workers:heartbeat:{worker_id}", "alive", ex=ttl)
        except RedisError as exc:
            logger.warning("Heartbeat failed", extra={"context_error": str(exc)})

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        try:
            await self._client.set(key, value, ex=ex)
        except RedisError as exc:
            logger.warning("Set failed", extra={"context_error": str(exc)})

    async def get(self, key: str) -> str | None:
        try:
            return await self._client.get(key)
        except RedisError as exc:
            logger.warning("Get failed", extra={"context_error": str(exc)})
            return None

    async def exists(self, key: str) -> int:
        """Check if a key exists."""
        try:
            return await self._client.exists(key)
        except RedisError as exc:
            logger.warning("Exists check failed", extra={"context_error": str(exc)})
            return 0

    async def publish(self, channel: str, message: str) -> None:
        """Publish a message to a channel."""
        try:
            await self._client.publish(channel, message)
        except RedisError as exc:
            logger.warning("Publish failed", extra={"context_error": str(exc)})

    async def lpush(self, key: str, value: str) -> None:
        """Push value to the left of a list."""
        try:
            await self._client.lpush(key, value)
        except RedisError as exc:
            logger.warning("LPUSH failed", extra={"context_error": str(exc)})

    async def ltrim(self, key: str, start: int, end: int) -> None:
        """Trim list to specified range."""
        try:
            await self._client.ltrim(key, start, end)
        except RedisError as exc:
            logger.warning("LTRIM failed", extra={"context_error": str(exc)})

    async def expire(self, key: str, seconds: int) -> None:
        """Set expiry on a key."""
        try:
            await self._client.expire(key, seconds)
        except RedisError as exc:
            logger.warning("EXPIRE failed", extra={"context_error": str(exc)})

    async def record_failure(self, key: str, value: str) -> None:
        await with_retry(
            lambda: self._client.rpush(key, value),
            retries=self._settings.max_retries,
            base_delay=self._settings.retry_backoff_base,
            logger=logger,
            operation_name="redis_record_failure",
        )







    async def rpoplpush(self, source: str, destination: str) -> str | None:
        try:
            return await self._client.rpoplpush(source, destination)
        except RedisError as exc:
            logger.warning("RPOPLPUSH failed", extra={"context_error": str(exc)})
            return None

    async def schedule_delay(self, key: str, value: str, timestamp: float) -> None:
        """Schedule a task for later execution using ZSET."""
        try:
            # ZADD key score member
            await self._client.zadd(key, {value: timestamp})
        except RedisError as exc:
            logger.error("Failed to schedule delayed task", extra={"context_error": str(exc)})

    async def fetch_ready_delayed_tasks(self, key: str) -> list[str]:
        """Fetch and remove tasks that are ready to be processed."""
        import time
        now = time.time()
        results = []
        try:
            # Watch key for atomic pop
            async with self._client.pipeline() as pipe:
                # 1. Get ready items
                await pipe.zrangebyscore(key, "-inf", now)
                # 2. Remove them
                await pipe.zremrangebyscore(key, "-inf", now)
                
                response = await pipe.execute()
                items = response[0]
                removed_count = response[1]
                
                # Check if we actually removed what we fetched (race condition minimal with strict single consumer, 
                # but multiple workers might race. ZPOPMIN is better but doesn't filter by score easily in old redis.
                # Actually, ZRANGE + ZREM is not atomic between the two unless in Lua.
                # BUT for now, simple implementation:
                # If multiple workers, we might process twice. 
                # Ideally use Lua script.
                pass 
                return items
        except RedisError as exc:
            logger.error("Failed to fetch delayed tasks", extra={"context_error": str(exc)})
            return []
            
    # Better implementation using Lua for atomicity
    async def fetch_ready_atomic(self, key: str, limit: int = 10) -> list[str]:
        import time
        now = time.time()
        lua_script = """
        local key = KEYS[1]
        local now = ARGV[1]
        local limit = tonumber(ARGV[2])
        
        local items = redis.call('zrangebyscore', key, '-inf', now, 'LIMIT', 0, limit)
        if #items > 0 then
            redis.call('zrem', key, unpack(items))
        end
        return items
        """
        try:
            return await self._client.eval(lua_script, 1, key, now, limit)
        except RedisError as exc:
            logger.error("Atomic fetch delayed failed", extra={"context_error": str(exc)})
            return []

    async def close(self) -> None:
        await self._client.close()
