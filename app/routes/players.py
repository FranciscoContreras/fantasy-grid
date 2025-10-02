from flask import Blueprint, jsonify, request
from flask import Blueprint, request, jsonify
from app.services.api_client import FantasyAPIClient
from app.services.analyzer import PlayerAnalyzer
from app.services.ai_grader import AIGrader
from app.database import execute_query
from app.utils.cache import cached_route, get_cached_or_fetch
from app.validation.decorators import validate_query_params
from app.validation.schemas import PlayerSearchSchema
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('players', __name__, url_prefix='/api/players')

api_client = FantasyAPIClient()
analyzer = PlayerAnalyzer()
grader = AIGrader()


@bp.route('/search', methods=['GET'])
@cached_route(expiry=1800, key_prefix='players_search')  # Cache for 30 minutes
@validate_query_params(PlayerSearchSchema)
def search_players(data):
    """
    Search for players by name/position
    Query params:
        - q: search query
        - position: optional position filter (QB, RB, WR, TE, etc.)
    """
    query = data.get('query', '')
    position = data.get('position')

    try:
        players = api_client.search_players(query, position)
        logger.info(f"Player search: query='{query}', position={position}, results={len(players)}")
        return jsonify({
            'data': players,
            'meta': {
                'query': query,
                'position': position,
                'count': len(players)
            }
        })
    except Exception as e:
        logger.error(f"Player search failed: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/<player_id>', methods=['GET'])
@cached_route(expiry=3600, key_prefix='player_details')  # Cache for 1 hour
def get_player(player_id):
    """Get detailed player information"""
    try:
        player = api_client.get_player_data(player_id)
        return jsonify({'data': player})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<player_id>/analysis', methods=['GET'])
def analyze_player(player_id):
    """
    Analyze a player's matchup and provide recommendations
    Query params:
        - opponent: opponent team ID or abbreviation
        - location: optional game location for weather data
    """
    opponent = request.args.get('opponent')
    location = request.args.get('location')

    if not opponent:
        return jsonify({'error': 'Query parameter "opponent" is required'}), 400

    try:
        # Get player data
        player = api_client.get_player_data(player_id)

        # Get opponent defense stats
        defense_stats = api_client.get_defense_stats(opponent)

        # Get weather if location provided
        weather = {}
        if location:
            try:
                weather = api_client.get_weather_data(location)
            except:
                # Weather is optional, continue without it
                pass

        # Get player career stats for grading
        try:
            career_stats = api_client.get_player_career_stats(player_id)
            # Use most recent season or calculate average
            avg_points = career_stats.get('data', [{}])[0].get('fantasy_points', 10) if career_stats.get('data') else 10
        except:
            avg_points = 10  # Default fallback

        # Calculate matchup score
        matchup_score = analyzer.calculate_matchup_score(player, defense_stats)

        # Calculate weather impact
        weather_impact = analyzer.calculate_weather_impact(
            weather.get('data', {}) if weather else {},
            player.get('data', {}).get('position', 'RB') if isinstance(player, dict) and 'data' in player else player.get('position', 'RB')
        )

        # AI grading
        player_position = player.get('data', {}).get('position', 'RB') if isinstance(player, dict) and 'data' in player else player.get('position', 'RB')

        features = [
            avg_points,
            matchup_score,
            weather_impact,
            75  # Consistency rating placeholder
        ]
        ai_grade = grader.grade_player(features)

        # Generate recommendation
        recommendation = _generate_recommendation(matchup_score, weather_impact, ai_grade)

        # Save analysis to database
        try:
            _save_analysis_history(
                player_id,
                opponent,
                matchup_score,
                weather_impact,
                ai_grade['grade'],
                ai_grade['predicted_points'],
                recommendation['status']
            )
            logger.info(f"Analysis saved for player {player_id} vs {opponent}")
        except Exception as db_error:
            # Log but don't fail the request if database save fails
            logger.error(f"Failed to save analysis history: {db_error}", exc_info=True)

        return jsonify({
            'data': {
                'player': player.get('data', player) if isinstance(player, dict) and 'data' in player else player,
                'matchup_score': matchup_score,
                'weather_impact': weather_impact,
                'weather_data': weather.get('data', {}) if weather else None,
                'ai_grade': ai_grade,
                'recommendation': recommendation
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<player_id>/career', methods=['GET'])
@cached_route(expiry=7200, key_prefix='player_career')  # Cache for 2 hours
def get_player_career(player_id):
    """Get player career statistics"""
    try:
        career_stats = api_client.get_player_career_stats(player_id)
        return jsonify(career_stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<player_id>/history', methods=['GET'])
def get_analysis_history(player_id):
    """Get historical analysis for a player"""
    try:
        limit = request.args.get('limit', 10, type=int)

        query = """
            SELECT player_id, opponent, matchup_score, weather_impact,
                   ai_grade, predicted_points, recommendation, analyzed_at
            FROM analysis_history
            WHERE player_id = %s
            ORDER BY analyzed_at DESC
            LIMIT %s
        """

        history = execute_query(query, (player_id, limit), fetch_all=True)

        # Convert datetime to string for JSON serialization
        if history:
            history = [
                {
                    **row,
                    'analyzed_at': row['analyzed_at'].isoformat() if row.get('analyzed_at') else None
                }
                for row in history
            ]

        return jsonify({
            'data': history or [],
            'meta': {
                'player_id': player_id,
                'count': len(history) if history else 0
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _save_analysis_history(player_id, opponent, matchup_score, weather_impact, ai_grade, predicted_points, recommendation):
    """Save analysis to database for historical tracking"""
    query = """
        INSERT INTO analysis_history
        (player_id, opponent, matchup_score, weather_impact, ai_grade, predicted_points, recommendation)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    execute_query(query, (player_id, opponent, matchup_score, weather_impact, ai_grade, predicted_points, recommendation))


def _generate_recommendation(matchup, weather, ai_grade):
    """
    Generate start/sit recommendation based on analysis

    Args:
        matchup: Matchup score (0-100)
        weather: Weather impact score (0-100)
        ai_grade: AI grade dict with predicted_points

    Returns:
        dict with status and confidence
    """
    # Weighted score calculation
    overall_score = (matchup * 0.4 + weather * 0.2 + ai_grade['predicted_points'] * 3) / 4

    if overall_score >= 16:
        return {
            'status': 'START',
            'confidence': 'HIGH',
            'reason': f'Strong matchup (score: {matchup}/100) and high projected points ({ai_grade["predicted_points"]})'
        }
    elif overall_score >= 10:
        return {
            'status': 'CONSIDER',
            'confidence': 'MEDIUM',
            'reason': f'Average matchup with moderate upside. Grade: {ai_grade["grade"]}'
        }
    else:
        return {
            'status': 'BENCH',
            'confidence': 'MEDIUM',
            'reason': f'Difficult matchup (score: {matchup}/100) or low projected points'
        }
