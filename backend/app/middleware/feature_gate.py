"""
Feature gating middleware
Enforces subscription tier limits on API endpoints
"""
from functools import wraps
from flask import jsonify
from app.models.database import get_db
from datetime import datetime, timedelta

# Feature limits by tier
FEATURE_LIMITS = {
    'free': {
        'player_analysis': 5,  # 5 per week
        'matchup_comparison': 5,  # 5 per week
        'roster_optimization': 0,  # Not available
        'trade_analysis': 0,  # Not available
        'season_projections': 0,  # Not available
    },
    'premium': {
        'player_analysis': -1,  # Unlimited
        'matchup_comparison': -1,  # Unlimited
        'roster_optimization': 10,  # 10 per week
        'trade_analysis': 10,  # 10 per week
        'season_projections': 0,  # Not available
    },
    'pro': {
        'player_analysis': -1,  # Unlimited
        'matchup_comparison': -1,  # Unlimited
        'roster_optimization': -1,  # Unlimited
        'trade_analysis': -1,  # Unlimited
        'season_projections': -1,  # Unlimited
    }
}


def check_feature_access(user_id: int, feature: str, tier: str) -> tuple[bool, dict]:
    """
    Check if user has access to feature based on tier and usage

    Args:
        user_id: User ID
        feature: Feature name
        tier: User's subscription tier

    Returns:
        Tuple of (has_access: bool, details: dict)
    """
    limit = FEATURE_LIMITS.get(tier, {}).get(feature, 0)

    # Unlimited access
    if limit == -1:
        return True, {'allowed': True, 'limit': -1, 'usage': 0}

    # Feature not available for tier
    if limit == 0:
        return False, {
            'allowed': False,
            'reason': f'Feature not available in {tier} tier',
            'upgrade_required': True
        }

    # Check usage
    db = get_db()
    cursor = db.cursor()

    # Get or create usage record
    cursor.execute(
        """
        SELECT usage_count, last_reset
        FROM feature_usage
        WHERE user_id = %s AND feature = %s
        """,
        (user_id, feature)
    )
    result = cursor.fetchone()

    if not result:
        # Create usage record
        cursor.execute(
            """
            INSERT INTO feature_usage (user_id, feature, usage_count, last_reset)
            VALUES (%s, %s, 0, CURRENT_TIMESTAMP)
            RETURNING usage_count, last_reset
            """,
            (user_id, feature)
        )
        db.commit()
        result = cursor.fetchone()

    usage_count, last_reset = result

    # Reset if it's been a week
    if last_reset < datetime.now() - timedelta(days=7):
        cursor.execute(
            """
            UPDATE feature_usage
            SET usage_count = 0, last_reset = CURRENT_TIMESTAMP
            WHERE user_id = %s AND feature = %s
            """,
            (user_id, feature)
        )
        db.commit()
        usage_count = 0

    cursor.close()

    # Check if limit exceeded
    if usage_count >= limit:
        return False, {
            'allowed': False,
            'reason': f'Weekly limit of {limit} reached',
            'usage': usage_count,
            'limit': limit,
            'reset_at': (last_reset + timedelta(days=7)).isoformat(),
            'upgrade_required': True
        }

    return True, {
        'allowed': True,
        'usage': usage_count,
        'limit': limit,
        'remaining': limit - usage_count
    }


def track_feature_usage(user_id: int, feature: str):
    """
    Increment feature usage counter

    Args:
        user_id: User ID
        feature: Feature name
    """
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE feature_usage
        SET usage_count = usage_count + 1
        WHERE user_id = %s AND feature = %s
        """,
        (user_id, feature)
    )
    db.commit()
    cursor.close()


def require_feature(feature: str):
    """
    Decorator to enforce feature access based on subscription tier

    Args:
        feature: Feature name to check

    Usage:
        @bp.route('/analyze')
        @login_required
        @require_feature('player_analysis')
        def analyze_player(current_user):
            # Feature logic here
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            user_id = current_user['id']

            # Get user's subscription tier
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "SELECT tier FROM subscriptions WHERE user_id = %s",
                (user_id,)
            )
            result = cursor.fetchone()
            cursor.close()

            tier = result[0] if result else 'free'

            # Check feature access
            has_access, details = check_feature_access(user_id, feature, tier)

            if not has_access:
                return jsonify({
                    'error': 'Feature access denied',
                    'details': details
                }), 403

            # Track usage if allowed
            track_feature_usage(user_id, feature)

            # Add feature details to response (optional)
            current_user['feature_access'] = details

            return f(current_user, *args, **kwargs)

        return decorated_function
    return decorator


def get_user_tier(user_id: int) -> str:
    """
    Get user's current subscription tier

    Args:
        user_id: User ID

    Returns:
        Tier name (free, premium, pro)
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT tier FROM subscriptions WHERE user_id = %s",
        (user_id,)
    )
    result = cursor.fetchone()
    cursor.close()

    return result[0] if result else 'free'
