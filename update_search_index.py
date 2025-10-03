#!/usr/bin/env python3
"""
Background job to update search index periodically.
Runs on Heroku Scheduler or as a worker dyno.
"""
import sys
import os
import time
import logging
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.search.indexer import get_indexer
from app.services.search import get_search_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def update_index():
    """Update the search index with latest data from API"""
    logger.info("=" * 60)
    logger.info("🔄 Starting Search Index Update Job")
    logger.info(f"⏰ Run time: {datetime.utcnow().isoformat()}Z")
    logger.info("=" * 60)

    try:
        indexer = get_indexer()

        # Update players (incremental update)
        logger.info("\n📊 Updating player index...")
        player_count = indexer.index_all_players()
        logger.info(f"✅ Indexed {player_count} players")

        # Update teams
        logger.info("\n🏈 Updating team index...")
        team_count = indexer.index_all_teams()
        logger.info(f"✅ Indexed {team_count} teams")

        # Get final stats
        search_engine = get_search_engine()
        stats = search_engine.get_index_stats()

        logger.info("\n📈 Updated Index Statistics:")
        logger.info(f"  - Total documents: {stats.get('total_documents', 0)}")
        logger.info(f"  - Total unique terms: {stats.get('total_terms', 0)}")
        logger.info(f"  - Total index entries: {stats.get('total_index_entries', 0)}")
        logger.info(f"  - Documents by type:")
        for doc_type, count in stats.get('documents_by_type', {}).items():
            logger.info(f"    • {doc_type}: {count}")

        logger.info("\n✅ Search index updated successfully!")
        return 0

    except Exception as e:
        logger.error(f"❌ Failed to update search index: {e}", exc_info=True)
        return 1


def run_continuous(interval_seconds=3600):
    """
    Run index updates continuously at specified interval.
    Used for worker dyno mode.

    Args:
        interval_seconds: Time between updates (default: 1 hour)
    """
    logger.info(f"🔁 Starting continuous index update worker (interval: {interval_seconds}s)")

    while True:
        try:
            update_index()
            logger.info(f"\n⏳ Sleeping for {interval_seconds} seconds until next update...")
            time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("\n👋 Shutting down worker...")
            break
        except Exception as e:
            logger.error(f"❌ Worker error: {e}", exc_info=True)
            # Sleep a bit before retrying
            time.sleep(60)


if __name__ == '__main__':
    # Check if running in continuous mode
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        # Get interval from env or use default (1 hour)
        interval = int(os.getenv('INDEX_UPDATE_INTERVAL', 3600))
        sys.exit(run_continuous(interval))
    else:
        # One-time update (for Heroku Scheduler)
        sys.exit(update_index())
