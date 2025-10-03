from flask import Blueprint, jsonify, request
from app.services.league_intelligence import LeagueIntelligence
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('league', __name__, url_prefix='/api/league')

league_intelligence = LeagueIntelligence()


@bp.route('/opponent/analyze', methods=['POST'])
def analyze_opponent():
    """
    Analyze opponent's roster and suggest game plan
    Request body:
        {
            "opponent_roster": [{"id": "...", "position": "...", ...}],
            "your_roster": [{"id": "...", "position": "...", ...}],
            "week": 5,  // optional
            "season": 2024  // optional
        }
    """
    try:
        data = request.json
        opponent_roster = data.get('opponent_roster', [])
        your_roster = data.get('your_roster', [])
        week = data.get('week')
        season = data.get('season', 2024)

        if not opponent_roster or not your_roster:
            return jsonify({'error': 'Both rosters are required'}), 400

        result = league_intelligence.analyze_opponent(
            opponent_roster=opponent_roster,
            your_roster=your_roster,
            week=week,
            season=season
        )

        if 'error' in result:
            return jsonify(result), 500

        return jsonify({
            'data': result,
            'meta': {
                'opponent_players': len(opponent_roster),
                'your_players': len(your_roster),
                'week': week
            }
        })

    except Exception as e:
        logger.error(f"Error analyzing opponent: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/playoffs/simulate', methods=['POST'])
def simulate_playoffs():
    """
    Simulate playoff odds using Monte Carlo simulation
    Request body:
        {
            "current_record": {"wins": 6, "losses": 3},
            "remaining_schedule": [
                {"week": 11, "opponent": "Team A", "win_probability": 65},
                {"week": 12, "opponent": "Team B", "win_probability": 45}
            ],
            "league_standings": [...],  // optional
            "num_simulations": 1000  // optional, default 1000
        }
    """
    try:
        data = request.json
        current_record = data.get('current_record')
        remaining_schedule = data.get('remaining_schedule', [])
        league_standings = data.get('league_standings')
        num_simulations = data.get('num_simulations', 1000)

        if not current_record:
            return jsonify({'error': 'current_record is required'}), 400

        if 'wins' not in current_record or 'losses' not in current_record:
            return jsonify({'error': 'current_record must include wins and losses'}), 400

        # Validate num_simulations
        if num_simulations < 100:
            num_simulations = 100
        elif num_simulations > 10000:
            num_simulations = 10000

        result = league_intelligence.simulate_playoffs(
            current_record=current_record,
            remaining_schedule=remaining_schedule,
            league_standings=league_standings,
            num_simulations=num_simulations
        )

        if 'error' in result:
            return jsonify(result), 500

        return jsonify({
            'data': result,
            'meta': {
                'simulations': num_simulations,
                'games_remaining': len(remaining_schedule)
            }
        })

    except Exception as e:
        logger.error(f"Error simulating playoffs: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
