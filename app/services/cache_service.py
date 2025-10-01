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


def generate_analysis_cache_key(player_id, player_name, opponent_team, week, season):
    """
    Generate consistent cache key for AI analysis.

    Args:
        player_id: Player ID (may be None)
        player_name: Player name (required)
        opponent_team: Opponent team abbreviation
        week: Week number
        season: Season year

    Returns:
        Cache key string
    """
    # Use player_name as fallback if player_id is None
    identifier = player_id if player_id else player_name.replace(' ', '_')
    return f"analysis:{identifier}:{opponent_team}:{week}:{season}"


def get_cached_analysis(player_id, player_name, opponent_team, week, season):
    """
    Get cached AI analysis using two-tier caching (Redis -> PostgreSQL).

    Args:
        player_id: Player ID
        player_name: Player name
        opponent_team: Opponent team abbreviation
        week: Week number
        season: Season year

    Returns:
        Cached analysis dict or None
    """
    from app.database import execute_query

    # Generate cache key
    cache_key = generate_analysis_cache_key(player_id, player_name, opponent_team, week, season)

    # 1. Check Redis first (fastest)
    redis_cached = cache.get(cache_key)
    if redis_cached:
        logger.debug(f"Redis cache hit for {cache_key}")
        return redis_cached

    # 2. Check PostgreSQL (persistent)
    try:
        query = """
            SELECT
                reasoning, matchup_score, projected_points,
                recommendation, ai_grade, confidence_score,
                injury_status, opponent_defense_rank, historical_performance
            FROM ai_analysis_cache
            WHERE (player_id = %s OR player_name = %s)
              AND opponent_team = %s
              AND week = %s
              AND season = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        result = execute_query(query, (player_id, player_name, opponent_team, week, season))

        if result and len(result) > 0:
            db_cached = result[0]
            logger.info(f"PostgreSQL cache hit for {player_name} vs {opponent_team} Week {week}")

            # Reconstruct analysis dict
            analysis = {
                'reasoning': db_cached.get('reasoning'),
                'matchup_score': float(db_cached.get('matchup_score', 0)) if db_cached.get('matchup_score') else None,
                'projected_points': float(db_cached.get('projected_points', 0)) if db_cached.get('projected_points') else None,
                'recommendation': db_cached.get('recommendation'),
                'ai_grade': db_cached.get('ai_grade'),
                'confidence_score': float(db_cached.get('confidence_score', 0)) if db_cached.get('confidence_score') else None,
                'injury_status': db_cached.get('injury_status'),
                'opponent_defense_rank': db_cached.get('opponent_defense_rank'),
                'historical_performance': db_cached.get('historical_performance')
            }

            # Store back in Redis for next time (7 days)
            cache.set(cache_key, analysis, ttl_seconds=604800)

            return analysis
    except Exception as e:
        logger.error(f"Error checking PostgreSQL cache: {e}")

    return None


def cache_analysis(player_id, player_name, position, team, opponent_team, week, season,
                   matchup_score, projected_points, recommendation, ai_grade,
                   confidence_score, reasoning, injury_status=None,
                   opponent_defense_rank=None, historical_performance=None):
    """
    Store AI analysis in both Redis and PostgreSQL.

    Args:
        player_id: Player ID
        player_name: Player name
        position: Player position
        team: Player team
        opponent_team: Opponent team abbreviation
        week: Week number
        season: Season year
        matchup_score: Matchup score
        projected_points: Projected points
        recommendation: START/SIT/CONSIDER
        ai_grade: Letter grade
        confidence_score: Confidence score
        reasoning: AI-generated reasoning text
        injury_status: Optional injury status
        opponent_defense_rank: Optional defensive rank
        historical_performance: Optional historical data (JSONB)
    """
    from app.database import execute_query
    import json

    # Generate cache key
    cache_key = generate_analysis_cache_key(player_id, player_name, opponent_team, week, season)

    # Analysis data for Redis
    analysis = {
        'reasoning': reasoning,
        'matchup_score': matchup_score,
        'projected_points': projected_points,
        'recommendation': recommendation,
        'ai_grade': ai_grade,
        'confidence_score': confidence_score,
        'injury_status': injury_status,
        'opponent_defense_rank': opponent_defense_rank,
        'historical_performance': historical_performance
    }

    # 1. Store in Redis (7 days TTL)
    cache.set(cache_key, analysis, ttl_seconds=604800)
    logger.debug(f"Cached analysis in Redis: {cache_key}")

    # 2. Store in PostgreSQL (permanent)
    try:
        # Convert historical_performance to JSON string if it's a dict
        historical_json = None
        if historical_performance:
            if isinstance(historical_performance, dict):
                historical_json = json.dumps(historical_performance)
            elif isinstance(historical_performance, str):
                historical_json = historical_performance

        query = """
            INSERT INTO ai_analysis_cache (
                player_id, player_name, position, team, opponent_team,
                week, season, matchup_score, projected_points,
                recommendation, ai_grade, confidence_score, reasoning,
                injury_status, opponent_defense_rank, historical_performance
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (player_id, opponent_team, week, season)
            DO UPDATE SET
                reasoning = EXCLUDED.reasoning,
                matchup_score = EXCLUDED.matchup_score,
                projected_points = EXCLUDED.projected_points,
                recommendation = EXCLUDED.recommendation,
                ai_grade = EXCLUDED.ai_grade,
                confidence_score = EXCLUDED.confidence_score,
                injury_status = EXCLUDED.injury_status,
                opponent_defense_rank = EXCLUDED.opponent_defense_rank,
                historical_performance = EXCLUDED.historical_performance,
                created_at = NOW()
        """
        execute_query(query, (
            player_id, player_name, position, team, opponent_team,
            week, season, matchup_score, projected_points,
            recommendation, ai_grade, confidence_score, reasoning,
            injury_status, opponent_defense_rank, historical_json
        ))
        logger.info(f"Cached analysis in PostgreSQL: {player_name} vs {opponent_team} Week {week}")
    except Exception as e:
        logger.error(f"Error caching analysis in PostgreSQL: {e}")
        # Don't fail if DB caching fails - Redis cache still works
