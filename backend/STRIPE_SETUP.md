# Stripe Payment Integration Setup

This guide explains how to configure Stripe payments for your football predictions application.

## 1. Get Your Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Sign up or log in to your account
3. Navigate to **Developers > API keys**
4. Copy your **Publishable key** and **Secret key**

## 2. Configure Environment Variables

Edit the `backend/.env` file and replace the placeholder values:

```env
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_actual_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_publishable_key_here

# Stripe Webhook (optional for now)
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

## 3. Install Dependencies

Make sure you have the required packages:

```bash
pip install -r requirements.txt
```

## 4. Test the Integration

1. Start your backend server:
   ```bash
   cd backend
   python main.py
   ```

2. Open your frontend and try the subscription modal
3. Use Stripe's test card numbers:
   - **Success**: `4242 4242 4242 4242`
   - **Decline**: `4000 0000 0000 0002`
   - **Expiry**: Any future date
   - **CVC**: Any 3 digits

## 5. Webhook Setup (Optional)

For production, you'll want to set up webhooks:

1. In Stripe Dashboard, go to **Developers > Webhooks**
2. Add endpoint: `https://your-domain.com/api/webhook`
3. Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`
4. Copy the webhook secret to your `.env` file

## 6. Security Notes

- ✅ Never commit your `.env` file to version control
- ✅ Use test keys for development
- ✅ Use production keys only in production
- ✅ Keep your secret key secure

## 7. Production Deployment

When deploying to production:

1. Update your Stripe keys to production keys
2. Set up proper webhook endpoints
3. Configure your domain in Stripe settings
4. Test the complete payment flow

## API Endpoints

- `POST /api/create-payment-intent` - Creates a payment intent
- `POST /api/webhook` - Handles Stripe webhooks

## Frontend Integration

The frontend automatically loads the Stripe script and handles:
- Card element rendering
- Payment form submission
- Error handling
- Success confirmation

## Troubleshooting

- **"Invalid API key"**: Check your Stripe keys in `.env`
- **"Card declined"**: Use test card numbers
- **"Webhook error"**: Check webhook secret and endpoint URL 