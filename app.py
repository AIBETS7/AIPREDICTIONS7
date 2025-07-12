from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import os
import psycopg
from datetime import datetime, timedelta
import json
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Stripe
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
if not stripe.api_key:
    print("WARNING: STRIPE_SECRET_KEY not found in environment variables")

app = Flask(__name__, static_folder='public')
CORS(app, origins=[
    'https://astonishing-strudel-9a916f.netlify.app',
    'https://myfootballpredictions.onrender.com',
    'http://localhost:3000',
    'http://localhost:5000'
])

def get_db_connection():
    """Create a database connection using the DATABASE_URL environment variable"""
    try:
        # Get DATABASE_URL from environment variable
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            print("DATABASE_URL environment variable not set")
            return None
            
        if DATABASE_URL.startswith('postgresql://'):
            url = DATABASE_URL.replace('postgresql://', '')
            if '@' in url:
                credentials, rest = url.split('@')
                user, password = credentials.split(':')
                if '/' in rest:
                    host_port, database_with_params = rest.split('/', 1)
                    database = database_with_params.split('?')[0]
                    if ':' in host_port:
                        host, port = host_port.split(':')
                    else:
                        host, port = host_port, '5432'
                    conn = psycopg.connect(
                        host=host,
                        port=port,
                        dbname=database,
                        user=user,
                        password=password,
                        sslmode='require'
                    )
                    return conn
        else:
            print(f"Unsupported database URL format: {DATABASE_URL}")
            return None
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.route('/')
def index():
    """Serve the main predictions page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from the public directory"""
    # Serve index.html from root directory
    if filename == 'index.html':
        return send_from_directory('.', filename)
    # Serve other files from public directory
    return send_from_directory('public', filename)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/daily-picks')
def get_daily_picks():
    """Get today's picks from JSON file created by backend script"""
    try:
        # Return the actual pick that was sent to Telegram
        return jsonify([
            {
                'id': 'manta_vs_catolica_2025',
                'home_team': 'Manta FC',
                'away_team': 'Universidad Catolica',
                'prediction': 'Manta FC',
                'prediction_type': 'Match Winner',
                'confidence': 70.0,
                'odds': 1.80,
                'match_time': '2025-07-12 21:00',
                'reasoning': 'Manta FC has a strong home record. This is an automated test pick.',
                'tipster': 'AI Predictor Pro',
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=3)).isoformat()
            }
        ])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """Create a Stripe payment intent for subscription"""
    try:
        data = request.get_json()
        amount = data.get('amount', 1500)  # €15.00 in cents
        currency = data.get('currency', 'eur')
        email = data.get('email', '')
        
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            automatic_payment_methods={
                'enabled': True,
            },
            metadata={
                'email': email,
                'subscription_type': 'monthly'
            }
        )
        
        publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        if not publishable_key:
            return jsonify({
                'success': False,
                'error': 'Stripe publishable key not configured'
            }), 500
            
        return jsonify({
            'success': True,
            'client_secret': intent.client_secret,
            'publishable_key': publishable_key
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET', '')
        )
    except ValueError as e:
        print(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        print(f"Payment succeeded: {payment_intent['id']}")
        # Here you would typically:
        # 1. Update user subscription status
        # 2. Send confirmation email
        # 3. Grant access to premium features
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        print(f"Payment failed: {payment_intent['id']}")
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, host='0.0.0.0', port=port) 