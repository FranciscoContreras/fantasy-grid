#!/usr/bin/env python3
"""
Build search index from Grid Iron Mind API.
Can be run locally or on Heroku.
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.search.indexer import get_indexer
from app.services.search import get_search_engine

def main():
    print("🔄 Building Fantasy Grid Search Index")
    print("=" * 60)

    indexer = get_indexer()

    # Index players (no limit = all players)
    print("\n📊 Indexing players from Grid Iron Mind API...")
    player_count = indexer.index_all_players()
    print(f"✅ Indexed {player_count} players")

    # Index teams
    print("\n🏈 Indexing teams...")
    team_count = indexer.index_all_teams()
    print(f"✅ Indexed {team_count} teams")

    # Get final stats
    search_engine = get_search_engine()
    stats = search_engine.get_index_stats()

    print("\n📈 Final Index Statistics:")
    print(f"  - Total documents: {stats.get('total_documents', 0)}")
    print(f"  - Total unique terms: {stats.get('total_terms', 0)}")
    print(f"  - Total index entries: {stats.get('total_index_entries', 0)}")
    print(f"  - Documents by type:")
    for doc_type, count in stats.get('documents_by_type', {}).items():
        print(f"    • {doc_type}: {count}")

    print("\n✅ Search index built successfully!")
    print("\nTest it:")
    print("  curl 'https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/search/query?q=mahomes'")

    return 0

if __name__ == '__main__':
    sys.exit(main())
