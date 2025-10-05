from flask import Blueprint, jsonify, request, Response
from app.services.api_client import FantasyAPIClient
from app.services.analyzer import PlayerAnalyzer
from app.services.matchup_exploiter import MatchupExploiter
import csv
import io
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

api_client = FantasyAPIClient()
analyzer = PlayerAnalyzer()
matchup_exploiter = MatchupExploiter()


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


@bp.route('/export/csv', methods=['POST'])
def export_comparison_csv():
    """
    Export player comparison data to CSV
    Request body:
        {
            "player_ids": ["id1", "id2", "id3"],
            "opponent_ids": ["opp1", "opp2", "opp3"]  // optional
        }
    """
    data = request.json
    player_ids = data.get('player_ids', [])
    opponent_ids = data.get('opponent_ids', [])

    if not player_ids:
        return jsonify({'error': 'player_ids required'}), 400

    try:
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        headers = ['Player Name', 'Position', 'Team', 'Opponent', 'Matchup Score', 'Recommendation']
        writer.writerow(headers)

        # Get player data and write rows
        for i, player_id in enumerate(player_ids):
            try:
                player = api_client.get_player_data(player_id)
                player_data = player.get('data', player) if isinstance(player, dict) and 'data' in player else player

                row = [
                    player_data.get('name', 'Unknown'),
                    player_data.get('position', 'N/A'),
                    player_data.get('team', {}).get('abbreviation', 'N/A') if isinstance(player_data.get('team'), dict) else 'N/A',
                ]

                # Add opponent and matchup data if available
                if opponent_ids and i < len(opponent_ids):
                    opponent_id = opponent_ids[i]
                    try:
                        defense_stats = api_client.get_defense_stats(opponent_id)
                        matchup_score = analyzer.calculate_matchup_score(player_data, defense_stats)
                        row.extend([
                            opponent_id,
                            f"{matchup_score:.1f}",
                            _score_to_strength(matchup_score)
                        ])
                    except:
                        row.extend(['N/A', 'N/A', 'N/A'])
                else:
                    row.extend(['N/A', 'N/A', 'N/A'])

                writer.writerow(row)

            except Exception as e:
                logger.error(f"Error processing player {player_id}: {e}")
                continue

        # Prepare response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=player_comparison.csv'
            }
        )

    except Exception as e:
        logger.error(f"CSV export failed: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/favorable-matchups', methods=['GET'])
def get_favorable_matchups():
    """
    Find players with favorable matchups (facing weak defenses)
    Query params:
        - position: Filter by position (QB, RB, WR, TE)
        - week: Week number for matchup analysis
        - season: NFL season year (default: 2024)
        - min_ownership: Minimum ownership % (default: 0.0)
        - max_ownership: Maximum ownership % (default: 50.0)
    """
    try:
        position = request.args.get('position')
        week = request.args.get('week', type=int)
        season = request.args.get('season', default=2025, type=int)
        min_ownership = request.args.get('min_ownership', default=0.0, type=float)
        max_ownership = request.args.get('max_ownership', default=50.0, type=float)

        result = matchup_exploiter.find_favorable_matchups(
            position=position,
            week=week,
            season=season,
            min_ownership=min_ownership,
            max_ownership=max_ownership
        )

        if 'error' in result:
            return jsonify(result), 500

        return jsonify({
            'data': result,
            'meta': {
                'count': len(result.get('players', [])),
                'filters': {
                    'position': position,
                    'week': week,
                    'season': season,
                    'ownership_range': [min_ownership, max_ownership]
                }
            }
        })

    except Exception as e:
        logger.error(f"Error finding favorable matchups: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/schedule-lookahead/<player_id>', methods=['GET'])
def get_schedule_lookahead(player_id):
    """
    Get schedule lookahead for a player (next 3-4 weeks)
    Path params:
        - player_id: Player ID
    Query params:
        - weeks_ahead: Number of weeks to look ahead (default: 4)
        - season: NFL season year (default: 2024)
    """
    try:
        weeks_ahead = request.args.get('weeks_ahead', default=4, type=int)
        season = request.args.get('season', default=2025, type=int)

        result = matchup_exploiter.get_schedule_lookahead(
            player_id=player_id,
            weeks_ahead=weeks_ahead,
            season=season
        )

        if 'error' in result:
            return jsonify(result), 404 if result['error'] == 'Player not found' else 500

        return jsonify({
            'data': result,
            'meta': {
                'player_id': player_id,
                'weeks_ahead': weeks_ahead,
                'season': season
            }
        })

    except Exception as e:
        logger.error(f"Error getting schedule lookahead for player {player_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/defense-heatmap', methods=['GET'])
def get_defense_heatmap():
    """
    Get defensive weakness heatmap for all NFL teams
    Query params:
        - position: Filter by position (QB, RB, WR, TE)
        - season: NFL season year (default: 2024)
    """
    try:
        position = request.args.get('position')
        season = request.args.get('season', default=2025, type=int)

        result = matchup_exploiter.get_defense_heatmap(
            position=position,
            season=season
        )

        if 'error' in result:
            return jsonify(result), 500

        return jsonify({
            'data': result,
            'meta': {
                'position': position,
                'season': season,
                'team_count': len(result.get('heatmap', []))
            }
        })

    except Exception as e:
        logger.error(f"Error getting defense heatmap: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
