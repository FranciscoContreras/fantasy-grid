"""
Yahoo Fantasy OAuth and Roster Import Routes

Handles:
- OAuth 2.0 authentication flow
- League fetching
- Roster importing
- Sync operations
"""

from flask import Blueprint, request, jsonify, redirect, session, url_for
from app.routes.auth import require_auth
from app.services.yahoo_oauth_service import YahooOAuthService
from app.services.yahoo_fantasy_client import YahooFantasyClient
from app.services.yahoo_roster_import_service import YahooRosterImportService
from app.validation.decorators import validate_json
from marshmallow import Schema, fields, validate
import logging
import os

logger = logging.getLogger(__name__)

bp = Blueprint('yahoo', __name__, url_prefix='/api/yahoo')

# Initialize services
oauth_service = YahooOAuthService()
import_service = YahooRosterImportService()


# ============================================================================
# OAuth Flow Routes
# ============================================================================

@bp.route('/auth', methods=['GET'])
def start_oauth():
    """
    Initiate Yahoo OAuth flow

    Redirects user to Yahoo login page
    Accepts token via query parameter or Authorization header
    """
    try:
        # Try to get token from query parameter first (for browser redirects)
        token = request.args.get('token')

        # If not in query param, try Authorization header
        if not token:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Missing or invalid authorization'}), 401

        # Validate token and get user
        from app.services.auth_service import AuthService
        payload = AuthService.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401

        user_id = payload['user_id']

        # Generate OAuth URL with state for CSRF protection
        auth_url, state = oauth_service.get_authorization_url()

        # Store state in session for validation
        session['yahoo_oauth_state'] = state
        session['yahoo_oauth_user_id'] = user_id

        logger.info(f"Starting Yahoo OAuth for user {user_id}")

        # Redirect to Yahoo OAuth page
        return redirect(auth_url)

    except Exception as e:
        logger.error(f"Error starting Yahoo OAuth: {e}")
        # Redirect to frontend with error
        frontend_url = os.getenv('FRONTEND_URL', '')
        return redirect(f"{frontend_url}/rosters?yahoo_error=auth_failed")


@bp.route('/callback', methods=['GET'])
def oauth_callback():
    """
    Handle Yahoo OAuth callback

    Yahoo redirects here after user authorizes the app
    """
    try:
        # Get authorization code and state
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')

        # Check for OAuth errors
        if error:
            logger.error(f"Yahoo OAuth error: {error}")
            frontend_url = os.getenv('FRONTEND_URL', '')
            return redirect(f"{frontend_url}/rosters?yahoo_error={error}")

        # Validate state (CSRF protection)
        session_state = session.get('yahoo_oauth_state')
        if not state or state != session_state:
            logger.error("Invalid OAuth state - possible CSRF attack")
            frontend_url = os.getenv('FRONTEND_URL', '')
            return redirect(f"{frontend_url}/rosters?yahoo_error=invalid_state")

        # Get user ID from session
        user_id = session.get('yahoo_oauth_user_id')
        if not user_id:
            logger.error("No user ID in session")
            frontend_url = os.getenv('FRONTEND_URL', '')
            return redirect(f"{frontend_url}/rosters?yahoo_error=session_expired")

        # Exchange authorization code for access token
        token_data = oauth_service.exchange_code_for_token(code)
        if not token_data:
            logger.error("Failed to exchange authorization code")
            frontend_url = os.getenv('FRONTEND_URL', '')
            return redirect(f"{frontend_url}/rosters?yahoo_error=token_exchange_failed")

        # Save tokens to database
        success = oauth_service.save_tokens(user_id, token_data)
        if not success:
            logger.error(f"Failed to save tokens for user {user_id}")
            frontend_url = os.getenv('FRONTEND_URL', '')
            return redirect(f"{frontend_url}/rosters?yahoo_error=token_save_failed")

        # Clear session
        session.pop('yahoo_oauth_state', None)
        session.pop('yahoo_oauth_user_id', None)

        logger.info(f"Yahoo OAuth successful for user {user_id}")

        # Redirect to frontend with success indicator
        frontend_url = os.getenv('FRONTEND_URL', '')
        return redirect(f"{frontend_url}/?yahoo_auth=success")

    except Exception as e:
        logger.error(f"Error in Yahoo OAuth callback: {e}", exc_info=True)
        frontend_url = os.getenv('FRONTEND_URL', '')
        return redirect(f"{frontend_url}/rosters?yahoo_error=callback_failed")


# ============================================================================
# League and Roster Routes
# ============================================================================

