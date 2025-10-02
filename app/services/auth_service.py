"""
Authentication service for user management
"""
import os
import jwt
import logging
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from app.database import execute_query

logger = logging.getLogger(__name__)

bcrypt = Bcrypt()

# JWT configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24


class AuthService:
    """Service for user authentication and authorization"""

    @staticmethod
    def hash_password(password):
        """
        Hash a password using bcrypt

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        return bcrypt.generate_password_hash(password).decode('utf-8')

    @staticmethod
    def verify_password(password, password_hash):
        """
        Verify a password against its hash

        Args:
            password: Plain text password
            password_hash: Hashed password

        Returns:
            Boolean indicating if password matches
        """
        return bcrypt.check_password_hash(password_hash, password)

    @staticmethod
    def create_user(email, username, password, first_name=None, last_name=None):
        """
        Create a new user account

        Args:
            email: User email (must be unique)
            username: Username (must be unique)
            password: Plain text password (will be hashed)
            first_name: Optional first name
            last_name: Optional last name

        Returns:
            User dict or None if creation fails

        Raises:
            ValueError: If user already exists
        """
        try:
            # Check if user already exists
            existing = execute_query(
                "SELECT id FROM users WHERE email = %s OR username = %s",
                (email, username)
            )

            if existing:
                raise ValueError("User with this email or username already exists")

            # Hash password
            password_hash = AuthService.hash_password(password)

            # Insert user
            query = """
                INSERT INTO users (email, username, password_hash, first_name, last_name)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, email, username, first_name, last_name, is_active, created_at
            """

            result = execute_query(
                query,
                (email, username, password_hash, first_name, last_name),
                fetch_one=True
            )

            if result and len(result) > 0:
                user = result[0]
                logger.info(f"User created: {username} ({email})")
                return user

            return None

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise Exception(f"Failed to create user: {str(e)}")

    @staticmethod
    def authenticate_user(email_or_username, password):
        """
        Authenticate a user by email/username and password

        Args:
            email_or_username: Email or username
            password: Plain text password

        Returns:
            User dict if authentication successful, None otherwise
        """
        try:
            # Find user by email or username
            query = """
                SELECT id, email, username, password_hash, first_name, last_name,
                       is_active, is_verified
                FROM users
                WHERE (email = %s OR username = %s) AND is_active = true
            """

            result = execute_query(
                query,
                (email_or_username, email_or_username),
                fetch_one=True
            )

            if not result or len(result) == 0:
                logger.warning(f"Authentication failed: User not found ({email_or_username})")
                return None

            user = result[0]
            password_hash = user.get('password_hash')

            # Verify password
            if not AuthService.verify_password(password, password_hash):
                logger.warning(f"Authentication failed: Invalid password ({email_or_username})")
                return None

            # Update last login
            execute_query(
                "UPDATE users SET last_login_at = NOW() WHERE id = %s",
                (user['id'],)
            )

            # Remove password_hash from response
            user_data = {k: v for k, v in user.items() if k != 'password_hash'}

            logger.info(f"User authenticated: {user_data['username']}")
            return user_data

        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    @staticmethod
    def generate_token(user_id, username, email):
        """
        Generate a JWT token for a user

        Args:
            user_id: User ID
            username: Username
            email: User email

        Returns:
            JWT token string
        """
        try:
            payload = {
                'user_id': user_id,
                'username': username,
                'email': email,
                'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
                'iat': datetime.utcnow()
            }

            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            return token

        except Exception as e:
            logger.error(f"Error generating token: {e}")
            raise

    @staticmethod
    def verify_token(token):
        """
        Verify and decode a JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded payload dict or None if invalid
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None

    @staticmethod
    def get_user_by_id(user_id):
        """
        Get user by ID

        Args:
            user_id: User ID

        Returns:
            User dict or None
        """
        try:
            query = """
                SELECT id, email, username, first_name, last_name,
                       is_active, is_verified, last_login_at, created_at
                FROM users
                WHERE id = %s AND is_active = true
            """

            result = execute_query(query, (user_id,), fetch_one=True)

            if result and len(result) > 0:
                return result[0]

            return None

        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    @staticmethod
    def update_user(user_id, **kwargs):
        """
        Update user information

        Args:
            user_id: User ID
            **kwargs: Fields to update (first_name, last_name, email, username)

        Returns:
            Updated user dict or None
        """
        try:
            # Build UPDATE query dynamically
            allowed_fields = ['first_name', 'last_name', 'email', 'username']
            updates = []
            values = []

            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    updates.append(f"{field} = %s")
                    values.append(value)

            if not updates:
                return AuthService.get_user_by_id(user_id)

            # Add updated_at
            updates.append("updated_at = NOW()")
            values.append(user_id)

            query = f"""
                UPDATE users
                SET {', '.join(updates)}
                WHERE id = %s
                RETURNING id, email, username, first_name, last_name, is_active, updated_at
            """

            result = execute_query(query, tuple(values), fetch_one=True)

            if result and len(result) > 0:
                logger.info(f"User updated: {user_id}")
                return result[0]

            return None

        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise Exception(f"Failed to update user: {str(e)}")

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        Change user password

        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password

        Returns:
            Boolean indicating success
        """
        try:
            # Get current password hash
            result = execute_query(
                "SELECT password_hash FROM users WHERE id = %s",
                (user_id,),
                fetch_one=True
            )

            if not result or len(result) == 0:
                return False

            current_hash = result[0]['password_hash']

            # Verify old password
            if not AuthService.verify_password(old_password, current_hash):
                logger.warning(f"Password change failed: Invalid old password (user_id={user_id})")
                return False

            # Hash and update new password
            new_hash = AuthService.hash_password(new_password)
            execute_query(
                "UPDATE users SET password_hash = %s, updated_at = NOW() WHERE id = %s",
                (new_hash, user_id)
            )

            logger.info(f"Password changed for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False
