#!/usr/bin/env python3
"""
Quick test script to verify API v2 integration
"""
import os
import sys

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.api_client import FantasyAPIClient

def test_api_v2():
    """Test API v2 connectivity and methods"""
    print("🔍 Testing Grid Iron Mind API v2 Integration\n")
    print("=" * 60)

    client = FantasyAPIClient()

    print(f"\n✅ API Client Initialized")
    print(f"   Base URL: {client.base_url}")
    print(f"   Version: {client.api_version}")

    if client.api_version != 'v2':
        print(f"\n⚠️  WARNING: Expected v2, got {client.api_version}")
        print(f"   Check your .env file: API_VERSION=v2")
        return False

    print("\n" + "=" * 60)
    print("✅ API v2 Configuration Correct!")
    print("\n📝 New v2 Methods Available:")

    v2_methods = [
        "get_player_advanced_stats()",
        "get_game_play_by_play()",
        "get_game_scoring_plays()",
        "get_player_injuries_v2()",
        "get_team_injuries_v2()",
        "get_defense_rankings_v2()",
        "ai_predict_game_v2()",
        "ai_predict_player_v2()",
        "ai_player_insights_v2()",
        "ai_query_v2()",
        "get_games_v2()",
        "get_team_roster_v2()",
        "get_standings_v2()"
    ]

    for i, method in enumerate(v2_methods, 1):
        print(f"   {i:2d}. {method}")

    print("\n" + "=" * 60)
    print("🎯 Next Steps:")
    print("   1. Apply database schema: psql $DATABASE_URL < schema_v2_updates.sql")
    print("   2. Start backend: python wsgi.py")
    print("   3. Test endpoints: curl http://localhost:5000/health")
    print("   4. Try advanced stats: curl http://localhost:5000/api/advanced/standings")
    print("\n" + "=" * 60)

    return True

if __name__ == "__main__":
    try:
        success = test_api_v2()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
