#!/usr/bin/env python3
"""
Stripe configuration for AI Predictions 7
Environment variables and configuration settings
"""

import os
# For local development, you can use python-dotenv to load .env files:
# from dotenv import load_dotenv; load_dotenv()

# Stripe Configuration
STRIPE_CONFIG = {
    # Keys must be set in environment variables or .env file (never hardcoded)
    'publishable_key': os.getenv('STRIPE_PUBLISHABLE_KEY'),
    'secret_key': os.getenv('STRIPE_SECRET_KEY'),
    'webhook_secret': os.getenv('STRIPE_WEBHOOK_SECRET'),
    # Product and Price IDs (set in environment or .env)
    'subscription_price_id': os.getenv('STRIPE_SUBSCRIPTION_PRICE_ID', 'price_1RkT8uLgWyziDhelTj4PyhNd'),
    'single_pick_price_id': os.getenv('STRIPE_SINGLE_PICK_PRICE_ID', 'price_1RkT8vLgWyziDhelUuw6X0pv'),
    # Payment amounts (in cents)
    'subscription_amount': 1500,  # €15.00
    'single_pick_amount': 399,    # €3.99
    # Currency
    'currency': 'eur',
    # Webhook events to handle
    'webhook_events': [
        'payment_intent.succeeded',
        'payment_intent.payment_failed',
        'customer.subscription.created',
        'customer.subscription.updated',
        'customer.subscription.deleted',
        'invoice.payment_succeeded',
        'invoice.payment_failed'
    ]
}

# IMPORTANT:
# - Set STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_WEBHOOK_SECRET, STRIPE_SUBSCRIPTION_PRICE_ID, and STRIPE_SINGLE_PICK_PRICE_ID
#   in your Render/production environment and in a local .env file (never commit secrets to git)
