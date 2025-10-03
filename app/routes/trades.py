from flask import Blueprint, jsonify, request
from app.services.trade_analyzer import TradeAnalyzer
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('trades', __name__, url_prefix='/api/trades')

trade_analyzer = TradeAnalyzer()


@bp.route('/evaluate', methods=['POST'])
def evaluate_trade():
    """
    Evaluate a trade proposal between two teams
    Request body:
        {
            "team_a_gives": ["player_id_1", "player_id_2"],
            "team_b_gives": ["player_id_3"],
            "season": 2024  // optional
        }
    """
    try:
        data = request.json
        team_a_gives = data.get('team_a_gives', [])
        team_b_gives = data.get('team_b_gives', [])
        season = data.get('season', 2024)

        if not team_a_gives or not team_b_gives:
            return jsonify({'error': 'Both teams must give at least one player'}), 400

        result = trade_analyzer.evaluate_trade(
            team_a_gives=team_a_gives,
            team_b_gives=team_b_gives,
            season=season
        )

        if 'error' in result:
            return jsonify(result), 500

        return jsonify({
            'data': result,
            'meta': {
                'team_a_count': len(team_a_gives),
                'team_b_count': len(team_b_gives),
                'trade_type': result.get('analysis', {}).get('trade_type')
            }
        })

    except Exception as e:
        logger.error(f"Error evaluating trade: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/suggestions/<player_id>', methods=['GET'])
def get_trade_suggestions(player_id):
    """
    Get trade suggestions for a given player
    Path params:
        - player_id: Player ID to trade away
    Query params:
        - positions: Comma-separated list of desired positions (e.g., "RB,WR")
        - season: NFL season year (default: 2024)
    """
    try:
        positions_str = request.args.get('positions')
        target_positions = positions_str.split(',') if positions_str else None
        season = request.args.get('season', default=2024, type=int)

        result = trade_analyzer.suggest_trades(
            player_id=player_id,
            target_positions=target_positions,
            season=season
        )

        if 'error' in result:
            return jsonify(result), 404 if result['error'] == 'Player not found' else 500

        return jsonify({
            'data': result,
            'meta': {
                'player_id': player_id,
                'target_positions': target_positions,
                'suggestion_count': result.get('total_suggestions', 0)
            }
        })

    except Exception as e:
        logger.error(f"Error getting trade suggestions for player {player_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
