"""
Billing and subscription routes
Handles Stripe checkout, webhooks, and subscription management
"""
from flask import Blueprint, jsonify, request
from app.services.stripe_service import StripeService, get_subscription_tiers
from app.middleware.auth import login_required
from app.models.database import get_db

bp = Blueprint('billing', __name__, url_prefix='/api/billing')

stripe_service = StripeService()


@bp.route('/tiers', methods=['GET'])
def get_tiers():
    """
    Get all subscription tiers

    Returns:
        200: List of subscription tiers with pricing and features
    """
    tiers = get_subscription_tiers()

    # Format for frontend
    tier_list = []
    for tier_id, config in tiers.items():
        tier_list.append({
            'id': tier_id,
            'name': config['name'],
            'price': config['amount'] / 100 if config['amount'] else 0,  # Convert cents to dollars
            'features': config['features']
        })

    return jsonify({
        'data': tier_list
    })


@bp.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session(current_user):
    """
    Create Stripe checkout session for subscription

    Request body:
        {
            "tier": "premium" | "pro",
            "success_url": "https://...",
            "cancel_url": "https://..."
        }

    Returns:
        200: Checkout session with URL
        400: Invalid request
    """
    data = request.json
    tier = data.get('tier')
    success_url = data.get('success_url', request.host_url + 'billing/success')
    cancel_url = data.get('cancel_url', request.host_url + 'billing/cancel')

    if not tier or tier not in ['premium', 'pro']:
        return jsonify({'error': 'Invalid tier'}), 400

    try:
        session = stripe_service.create_checkout_session(
            user_id=str(current_user['id']),
            tier=tier,
            success_url=success_url,
            cancel_url=cancel_url
        )

        return jsonify({
            'data': session
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/create-portal-session', methods=['POST'])
@login_required
def create_portal_session(current_user):
    """
    Create Stripe customer portal session for subscription management

    Request body:
        {
            "return_url": "https://..."
        }

    Returns:
        200: Portal session with URL
        404: No active subscription
    """
    return_url = request.json.get('return_url', request.host_url)

    # Get user's Stripe customer ID from database
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT stripe_customer_id FROM subscriptions WHERE user_id = %s",
        (current_user['id'],)
    )
    result = cursor.fetchone()
    cursor.close()

    if not result or not result[0]:
        return jsonify({'error': 'No active subscription found'}), 404

    try:
        session = stripe_service.create_customer_portal_session(
            customer_id=result[0],
            return_url=return_url
        )

        return jsonify({
            'data': session
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/subscription', methods=['GET'])
@login_required
def get_subscription(current_user):
    """
    Get current user's subscription

    Returns:
        200: Subscription details
        404: No subscription found
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT tier, status, current_period_end, cancel_at_period_end, stripe_subscription_id
        FROM subscriptions
        WHERE user_id = %s
        """,
        (current_user['id'],)
    )
    result = cursor.fetchone()
    cursor.close()

    if not result:
        # Create free tier subscription if none exists
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO subscriptions (user_id, tier, status)
            VALUES (%s, 'free', 'active')
            ON CONFLICT (user_id) DO NOTHING
            RETURNING tier, status
            """,
            (current_user['id'],)
        )
        db.commit()
        cursor.close()

        return jsonify({
            'data': {
                'tier': 'free',
                'status': 'active'
            }
        })

    tier, status, period_end, cancel_at_period_end, stripe_subscription_id = result

    subscription_data = {
        'tier': tier,
        'status': status,
        'current_period_end': period_end.isoformat() if period_end else None,
        'cancel_at_period_end': cancel_at_period_end
    }

    # Get live Stripe data if subscription exists
    if stripe_subscription_id:
        stripe_sub = stripe_service.get_subscription(stripe_subscription_id)
        if stripe_sub:
            subscription_data['stripe_status'] = stripe_sub['status']

    return jsonify({
        'data': subscription_data
    })


@bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhooks

    Events handled:
        - checkout.session.completed: Subscription created
        - customer.subscription.updated: Subscription updated
        - customer.subscription.deleted: Subscription canceled
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    event = stripe_service.verify_webhook_signature(payload, sig_header)

    if not event:
        return jsonify({'error': 'Invalid signature'}), 400

    event_type = event['type']
    data = event['data']['object']

    db = get_db()
    cursor = db.cursor()

    try:
        if event_type == 'checkout.session.completed':
            # Subscription created
            user_id = data['client_reference_id']
            customer_id = data['customer']
            subscription_id = data['subscription']
            tier = data['metadata']['tier']

            cursor.execute(
                """
                INSERT INTO subscriptions (user_id, tier, stripe_customer_id, stripe_subscription_id, status)
                VALUES (%s, %s, %s, %s, 'active')
                ON CONFLICT (user_id)
                DO UPDATE SET
                    tier = EXCLUDED.tier,
                    stripe_customer_id = EXCLUDED.stripe_customer_id,
                    stripe_subscription_id = EXCLUDED.stripe_subscription_id,
                    status = 'active',
                    updated_at = CURRENT_TIMESTAMP
                """,
                (user_id, tier, customer_id, subscription_id)
            )
            db.commit()

        elif event_type == 'customer.subscription.updated':
            # Subscription updated (plan change, renewal, etc.)
            subscription_id = data['id']
            status = data['status']
            current_period_end = data['current_period_end']
            cancel_at_period_end = data['cancel_at_period_end']

            # Get tier from price
            price_id = data['items']['data'][0]['price']['id']
            tier = stripe_service.get_tier_from_price_id(price_id) or 'free'

            cursor.execute(
                """
                UPDATE subscriptions
                SET tier = %s, status = %s, current_period_end = to_timestamp(%s),
                    cancel_at_period_end = %s, updated_at = CURRENT_TIMESTAMP
                WHERE stripe_subscription_id = %s
                """,
                (tier, status, current_period_end, cancel_at_period_end, subscription_id)
            )
            db.commit()

        elif event_type == 'customer.subscription.deleted':
            # Subscription canceled
            subscription_id = data['id']

            cursor.execute(
                """
                UPDATE subscriptions
                SET tier = 'free', status = 'canceled', updated_at = CURRENT_TIMESTAMP
                WHERE stripe_subscription_id = %s
                """,
                (subscription_id,)
            )
            db.commit()

    except Exception as e:
        db.rollback()
        print(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

    return jsonify({'status': 'success'})