@bp.route('/leagues', methods=['GET'])
@require_auth
def get_leagues(current_user):
    """
    Get user's Yahoo fantasy leagues

    Requires valid Yahoo OAuth token
    """
    try:
        user_id = current_user['id']

        # Get valid access token (auto-refreshes if expired)
        access_token = oauth_service.get_valid_token(user_id)
        if not access_token:
            return jsonify({
                'error': 'No Yahoo authorization found. Please connect your Yahoo account first.',
                'needs_auth': True
            }), 401

        # Create Yahoo client and fetch leagues
        yahoo_client = YahooFantasyClient(access_token)
        leagues = yahoo_client.get_user_leagues()

        logger.info(f"Fetched {len(leagues)} Yahoo leagues for user {user_id}")

        return jsonify({
            'data': {
                'leagues': leagues,
                'count': len(leagues)
            }
        })

    except Exception as e:
        logger.error(f"Error fetching Yahoo leagues: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch Yahoo leagues'}), 500


class ImportRosterSchema(Schema):
    """Schema for roster import request"""
    team_key = fields.Str(required=True, validate=validate.Length(min=1))
    roster_name = fields.Str(required=False, validate=validate.Length(min=1, max=100))


@bp.route('/import', methods=['POST'])
@require_auth
@validate_json(ImportRosterSchema)
def import_roster(current_user, validated_data):
    """
    Import a Yahoo fantasy roster

    Request body:
    {
        "team_key": "nfl.l.12345.t.1",
        "roster_name": "My Yahoo Team" (optional)
    }
    """
    try:
        user_id = current_user['id']
        team_key = validated_data['team_key']
        roster_name = validated_data.get('roster_name')

        # Get valid access token
        access_token = oauth_service.get_valid_token(user_id)
        if not access_token:
            return jsonify({
                'error': 'No Yahoo authorization found. Please connect your Yahoo account first.',
                'needs_auth': True
            }), 401

        # Create Yahoo client
        yahoo_client = YahooFantasyClient(access_token)

        # Import roster
        result = import_service.import_roster(
            user_id=user_id,
            yahoo_client=yahoo_client,
            team_key=team_key,
            roster_name=roster_name
        )

        if not result.get('success'):
            return jsonify({'error': result.get('error', 'Import failed')}), 500

        logger.info(
            f"Imported Yahoo roster for user {user_id}: "
            f"{result['matched_players']}/{result['total_players']} players matched"
        )

        return jsonify({
            'data': result,
            'message': f"Successfully imported {result['matched_players']} players"
        })

    except Exception as e:
        logger.error(f"Error importing Yahoo roster: {e}", exc_info=True)
        return jsonify({'error': 'Failed to import roster'}), 500


@bp.route('/roster/preview/<team_key>', methods=['GET'])
@require_auth
def preview_roster(current_user, team_key):
    """
    Preview a Yahoo roster before importing

    URL parameter: team_key (e.g., nfl.l.12345.t.1)
    """
    try:
        user_id = current_user['id']

        # Get valid access token
        access_token = oauth_service.get_valid_token(user_id)
        if not access_token:
            return jsonify({
                'error': 'No Yahoo authorization found',
                'needs_auth': True
            }), 401

        # Create Yahoo client and fetch roster
        yahoo_client = YahooFantasyClient(access_token)
        roster = yahoo_client.get_team_roster(team_key)

        if not roster:
            return jsonify({'error': 'Failed to fetch roster from Yahoo'}), 500

        return jsonify({'data': roster})

    except Exception as e:
        logger.error(f"Error previewing Yahoo roster: {e}", exc_info=True)
        return jsonify({'error': 'Failed to preview roster'}), 500


# ============================================================================
# Sync and Management Routes
# ============================================================================

@bp.route('/sync/<int:roster_id>', methods=['POST'])
@require_auth
def sync_roster(current_user, roster_id):
    """
    Sync an imported Yahoo roster with latest data

    Updates roster to match current Yahoo roster (adds/removes players)
    """
    try:
        user_id = current_user['id']

        # Verify roster belongs to user
        from app.routes.rosters import verify_roster_ownership
        is_owner, error_response = verify_roster_ownership(roster_id, user_id)
        if not is_owner:
            return error_response

        # Get valid access token
        access_token = oauth_service.get_valid_token(user_id)
        if not access_token:
            return jsonify({
                'error': 'No Yahoo authorization found',
                'needs_auth': True
            }), 401

        # Create Yahoo client
        yahoo_client = YahooFantasyClient(access_token)

        # Sync roster
        result = import_service.sync_roster(roster_id, yahoo_client)

        if not result.get('success'):
            return jsonify({'error': result.get('error', 'Sync failed')}), 500

        logger.info(f"Synced Yahoo roster {roster_id}: +{result['added']} -{result['removed']}")

        return jsonify({
            'data': result,
            'message': f"Roster synced: {result['added']} added, {result['removed']} removed"
        })

    except Exception as e:
        logger.error(f"Error syncing Yahoo roster: {e}", exc_info=True)
        return jsonify({'error': 'Failed to sync roster'}), 500


@bp.route('/disconnect', methods=['POST'])
@require_auth
def disconnect_yahoo(current_user):
    """
    Disconnect Yahoo account (revoke OAuth tokens)

    This does NOT delete imported rosters, just removes the OAuth connection
    """
    try:
        user_id = current_user['id']

        success = oauth_service.revoke_token(user_id)

        if not success:
            return jsonify({'error': 'Failed to disconnect Yahoo account'}), 500

        logger.info(f"Disconnected Yahoo account for user {user_id}")

        return jsonify({
            'message': 'Yahoo account disconnected successfully'
        })

    except Exception as e:
        logger.error(f"Error disconnecting Yahoo: {e}", exc_info=True)
        return jsonify({'error': 'Failed to disconnect Yahoo account'}), 500


@bp.route('/status', methods=['GET'])
@require_auth
def check_status(current_user):
    """
    Check Yahoo OAuth connection status

    Returns whether user has a valid Yahoo token
    """
    try:
        user_id = current_user['id']

        has_token = oauth_service.has_valid_token(user_id)

        return jsonify({
            'data': {
                'connected': has_token,
                'provider': 'yahoo'
            }
        })

    except Exception as e:
        logger.error(f"Error checking Yahoo status: {e}", exc_info=True)
        return jsonify({'error': 'Failed to check Yahoo status'}), 500
