"""
Stripe payment integration service
Handles subscriptions, checkout, and webhooks
"""
import stripe
import os
from typing import Dict, Optional

# Initialize Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Subscription tier pricing (in cents)
SUBSCRIPTION_TIERS = {
    'free': {
        'price_id': None,
        'name': 'Free',
        'amount': 0,
        'features': [
            'Basic player analysis',
            '5 matchup comparisons per week',
            'Standard AI recommendations'
        ]
    },
    'premium': {
        'price_id': os.getenv('STRIPE_PREMIUM_PRICE_ID'),
        'name': 'Premium',
        'amount': 999,  # $9.99/month
        'features': [
            'Unlimited player analysis',
            'Unlimited matchup comparisons',
            'Advanced AI insights',
            'Real-time injury updates',
            'Weather impact analysis'
        ]
    },
    'pro': {
        'price_id': os.getenv('STRIPE_PRO_PRICE_ID'),
        'name': 'Pro',
        'amount': 1999,  # $19.99/month
        'features': [
            'Everything in Premium',
            'Custom lineup optimizer',
            'Trade analyzer',
            'Season-long projections',
            'Priority support',
            'API access'
        ]
    }
}


class StripeService:
    """Stripe payment service"""

    @staticmethod
    def create_checkout_session(
        user_id: str,
        tier: str,
        success_url: str,
        cancel_url: str
    ) -> Dict:
        """
        Create a Stripe Checkout session for subscription

        Args:
            user_id: User ID
            tier: Subscription tier (premium, pro)
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel

        Returns:
            Checkout session dict with id and url
        """
        if tier not in ['premium', 'pro']:
            raise ValueError(f"Invalid tier: {tier}")

        price_id = SUBSCRIPTION_TIERS[tier]['price_id']

        if not price_id:
            raise ValueError(f"Price ID not configured for tier: {tier}")

        session = stripe.checkout.Session.create(
            customer_email=None,  # Optionally collect email
            client_reference_id=user_id,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            metadata={
                'user_id': user_id,
                'tier': tier
            }
        )

        return {
            'id': session.id,
            'url': session.url
        }

    @staticmethod
    def create_customer_portal_session(
        customer_id: str,
        return_url: str
    ) -> Dict:
        """
        Create a Stripe Customer Portal session for managing subscription

        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal

        Returns:
            Portal session dict with url
        """
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )

        return {
            'url': session.url
        }

    @staticmethod
    def get_subscription(subscription_id: str) -> Optional[Dict]:
        """
        Get subscription details

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Subscription dict or None
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                'id': subscription.id,
                'status': subscription.status,
                'customer_id': subscription.customer,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end,
                'items': [{
                    'price_id': item.price.id,
                    'product_id': item.price.product
                } for item in subscription['items']['data']]
            }
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            return None

    @staticmethod
    def cancel_subscription(subscription_id: str) -> bool:
        """
        Cancel subscription at period end

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            True if successful
        """
        try:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            return True
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            return False

    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str) -> Optional[Dict]:
        """
        Verify Stripe webhook signature

        Args:
            payload: Raw request body
            signature: Stripe-Signature header

        Returns:
            Event dict if valid, None otherwise
        """
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

        if not webhook_secret:
            raise ValueError("Webhook secret not configured")

        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return event
        except ValueError as e:
            # Invalid payload
            print(f"Invalid payload: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            print(f"Invalid signature: {e}")
            return None

    @staticmethod
    def get_tier_from_price_id(price_id: str) -> Optional[str]:
        """
        Get tier name from Stripe price ID

        Args:
            price_id: Stripe price ID

        Returns:
            Tier name (free, premium, pro) or None
        """
        for tier, config in SUBSCRIPTION_TIERS.items():
            if config['price_id'] == price_id:
                return tier
        return None


def get_subscription_tiers() -> Dict:
    """Get all subscription tier info"""
    return SUBSCRIPTION_TIERS
