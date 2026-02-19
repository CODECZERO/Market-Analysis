"""
Smart Cache System
Intelligent multi-level caching with predictive prefetching

Features:
- LRU cache with priority levels
- Predictive prefetching (learns access patterns)
- Smart TTL based on stock volatility
- Automatic cache optimization
"""

import time
from typing import Any, Dict, Optional, List, Tuple
from collections import OrderedDict
from datetime import datetime, timedelta
import json
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class SmartCache:
    """
    Intelligent cache with learning capabilities
    
    Features:
    1. LRU eviction with priority
    2. Predictive prefetching
    3. Volatility-based TTL
    4. Usage pattern learning
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Args:
            max_size: Maximum cache entries
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        
        # Main cache storage (LRU)
        self.cache: OrderedDict = OrderedDict()
        
        # Metadata for each entry
        self.metadata: Dict[str, Dict] = {}
        
        # Access patterns for prediction
        self.access_patterns: Dict[str, List[str]] = {}  # symbol -> [next symbols]
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'prefetch_hits': 0,
            'evictions': 0,
        }
        
        # Priority weights
        self.priority_symbols = set()  # High-priority stocks
    
    def get(self, key: str, learn: bool = True) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            learn: Whether to learn access pattern
        
        Returns:
            Cached value or None
        """
        # Check if key exists and not expired
        if key in self.cache:
            meta = self.metadata.get(key, {})
            
            # Check expiration
            if meta.get('expires_at', float('inf')) > time.time():
                # Move to end (LRU)
                self.cache.move_to_end(key)
                
                # Update access count
                meta['access_count'] = meta.get('access_count', 0) + 1
                meta['last_access'] = time.time()
                
                # Record hit
                self.stats['hits'] += 1
                
                # Check if this was a prefetch hit
                if meta.get('prefetched'):
                    self.stats['prefetch_hits'] += 1
                    meta['prefetched'] = False
                
                # Learn access pattern
                if learn:
                    self._learn_pattern(key)
                
                logger.debug(f"Cache HIT: {key}")
                return self.cache[key]
            else:
                # Expired, remove
                self._evict(key)
        
        # Cache miss
        self.stats['misses'] += 1
        logger.debug(f"Cache MISS: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            priority: int = 0, volatility: float = 0.5):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = default)
            priority: Priority level (0-10, higher = keep longer)
            volatility: Stock volatility (0-1, affects TTL)
        """
        # Calculate smart TTL
        effective_ttl = self._calculate_ttl(ttl or self.default_ttl, volatility, priority)
        
        # Evict if at capacity and not priority
        if len(self.cache) >= self.max_size and key not in self.cache:
            if priority < 5:  # Don't evict for high priority
                self._evict_lru()
        
        # Store value
        self.cache[key] = value
        self.cache.move_to_end(key)
        
        # Store metadata
        self.metadata[key] = {
            'stored_at': time.time(),
            'expires_at': time.time() + effective_ttl,
            'ttl': effective_ttl,
            'priority': priority,
            'volatility': volatility,
            'access_count': 0,
            'last_access': time.time(),
            'prefetched': False,
        }
        
        logger.debug(f"Cache SET: {key} (TTL: {effective_ttl}s, priority: {priority})")
    
    def prefetch(self, keys: List[str], fetch_func: callable):
        """
        Prefetch multiple keys
        
        Args:
            keys: List of keys to prefetch
            fetch_func: Function to fetch data (takes key, returns value)
        """
        for key in keys:
            if key not in self.cache:
                try:
                    value = fetch_func(key)
                    self.set(key, value)
                    self.metadata[key]['prefetched'] = True
                    logger.info(f"Prefetched: {key}")
                except Exception as e:
                    logger.error(f"Prefetch failed for {key}: {e}")
    
    def predict_next(self, current_key: str, limit: int = 3) -> List[str]:
        """
        Predict what user will request next
        
        Args:
            current_key: Current symbol/key
            limit: Max predictions
        
        Returns:
            List of predicted next keys
        """
        if current_key not in self.access_patterns:
            return []
        
        # Get patterns
        patterns = self.access_patterns[current_key]
        
        # Count frequency
        from collections import Counter
        counter = Counter(patterns)
        
        # Return most common
        return [k for k, v in counter.most_common(limit)]
    
    def get_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.stats['hits'] + self.stats['misses']
        if total == 0:
            return 0.0
        return self.stats['hits'] / total
    
    def get_prefetch_effectiveness(self) -> float:
        """Calculate prefetch effectiveness"""
        if self.stats['hits'] == 0:
            return 0.0
        return self.stats['prefetch_hits'] / self.stats['hits']
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.metadata.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            **self.stats,
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': self.get_hit_rate(),
            'prefetch_effectiveness': self.get_prefetch_effectiveness(),
        }
    
    def _calculate_ttl(self, base_ttl: int, volatility: float, priority: int) -> int:
        """
        Calculate smart TTL based on volatility and priority
        
        High volatility → Shorter TTL (data changes fast)
        High priority → Longer TTL (keep important data)
        """
        # Volatility adjustment (0.5x to 2x)
        volatility_factor = 2 - volatility  # High volatility = lower factor
        
        # Priority adjustment (1x to 3x)
        priority_factor = 1 + (priority / 5)  # Priority 10 = 3x
        
        # Combined
        ttl = int(base_ttl * volatility_factor * priority_factor)
        
        # Bounds
        return max(60, min(ttl, 3600))  # 1 min to 1 hour
    
    def _learn_pattern(self, current_key: str):
        """
        Learn access patterns for prediction
        
        Tracks: After accessing X, user often accesses Y
        """
        # Get last accessed key
        if hasattr(self, '_last_key') and self._last_key:
            # Record pattern: last_key → current_key
            if self._last_key not in self.access_patterns:
                self.access_patterns[self._last_key] = []
            
            self.access_patterns[self._last_key].append(current_key)
            
            # Keep last 50 patterns per key
            if len(self.access_patterns[self._last_key]) > 50:
                self.access_patterns[self._last_key] = self.access_patterns[self._last_key][-50:]
        
        # Update last key
        self._last_key = current_key
    
    def _evict(self, key: str):
        """Evict specific key"""
        if key in self.cache:
            del self.cache[key]
            del self.metadata[key]
            self.stats['evictions'] += 1
            logger.debug(f"Evicted: {key}")
    
    def _evict_lru(self):
        """Evict least recently used (considering priority)"""
        if not self.cache:
            return
        
        # Find lowest priority, oldest access
        min_score = float('inf')
        evict_key = None
        
        for key in self.cache:
            meta = self.metadata.get(key, {})
            priority = meta.get('priority', 0)
            last_access = meta.get('last_access', 0)
            
            # Score: lower is worse (prioritize recent + high priority)
            score = (time.time() - last_access) / (priority + 1)
            
            if score > min_score:
                min_score = score
                evict_key = key
        
        if evict_key:
            self._evict(evict_key)


# Decorator for auto-caching function results
def cached(cache: SmartCache, ttl: int = 300, priority: int = 0):
    """
    Decorator to auto-cache function results
    
    Usage:
        @cached(my_cache, ttl=600, priority=5)
        def get_stock_data(symbol):
            return expensive_operation(symbol)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and args
            cache_key = f"{func.__name__}:{json.dumps(args)}:{json.dumps(kwargs, sort_keys=True)}"
            
            # Try cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result, ttl=ttl, priority=priority)
            
            return result
        
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    # Create cache
    cache = SmartCache(max_size=100, default_ttl=300)
    
    # Simulate stock data
    print("=" * 60)
    print("SMART CACHE DEMO")
    print("=" * 60)
    
    # Set some data
    cache.set('TCS.NS', {'price': 3845, 'analysis': '...'}, priority=8, volatility=0.3)
    cache.set('INFY.NS', {'price': 1456, 'analysis': '...'}, priority=7, volatility=0.4)
    cache.set('WIPRO.NS', {'price': 432, 'analysis': '...'}, priority=5, volatility=0.6)
    
    print(f"\n✅ Stored 3 stocks")
    
    # Access pattern: TCS → INFY → WIPRO
    cache.get('TCS.NS')
    cache.get('INFY.NS')
    cache.get('TCS.NS')
    cache.get('WIPRO.NS')
    cache.get('TCS.NS')
    cache.get('INFY.NS')
    
    print(f"\n📊 Learned access patterns")
    
    # Predict next
    predictions = cache.predict_next('TCS.NS')
    print(f"\n🔮 After TCS.NS, user likely requests: {predictions}")
    
    # Stats
    stats = cache.get_stats()
    print(f"\n📈 Cache Statistics:")
    print(f"  Size: {stats['size']}/{stats['max_size']}")
    print(f"  Hit Rate: {stats['hit_rate']:.1%}")
    print(f"  Hits: {stats['hits']}, Misses: {stats['misses']}")
    
    print("\n" + "=" * 60)
