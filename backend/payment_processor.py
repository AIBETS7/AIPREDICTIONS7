#!/usr/bin/env python3
"""
Payment processor for AI Predictions 7
Handles subscription and single pick payments with Stripe
"""

import os
import stripe
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy import create_engine, text
from config.database import DATABASE_URL
from flask import Blueprint, request, jsonify
import requests

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_your_secret_key_here')

class PaymentProcessor:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        
    def create_subscription_payment(self, payment_method_id, email, amount=1500):
        """Create a subscription payment (€15/month)"""
        try:
            logger.info(f"Creating subscription payment for {email}")
            
            # Create customer
            customer = stripe.Customer.create(
                email=email,
                payment_method=payment_method_id,
                invoice_settings={
                    'default_payment_method': payment_method_id,
                }
            )
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': os.getenv('STRIPE_SUBSCRIPTION_PRICE_ID', 'price_your_subscription_id')}],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent'],
            )
            
            # Store subscription in database
            self._store_subscription(customer.id, subscription.id, email, amount)
            
            return {
                'success': True,
                'subscription_id': subscription.id,
                'customer_id': customer.id,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret
            }
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_single_pick_payment(self, payment_method_id, email, amount=399):
        """Create a single pick payment (€3.99)"""
        try:
            logger.info(f"Creating single pick payment for {email}")
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='eur',
                payment_method=payment_method_id,
                customer_email=email,
                description='AI Predictions 7 - Single Pick Payment',
                metadata={
                    'type': 'single_pick',
                    'email': email
                }
            )
            
            # Confirm payment
            payment_intent = stripe.PaymentIntent.confirm(payment_intent.id)
            
            if payment_intent.status == 'succeeded':
                # Store single pick payment in database
                self._store_single_pick_payment(payment_intent.id, email, amount)
                
                return {
                    'success': True,
                    'payment_intent_id': payment_intent.id,
                    'amount': amount
                }
            else:
                return {
                    'success': False,
                    'error': f'Payment failed: {payment_intent.status}'
                }
                
        except Exception as e:
            logger.error(f"Error creating single pick payment: {e}")
            return {'success': False, 'error': str(e)}
    
    def _store_subscription(self, customer_id, subscription_id, email, amount):
        """Store subscription in database"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO subscriptions (
                        customer_id, subscription_id, email, amount, 
                        status, created_at, expires_at
                    ) VALUES (
                        :customer_id, :subscription_id, :email, :amount,
                        'active', :created_at, :expires_at
                    )
                """), {
                    'customer_id': customer_id,
                    'subscription_id': subscription_id,
                    'email': email,
                    'amount': amount,
                    'created_at': datetime.now().isoformat(),
                    'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
                })
                
            logger.info(f"Subscription stored for {email}")
            
        except Exception as e:
            logger.error(f"Error storing subscription: {e}")
    
    def _store_single_pick_payment(self, payment_intent_id, email, amount):
        """Store single pick payment in database"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO single_pick_payments (
                        payment_intent_id, email, amount, 
                        status, created_at, expires_at
                    ) VALUES (
                        :payment_intent_id, :email, :amount,
                        'active', :created_at, :expires_at
                    )
                """), {
                    'payment_intent_id': payment_intent_id,
                    'email': email,
                    'amount': amount,
                    'created_at': datetime.now().isoformat(),
                    'expires_at': (datetime.now() + timedelta(days=1)).isoformat()
                })
                
            logger.info(f"Single pick payment stored for {email}")
            
        except Exception as e:
            logger.error(f"Error storing single pick payment: {e}")
    
    def check_subscription_status(self, email):
        """Check if user has active subscription"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM subscriptions 
                    WHERE email = :email AND status = 'active' 
                    AND expires_at > :now
                """), {
                    'email': email,
                    'now': datetime.now().isoformat()
                })
                
                subscription = result.fetchone()
                return subscription is not None
                
        except Exception as e:
            logger.error(f"Error checking subscription: {e}")
            return False
    
    def check_single_pick_access(self, email):
        """Check if user has single pick access for today"""
        try:
            today = datetime.now().date()
            
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM single_pick_payments 
                    WHERE email = :email AND status = 'active' 
                    AND DATE(created_at) = :today
                """), {
                    'email': email,
                    'today': today.isoformat()
                })
                
                payment = result.fetchone()
                return payment is not None
                
        except Exception as e:
            logger.error(f"Error checking single pick access: {e}")
            return False
    
    def create_payment_tables(self):
        """Create payment tables if they don't exist"""
        try:
            with self.engine.connect() as conn:
                # Create subscriptions table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS subscriptions (
                        id SERIAL PRIMARY KEY,
                        customer_id VARCHAR(255) NOT NULL,
                        subscription_id VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        amount INTEGER NOT NULL,
                        status VARCHAR(50) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL
                    )
                """))
                
                # Create single_pick_payments table
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS single_pick_payments (
                        id SERIAL PRIMARY KEY,
                        payment_intent_id VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        amount INTEGER NOT NULL,
                        status VARCHAR(50) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL
                    )
                """))
                
            logger.info("Payment tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating payment tables: {e}")

# Initialize payment processor
payment_processor = PaymentProcessor() 

paypal_bp = Blueprint('paypal', __name__)

PAYPAL_CLIENT_ID = "AR9zfWfiS2VWDSwiD0LJjmb5sVFi8fYTs8jeaMF3mnoXN9joD8FVmLc31ivLD0OgK2sDJzGYnClpmbs8"
PAYPAL_SECRET = "EGnbsH_g8vZcI37HP_JD2fofXBxwaYm8DXCRjkWfGETFxrzv2dlkCTYn76AvTNcskmRHuaXUvSC3cTHF"
PAYPAL_PLAN_ID = "P-83297886X25956314NB3XIXI"

# Obtiene el access token de PayPal producción
def get_paypal_access_token():
    url = "https://api-m.paypal.com/v1/oauth2/token"
    auth = (PAYPAL_CLIENT_ID, PAYPAL_SECRET)
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data, auth=auth)
    response.raise_for_status()
    return response.json()["access_token"]

# Obtiene los detalles de la suscripción
def get_subscription_details(subscription_id):
    access_token = get_paypal_access_token()
    url = f"https://api-m.paypal.com/v1/billing/subscriptions/{subscription_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

@paypal_bp.route('/api/paypal/subscription', methods=['POST'])
def handle_subscription():
    data = request.get_json()
    subscription_id = data.get('subscriptionID')
    if not subscription_id:
        return jsonify({"error": "No subscriptionID provided"}), 400

    try:
        subscription = get_subscription_details(subscription_id)
        status = subscription.get("status")
        plan_id = subscription.get("plan_id")
        if status == "ACTIVE" and plan_id == PAYPAL_PLAN_ID:
            return jsonify({"success": True, "message": "Suscripción activa y válida", "subscription": subscription})
        elif plan_id != PAYPAL_PLAN_ID:
            return jsonify({"success": False, "message": "El plan de la suscripción no coincide.", "subscription": subscription}), 400
        else:
            return jsonify({"success": False, "message": f"Estado de la suscripción: {status}", "subscription": subscription}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500 