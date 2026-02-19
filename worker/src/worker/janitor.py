"""
Janitor Worker - TTL Cleanup for Old Mentions

This worker runs periodically to:
1. Delete mentions older than RETENTION_DAYS from MongoDB
2. Clean up orphaned Redis keys
3. Log storage metrics

Can be run as a cron job or scheduled task.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from redis import asyncio as redis_asyncio

from .config import get_settings
from .logger import get_logger

logger = get_logger(__name__)

# Configuration
RETENTION_DAYS = 90  # Keep mentions for 90 days
BATCH_SIZE = 500  # Delete in batches to avoid memory issues
REDIS_KEY_PATTERNS = [
    "brands:*:mentions:*",
    "brands:*:chunks:*",
    "spike_history:*",
]


class JanitorWorker:
    """Cleans up old data from MongoDB and Redis."""

    def __init__(
        self,
        mongo_uri: str,
        redis_url: str,
        retention_days: int = RETENTION_DAYS,
    ) -> None:
        self.mongo_uri = mongo_uri
        self.redis_url = redis_url
        self.retention_days = retention_days
        self._mongo: AsyncIOMotorClient | None = None
        self._redis: redis_asyncio.Redis | None = None

    async def connect(self) -> None:
        """Establish database connections."""
        self._mongo = AsyncIOMotorClient(self.mongo_uri)
        self._redis = redis_asyncio.Redis.from_url(self.redis_url, decode_responses=True)
        
        # Test connections
        await self._mongo.admin.command("ping")
        await self._redis.ping()
        logger.info("Janitor connected to databases")

    async def close(self) -> None:
        """Close database connections."""
        if self._mongo:
            self._mongo.close()
        if self._redis:
            await self._redis.close()
        logger.info("Janitor disconnected")

    async def cleanup_old_mentions(self) -> dict[str, Any]:
        """Delete mentions older than retention period."""
        if not self._mongo:
            raise RuntimeError("Not connected to MongoDB")

        db = self._mongo.get_database("brandtracker")
        mentions_collection = db.get_collection("mentions")

        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        
        # Count before deletion
        total_count = await mentions_collection.count_documents({})
        old_count = await mentions_collection.count_documents({
            "createdAt": {"$lt": cutoff_date}
        })

        if old_count == 0:
            logger.info("No old mentions to delete", extra={
                "cutoff_date": cutoff_date.isoformat(),
                "retention_days": self.retention_days,
            })
            return {"deleted": 0, "total": total_count}

        # Delete in batches
        deleted_total = 0
        while True:
            # Find batch to delete
            cursor = mentions_collection.find(
                {"createdAt": {"$lt": cutoff_date}},
                {"_id": 1}
            ).limit(BATCH_SIZE)
            
            ids_to_delete = [doc["_id"] async for doc in cursor]
            
            if not ids_to_delete:
                break

            result = await mentions_collection.delete_many({
                "_id": {"$in": ids_to_delete}
            })
            deleted_total += result.deleted_count
            
            logger.debug(f"Deleted batch of {result.deleted_count} mentions")
            await asyncio.sleep(0.1)  # Small delay to avoid overwhelming DB

        logger.info("Mention cleanup complete", extra={
            "deleted": deleted_total,
            "cutoff_date": cutoff_date.isoformat(),
            "remaining": total_count - deleted_total,
        })

        return {
            "deleted": deleted_total,
            "total_before": total_count,
            "total_after": total_count - deleted_total,
            "cutoff_date": cutoff_date.isoformat(),
        }

    async def cleanup_orphaned_redis_keys(self) -> dict[str, Any]:
        """Clean up expired Redis keys that weren't auto-deleted."""
        if not self._redis:
            raise RuntimeError("Not connected to Redis")

        deleted_count = 0
        scanned_count = 0

        for pattern in REDIS_KEY_PATTERNS:
            cursor = 0
            while True:
                cursor, keys = await self._redis.scan(
                    cursor=cursor, 
                    match=pattern, 
                    count=100
                )
                scanned_count += len(keys)

                for key in keys:
                    # Check if key has no TTL and is old
                    ttl = await self._redis.ttl(key)
                    if ttl == -1:  # No expiration set
                        # Set a TTL of 7 days on orphaned keys
                        await self._redis.expire(key, 7 * 24 * 60 * 60)
                        deleted_count += 1

                if cursor == 0:
                    break

        logger.info("Redis cleanup complete", extra={
            "keys_scanned": scanned_count,
            "ttl_set": deleted_count,
        })

        return {
            "keys_scanned": scanned_count,
            "ttl_set_on_orphans": deleted_count,
        }

    async def get_storage_stats(self) -> dict[str, Any]:
        """Get current storage statistics."""
        if not self._mongo or not self._redis:
            raise RuntimeError("Not connected to databases")

        db = self._mongo.get_database("brandtracker")
        
        # MongoDB stats
        mentions_count = await db.mentions.count_documents({})
        brands_count = await db.brands.count_documents({})
        users_count = await db.users.count_documents({})

        # Redis stats
        redis_info = await self._redis.info("memory")
        redis_memory_mb = redis_info.get("used_memory", 0) / (1024 * 1024)

        stats = {
            "mongodb": {
                "mentions": mentions_count,
                "brands": brands_count,
                "users": users_count,
            },
            "redis": {
                "memory_mb": round(redis_memory_mb, 2),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        logger.info("Storage stats collected", extra=stats)
        return stats

    async def run_full_cleanup(self) -> dict[str, Any]:
        """Run all cleanup tasks."""
        logger.info("Starting full cleanup cycle")
        
        results = {
            "started_at": datetime.utcnow().isoformat(),
            "mentions": {},
            "redis": {},
            "stats": {},
        }

        try:
            await self.connect()
            
            # Get stats before cleanup
            results["stats"]["before"] = await self.get_storage_stats()
            
            # Run cleanups
            results["mentions"] = await self.cleanup_old_mentions()
            results["redis"] = await self.cleanup_orphaned_redis_keys()
            
            # Get stats after cleanup
            results["stats"]["after"] = await self.get_storage_stats()
            
            results["completed_at"] = datetime.utcnow().isoformat()
            results["success"] = True
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            results["error"] = str(e)
            results["success"] = False
        finally:
            await self.close()

        return results


async def main():
    """Entry point for janitor worker."""
    settings = get_settings()
    
    # Get MongoDB URI from environment or construct it
    import os
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/brandtracker")
    
    janitor = JanitorWorker(
        mongo_uri=mongo_uri,
        redis_url=settings.redis_url,
        retention_days=RETENTION_DAYS,
    )
    
    results = await janitor.run_full_cleanup()
    
    if results.get("success"):
        logger.info("Janitor completed successfully", extra=results)
    else:
        logger.error("Janitor failed", extra=results)
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
