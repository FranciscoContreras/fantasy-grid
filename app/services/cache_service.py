import os
import json
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, caching disabled")


class CacheService:
    """
    Caching service using Redis for expensive operations.
    Falls back to in-memory dict if Redis unavailable.
    """

    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}  # Fallback in-memory cache

        if REDIS_AVAILABLE:
            redis_url = os.getenv('REDIS_URL')
            if redis_url:
                try:
                    self.redis_client = redis.from_url(redis_url, decode_responses=True)
                    self.redis_client.ping()
                    logger.info("Redis cache initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to connect to Redis: {e}. Using in-memory cache.")
                    self.redis_client = None

    def get(self, key):
        """Get value from cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        return None

    def set(self, key, value, ttl_seconds=3600):
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl_seconds: Time to live in seconds (default 1 hour)
        """
        try:
            serialized = json.dumps(value)
            if self.redis_client:
                self.redis_client.setex(key, ttl_seconds, serialized)
            else:
                # Simple in-memory cache (no TTL support)
                self.memory_cache[key] = value
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")

    def delete(self, key):
        """Delete key from cache"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")

    def clear_pattern(self, pattern):
        """
        Clear all keys matching pattern (e.g., 'weather:*')
        Only works with Redis, not in-memory cache.
        """
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")


# Global cache instance
cache = CacheService()


def cache_weather(team_abbr, weather_data):
    """Cache weather data for a team (24 hour TTL)"""
    key = f"weather:{team_abbr}"
    cache.set(key, weather_data, ttl_seconds=86400)  # 24 hours


def get_cached_weather(team_abbr):
    """Get cached weather data for a team"""
    key = f"weather:{team_abbr}"
    return cache.get(key)


def cache_ai_response(prompt_hash, response):
    """Cache AI response (7 day TTL for reusability)"""
    key = f"ai:{prompt_hash}"
    cache.set(key, response, ttl_seconds=604800)  # 7 days


def get_cached_ai_response(prompt_hash):
    """Get cached AI response"""
    key = f"ai:{prompt_hash}"
    return cache.get(key)
