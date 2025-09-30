from flask import Blueprint, jsonify, request
from app.services.api_client import FantasyAPIClient
from app.services.analyzer import PlayerAnalyzer
from app.services.ai_grader import AIGrader

bp = Blueprint('players', __name__, url_prefix='/api/players')

api_client = FantasyAPIClient()
analyzer = PlayerAnalyzer()
grader = AIGrader()


@bp.route('/search', methods=['GET'])
def search_players():
    """
    Search for players by name/position
    Query params:
        - q: search query
        - position: optional position filter (QB, RB, WR, TE, etc.)
    """
    query = request.args.get('q', '')
    position = request.args.get('position', None)

    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    try:
        players = api_client.search_players(query, position)
        return jsonify({
            'data': players,
            'meta': {
                'query': query,
                'position': position,
                'count': len(players)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<player_id>', methods=['GET'])
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
def get_player_career(player_id):
    """Get player career statistics"""
    try:
        career_stats = api_client.get_player_career_stats(player_id)
        return jsonify(career_stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
