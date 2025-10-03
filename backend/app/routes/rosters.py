"""
Roster management endpoints
"""
from flask import Blueprint, jsonify, request
from app.middleware.auth import login_required
from app.models.database import get_db_cursor
from datetime import datetime

bp = Blueprint('rosters', __name__, url_prefix='/api/rosters')


@bp.route('', methods=['GET'])
@login_required
def get_rosters(current_user):
    """Get all rosters for the current user"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, league_name, scoring_type, created_at, updated_at
                FROM user_rosters
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (current_user['id'],)
            )
            rosters = cursor.fetchall()

            roster_list = []
            for roster in rosters:
                roster_list.append({
                    'id': roster[0],
                    'name': roster[1],
                    'league_name': roster[2],
                    'scoring_type': roster[3],
                    'created_at': roster[4].isoformat() if roster[4] else None,
                    'updated_at': roster[5].isoformat() if roster[5] else None
                })

            return jsonify({'data': roster_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('', methods=['POST'])
@login_required
def create_roster(current_user):
    """Create a new roster"""
    try:
        data = request.json
        name = data.get('name')
        league_name = data.get('league_name', 'My League')
        scoring_type = data.get('scoring_type', 'PPR')

        if not name:
            return jsonify({'error': 'Roster name is required'}), 400

        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO user_rosters (user_id, name, league_name, scoring_type)
                VALUES (%s, %s, %s, %s)
                RETURNING id, name, league_name, scoring_type, created_at
                """,
                (current_user['id'], name, league_name, scoring_type)
            )
            new_roster = cursor.fetchone()

            return jsonify({
                'data': {
                    'id': new_roster[0],
                    'name': new_roster[1],
                    'league_name': new_roster[2],
                    'scoring_type': new_roster[3],
                    'created_at': new_roster[4].isoformat() if new_roster[4] else None
                }
            }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:roster_id>', methods=['GET'])
@login_required
def get_roster(current_user, roster_id):
    """Get a specific roster with players"""
    try:
        with get_db_cursor() as cursor:
            # Get roster details
            cursor.execute(
                """
                SELECT id, name, league_name, scoring_type, created_at, updated_at
                FROM user_rosters
                WHERE id = %s AND user_id = %s
                """,
                (roster_id, current_user['id'])
            )
            roster = cursor.fetchone()

            if not roster:
                return jsonify({'error': 'Roster not found'}), 404

            # Get players in roster
            cursor.execute(
                """
                SELECT id, player_id, player_name, position, team, roster_slot, is_starter, injury_status
                FROM roster_players
                WHERE roster_id = %s
                ORDER BY
                    CASE roster_slot
                        WHEN 'QB' THEN 1
                        WHEN 'RB' THEN 2
                        WHEN 'WR' THEN 3
                        WHEN 'TE' THEN 4
                        WHEN 'FLEX' THEN 5
                        WHEN 'K' THEN 6
                        WHEN 'DEF' THEN 7
                        WHEN 'BENCH' THEN 8
                    END
                """,
                (roster_id,)
            )
            players = cursor.fetchall()

            player_list = []
            for player in players:
                player_list.append({
                    'id': player[0],
                    'player_id': player[1],
                    'player_name': player[2],
                    'position': player[3],
                    'team': player[4],
                    'roster_slot': player[5],
                    'is_starter': player[6],
                    'injury_status': player[7]
                })

            return jsonify({
                'data': {
                    'id': roster[0],
                    'name': roster[1],
                    'league_name': roster[2],
                    'scoring_type': roster[3],
                    'created_at': roster[4].isoformat() if roster[4] else None,
                    'updated_at': roster[5].isoformat() if roster[5] else None,
                    'players': player_list
                }
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:roster_id>', methods=['PUT'])
@login_required
def update_roster(current_user, roster_id):
    """Update roster details"""
    try:
        data = request.json

        with get_db_cursor() as cursor:
            # Verify ownership
            cursor.execute(
                "SELECT id FROM user_rosters WHERE id = %s AND user_id = %s",
                (roster_id, current_user['id'])
            )
            if not cursor.fetchone():
                return jsonify({'error': 'Roster not found'}), 404

            # Update roster
            updates = []
            values = []

            if 'name' in data:
                updates.append('name = %s')
                values.append(data['name'])
            if 'league_name' in data:
                updates.append('league_name = %s')
                values.append(data['league_name'])
            if 'scoring_type' in data:
                updates.append('scoring_type = %s')
                values.append(data['scoring_type'])

            updates.append('updated_at = CURRENT_TIMESTAMP')
            values.append(roster_id)

            cursor.execute(
                f"UPDATE user_rosters SET {', '.join(updates)} WHERE id = %s RETURNING id, name, league_name, scoring_type",
                tuple(values)
            )
            updated_roster = cursor.fetchone()

            return jsonify({
                'data': {
                    'id': updated_roster[0],
                    'name': updated_roster[1],
                    'league_name': updated_roster[2],
                    'scoring_type': updated_roster[3]
                }
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:roster_id>', methods=['DELETE'])
@login_required
def delete_roster(current_user, roster_id):
    """Delete a roster"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "DELETE FROM user_rosters WHERE id = %s AND user_id = %s RETURNING id",
                (roster_id, current_user['id'])
            )
            deleted = cursor.fetchone()

            if not deleted:
                return jsonify({'error': 'Roster not found'}), 404

            return jsonify({'message': 'Roster deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:roster_id>/players', methods=['POST'])
@login_required
def add_player_to_roster(current_user, roster_id):
    """Add a player to a roster"""
    try:
        data = request.json

        with get_db_cursor() as cursor:
            # Verify roster ownership
            cursor.execute(
                "SELECT id FROM user_rosters WHERE id = %s AND user_id = %s",
                (roster_id, current_user['id'])
            )
            if not cursor.fetchone():
                return jsonify({'error': 'Roster not found'}), 404

            # Add player
            cursor.execute(
                """
                INSERT INTO roster_players
                (roster_id, player_id, player_name, position, team, roster_slot, is_starter, injury_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, player_id, player_name, position, team, roster_slot, is_starter, injury_status
                """,
                (
                    roster_id,
                    data.get('player_id'),
                    data.get('player_name'),
                    data.get('position'),
                    data.get('team'),
                    data.get('roster_slot', 'BENCH'),
                    data.get('is_starter', False),
                    data.get('injury_status', 'HEALTHY')
                )
            )
            new_player = cursor.fetchone()

            return jsonify({
                'data': {
                    'id': new_player[0],
                    'player_id': new_player[1],
                    'player_name': new_player[2],
                    'position': new_player[3],
                    'team': new_player[4],
                    'roster_slot': new_player[5],
                    'is_starter': new_player[6],
                    'injury_status': new_player[7]
                }
            }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:roster_id>/players/<int:player_roster_id>', methods=['PUT'])
@login_required
def update_roster_player(current_user, roster_id, player_roster_id):
    """Update a player in the roster"""
    try:
        data = request.json

        with get_db_cursor() as cursor:
            # Verify roster ownership
            cursor.execute(
                "SELECT id FROM user_rosters WHERE id = %s AND user_id = %s",
                (roster_id, current_user['id'])
            )
            if not cursor.fetchone():
                return jsonify({'error': 'Roster not found'}), 404

            # Update player
            updates = []
            values = []

            if 'roster_slot' in data:
                updates.append('roster_slot = %s')
                values.append(data['roster_slot'])
            if 'is_starter' in data:
                updates.append('is_starter = %s')
                values.append(data['is_starter'])
            if 'injury_status' in data:
                updates.append('injury_status = %s')
                values.append(data['injury_status'])

            values.extend([player_roster_id, roster_id])

            cursor.execute(
                f"""
                UPDATE roster_players
                SET {', '.join(updates)}
                WHERE id = %s AND roster_id = %s
                RETURNING id, player_id, player_name, position, team, roster_slot, is_starter, injury_status
                """,
                tuple(values)
            )
            updated_player = cursor.fetchone()

            if not updated_player:
                return jsonify({'error': 'Player not found in roster'}), 404

            return jsonify({
                'data': {
                    'id': updated_player[0],
                    'player_id': updated_player[1],
                    'player_name': updated_player[2],
                    'position': updated_player[3],
                    'team': updated_player[4],
                    'roster_slot': updated_player[5],
                    'is_starter': updated_player[6],
                    'injury_status': updated_player[7]
                }
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:roster_id>/players/<int:player_roster_id>', methods=['DELETE'])
@login_required
def remove_player_from_roster(current_user, roster_id, player_roster_id):
    """Remove a player from the roster"""
    try:
        with get_db_cursor() as cursor:
            # Verify roster ownership
            cursor.execute(
                "SELECT id FROM user_rosters WHERE id = %s AND user_id = %s",
                (roster_id, current_user['id'])
            )
            if not cursor.fetchone():
                return jsonify({'error': 'Roster not found'}), 404

            # Delete player
            cursor.execute(
                "DELETE FROM roster_players WHERE id = %s AND roster_id = %s RETURNING id",
                (player_roster_id, roster_id)
            )
            deleted = cursor.fetchone()

            if not deleted:
                return jsonify({'error': 'Player not found in roster'}), 404

            return jsonify({'message': 'Player removed from roster successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
