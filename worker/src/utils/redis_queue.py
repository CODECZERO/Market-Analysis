"""
Redis Queue Manager
Manages background job queues for stock analysis
"""

import redis
from typing import Dict, Any, Optional
import json
import logging
import os

logger = logging.getLogger(__name__)

# Redis queue names with priorities
QUEUES = {
    # High priority (real-time)
    'queue_market_data_fetch': {'priority': 'high', 'timeout': 30},
    'queue_sentiment_scrape': {'priority': 'high', 'timeout': 60},
    
    # Medium priority (analysis)
    'queue_llm_phase1_what_why': {'priority': 'medium', 'timeout': 120},
    'queue_technical_indicators': {'priority': 'medium', 'timeout': 60},
    'queue_quant_strategies': {'priority': 'medium', 'timeout': 90},
    'queue_llm_phase2_when_where': {'priority': 'medium', 'timeout': 120},
    
    # Low priority (heavy computation)
    'queue_ml_prediction': {'priority': 'low', 'timeout': 180},
    'queue_llm_phase3_how': {'priority': 'low', 'timeout': 120},
    'queue_report_generation': {'priority': 'low', 'timeout': 60}
}


class RedisQueueManager:
    """Manage Redis queues for async task processing"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize Redis connection
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info(f"Connected to Redis: {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def enqueue_task(
        self,
        queue_name: str,
        task_data: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> str:
        """
        Add task to queue
        
        Args:
            queue_name: Name of the queue
            task_data: Task payload
            task_id: Optional task ID
            
        Returns:
            Task ID
        """
        if queue_name not in QUEUES:
            raise ValueError(f"Unknown queue: {queue_name}")
        
        # Generate task ID if not provided
        if not task_id:
            task_id = f"{queue_name}:{task_data.get('symbol', 'unknown')}:{int(os.times()[4] * 1000)}"
        
        # Create task envelope
        task_envelope = {
            'id': task_id,
            'data': task_data,
            'queue': queue_name,
            'priority': QUEUES[queue_name]['priority'],
            'timeout': QUEUES[queue_name]['timeout']
        }
        
        # Push to queue
        self.redis_client.lpush(queue_name, json.dumps(task_envelope))
        
        # Set expiration (24 hours)
        self.redis_client.expire(queue_name, 86400)
        
        logger.info(f"Enqueued task {task_id} to {queue_name}")
        return task_id
    
    def dequeue_task(self, queue_name: str, timeout: int = 5) -> Optional[Dict]:
        """
        Get task from queue (blocking)
        
        Args:
            queue_name: Queue to dequeue from
            timeout: Block timeout in seconds
            
        Returns:
            Task data or None
        """
        result = self.redis_client.brpop(queue_name, timeout=timeout)
        
        if result:
            _, task_json = result
            task = json.loads(task_json)
            logger.info(f"Dequeued task {task['id']} from {queue_name}")
            return task
        
        return None
    
    def get_queue_length(self, queue_name: str) -> int:
        """Get number of tasks in queue"""
        return self.redis_client.llen(queue_name)
    
    def clear_queue(self, queue_name: str):
        """Clear all tasks from queue"""
        self.redis_client.delete(queue_name)
        logger.info(f"Cleared queue {queue_name}")
    
    def get_all_queue_stats(self) -> Dict[str, int]:
        """Get stats for all queues"""
        stats = {}
        for queue_name in QUEUES.keys():
            stats[queue_name] = self.get_queue_length(queue_name)
        return stats
    
    # Cache operations
    
    def cache_set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ):
        """
        Set cache value
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        self.redis_client.setex(
            key,
            ttl,
            json.dumps(value) if not isinstance(value, str) else value
        )
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get cache value"""
        value = self.redis_client.get(key)
        
        if value:
            try:
                return json.loads(value)
            except:
                return value
        
        return None
    
    def cache_delete(self, key: str):
        """Delete cache key"""
        self.redis_client.delete(key)


# Convenience functions

def get_queue_manager() -> RedisQueueManager:
    """Get global queue manager instance"""
    return RedisQueueManager()


def enqueue_analysis(symbol: str, exchange: str = "NSE") -> str:
    """Quick helper to enqueue stock analysis"""
    manager = get_queue_manager()
    
    task_data = {
        'symbol': symbol,
        'exchange': exchange,
        'type': 'full_analysis'
    }
    
    task_id = manager.enqueue_task('queue_market_data_fetch', task_data)
    return task_id


if __name__ == "__main__":
    # Test Redis connection
    logging.basicConfig(level=logging.INFO)
    
    manager = RedisQueueManager()
    
    # Test enqueue
    task_id = enqueue_analysis("RELIANCE", "NSE")
    print(f"Enqueued task: {task_id}")
    
    # Get stats
    stats = manager.get_all_queue_stats()
    print("\nQueue Stats:")
    for queue, count in stats.items():
        print(f"  {queue}: {count} tasks")
