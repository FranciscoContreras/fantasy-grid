"""
Celery tasks for player analysis
"""
from app.tasks import celery_app
from app.services.api_client import FantasyAPIClient
from app.services.analyzer import PlayerAnalyzer
from app.services.ai_grader import AIGrader


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def analyze_player_matchup(self, player_id, opponent_id, location=None):
    """
    Analyze player matchup in background

    Args:
        self: Celery task instance
        player_id: Player ID to analyze
        opponent_id: Opponent team ID
        location: Optional game location for weather

    Returns:
        dict: Analysis results with matchup score, weather impact, AI grade
    """
    try:
        api_client = FantasyAPIClient()
        analyzer = PlayerAnalyzer()
        grader = AIGrader()

        # Get player data
        player = api_client.get_player_data(player_id)

        # Get opponent defense stats
        defense_stats = api_client.get_defense_stats(opponent_id)

        # Get weather if location provided
        weather = {}
        if location:
            try:
                weather = api_client.get_weather_data(location)
            except:
                pass  # Weather is optional

        # Get player career stats for grading
        try:
            career_stats = api_client.get_player_career_stats(player_id)
            avg_points = career_stats.get('data', [{}])[0].get('fantasy_points', 10) if career_stats.get('data') else 10
        except:
            avg_points = 10  # Default fallback

        # Calculate matchup score
        matchup_score = analyzer.calculate_matchup_score(player, defense_stats)

        # Calculate weather impact
        player_position = player.get('data', {}).get('position', 'RB') if isinstance(player, dict) and 'data' in player else player.get('position', 'RB')
        weather_impact = analyzer.calculate_weather_impact(
            weather.get('data', {}) if weather else {},
            player_position
        )

        # AI grading
        features = [avg_points, matchup_score, weather_impact, 75]
        ai_grade = grader.grade_player(features)

        # Generate recommendation
        overall_score = (matchup_score * 0.4 + weather_impact * 0.2 + ai_grade['predicted_points'] * 3) / 4

        if overall_score >= 70:
            recommendation = {'status': 'START', 'confidence': 'HIGH'}
        elif overall_score >= 50:
            recommendation = {'status': 'CONSIDER', 'confidence': 'MEDIUM'}
        else:
            recommendation = {'status': 'BENCH', 'confidence': 'LOW'}

        return {
            'player': player.get('data', player) if isinstance(player, dict) and 'data' in player else player,
            'matchup_score': matchup_score,
            'weather_impact': weather_impact,
            'weather_data': weather.get('data', {}) if weather else None,
            'ai_grade': ai_grade,
            'recommendation': recommendation,
            'status': 'completed'
        }

    except Exception as exc:
        # Retry on failure
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3)
def compare_players_task(self, player_ids, opponent_ids=None):
    """
    Compare multiple players in background

    Args:
        self: Celery task instance
        player_ids: List of player IDs
        opponent_ids: Optional list of opponent team IDs

    Returns:
        list: Comparison results
    """
    try:
        api_client = FantasyAPIClient()
        analyzer = PlayerAnalyzer()

        comparisons = []

        for i, player_id in enumerate(player_ids):
            player = api_client.get_player_data(player_id)

            comparison_data = {
                'player': player.get('data', player) if isinstance(player, dict) and 'data' in player else player,
                'player_id': player_id
            }

            if opponent_ids and i < len(opponent_ids):
                opponent_id = opponent_ids[i]
                try:
                    defense_stats = api_client.get_defense_stats(opponent_id)
                    matchup_score = analyzer.calculate_matchup_score(player, defense_stats)
                    comparison_data['matchup_score'] = matchup_score
                    comparison_data['opponent'] = opponent_id
                except:
                    pass

            comparisons.append(comparison_data)

        # Sort by matchup score if available
        if any('matchup_score' in c for c in comparisons):
            comparisons.sort(key=lambda x: x.get('matchup_score', 0), reverse=True)

        return {
            'comparisons': comparisons,
            'count': len(comparisons),
            'status': 'completed'
        }

    except Exception as exc:
        raise self.retry(exc=exc)
