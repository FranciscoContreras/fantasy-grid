from flask import Blueprint, request, jsonify, redirect, url_for
from app.routes.auth import require_auth
from app.services.yahoo_oauth_service import YahooOAuthService
from app.database import execute_query
import os
import logging

bp = Blueprint('yahoo', __name__, url_prefix='/api/yahoo')
logger = logging.getLogger(__name__)

# Initialize Yahoo OAuth service
yahoo_service = YahooOAuthService()

@bp.route('/auth')
def yahoo_auth():
    """
    Initiate Yahoo OAuth flow

    Query params:
    - token: JWT token for authentication
    """
    token = request.args.get('token')
    if not token:
        return jsonify({'error': 'Authentication token required'}), 401

    if not yahoo_service.is_configured():
        return jsonify({
            'error': 'Yahoo OAuth not configured',
            'message': 'Yahoo OAuth credentials are missing. Please contact support.'
        }), 503

    try:
        # Verify the JWT token to get user ID
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        payload = auth_service.verify_token(token)

        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        user_id = payload['user_id']

        # Generate Yahoo OAuth URL for this user
        auth_data = yahoo_service.get_auth_url(user_id)

        # Redirect user to Yahoo OAuth
        return redirect(auth_data['auth_url'])

    except Exception as e:
        logger.error(f"Yahoo OAuth initiation failed: {e}")
        return jsonify({'error': 'Failed to initiate Yahoo authentication'}), 500

@bp.route('/callback')
def yahoo_callback():
    """
    Handle Yahoo OAuth callback

    Query params:
    - code: Authorization code from Yahoo
    - state: CSRF protection state
    """
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')

    if error:
        logger.error(f"Yahoo OAuth error: {error}")
        # Redirect to frontend with error
        frontend_url = os.getenv('FRONTEND_URL', 'https://fantasy-grid-8e65f9ca9754.herokuapp.com')
        return redirect(f"{frontend_url}/?yahoo_error={error}")

    if not code or not state:
        return jsonify({'error': 'Missing authorization code or state'}), 400

    try:
        # Extract user_id from state (we need to store this in our OAuth state)
        # For now, we'll need to modify the state handling to include user info
        # This is a simplified version - in production, decrypt/decode the state properly

        # For demonstration, let's assume we can get user_id from the state
        # In reality, you'd store state->user_id mapping in the database
        query = "SELECT user_id FROM yahoo_oauth_states WHERE state = %s"
        result = execute_query(query, (state,))

        if not result:
            return jsonify({'error': 'Invalid or expired state'}), 400

        user_id = result[0]['user_id']

        # Exchange code for tokens
        token_data = yahoo_service.exchange_code_for_token(code, state, user_id)

        # Redirect to frontend with success
        frontend_url = os.getenv('FRONTEND_URL', 'https://fantasy-grid-8e65f9ca9754.herokuapp.com')
        return redirect(f"{frontend_url}/?yahoo_success=true")

    except Exception as e:
        logger.error(f"Yahoo OAuth callback failed: {e}")
        frontend_url = os.getenv('FRONTEND_URL', 'https://fantasy-grid-8e65f9ca9754.herokuapp.com')
        return redirect(f"{frontend_url}/?yahoo_error=callback_failed")

@bp.route('/leagues')
@require_auth
def get_yahoo_leagues(current_user):
    """
    Get user's Yahoo Fantasy leagues for the authenticated user

    Returns list of leagues or indicates need for OAuth
    """
    user_id = current_user['id']

    if not yahoo_service.is_configured():
        return jsonify({
            'error': 'Yahoo OAuth not configured',
            'message': 'Yahoo OAuth credentials are missing. Please contact support.'
        }), 503

    try:
        # Check if user has valid Yahoo tokens
        leagues = yahoo_service.get_user_leagues(user_id)

        return jsonify({
            'data': {
                'leagues': leagues,
                'message': f'Found {len(leagues)} leagues for user'
            },
            'success': True
        })

    except Exception as e:
        logger.error(f"Failed to get user leagues: {e}")

        # If it's a token issue, indicate user needs to authenticate
        if 'token' in str(e).lower() or 'access' in str(e).lower():
            return jsonify({
                'data': {
                    'leagues': [],
                    'message': 'Yahoo authentication required'
                },
                'needs_auth': True
            })

        return jsonify({
            'error': 'Failed to fetch Yahoo leagues',
            'message': str(e)
        }), 500

