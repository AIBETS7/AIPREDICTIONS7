#!/usr/bin/env python3
"""
Setup Stripe products and prices for AI Predictions 7
Creates the necessary products and prices in Stripe
"""

import stripe
import os
from stripe_config import STRIPE_CONFIG

# Set the Stripe API key
stripe.api_key = STRIPE_CONFIG['secret_key']

def create_products_and_prices():
    """Create products and prices in Stripe"""
    
    print("Setting up Stripe products and prices...")
    
    try:
        # Create subscription product
        subscription_product = stripe.Product.create(
            name="AI Predictions 7 Monthly Subscription",
            description="Access to daily AI-generated football predictions for Spanish and European leagues",
            metadata={
                "type": "subscription",
                "service": "ai_predictions"
            }
        )
        
        print(f"✅ Created subscription product: {subscription_product.id}")
        
        # Create subscription price
        subscription_price = stripe.Price.create(
            product=subscription_product.id,
            unit_amount=1500,  # €15.00 in cents
            currency='eur',
            recurring={
                'interval': 'month'
            },
            metadata={
                "type": "subscription_price",
                "amount_eur": "15.00"
            }
        )
        
        print(f"✅ Created subscription price: {subscription_price.id}")
        
        # Create single pick product
        single_pick_product = stripe.Product.create(
            name="AI Predictions 7 Single Pick",
            description="One-time access to a single AI-generated football prediction",
            metadata={
                "type": "single_pick",
                "service": "ai_predictions"
            }
        )
        
        print(f"✅ Created single pick product: {single_pick_product.id}")
        
        # Create single pick price
        single_pick_price = stripe.Price.create(
            product=single_pick_product.id,
            unit_amount=399,  # €3.99 in cents
            currency='eur',
            metadata={
                "type": "single_pick_price",
                "amount_eur": "3.99"
            }
        )
        
        print(f"✅ Created single pick price: {single_pick_price.id}")
        
        # Print configuration for environment variables
        print("\n" + "="*50)
        print("STRIPE CONFIGURATION")
        print("="*50)
        print(f"STRIPE_SUBSCRIPTION_PRICE_ID={subscription_price.id}")
        print(f"STRIPE_SINGLE_PICK_PRICE_ID={single_pick_price.id}")
        print("\nAdd these to your environment variables or update stripe_config.py")
        
        return {
            'subscription_price_id': subscription_price.id,
            'single_pick_price_id': single_pick_price.id
        }
        
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def update_config_file(price_ids):
    """Update the stripe_config.py file with the new price IDs"""
    
    if not price_ids:
        return
    
    try:
        # Read current config
        with open('stripe_config.py', 'r') as f:
            content = f.read()
        
        # Update price IDs
        content = content.replace(
            "'subscription_price_id': os.getenv('STRIPE_SUBSCRIPTION_PRICE_ID', 'price_your_subscription_id')",
            f"'subscription_price_id': os.getenv('STRIPE_SUBSCRIPTION_PRICE_ID', '{price_ids['subscription_price_id']}')"
        )
        
        content = content.replace(
            "'single_pick_price_id': os.getenv('STRIPE_SINGLE_PICK_PRICE_ID', 'price_your_single_pick_id')",
            f"'single_pick_price_id': os.getenv('STRIPE_SINGLE_PICK_PRICE_ID', '{price_ids['single_pick_price_id']}')"
        )
        
        # Write updated config
        with open('stripe_config.py', 'w') as f:
            f.write(content)
        
        print("✅ Updated stripe_config.py with new price IDs")
        
    except Exception as e:
        print(f"❌ Error updating config file: {e}")

if __name__ == "__main__":
    print("Setting up Stripe products and prices for AI Predictions 7...")
    print(f"Using Stripe account: {stripe.api_key[:12]}...")
    
    price_ids = create_products_and_prices()
    
    if price_ids:
        update_config_file(price_ids)
        print("\n✅ Stripe setup completed successfully!")
        print("\nNext steps:")
        print("1. Set up webhooks in your Stripe dashboard")
        print("2. Deploy the updated code")
        print("3. Test the payment flow")
    else:
        print("\n❌ Stripe setup failed. Please check the errors above.") 