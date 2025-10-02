import redis
import json
import os
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Initialize Redis connection
try:
    REDIS_URL = os.getenv('REDIS_URL')
    if REDIS_URL:
        # Heroku Redis requires SSL but uses self-signed certs
        cache = redis.from_url(
            REDIS_URL,
            decode_responses=True,
            ssl_cert_reqs=None  # Disable SSL cert verification for Heroku Redis
        )
        CACHE_ENABLED = True
        logger.info("Redis cache initialized successfully")
    else:
        cache = None
        CACHE_ENABLED = False
        logger.warning("REDIS_URL not found, caching disabled")
except Exception as e:
    cache = None
    CACHE_ENABLED = False
    logger.error(f"Failed to initialize Redis: {e}")


def get_cached_or_fetch(key, fetch_func, expiry=3600):
    """
    Get data from cache or fetch it and cache the result

    Args:
        key: Cache key
        fetch_func: Function to call if cache miss
        expiry: Cache expiry in seconds (default 1 hour)

    Returns:
        Cached or fetched data
    """
    if not CACHE_ENABLED:
        return fetch_func()

    try:
        # Try to get from cache
        cached = cache.get(key)
        if cached:
            logger.debug(f"Cache HIT for key: {key}")
            return json.loads(cached)

        # Cache miss - fetch data
        logger.debug(f"Cache MISS for key: {key}")
        data = fetch_func()

        # Store in cache
        cache.setex(key, expiry, json.dumps(data))
        return data

    except Exception as e:
        logger.error(f"Cache error for key {key}: {e}")
        # Fallback to fetching without cache
        return fetch_func()


