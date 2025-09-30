from flask import Blueprint, jsonify, request
from app.services.api_client import FantasyAPIClient
from app.services.analyzer import PlayerAnalyzer

bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

api_client = FantasyAPIClient()
analyzer = PlayerAnalyzer()


@bp.route('/compare', methods=['POST'])
def compare_players():
    """
    Compare multiple players side-by-side
    Request body:
        {
            "player_ids": ["id1", "id2", "id3"],
            "opponent_ids": ["opp1", "opp2", "opp3"]  // optional, same length as player_ids
        }
    """
    data = request.json
    player_ids = data.get('player_ids', [])
    opponent_ids = data.get('opponent_ids', [])

    if not player_ids or len(player_ids) < 2:
        return jsonify({'error': 'At least 2 player IDs required for comparison'}), 400

    try:
        comparisons = []

        for i, player_id in enumerate(player_ids):
            # Get player data
            player = api_client.get_player_data(player_id)

            comparison_data = {
                'player': player.get('data', player) if isinstance(player, dict) and 'data' in player else player,
                'player_id': player_id
            }

            # If opponent provided, add matchup analysis
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

        return jsonify({
            'data': comparisons,
            'meta': {
                'count': len(comparisons)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/percentage-calculator', methods=['POST'])
def calculate_percentages():
    """
    Calculate success probability for various scenarios
    Request body:
        {
            "factors": {
                "matchup_score": 75,
                "weather_impact": 90,
                "injury_status": "healthy",
                "home_away": "home"
            }
        }
    """
    data = request.json
    factors = data.get('factors', {})

    try:
        probability = _calculate_probability(factors)

        return jsonify({
            'data': {
                'probability': probability,
                'factors_analyzed': factors,
                'recommendation': _probability_to_recommendation(probability)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/matchup-strength', methods=['GET'])
def matchup_strength():
    """
    Analyze matchup strength between player position and defense
    Query params:
        - position: Player position (QB, RB, WR, TE)
        - defense_team: Defense team ID
    """
    position = request.args.get('position')
    defense_team = request.args.get('defense_team')

    if not position or not defense_team:
        return jsonify({'error': 'Both position and defense_team parameters required'}), 400

    try:
        # Get defense stats
        defense_stats = api_client.get_defense_stats(defense_team)

        # Mock player data for position-based analysis
        mock_player = {
            'position': position,
            'avg_points': 12  # Generic baseline
        }

        matchup_score = analyzer.calculate_matchup_score(mock_player, defense_stats)

        return jsonify({
            'data': {
                'position': position,
                'defense_team': defense_team,
                'matchup_score': matchup_score,
                'strength': _score_to_strength(matchup_score)
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _calculate_probability(factors):
    """
    Calculate success probability based on various factors

    Args:
        factors: dict of factors affecting probability

    Returns:
        float: probability percentage (0-100)
    """
    base_probability = 50.0

    # Matchup score adjustment
    matchup_score = factors.get('matchup_score', 50)
    if matchup_score > 70:
        base_probability += 15
    elif matchup_score < 30:
        base_probability -= 15

    # Weather impact adjustment
    weather_impact = factors.get('weather_impact', 100)
    if weather_impact < 50:
        base_probability -= 10
    elif weather_impact > 90:
        base_probability += 5

    # Injury status
    injury_status = factors.get('injury_status', '').lower()
    if injury_status in ['questionable', 'doubtful']:
        base_probability -= 20
    elif injury_status == 'out':
        base_probability = 0

    # Home/away advantage
    home_away = factors.get('home_away', '').lower()
    if home_away == 'home':
        base_probability += 5
    elif home_away == 'away':
        base_probability -= 3

    # Ensure probability stays within bounds
    return min(95, max(5, base_probability))


def _probability_to_recommendation(probability):
    """Convert probability to recommendation"""
    if probability >= 70:
        return 'HIGHLY FAVORABLE'
    elif probability >= 50:
        return 'FAVORABLE'
    elif probability >= 30:
        return 'RISKY'
    else:
        return 'UNFAVORABLE'


def _score_to_strength(score):
    """Convert matchup score to strength descriptor"""
    if score >= 80:
        return 'EXCELLENT'
    elif score >= 60:
        return 'GOOD'
    elif score >= 40:
        return 'AVERAGE'
    elif score >= 20:
        return 'POOR'
    else:
        return 'VERY DIFFICULT'
