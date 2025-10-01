from flask import Blueprint, request, jsonify
from app.database import execute_query
import logging

bp = Blueprint('rosters', __name__, url_prefix='/api/rosters')
logger = logging.getLogger(__name__)


@bp.route('', methods=['GET'])
def get_rosters():
    """Get all rosters for a user"""
    user_id = request.args.get('user_id', 'default_user')

    try:
        query = """
            SELECT id, user_id, name, league_name, scoring_type, is_active, created_at
            FROM rosters
            WHERE user_id = %s
            ORDER BY is_active DESC, created_at DESC
        """
        rosters = execute_query(query, (user_id,))

        return jsonify({
            'data': rosters,
            'count': len(rosters)
        })
    except Exception as e:
        logger.error(f"Error fetching rosters: {str(e)}")
        return jsonify({'error': 'Failed to fetch rosters'}), 500


@bp.route('', methods=['POST'])
def create_roster():
    """Create a new roster"""
    data = request.json
    user_id = data.get('user_id', 'default_user')
    name = data.get('name')
    league_name = data.get('league_name', '')
    scoring_type = data.get('scoring_type', 'PPR')

    if not name:
        return jsonify({'error': 'Roster name is required'}), 400

    try:
        query = """
            INSERT INTO rosters (user_id, name, league_name, scoring_type)
            VALUES (%s, %s, %s, %s)
            RETURNING id, user_id, name, league_name, scoring_type, is_active, created_at
        """
        result = execute_query(query, (user_id, name, league_name, scoring_type))

        if result:
            return jsonify({'data': result[0]}), 201
        else:
            return jsonify({'error': 'Failed to create roster'}), 500
    except Exception as e:
        logger.error(f"Error creating roster: {str(e)}")
        return jsonify({'error': 'Failed to create roster'}), 500


