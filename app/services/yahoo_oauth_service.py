"""
Yahoo OAuth and Fantasy Sports API Integration Service

Handles OAuth 2.0 flow and Fantasy Sports API calls for Yahoo Fantasy Football
"""
import requests
import base64
import os
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs
from app.database import execute_query
import secrets

logger = logging.getLogger(__name__)

class YahooOAuthService:
    """Service for Yahoo OAuth 2.0 and Fantasy Sports API integration"""

    def __init__(self):
        self.client_id = os.getenv('YAHOO_CLIENT_ID')
        self.client_secret = os.getenv('YAHOO_CLIENT_SECRET')
        self.redirect_uri = os.getenv('YAHOO_REDIRECT_URI', 'https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/yahoo/callback')

        # Yahoo OAuth endpoints
        self.auth_url = 'https://api.login.yahoo.com/oauth2/request_auth'
        self.token_url = 'https://api.login.yahoo.com/oauth2/get_token'
        self.fantasy_api_base = 'https://fantasysports.yahooapis.com/fantasy/v2'

        if not self.client_id or not self.client_secret:
            logger.warning("Yahoo OAuth credentials not configured")

    def is_configured(self):
        """Check if Yahoo OAuth is properly configured"""
        return bool(self.client_id and self.client_secret)

    def get_auth_url(self, user_id, state=None):
        """
        Generate Yahoo OAuth authorization URL

        Args:
            user_id: Internal user ID for state tracking
            state: Optional state parameter (auto-generated if not provided)

        Returns:
            dict: Authorization URL and state
        """
        if not self.is_configured():
            raise Exception("Yahoo OAuth not configured")

        # Generate state for CSRF protection
        if not state:
            state = secrets.token_urlsafe(32)

        # Store state in database for validation
        self._store_oauth_state(user_id, state)

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'fspt-r',  # Fantasy Sports read permissions
            'state': state
        }

        auth_url = f"{self.auth_url}?{urlencode(params)}"

        return {
            'auth_url': auth_url,
            'state': state
        }

    def exchange_code_for_token(self, code, state, user_id):
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from Yahoo
            state: State parameter for CSRF validation
            user_id: Internal user ID

        Returns:
            dict: Token response with access_token, refresh_token, etc.
        """
        if not self.is_configured():
            raise Exception("Yahoo OAuth not configured")

        # Validate state to prevent CSRF attacks
        if not self._validate_oauth_state(user_id, state):
            raise Exception("Invalid OAuth state")

        # Prepare token exchange request
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri
        }

        try:
            response = requests.post(self.token_url, headers=headers, data=data, timeout=10)
            response.raise_for_status()

            token_data = response.json()

            # Store tokens in database
            self._store_user_tokens(user_id, token_data)

            # Clean up OAuth state
            self._cleanup_oauth_state(user_id, state)

            return token_data

        except requests.RequestException as e:
            logger.error(f"Token exchange failed: {e}")
            raise Exception(f"Failed to exchange code for token: {e}")

    def refresh_access_token(self, user_id):
        """
        Refresh expired access token using refresh token

        Args:
            user_id: Internal user ID

        Returns:
            dict: New token data
        """
        if not self.is_configured():
            raise Exception("Yahoo OAuth not configured")

        # Get stored refresh token
        refresh_token = self._get_user_refresh_token(user_id)
        if not refresh_token:
            raise Exception("No refresh token found")

        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        try:
            response = requests.post(self.token_url, headers=headers, data=data, timeout=10)
            response.raise_for_status()

            token_data = response.json()

            # Update stored tokens
            self._store_user_tokens(user_id, token_data)

            return token_data

        except requests.RequestException as e:
            logger.error(f"Token refresh failed: {e}")
            raise Exception(f"Failed to refresh token: {e}")

    def get_user_leagues(self, user_id):
        """
        Get user's Yahoo Fantasy Football leagues

        Args:
            user_id: Internal user ID

        Returns:
            list: User's fantasy leagues
        """
        access_token = self._get_valid_access_token(user_id)
        if not access_token:
            raise Exception("No valid access token")

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Get current season (Yahoo uses current year for active season)
        current_year = datetime.now().year

        # Get user's games for current season
        url = f"{self.fantasy_api_base}/users;use_login=1/games;game_keys=nfl.l.{current_year}/leagues"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse Yahoo's XML response (they use XML by default)
            leagues = self._parse_leagues_response(response.text)

            return leagues

        except requests.RequestException as e:
            logger.error(f"Failed to fetch user leagues: {e}")
            raise Exception(f"Failed to fetch leagues: {e}")

    def get_team_roster(self, user_id, team_key):
        """
        Get roster for a specific Yahoo Fantasy team

        Args:
            user_id: Internal user ID
            team_key: Yahoo team key (e.g., "nfl.l.12345.t.1")

        Returns:
            list: Team roster with player details
        """
        access_token = self._get_valid_access_token(user_id)
        if not access_token:
            raise Exception("No valid access token")

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Get team roster
        url = f"{self.fantasy_api_base}/team/{team_key}/roster"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse roster response
            roster = self._parse_roster_response(response.text)

            return roster

        except requests.RequestException as e:
            logger.error(f"Failed to fetch team roster: {e}")
            raise Exception(f"Failed to fetch roster: {e}")

    def _get_valid_access_token(self, user_id):
        """Get valid access token, refreshing if necessary"""
        try:
            query = """
                SELECT access_token, expires_at, refresh_token
                FROM yahoo_tokens
                WHERE user_id = %s
            """
            result = execute_query(query, (user_id,))

            if not result:
                return None

            token_data = result[0]
            expires_at = token_data['expires_at']

            # Check if token is expired (with 5 minute buffer)
            if expires_at and datetime.utcnow() + timedelta(minutes=5) > expires_at:
                # Token expired, try to refresh
                try:
                    self.refresh_access_token(user_id)
                    # Get new token
                    new_result = execute_query(query, (user_id,))
                    return new_result[0]['access_token'] if new_result else None
                except Exception as e:
                    logger.error(f"Failed to refresh token: {e}")
                    return None

            return token_data['access_token']

        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            return None

    def _store_oauth_state(self, user_id, state):
        """Store OAuth state for CSRF validation"""
        try:
            query = """
                INSERT INTO yahoo_oauth_states (user_id, state, created_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    state = EXCLUDED.state,
                    created_at = EXCLUDED.created_at
            """
            execute_query(query, (user_id, state, datetime.utcnow()))
        except Exception as e:
            logger.error(f"Failed to store OAuth state: {e}")

    def _validate_oauth_state(self, user_id, state):
        """Validate OAuth state for CSRF protection"""
        try:
            query = """
                SELECT state, created_at
                FROM yahoo_oauth_states
                WHERE user_id = %s AND state = %s
            """
            result = execute_query(query, (user_id, state))

            if not result:
                return False

            # Check if state is not too old (15 minutes max)
            created_at = result[0]['created_at']
            if datetime.utcnow() - created_at > timedelta(minutes=15):
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating OAuth state: {e}")
            return False

    def _cleanup_oauth_state(self, user_id, state):
        """Remove used OAuth state"""
        try:
            query = "DELETE FROM yahoo_oauth_states WHERE user_id = %s AND state = %s"
            execute_query(query, (user_id, state))
        except Exception as e:
            logger.error(f"Failed to cleanup OAuth state: {e}")

    def _store_user_tokens(self, user_id, token_data):
        """Store or update user's Yahoo tokens"""
        try:
            expires_in = token_data.get('expires_in', 3600)
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

            query = """
                INSERT INTO yahoo_tokens (
                    user_id, access_token, refresh_token, expires_at, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    access_token = EXCLUDED.access_token,
                    refresh_token = EXCLUDED.refresh_token,
                    expires_at = EXCLUDED.expires_at,
                    updated_at = EXCLUDED.updated_at
            """

            now = datetime.utcnow()
            execute_query(query, (
                user_id,
                token_data['access_token'],
                token_data.get('refresh_token'),
                expires_at,
                now,
                now
            ))

        except Exception as e:
            logger.error(f"Failed to store user tokens: {e}")

    def _get_user_refresh_token(self, user_id):
        """Get user's refresh token"""
        try:
            query = "SELECT refresh_token FROM yahoo_tokens WHERE user_id = %s"
            result = execute_query(query, (user_id,))
            return result[0]['refresh_token'] if result else None
        except Exception as e:
            logger.error(f"Error getting refresh token: {e}")
            return None

    def _parse_leagues_response(self, xml_response):
        """Parse Yahoo leagues XML response into Python objects"""
        try:
            root = ET.fromstring(xml_response)
            leagues = []

            # Navigate through Yahoo's XML structure
            # Typical structure: fantasy_content -> users -> user -> games -> game -> leagues -> league
            for league in root.findall('.//league'):
                league_key = self._get_xml_text(league, 'league_key')
                league_id = self._get_xml_text(league, 'league_id')
                name = self._get_xml_text(league, 'name')
                num_teams = self._get_xml_text(league, 'num_teams')
                season = self._get_xml_text(league, 'season')

                # Get user's team in this league
                teams = league.findall('.//teams/team') or league.findall('.//team')
                for team in teams:
                    team_key = self._get_xml_text(team, 'team_key')
                    team_id = self._get_xml_text(team, 'team_id')
                    team_name = self._get_xml_text(team, 'name')

                    if team_key and team_name:  # Valid team found
                        leagues.append({
                            'league_key': league_key,
                            'league_id': league_id,
                            'name': name,
                            'team_key': team_key,
                            'team_id': team_id,
                            'team_name': team_name,
                            'num_teams': int(num_teams) if num_teams and num_teams.isdigit() else 0,
                            'season': season or str(datetime.now().year)
                        })

            return leagues

        except ET.ParseError as e:
            logger.error(f"Failed to parse leagues XML: {e}")
            # Return placeholder data if XML parsing fails
            return [
                {
                    'league_key': 'nfl.l.12345',
                    'league_id': '12345',
                    'name': 'Sample Fantasy League',
                    'team_key': 'nfl.l.12345.t.1',
                    'team_id': '1',
                    'team_name': 'Sample Team',
                    'num_teams': 12,
                    'season': str(datetime.now().year)
                }
            ]
        except Exception as e:
            logger.error(f"Unexpected error parsing leagues: {e}")
            return []

    def _parse_roster_response(self, xml_response):
        """Parse Yahoo roster XML response into Python objects"""
        try:
            root = ET.fromstring(xml_response)
            roster = []

            # Navigate through Yahoo's roster XML structure
            # Typical structure: fantasy_content -> team -> roster -> players -> player
            for player in root.findall('.//player'):
                player_key = self._get_xml_text(player, 'player_key')
                player_id = self._get_xml_text(player, 'player_id')

                # Player name
                name_elem = player.find('.//name')
                name = name_elem.find('full').text if name_elem is not None and name_elem.find('full') is not None else 'Unknown Player'

                # Editorial info (position, team)
                editorial = player.find('.//editorial_player_key')
                position = self._get_xml_text(player, './/display_position') or self._get_xml_text(player, './/primary_position')
                team_abbr = self._get_xml_text(player, './/editorial_team_abbr')

                # Selected position (roster position)
                selected_position = player.find('.//selected_position')
                roster_position = 'BENCH'
                if selected_position is not None:
                    pos_elem = selected_position.find('position')
                    if pos_elem is not None:
                        roster_position = pos_elem.text

                if player_key and name:  # Valid player
                    roster.append({
                        'player_key': player_key,
                        'player_id': player_id,
                        'name': name,
                        'position': position or 'UNKNOWN',
                        'team': team_abbr or 'FA',
                        'roster_position': roster_position
                    })

            return roster

        except ET.ParseError as e:
            logger.error(f"Failed to parse roster XML: {e}")
            # Return placeholder data if XML parsing fails
            return [
                {
                    'player_key': 'nfl.p.12345',
                    'player_id': '12345',
                    'name': 'Sample Player',
                    'position': 'QB',
                    'team': 'KC',
                    'roster_position': 'QB'
                }
            ]
        except Exception as e:
            logger.error(f"Unexpected error parsing roster: {e}")
            return []

    def _get_xml_text(self, element, path):
        """Safely extract text from XML element"""
        try:
            if element is None:
                return None

            found = element.find(path)
            return found.text if found is not None else None

        except Exception as e:
            logger.debug(f"Error extracting XML text for path {path}: {e}")
            return None