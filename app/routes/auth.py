"""
Authentication routes for user registration, login, and management
"""
from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.validation.decorators import validate_json_body
from app.validation.schemas import RegisterSchema, LoginSchema, UpdateUserSchema, ChangePasswordSchema
from functools import wraps
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

auth_service = AuthService()


def require_auth(f):
    """
    Decorator to require authentication for a route

    Usage:
        @bp.route('/protected')
        @require_auth
        def protected_route(current_user):
            return jsonify({'user': current_user})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid authorization header'}), 401

        token = auth_header.split(' ')[1]

        # Verify token
        payload = auth_service.verify_token(token)

        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Get user from database
        user = auth_service.get_user_by_id(payload['user_id'])

        if not user:
            return jsonify({'error': 'User not found or inactive'}), 401

        # Pass user to route function
        return f(current_user=user, *args, **kwargs)

    return decorated_function


@bp.route('/register', methods=['POST'])
@validate_json_body(RegisterSchema)
def register(data):
    """
    Register a new user

    Request body:
        {
            "email": "user@example.com",
            "username": "username",
            "password": "securepassword",
            "first_name": "John",  // optional
            "last_name": "Doe"  // optional
        }

    Returns:
        201: User created successfully with auth token
        400: Validation error or user already exists
        500: Server error
    """
    try:
        user = auth_service.create_user(
            email=data['email'],
            username=data['username'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )

        if not user:
            return jsonify({'error': 'Failed to create user'}), 500

        # Generate token
        token = auth_service.generate_token(
            user_id=user['id'],
            username=user['username'],
            email=user['email']
        )

        logger.info(f"User registered: {user['username']}")

        return jsonify({
            'message': 'User created successfully',
            'data': {
                'user': user,
                'token': token
            }
        }), 201

    except ValueError as e:
        # User already exists
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        return jsonify({'error': 'Failed to register user'}), 500


@bp.route('/login', methods=['POST'])
@validate_json_body(LoginSchema)
def login(data):
    """
    Login with email/username and password

    Request body:
        {
            "email_or_username": "user@example.com",  // or username
            "password": "securepassword"
        }

    Returns:
        200: Login successful with auth token
        401: Invalid credentials
        500: Server error
    """
    try:
        user = auth_service.authenticate_user(
            email_or_username=data['email_or_username'],
            password=data['password']
        )

        if not user:
            return jsonify({'error': 'Invalid email/username or password'}), 401

        # Generate token
        token = auth_service.generate_token(
            user_id=user['id'],
            username=user['username'],
            email=user['email']
        )

        logger.info(f"User logged in: {user['username']}")

        return jsonify({
            'message': 'Login successful',
            'data': {
                'user': user,
                'token': token
            }
        })

    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        return jsonify({'error': 'Failed to login'}), 500


@bp.route('/me', methods=['GET'])
@require_auth
def get_current_user(current_user):
    """
    Get current user information

    Headers:
        Authorization: Bearer <token>

    Returns:
        200: User information
        401: Unauthorized
    """
    return jsonify({'data': current_user})


@bp.route('/me', methods=['PUT'])
@require_auth
@validate_json_body(UpdateUserSchema)
def update_current_user(current_user, data):
    """
    Update current user information

    Headers:
        Authorization: Bearer <token>

    Request body:
        {
            "first_name": "John",  // optional
            "last_name": "Doe",  // optional
            "email": "newemail@example.com",  // optional
            "username": "newusername"  // optional
        }

    Returns:
        200: User updated successfully
        400: Validation error
        401: Unauthorized
        500: Server error
    """
    try:
        updated_user = auth_service.update_user(
            user_id=current_user['id'],
            **data
        )

        if not updated_user:
            return jsonify({'error': 'Failed to update user'}), 500

        logger.info(f"User updated: {updated_user['username']}")

        return jsonify({
            'message': 'User updated successfully',
            'data': updated_user
        })

    except Exception as e:
        logger.error(f"Update user error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/change-password', methods=['POST'])
@require_auth
@validate_json_body(ChangePasswordSchema)
def change_password(current_user, data):
    """
    Change user password

    Headers:
        Authorization: Bearer <token>

    Request body:
        {
            "old_password": "currentpassword",
            "new_password": "newsecurepassword"
        }

    Returns:
        200: Password changed successfully
        400: Invalid old password
        401: Unauthorized
        500: Server error
    """
    try:
        success = auth_service.change_password(
            user_id=current_user['id'],
            old_password=data['old_password'],
            new_password=data['new_password']
        )

        if not success:
            return jsonify({'error': 'Invalid old password'}), 400

        logger.info(f"Password changed for user {current_user['username']}")

        return jsonify({'message': 'Password changed successfully'})

    except Exception as e:
        logger.error(f"Change password error: {e}", exc_info=True)
        return jsonify({'error': 'Failed to change password'}), 500


@bp.route('/verify-token', methods=['POST'])
def verify_token():
    """
    Verify if a token is valid

    Request body:
        {
            "token": "jwt_token_string"
        }

    Returns:
        200: Token is valid with user info
        401: Token is invalid or expired
    """
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({'error': 'Token is required'}), 400

        payload = auth_service.verify_token(token)

        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Get fresh user data
        user = auth_service.get_user_by_id(payload['user_id'])

        if not user:
            return jsonify({'error': 'User not found'}), 401

        return jsonify({
            'message': 'Token is valid',
            'data': {'user': user}
        })

    except Exception as e:
        logger.error(f"Token verification error: {e}", exc_info=True)
        return jsonify({'error': 'Failed to verify token'}), 500
