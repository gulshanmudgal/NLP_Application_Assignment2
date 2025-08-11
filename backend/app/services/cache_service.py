"""
Cache service for storing translation results.
"""
import json
import hashlib
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """In-memory cache service for translation results."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize cache service.
        
        Args:
            max_size: Maximum number of cached items
            ttl_seconds: Time to live for cached items in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "size": 0,
            "evictions": 0
        }
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_expired_items())
        logger.info(f"Cache service initialized with max_size={max_size}, ttl={ttl_seconds}s")
    
    def generate_cache_key(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        model: str
    ) -> str:
        """Generate a unique cache key for translation request."""
        # Create a deterministic key from request parameters
        key_data = f"{text}|{source_lang}|{target_lang}|{model}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached item by key."""
        if key not in self.cache:
            self.stats["misses"] += 1
            return None
        
        item = self.cache[key]
        
        # Check if item has expired
        if self._is_expired(item):
            del self.cache[key]
            self.stats["size"] = len(self.cache)
            self.stats["misses"] += 1
            return None
        
        # Update access time
        item["last_accessed"] = datetime.utcnow()
        self.stats["hits"] += 1
        
        return item["value"]
    
    async def set(self, key: str, value: Any) -> None:
        """Set cached item."""
        # If cache is full, evict least recently used item
        if len(self.cache) >= self.max_size and key not in self.cache:
            await self._evict_lru()
        
        self.cache[key] = {
            "value": value,
            "created_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(seconds=self.ttl_seconds)
        }
        
        self.stats["size"] = len(self.cache)
        logger.debug(f"Cached item with key: {key}")
    
    async def delete(self, key: str) -> bool:
        """Delete cached item by key."""
        if key in self.cache:
            del self.cache[key]
            self.stats["size"] = len(self.cache)
            return True
        return False
    
    async def clear(self) -> None:
        """Clear all cached items."""
        self.cache.clear()
        self.stats["size"] = 0
        logger.info("Cache cleared")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests) if total_requests > 0 else 0
        
        return {
            "enabled": True,
            "size": self.stats["size"],
            "max_size": self.max_size,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "evictions": self.stats["evictions"],
            "ttl_seconds": self.ttl_seconds,
            "memory_usage_estimate_mb": self._estimate_memory_usage()
        }
    
    def _is_expired(self, item: Dict[str, Any]) -> bool:
        """Check if cached item has expired."""
        return datetime.utcnow() > item["expires_at"]
    
    async def _evict_lru(self) -> None:
        """Evict least recently used item."""
        if not self.cache:
            return
        
        # Find the least recently used item
        lru_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k]["last_accessed"]
        )
        
        del self.cache[lru_key]
        self.stats["evictions"] += 1
        self.stats["size"] = len(self.cache)
        
        logger.debug(f"Evicted LRU item: {lru_key}")
    
    async def _cleanup_expired_items(self) -> None:
        """Periodically clean up expired items."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                expired_keys = []
                now = datetime.utcnow()
                
                for key, item in self.cache.items():
                    if now > item["expires_at"]:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.cache[key]
                
                if expired_keys:
                    self.stats["size"] = len(self.cache)
                    logger.info(f"Cleaned up {len(expired_keys)} expired cache items")
                    
            except Exception as e:
                logger.error(f"Error during cache cleanup: {e}")
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB (rough approximation)."""
        if not self.cache:
            return 0.0
        
        # Very rough estimation: assume average 1KB per cache entry
        estimated_bytes = len(self.cache) * 1024
        return estimated_bytes / (1024 * 1024)


# Redis-based cache service (for production use)
class RedisCacheService:
    """Redis-based cache service for production environments."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", ttl_seconds: int = 3600):
        """
        Initialize Redis cache service.
        
        Args:
            redis_url: Redis connection URL
            ttl_seconds: Time to live for cached items
        """
        self.redis_url = redis_url
        self.ttl_seconds = ttl_seconds
        self.redis_client = None
        self.stats = {
            "hits": 0,
            "misses": 0
        }
        
        logger.info(f"Redis cache service initialized with URL: {redis_url}")
    
    async def _get_redis(self):
        """Get Redis client (lazy initialization)."""
        if self.redis_client is None:
            try:
                import redis.asyncio as redis
                self.redis_client = redis.from_url(self.redis_url)
                await self.redis_client.ping()
                logger.info("Redis connection established")
            except ImportError:
                logger.error("Redis package not installed. Install with: pip install redis")
                raise
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        
        return self.redis_client
    
    def generate_cache_key(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        model: str
    ) -> str:
        """Generate a unique cache key for translation request."""
        key_data = f"translation:{text}|{source_lang}|{target_lang}|{model}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached item by key."""
        try:
            redis_client = await self._get_redis()
            cached_data = await redis_client.get(key)
            
            if cached_data is None:
                self.stats["misses"] += 1
                return None
            
            self.stats["hits"] += 1
            return json.loads(cached_data)
            
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self.stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any) -> None:
        """Set cached item with TTL."""
        try:
            redis_client = await self._get_redis()
            serialized_value = json.dumps(value, default=str)
            await redis_client.setex(key, self.ttl_seconds, serialized_value)
            logger.debug(f"Cached item in Redis with key: {key}")
            
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def delete(self, key: str) -> bool:
        """Delete cached item by key."""
        try:
            redis_client = await self._get_redis()
            result = await redis_client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    async def clear(self) -> None:
        """Clear all cached items (use with caution in production)."""
        try:
            redis_client = await self._get_redis()
            await redis_client.flushdb()
            logger.warning("Redis cache cleared")
            
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            redis_client = await self._get_redis()
            info = await redis_client.info()
            
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total_requests) if total_requests > 0 else 0
            
            return {
                "enabled": True,
                "type": "redis",
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_rate": hit_rate,
                "ttl_seconds": self.ttl_seconds,
                "redis_info": {
                    "used_memory_mb": info.get("used_memory", 0) / (1024 * 1024),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Redis stats error: {e}")
            return {
                "enabled": False,
                "error": str(e)
            }
