#!/usr/bin/env python3
"""
Payment routes for AI Predictions 7
API endpoints for subscription and single pick payments
"""

from flask import Blueprint, request, jsonify
from loguru import logger
from payment_processor import payment_processor
import json

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/api/create-subscription', methods=['POST'])
def create_subscription():
    """Create a subscription payment"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        payment_method_id = data.get('payment_method_id')
        email = data.get('email')
        amount = data.get('amount', 1500)  # €15.00 in cents
        
        if not payment_method_id or not email:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Create subscription payment
        result = payment_processor.create_subscription_payment(
            payment_method_id=payment_method_id,
            email=email,
            amount=amount
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in create_subscription: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@payment_bp.route('/api/create-single-pick-payment', methods=['POST'])
def create_single_pick_payment():
    """Create a single pick payment"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        payment_method_id = data.get('payment_method_id')
        email = data.get('email')
        amount = data.get('amount', 399)  # €3.99 in cents
        
        if not payment_method_id or not email:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Create single pick payment
        result = payment_processor.create_single_pick_payment(
            payment_method_id=payment_method_id,
            email=email,
            amount=amount
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in create_single_pick_payment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@payment_bp.route('/api/check-access', methods=['POST'])
def check_access():
    """Check if user has access to daily picks"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'error': 'Email required'}), 400
        
        # Check subscription status
        has_subscription = payment_processor.check_subscription_status(email)
        
        # Check single pick access
        has_single_pick = payment_processor.check_single_pick_access(email)
        
        return jsonify({
            'success': True,
            'has_subscription': has_subscription,
            'has_single_pick': has_single_pick,
            'has_access': has_subscription or has_single_pick
        }), 200
        
    except Exception as e:
        logger.error(f"Error in check_access: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@payment_bp.route('/api/payment-status', methods=['GET'])
def payment_status():
    """Get payment system status"""
    try:
        return jsonify({
            'success': True,
            'status': 'operational',
            'subscription_price': '€15/month',
            'single_pick_price': '€3.99',
            'currency': 'EUR'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in payment_status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@payment_bp.route('/api/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    try:
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')
        
        # Verify webhook signature (you'll need to set up webhook endpoint in Stripe)
        # event = stripe.Webhook.construct_event(payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET'))
        
        # For now, just log the webhook
        logger.info(f"Received Stripe webhook: {payload[:200]}...")
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400 