@bp.route('/<int:roster_id>', methods=['GET'])
def get_roster(roster_id):
    """Get a specific roster with all players"""
    try:
        # Get roster details
        roster_query = """
            SELECT id, user_id, name, league_name, scoring_type, is_active, created_at
            FROM rosters
            WHERE id = %s
        """
        roster = execute_query(roster_query, (roster_id,))

        if not roster:
            return jsonify({'error': 'Roster not found'}), 404

        # Get all players in roster
        players_query = """
            SELECT id, player_id, player_name, position, team, roster_slot,
                   is_starter, injury_status, added_at
            FROM roster_players
            WHERE roster_id = %s
            ORDER BY
                CASE roster_slot
                    WHEN 'QB' THEN 1
                    WHEN 'RB1' THEN 2
                    WHEN 'RB2' THEN 3
                    WHEN 'WR1' THEN 4
                    WHEN 'WR2' THEN 5
                    WHEN 'WR3' THEN 6
                    WHEN 'TE' THEN 7
                    WHEN 'FLEX' THEN 8
                    WHEN 'K' THEN 9
                    WHEN 'DEF' THEN 10
                    ELSE 11
                END
        """
        players = execute_query(players_query, (roster_id,))

        roster_data = roster[0]
        roster_data['players'] = players

        return jsonify({'data': roster_data})
    except Exception as e:
        logger.error(f"Error fetching roster {roster_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch roster'}), 500


@bp.route('/<int:roster_id>', methods=['PUT'])
def update_roster(roster_id):
    """Update roster details"""
    data = request.json
    name = data.get('name')
    league_name = data.get('league_name')
    scoring_type = data.get('scoring_type')
    is_active = data.get('is_active')

    updates = []
    params = []

    if name:
        updates.append("name = %s")
        params.append(name)
    if league_name is not None:
        updates.append("league_name = %s")
        params.append(league_name)
    if scoring_type:
        updates.append("scoring_type = %s")
        params.append(scoring_type)
    if is_active is not None:
        updates.append("is_active = %s")
        params.append(is_active)

    if not updates:
        return jsonify({'error': 'No fields to update'}), 400

    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(roster_id)

    try:
        query = f"""
            UPDATE rosters
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, user_id, name, league_name, scoring_type, is_active, updated_at
        """
        result = execute_query(query, tuple(params))

        if result:
            return jsonify({'data': result[0]})
        else:
            return jsonify({'error': 'Roster not found'}), 404
    except Exception as e:
        logger.error(f"Error updating roster {roster_id}: {str(e)}")
        return jsonify({'error': 'Failed to update roster'}), 500


@bp.route('/<int:roster_id>', methods=['DELETE'])
def delete_roster(roster_id):
    """Delete a roster"""
    try:
        query = "DELETE FROM rosters WHERE id = %s"
        execute_query(query, (roster_id,))

        return jsonify({'message': 'Roster deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Error deleting roster {roster_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete roster'}), 500


@bp.route('/<int:roster_id>/players', methods=['POST'])
def add_player_to_roster(roster_id):
    """Add a player to a roster"""
    data = request.json
    player_id = data.get('player_id')
    player_name = data.get('player_name')
    position = data.get('position')
    team = data.get('team')
    roster_slot = data.get('roster_slot', 'BENCH')
    is_starter = data.get('is_starter', roster_slot != 'BENCH')
    injury_status = data.get('injury_status', 'HEALTHY')

    if not all([player_name, position, team]):
        return jsonify({'error': 'player_name, position, and team are required'}), 400

    try:
        query = """
            INSERT INTO roster_players
            (roster_id, player_id, player_name, position, team, roster_slot, is_starter, injury_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, player_id, player_name, position, team, roster_slot, is_starter, injury_status, added_at
        """
        result = execute_query(query, (roster_id, player_id, player_name, position, team,
                                      roster_slot, is_starter, injury_status))

        if result:
            return jsonify({'data': result[0]}), 201
        else:
            return jsonify({'error': 'Failed to add player'}), 500
    except Exception as e:
        logger.error(f"Error adding player to roster {roster_id}: {str(e)}")
        return jsonify({'error': 'Failed to add player'}), 500


@bp.route('/<int:roster_id>/players/<int:player_roster_id>', methods=['PUT'])
def update_roster_player(roster_id, player_roster_id):
    """Update a player's roster information"""
    data = request.json
    roster_slot = data.get('roster_slot')
    is_starter = data.get('is_starter')
    injury_status = data.get('injury_status')

    updates = []
    params = []

    if roster_slot:
        updates.append("roster_slot = %s")
        params.append(roster_slot)
    if is_starter is not None:
        updates.append("is_starter = %s")
        params.append(is_starter)
    if injury_status:
        updates.append("injury_status = %s")
        params.append(injury_status)

    if not updates:
        return jsonify({'error': 'No fields to update'}), 400

    params.extend([roster_id, player_roster_id])

    try:
        query = f"""
            UPDATE roster_players
            SET {', '.join(updates)}
            WHERE roster_id = %s AND id = %s
            RETURNING id, player_id, player_name, position, team, roster_slot, is_starter, injury_status
        """
        result = execute_query(query, tuple(params))

        if result:
            return jsonify({'data': result[0]})
        else:
            return jsonify({'error': 'Player not found'}), 404
    except Exception as e:
        logger.error(f"Error updating player {player_roster_id}: {str(e)}")
        return jsonify({'error': 'Failed to update player'}), 500


@bp.route('/<int:roster_id>/players/<int:player_roster_id>', methods=['DELETE'])
def remove_player_from_roster(roster_id, player_roster_id):
    """Remove a player from a roster"""
    try:
        query = "DELETE FROM roster_players WHERE roster_id = %s AND id = %s"
        execute_query(query, (roster_id, player_roster_id))

        return jsonify({'message': 'Player removed successfully'}), 200
    except Exception as e:
        logger.error(f"Error removing player {player_roster_id}: {str(e)}")
        return jsonify({'error': 'Failed to remove player'}), 500
