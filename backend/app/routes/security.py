"""
Security-related endpoints (CSRF tokens, etc.)
"""
from flask import Blueprint, jsonify
from flask_wtf.csrf import generate_csrf

bp = Blueprint('security', __name__, url_prefix='/api/security')


@bp.route('/csrf-token', methods=['GET'])
def get_csrf_token():
    """
    Get a CSRF token for making authenticated requests
    Frontend should call this on app load and include token in subsequent requests
    """
    token = generate_csrf()
    response = jsonify({'csrf_token': token})
    response.set_cookie(
        'csrf_token',
        value=token,
        secure=True,  # Only send over HTTPS in production
        httponly=False,  # JavaScript needs to read this
        samesite='Lax'
    )
    return response
