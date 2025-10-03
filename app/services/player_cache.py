"""
Player Cache Service
Caches all active NFL players for fast client-side search
"""

import json
import logging
from app.services.api_client import FantasyAPIClient
from app.utils.cache import get_redis_client
from app.database import execute_query

logger = logging.getLogger(__name__)

CACHE_KEY = 'all_active_players'
CACHE_EXPIRY = 86400  # 24 hours

def get_cached_players():
    """Get all cached players (from Redis or PostgreSQL)"""
    # Try Redis first
    redis_client = get_redis_client()
    if redis_client:
        try:
            cached = redis_client.get(CACHE_KEY)
            if cached:
                logger.info("Retrieved players from Redis cache")
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Redis cache read failed: {e}")

    # Try PostgreSQL cache table
    try:
        result = execute_query(
            "SELECT player_data FROM player_cache WHERE cache_key = %s AND expires_at > NOW()",
            (CACHE_KEY,),
            fetch_one=True
        )
        if result:
            logger.info("Retrieved players from PostgreSQL cache")
            return result['player_data']
    except Exception as e:
        logger.warning(f"PostgreSQL cache read failed: {e}")

    return None

def cache_all_players(force=False):
    """
    Cache all active NFL players by fetching from each position

    Args:
        force: If True, refresh cache even if it exists

    Returns:
        List of player dictionaries
    """
    # Check if cache exists and is fresh
    if not force:
        cached = get_cached_players()
        if cached:
            logger.info(f"Using existing cache with {len(cached)} players")
            return cached

    logger.info("Fetching all active players from API...")
    api_client = FantasyAPIClient()
    all_players = []
    positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF']

    for position in positions:
        try:
            # Fetch all players for this position (no query, just position filter)
            players = api_client.search_players(query='', position=position)
            all_players.extend(players)
            logger.info(f"Fetched {len(players)} {position} players")
        except Exception as e:
            logger.error(f"Failed to fetch {position} players: {e}")

    # Remove duplicates (some players might appear in multiple positions)
    unique_players = {}
    for player in all_players:
        player_id = player.get('id') or player.get('player_id') or player.get('nfl_id')
        if player_id and player_id not in unique_players:
            unique_players[player_id] = player

    all_players = list(unique_players.values())
    logger.info(f"Total unique players: {len(all_players)}")

    # Cache in Redis
    redis_client = get_redis_client()
    if redis_client:
        try:
            redis_client.setex(CACHE_KEY, CACHE_EXPIRY, json.dumps(all_players))
            logger.info("Cached players in Redis")
        except Exception as e:
            logger.warning(f"Redis cache write failed: {e}")

    # Cache in PostgreSQL as backup
    try:
        # Create table if not exists
        execute_query("""
            CREATE TABLE IF NOT EXISTS player_cache (
                cache_key VARCHAR(255) PRIMARY KEY,
                player_data JSONB NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Upsert cache
        execute_query("""
            INSERT INTO player_cache (cache_key, player_data, expires_at)
            VALUES (%s, %s, NOW() + INTERVAL '24 hours')
            ON CONFLICT (cache_key)
            DO UPDATE SET
                player_data = EXCLUDED.player_data,
                expires_at = EXCLUDED.expires_at
        """, (CACHE_KEY, json.dumps(all_players)))

        logger.info("Cached players in PostgreSQL")
    except Exception as e:
        logger.warning(f"PostgreSQL cache write failed: {e}")

    return all_players

def search_cached_players(query, position=None, limit=20):
    """
    Search cached players with fuzzy matching

    Args:
        query: Search query string
        position: Optional position filter (QB, RB, WR, TE, K, DEF)
        limit: Maximum results to return

    Returns:
        List of matching players, sorted by relevance
    """
    # Get cached players
    all_players = get_cached_players()

    # If cache is empty, fetch and cache
    if not all_players:
        all_players = cache_all_players()

    if not all_players:
        logger.error("Failed to get player cache")
        return []

    # Filter by position if specified
    if position:
        all_players = [p for p in all_players if p.get('position') == position]

    # If no query, return first N players
    if not query or len(query) < 2:
        return all_players[:limit]

    # Score and filter players (using existing fuzzy matching logic)
    from app.services.api_client import FantasyAPIClient
    api_client = FantasyAPIClient()
    scored_players = api_client._score_and_filter_players(all_players, query)

    return scored_players[:limit]

def refresh_player_cache():
    """Force refresh the player cache (call this from background job)"""
    logger.info("Forcing player cache refresh...")
    return cache_all_players(force=True)
