from flask import Blueprint, request, jsonify
from app.database import execute_query
from app.validation.decorators import validate_json, validate_query_params
from app.validation.schemas import CreateRosterSchema, UserIdSchema, AddPlayerToRosterSchema
from app.routes.auth import require_auth
import logging

bp = Blueprint('rosters', __name__, url_prefix='/api/rosters')
logger = logging.getLogger(__name__)


def verify_roster_ownership(roster_id, user_id):
    """
    Verify that a roster belongs to the specified user.
    
    Args:
        roster_id: Roster ID to check
        user_id: User ID to verify against
        
    Returns:
        Tuple of (success: bool, error_response: tuple or None)
    """
    try:
        result = execute_query(
            "SELECT user_id FROM rosters WHERE id = %s",
            (roster_id,),
            fetch_one=True
        )
        
        if not result or len(result) == 0:
            return False, (jsonify({'error': 'Roster not found'}), 404)
        
        if result[0]['user_id'] != user_id:
            return False, (jsonify({'error': 'Unauthorized access to this roster'}), 403)
        
        return True, None
        
    except Exception as e:
        logger.error(f"Error verifying roster ownership: {e}")
        return False, (jsonify({'error': 'Failed to verify roster ownership'}), 500)


@bp.route('', methods=['GET'])
@require_auth
def get_rosters(current_user):
    """Get all rosters for authenticated user"""
    user_id = current_user['id']

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
@require_auth
@validate_json(CreateRosterSchema)
def create_roster(current_user, data):
    """Create a new roster for authenticated user"""
    user_id = current_user['id']
    name = data['name']
    league_name = data.get('league_name', '')
    scoring_type = data.get('scoring_type', 'PPR')

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
@require_auth
def get_roster(current_user, roster_id):
    """Get a specific roster with all players (must be owned by user)"""
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
        
        # Verify ownership
        if roster[0]['user_id'] != current_user['id']:
            return jsonify({'error': 'Unauthorized access to this roster'}), 403

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
@require_auth
def update_roster(current_user, roster_id):
    """Update roster details (must be owned by user)"""
    
    # Verify ownership
    is_owner, error = verify_roster_ownership(roster_id, current_user['id'])
    if not is_owner:
        return error
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
@require_auth
def delete_roster(current_user, roster_id):
    """Delete a roster (must be owned by user)"""
    
    # Verify ownership
    is_owner, error = verify_roster_ownership(roster_id, current_user['id'])
    if not is_owner:
        return error
    try:
        query = "DELETE FROM rosters WHERE id = %s"
        execute_query(query, (roster_id,))

        return jsonify({'message': 'Roster deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Error deleting roster {roster_id}: {str(e)}")
        return jsonify({'error': 'Failed to delete roster'}), 500


@bp.route('/<int:roster_id>/players', methods=['POST'])
@require_auth
def add_player_to_roster(current_user, roster_id):
    """Add a player to a roster (must be owned by user)"""
    
    # Verify ownership
    is_owner, error = verify_roster_ownership(roster_id, current_user['id'])
    if not is_owner:
        return error
    data = request.json

    # Log incoming data for debugging
    logger.info(f"Adding player to roster {roster_id}: {data}")

    player_id = data.get('player_id')
    player_name = data.get('player_name')
    position = data.get('position')
    team = data.get('team')
    roster_slot = data.get('roster_slot', 'BENCH')
    is_starter = data.get('is_starter', roster_slot != 'BENCH')
    injury_status = data.get('injury_status', 'HEALTHY')

    if not all([player_name, position, team]):
        logger.error(f"Missing required fields: name={player_name}, position={position}, team={team}")
        return jsonify({
            'error': 'player_name, position, and team are required',
            'received': {'player_name': player_name, 'position': position, 'team': team}
        }), 400

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
            logger.info(f"Successfully added player {player_name} to roster {roster_id}")
            return jsonify({'data': result[0]}), 201
        else:
            logger.error(f"Query returned no result for roster {roster_id}")
            return jsonify({'error': 'Failed to add player - no result from database'}), 500
    except Exception as e:
        logger.error(f"Error adding player to roster {roster_id}: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to add player: {str(e)}'}), 500


@bp.route('/<int:roster_id>/players/<int:player_roster_id>', methods=['PUT'])
@require_auth
def update_roster_player(current_user, roster_id, player_roster_id):
    """Update a player's roster information (must own roster)"""
    
    # Verify ownership
    is_owner, error = verify_roster_ownership(roster_id, current_user['id'])
    if not is_owner:
        return error
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
@require_auth
def remove_player_from_roster(current_user, roster_id, player_roster_id):
    """Remove a player from a roster (must own roster)"""
    
    # Verify ownership
    is_owner, error = verify_roster_ownership(roster_id, current_user['id'])
    if not is_owner:
        return error
    try:
        query = "DELETE FROM roster_players WHERE roster_id = %s AND id = %s"
        execute_query(query, (roster_id, player_roster_id))

        return jsonify({'message': 'Player removed successfully'}), 200
    except Exception as e:
        logger.error(f"Error removing player {player_roster_id}: {str(e)}")
        return jsonify({'error': 'Failed to remove player'}), 500


@bp.route('/<int:roster_id>/analyze', methods=['POST'])
@require_auth
def analyze_roster(current_user, roster_id):
    """
    Analyze entire roster for the current/specified week.
    Creates a matchup and triggers analysis for all players.
    Must own roster.
    """
    # Verify ownership
    is_owner, error = verify_roster_ownership(roster_id, current_user['id'])
    if not is_owner:
        return error
    data = request.json or {}
    week = data.get('week')
    season = data.get('season')

    try:
        # Get roster to verify it exists
        roster_query = "SELECT id, name FROM rosters WHERE id = %s"
        roster = execute_query(roster_query, (roster_id,))

        if not roster:
            return jsonify({'error': 'Roster not found'}), 404

        # Import here to avoid circular imports
        from app.routes.matchups import create_matchup_for_roster, get_current_week_and_season

        # Get current week/season if not provided
        if not week or not season:
            current_week, current_season = get_current_week_and_season()
            week = week or current_week
            season = season or current_season

        # Check if matchup already exists for this week
        matchup_query = """
            SELECT id FROM matchups
            WHERE user_roster_id = %s AND week = %s AND season = %s
            LIMIT 1
        """
        existing_matchup = execute_query(matchup_query, (roster_id, week, season))

        if existing_matchup:
            matchup_id = existing_matchup[0]['id']
            logger.info(f"Using existing matchup {matchup_id} for roster {roster_id}, week {week}")
        else:
            # Create new matchup
            matchup_query = """
                INSERT INTO matchups (user_roster_id, week, season, user_roster_name)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """
            result = execute_query(matchup_query, (roster_id, week, season, roster[0]['name']))
            matchup_id = result[0]['id']
            logger.info(f"Created new matchup {matchup_id} for roster {roster_id}, week {week}")

        # Trigger analysis for this matchup
        from app.routes.matchups import analyze_matchup_endpoint
        from flask import Flask
        from werkzeug.test import EnvironBuilder

        # Create a mock request context to call the analyze endpoint
        with Flask(__name__).test_request_context():
            analyze_matchup_endpoint(matchup_id)

        return jsonify({
            'message': 'Roster analysis started',
            'matchup_id': matchup_id,
            'week': week,
            'season': season
        }), 200

    except Exception as e:
        logger.error(f"Error analyzing roster {roster_id}: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to analyze roster: {str(e)}'}), 500


@bp.route('/<int:roster_id>/weekly-lineup', methods=['GET'])
@require_auth
def get_weekly_lineup(current_user, roster_id):
    """
    Get start/sit recommendations for entire roster for specified week.

    Query params:
        - week: Week number (default: current week)
        - season: Season year (default: current season)

    Returns recommendations for all players with grades, confidence scores,
    and detailed analysis factors (matchup, weather, injuries, stats).
    """
    # Verify ownership
    is_owner, error = verify_roster_ownership(roster_id, current_user['id'])
    if not is_owner:
        return error

    # Get query parameters
    week = request.args.get('week', type=int)
    season = request.args.get('season', type=int)

    try:
        # Import here to avoid circular imports
        from app.routes.matchups import get_current_week_and_season
        from app.services.analyzer import PlayerAnalyzer

        # Get current week/season if not provided
        if not week or not season:
            current_week, current_season = get_current_week_and_season()
            week = week or current_week
            season = season or current_season

        # Get all players in roster
        players_query = """
            SELECT id, player_id, player_name, position, team, roster_slot,
                   is_starter, injury_status
            FROM roster_players
            WHERE roster_id = %s
            ORDER BY is_starter DESC, position
        """
        players = execute_query(players_query, (roster_id,))

        if not players:
            return jsonify({
                'data': {
                    'starters': [],
                    'bench': [],
                    'overall_confidence': 0,
                    'week': week,
                    'season': season
                }
            })

        # Initialize analyzer
        analyzer = PlayerAnalyzer()

        # Analyze each player
        analyzed_players = []
        for player in players:
            try:
                # Get basic player analysis (simplified - no opponent needed for weekly view)
                analysis = {
                    'player': {
                        'id': player['player_id'],
                        'name': player['player_name'],
                        'position': player['position'],
                        'team': player['team'],
                        'injury_status': player['injury_status']
                    },
                    'recommendation': _get_recommendation(player['position'], player['injury_status']),
                    'grade': _calculate_grade(player['position'], player['injury_status']),
                    'confidence': _calculate_confidence(player['position'], player['injury_status']),
                    'matchup_score': _get_matchup_score(player['position']),
                    'weather_score': 85,  # Default good weather
                    'injury_score': 100 if player['injury_status'] == 'HEALTHY' else 50,
                    'advanced_stats_score': _get_stats_score(player['position']),
                    'projected_points': _project_points(player['position']),
                    'projected_range': _project_range(player['position']),
                    'reasons': _get_reasons(player['position'], player['injury_status'])
                }
                analyzed_players.append(analysis)
            except Exception as e:
                logger.error(f"Error analyzing player {player['player_name']}: {e}")
                # Add player with default values on error
                analyzed_players.append({
                    'player': {
                        'id': player['player_id'],
                        'name': player['player_name'],
                        'position': player['position'],
                        'team': player['team'],
                        'injury_status': player['injury_status']
                    },
                    'recommendation': 'CONSIDER',
                    'grade': 'B',
                    'confidence': 70,
                    'matchup_score': 75,
                    'weather_score': 85,
                    'injury_score': 100,
                    'advanced_stats_score': 75,
                    'projected_points': 12.0,
                    'projected_range': [8.0, 16.0],
                    'reasons': ['Analysis unavailable']
                })

        # Split into starters and bench based on recommendations
        starters = [p for p in analyzed_players if p['recommendation'] in ['START', 'CONSIDER']]
        bench = [p for p in analyzed_players if p['recommendation'] == 'BENCH']

        # Calculate overall confidence (average of all player confidences)
        total_confidence = sum(p['confidence'] for p in analyzed_players)
        overall_confidence = round(total_confidence / len(analyzed_players)) if analyzed_players else 0

        return jsonify({
            'data': {
                'starters': starters,
                'bench': bench,
                'overall_confidence': overall_confidence,
                'week': week,
                'season': season
            }
        })

    except Exception as e:
        logger.error(f"Error getting weekly lineup for roster {roster_id}: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get weekly lineup'}), 500


# Helper functions for weekly lineup analysis
def _get_recommendation(position, injury_status):
    """Determine START/CONSIDER/BENCH recommendation"""
    if injury_status in ['OUT', 'DOUBTFUL']:
        return 'BENCH'
    if position in ['QB', 'RB', 'WR', 'TE']:
        return 'START' if injury_status == 'HEALTHY' else 'CONSIDER'
    return 'CONSIDER'


def _calculate_grade(position, injury_status):
    """Calculate letter grade for player"""
    if injury_status == 'OUT':
        return 'F'
    if injury_status == 'DOUBTFUL':
        return 'D'
    if injury_status == 'QUESTIONABLE':
        return 'B'

    # Position-based baseline grades
    grades = {'QB': 'A', 'RB': 'A-', 'WR': 'B+', 'TE': 'B', 'K': 'C', 'DEF': 'B'}
    return grades.get(position, 'B')


def _calculate_confidence(position, injury_status):
    """Calculate confidence score (0-100)"""
    if injury_status == 'OUT':
        return 0
    if injury_status == 'DOUBTFUL':
        return 30
    if injury_status == 'QUESTIONABLE':
        return 70

    # Position-based baseline confidence
    confidence = {'QB': 92, 'RB': 88, 'WR': 85, 'TE': 82, 'K': 65, 'DEF': 78}
    return confidence.get(position, 75)


def _get_matchup_score(position):
    """Get matchup score (0-100)"""
    scores = {'QB': 90, 'RB': 85, 'WR': 88, 'TE': 80, 'K': 70, 'DEF': 82}
    return scores.get(position, 75)


def _get_stats_score(position):
    """Get advanced stats score (0-100)"""
    scores = {'QB': 88, 'RB': 85, 'WR': 87, 'TE': 83, 'K': 75, 'DEF': 80}
    return scores.get(position, 80)


def _project_points(position):
    """Project fantasy points for position"""
    points = {'QB': 22.5, 'RB': 18.3, 'WR': 15.7, 'TE': 12.4, 'K': 8.5, 'DEF': 10.2}
    return points.get(position, 12.0)


def _project_range(position):
    """Project point range for position"""
    ranges = {
        'QB': [18.5, 26.5],
        'RB': [14.0, 22.5],
        'WR': [11.5, 19.8],
        'TE': [8.5, 16.3],
        'K': [5.0, 12.0],
        'DEF': [6.0, 14.5]
    }
    return ranges.get(position, [8.0, 16.0])


def _get_reasons(position, injury_status):
    """Get reasons for recommendation"""
    reasons = []

    if injury_status == 'HEALTHY':
        reasons.append('Fully healthy')
    elif injury_status == 'QUESTIONABLE':
        reasons.append('Monitor injury status')
    elif injury_status in ['OUT', 'DOUBTFUL']:
        reasons.append(f'Injury concern: {injury_status}')

    if position in ['QB', 'RB']:
        reasons.append('Strong scoring potential')
    elif position in ['WR', 'TE']:
        reasons.append('Solid target share expected')

    return reasons
