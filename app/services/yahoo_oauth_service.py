"""
Yahoo OAuth 2.0 Service for Fantasy Football Integration

Handles:
- OAuth URL generation with CSRF protection
- Authorization code exchange for access tokens
- Token storage and retrieval with encryption
- Automatic token refresh
- Token revocation
"""

import os
import secrets
import logging
from datetime import datetime, timedelta
from urllib.parse import urlencode
import requests
from cryptography.fernet import Fernet
import base64
from app.database import execute_query

logger = logging.getLogger(__name__)

# OAuth Endpoints
YAHOO_AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
YAHOO_TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"


class YahooOAuthService:
    """Service for Yahoo OAuth 2.0 authentication"""

    def __init__(self):
        self.client_id = os.getenv('YAHOO_CLIENT_ID')
        self.client_secret = os.getenv('YAHOO_CLIENT_SECRET')
        self.redirect_uri = os.getenv(
            'YAHOO_REDIRECT_URI',
            'https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/yahoo/callback'
        )

        # Initialize encryption key for token storage
        encryption_key = os.getenv('YAHOO_ENCRYPTION_KEY', Fernet.generate_key().decode())
        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)

    def get_authorization_url(self, state=None):
        """
        Generate Yahoo OAuth authorization URL

        Args:
            state: Optional CSRF protection state token

        Returns:
            Tuple of (auth_url, state)
        """
        if not self.client_id:
            raise ValueError("YAHOO_CLIENT_ID not configured")

        # Generate secure random state for CSRF protection
        if not state:
            state = secrets.token_urlsafe(32)

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'fspt-w',  # Fantasy Sports Read/Write permission (may include read)
            'state': state,
            'language': 'en-us'
        }

        auth_url = f"{YAHOO_AUTH_URL}?{urlencode(params)}"
        return auth_url, state

    def exchange_code_for_token(self, code):
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from Yahoo callback

        Returns:
            Dict with token data or None on failure
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("Yahoo OAuth credentials not configured")

        try:
            # Use Basic Auth (recommended by Yahoo)
            credentials = f"{self.client_id}:{self.client_secret}"
            basic_auth = base64.b64encode(credentials.encode()).decode()

            response = requests.post(
                YAHOO_TOKEN_URL,
                data={
                    'redirect_uri': self.redirect_uri,
                    'code': code,
                    'grant_type': 'authorization_code'
                },
                headers={
                    'Authorization': f'Basic {basic_auth}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                timeout=10  # Required: 10 second timeout per CLAUDE.md
            )

            response.raise_for_status()
            token_data = response.json()

            # Parse token response
            return {
                'access_token': token_data['access_token'],
                'refresh_token': token_data['refresh_token'],
                'token_type': token_data.get('token_type', 'bearer'),
                'expires_in': token_data['expires_in'],
                'yahoo_guid': token_data.get('xoauth_yahoo_guid')
            }

        except requests.exceptions.Timeout:
            logger.error("Yahoo token exchange timed out")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Yahoo token exchange failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token exchange: {e}")
            return None

    def refresh_access_token(self, refresh_token):
        """
        Refresh an expired access token

        Args:
            refresh_token: Yahoo refresh token

        Returns:
            Dict with new token data or None on failure
        """
        try:
            # Use Basic Auth (recommended by Yahoo)
            credentials = f"{self.client_id}:{self.client_secret}"
            basic_auth = base64.b64encode(credentials.encode()).decode()

            response = requests.post(
                YAHOO_TOKEN_URL,
                data={
                    'refresh_token': refresh_token,
                    'grant_type': 'refresh_token'
                },
                headers={
                    'Authorization': f'Basic {basic_auth}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                timeout=10
            )

            response.raise_for_status()
            token_data = response.json()

            return {
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token', refresh_token),  # Yahoo may not return new refresh token
                'token_type': token_data.get('token_type', 'bearer'),
                'expires_in': token_data['expires_in']
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Token refresh failed: {e}")
            return None

    def encrypt_token(self, token):
        """Encrypt token for secure storage"""
        return self.cipher.encrypt(token.encode()).decode()

    def decrypt_token(self, encrypted_token):
        """Decrypt token from storage"""
        try:
            return self.cipher.decrypt(encrypted_token.encode()).decode()
        except Exception as e:
            logger.error(f"Token decryption failed: {e}")
            return None

    def save_tokens(self, user_id, token_data):
        """
        Save OAuth tokens to database (encrypted)

        Args:
            user_id: User ID
            token_data: Dict with access_token, refresh_token, expires_in, yahoo_guid

        Returns:
            Boolean indicating success
        """
        try:
            # Encrypt tokens before storage
            encrypted_access = self.encrypt_token(token_data['access_token'])
            encrypted_refresh = self.encrypt_token(token_data['refresh_token'])

            # Calculate expiration time
            expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])

            # Upsert token record
            execute_query(
                """
                INSERT INTO yahoo_oauth_tokens
                    (user_id, access_token, refresh_token, token_type, expires_at, yahoo_guid)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id)
                DO UPDATE SET
                    access_token = EXCLUDED.access_token,
                    refresh_token = EXCLUDED.refresh_token,
                    token_type = EXCLUDED.token_type,
                    expires_at = EXCLUDED.expires_at,
                    yahoo_guid = EXCLUDED.yahoo_guid,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (user_id, encrypted_access, encrypted_refresh,
                 token_data['token_type'], expires_at, token_data.get('yahoo_guid'))
            )

            logger.info(f"Saved Yahoo OAuth tokens for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save tokens for user {user_id}: {e}")
            return False

    def get_valid_token(self, user_id):
        """
        Get valid access token for user (auto-refreshes if expired)

        Args:
            user_id: User ID

        Returns:
            Access token string or None
        """
        try:
            # Get token record from database
            result = execute_query(
                """
                SELECT access_token, refresh_token, expires_at, token_type
                FROM yahoo_oauth_tokens
                WHERE user_id = %s
                """,
                (user_id,),
                fetch_one=True
            )

            if not result or len(result) == 0:
                logger.warning(f"No Yahoo OAuth token found for user {user_id}")
                return None

            token_record = result[0]
            expires_at = token_record['expires_at']

            # Check if token is expired
            if datetime.now() >= expires_at:
                logger.info(f"Token expired for user {user_id}, refreshing...")

                # Decrypt refresh token
                refresh_token = self.decrypt_token(token_record['refresh_token'])
                if not refresh_token:
                    return None

                # Refresh token
                new_token_data = self.refresh_access_token(refresh_token)
                if not new_token_data:
                    return None

                # Save new tokens
                self.save_tokens(user_id, new_token_data)
                return new_token_data['access_token']

            # Token is still valid, decrypt and return
            return self.decrypt_token(token_record['access_token'])

        except Exception as e:
            logger.error(f"Error getting valid token for user {user_id}: {e}")
            return None

    def revoke_token(self, user_id):
        """
        Revoke and delete OAuth tokens for user

        Args:
            user_id: User ID

        Returns:
            Boolean indicating success
        """
        try:
            execute_query(
                "DELETE FROM yahoo_oauth_tokens WHERE user_id = %s",
                (user_id,)
            )
            logger.info(f"Revoked Yahoo OAuth tokens for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to revoke tokens for user {user_id}: {e}")
            return False

    def has_valid_token(self, user_id):
        """
        Check if user has a valid Yahoo OAuth token

        Args:
            user_id: User ID

        Returns:
            Boolean
        """
        token = self.get_valid_token(user_id)
        return token is not None