@bp.route('/import', methods=['POST'])
@require_auth
def import_yahoo_roster(current_user):
    """
    Import roster from Yahoo Fantasy for the authenticated user

    Body:
    - team_key: Yahoo team key
    - roster_name: Optional custom name for roster
    """
    data = request.get_json()

    if not data or 'team_key' not in data:
        return jsonify({'error': 'team_key is required'}), 400

    user_id = current_user['id']
    team_key = data['team_key']
    roster_name = data.get('roster_name', f'Yahoo Team {team_key.split(".")[-1]}')

    if not yahoo_service.is_configured():
        return jsonify({
            'error': 'Yahoo OAuth not configured',
            'message': 'Yahoo OAuth credentials are missing. Please contact support.'
        }), 503

    try:
        # Get roster from Yahoo
        yahoo_roster = yahoo_service.get_team_roster(user_id, team_key)

        # Create new roster in our database
        roster_query = """
            INSERT INTO rosters (user_id, name, league_name, scoring_type, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id
        """

        roster_result = execute_query(roster_query, (
            user_id,
            roster_name,
            'Yahoo Fantasy',
            'PPR'  # Default to PPR, could be extracted from Yahoo data
        ))

        if not roster_result:
            return jsonify({'error': 'Failed to create roster'}), 500

        roster_id = roster_result[0]['id']
        matched_players = 0

        # Import players from Yahoo roster
        for yahoo_player in yahoo_roster:
            try:
                # Insert player into our roster
                player_query = """
                    INSERT INTO roster_players (
                        roster_id, player_id, player_name, position, team,
                        roster_slot, is_starter, injury_status, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """

                execute_query(player_query, (
                    roster_id,
                    yahoo_player.get('player_id'),
                    yahoo_player.get('name'),
                    yahoo_player.get('position'),
                    yahoo_player.get('team'),
                    yahoo_player.get('roster_position', 'BENCH'),
                    yahoo_player.get('roster_position') != 'BN',  # Not bench = starter
                    'HEALTHY'  # Default injury status
                ))

                matched_players += 1

            except Exception as e:
                logger.warning(f"Failed to import player {yahoo_player.get('name')}: {e}")
                continue

        logger.info(f"Imported {matched_players} players for user {user_id} from Yahoo team {team_key}")

        return jsonify({
            'data': {
                'matched_players': matched_players,
                'roster_id': roster_id,
                'roster_name': roster_name,
                'message': f'Successfully imported {matched_players} players from Yahoo'
            },
            'success': True
        })

    except Exception as e:
        logger.error(f"Yahoo roster import failed: {e}")
        return jsonify({
            'error': 'Failed to import Yahoo roster',
            'message': str(e)
        }), 500

@bp.route('/status')
@require_auth
def yahoo_status(current_user):
    """
    Get Yahoo integration status for current user
    """
    user_id = current_user['id']

    if not yahoo_service.is_configured():
        return jsonify({
            'data': {
                'is_authenticated': False,
                'has_leagues': False,
                'configured': False,
                'message': 'Yahoo OAuth not configured'
            }
        })

    try:
        # Check if user has stored tokens
        query = """
            SELECT access_token, expires_at, refresh_token
            FROM yahoo_tokens
            WHERE user_id = %s
        """
        result = execute_query(query, (user_id,))

        has_tokens = bool(result)
        is_authenticated = False

        if has_tokens:
            token_data = result[0]
            # Check if token is still valid (not expired)
            from datetime import datetime
            expires_at = token_data['expires_at']
            is_authenticated = expires_at and datetime.utcnow() < expires_at

        return jsonify({
            'data': {
                'is_authenticated': is_authenticated,
                'has_tokens': has_tokens,
                'configured': True,
                'message': 'Yahoo OAuth ready' if is_authenticated else 'Authentication required'
            }
        })

    except Exception as e:
        logger.error(f"Yahoo status check failed: {e}")
        return jsonify({
            'data': {
                'is_authenticated': False,
                'has_leagues': False,
                'configured': True,
                'error': str(e)
            }
        })