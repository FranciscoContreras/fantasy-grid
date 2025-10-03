"""
Authentication middleware for JWT-based auth
"""
from functools import wraps
from flask import request, jsonify
import jwt
import os


def login_required(f):
    """
    Decorator to require JWT authentication
    Extracts user info from token and passes it to the route function

    Usage:
        @bp.route('/protected')
        @login_required
        def protected_route(current_user):
            return jsonify({'user_id': current_user['id']})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Check Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401

        try:
            # Decode JWT token
            secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])

            # Extract user info from payload
            current_user = {
                'id': payload.get('user_id'),
                'email': payload.get('email'),
                'username': payload.get('username')
            }

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401

        # Pass current_user to the decorated function
        return f(current_user, *args, **kwargs)

    return decorated_function


def optional_auth(f):
    """
    Decorator for optional authentication
    If token is present and valid, passes current_user, otherwise passes None

    Usage:
        @bp.route('/maybe-protected')
        @optional_auth
        def maybe_protected_route(current_user):
            if current_user:
                return jsonify({'message': 'Authenticated', 'user_id': current_user['id']})
            return jsonify({'message': 'Anonymous'})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        current_user = None

        # Check Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if token:
            try:
                # Decode JWT token
                secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
                payload = jwt.decode(token, secret_key, algorithms=['HS256'])

                # Extract user info from payload
                current_user = {
                    'id': payload.get('user_id'),
                    'email': payload.get('email'),
                    'username': payload.get('username')
                }
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                # Invalid token, but don't fail - just pass None
                pass

        # Pass current_user (or None) to the decorated function
        return f(current_user, *args, **kwargs)

    return decorated_function