def cached_route(expiry=3600, key_prefix=''):
    """
    Decorator to cache Flask route responses

    Args:
        expiry: Cache expiry in seconds
        key_prefix: Prefix for cache key

    Usage:
        @bp.route('/endpoint')
        @cached_route(expiry=1800, key_prefix='players')
        def my_endpoint():
            return jsonify(data)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not CACHE_ENABLED:
                return f(*args, **kwargs)

            # Build cache key from route and args
            from flask import request
            cache_key = f"{key_prefix}:{request.path}:{request.query_string.decode()}"

            try:
                # Check cache
                cached = cache.get(cache_key)
                if cached:
                    logger.debug(f"Route cache HIT: {cache_key}")
                    return json.loads(cached)

                # Execute route function
                logger.debug(f"Route cache MISS: {cache_key}")
                response = f(*args, **kwargs)

                # Cache the response if it's JSON
                if hasattr(response, 'get_json'):
                    cache.setex(cache_key, expiry, json.dumps(response.get_json()))

                return response

            except Exception as e:
                logger.error(f"Route cache error: {e}")
                return f(*args, **kwargs)

        return decorated_function
    return decorator


def invalidate_cache(pattern):
    """
    Invalidate cache keys matching a pattern

    Args:
        pattern: Redis key pattern (e.g., 'players:*')
    """
    if not CACHE_ENABLED:
        return

    try:
        keys = cache.keys(pattern)
        if keys:
            cache.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache keys matching: {pattern}")
    except Exception as e:
        logger.error(f"Cache invalidation error: {e}")


def clear_all_cache():
    """Clear all cache entries"""
    if not CACHE_ENABLED:
        return

    try:
        cache.flushdb()
        logger.info("All cache cleared")
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")


def get_cache_stats():
    """Get cache statistics"""
    if not CACHE_ENABLED:
        return {"enabled": False, "message": "Cache not available"}

    try:
        info = cache.info()
        return {
            "enabled": True,
            "connected_clients": info.get('connected_clients', 0),
            "used_memory_human": info.get('used_memory_human', 'N/A'),
            "total_commands_processed": info.get('total_commands_processed', 0),
            "keyspace_hits": info.get('keyspace_hits', 0),
            "keyspace_misses": info.get('keyspace_misses', 0),
            "hit_rate": calculate_hit_rate(
                info.get('keyspace_hits', 0),
                info.get('keyspace_misses', 0)
            )
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        return {"enabled": True, "error": str(e)}


def calculate_hit_rate(hits, misses):
    """Calculate cache hit rate percentage"""
    total = hits + misses
    if total == 0:
        return 0.0
    return round((hits / total) * 100, 2)



def invalidate_player_cache(player_id):
    """
    Invalidate all cache entries for a specific player.
    Call this when player data is updated.
    
    Args:
        player_id: Player ID to invalidate
    """
    if not CACHE_ENABLED:
        return
    
    try:
        patterns = [
            f"players:*{player_id}*",
            f"player_details:{player_id}*",
            f"player_career:{player_id}*",
            f"analysis:*{player_id}*"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            keys = cache.keys(pattern)
            if keys:
                cache.delete(*keys)
                total_invalidated += len(keys)
        
        logger.info(f"Invalidated {total_invalidated} cache entries for player {player_id}")
    except Exception as e:
        logger.error(f"Failed to invalidate player cache: {e}")


def invalidate_matchup_cache(matchup_id=None, week=None, season=None):
    """
    Invalidate matchup-related cache entries.
    Call this when matchup data changes.
    
    Args:
        matchup_id: Specific matchup ID (optional)
        week: Week number (optional)
        season: Season year (optional)
    """
    if not CACHE_ENABLED:
        return
    
    try:
        patterns = []
        
        if matchup_id:
            patterns.append(f"matchup:{matchup_id}*")
        
        if week and season:
            patterns.extend([
                f"matchups:*week={week}*season={season}*",
                f"analysis:*:{week}:{season}*"
            ])
        
        if not patterns:
            # Invalidate all matchup caches
            patterns = ["matchup:*", "matchups:*"]
        
        total_invalidated = 0
        for pattern in patterns:
            keys = cache.keys(pattern)
            if keys:
                cache.delete(*keys)
                total_invalidated += len(keys)
        
        logger.info(f"Invalidated {total_invalidated} matchup cache entries")
    except Exception as e:
        logger.error(f"Failed to invalidate matchup cache: {e}")


def invalidate_weather_cache(team_abbr=None):
    """
    Invalidate weather cache entries.
    Call this when weather data should be refreshed.
    
    Args:
        team_abbr: Team abbreviation (optional, None = all weather)
    """
    if not CACHE_ENABLED:
        return
    
    try:
        pattern = f"weather:{team_abbr}" if team_abbr else "weather:*"
        keys = cache.keys(pattern)
        
        if keys:
            cache.delete(*keys)
            logger.info(f"Invalidated {len(keys)} weather cache entries")
    except Exception as e:
        logger.error(f"Failed to invalidate weather cache: {e}")


def invalidate_analysis_cache(player_id=None, week=None, season=None):
    """
    Invalidate AI analysis cache entries.
    Call this when analysis should be regenerated.
    
    Args:
        player_id: Player ID (optional)
        week: Week number (optional)
        season: Season year (optional)
    """
    if not CACHE_ENABLED:
        return
    
    try:
        # Invalidate Redis cache
        if player_id and week and season:
            pattern = f"analysis:{player_id}:*:{week}:{season}"
        elif week and season:
            pattern = f"analysis:*:{week}:{season}"
        elif player_id:
            pattern = f"analysis:{player_id}:*"
        else:
            pattern = "analysis:*"
        
        keys = cache.keys(pattern)
        if keys:
            cache.delete(*keys)
            logger.info(f"Invalidated {len(keys)} Redis analysis cache entries")
        
        # Also invalidate PostgreSQL cache
        from app.database import execute_query
        
        if player_id and week and season:
            query = "DELETE FROM ai_analysis_cache WHERE player_id = %s AND week = %s AND season = %s"
            execute_query(query, (player_id, week, season))
            logger.info(f"Invalidated PostgreSQL analysis cache for player {player_id}, week {week}, season {season}")
        elif week and season:
            query = "DELETE FROM ai_analysis_cache WHERE week = %s AND season = %s"
            execute_query(query, (week, season))
            logger.info(f"Invalidated PostgreSQL analysis cache for week {week}, season {season}")
        elif player_id:
            query = "DELETE FROM ai_analysis_cache WHERE player_id = %s"
            execute_query(query, (player_id,))
            logger.info(f"Invalidated PostgreSQL analysis cache for player {player_id}")
        
    except Exception as e:
        logger.error(f"Failed to invalidate analysis cache: {e}")


def schedule_cache_cleanup(max_age_days=7):
    """
    Schedule periodic cleanup of old cache entries from PostgreSQL.
    Should be called periodically (e.g., daily cron job).
    
    Args:
        max_age_days: Maximum age of cache entries in days
    """
    try:
        from app.database import execute_query
        
        query = """
            DELETE FROM ai_analysis_cache
            WHERE created_at < NOW() - INTERVAL '%s days'
        """
        execute_query(query, (max_age_days,))
        logger.info(f"Cleaned up analysis cache entries older than {max_age_days} days")
    except Exception as e:
        logger.error(f"Failed to cleanup old cache entries: {e}")
