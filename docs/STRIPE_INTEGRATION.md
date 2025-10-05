# 💳 Stripe Payment Integration

This document explains how to set up and use the Stripe payment integration in the Agentic MicroSaaS platform.

## 🚀 Features

- **Subscription Management**: Create, manage, and cancel subscriptions
- **Customer Portal**: Self-service billing management
- **Payment History**: Track all payments and invoices
- **Webhook Handling**: Real-time subscription updates
- **Multiple Plans**: Support for Starter, Professional, and Enterprise tiers

## 📋 Setup Instructions

### 1. Stripe Account Setup

1. **Create a Stripe Account**:
   - Go to [stripe.com](https://stripe.com) and create an account
   - Complete the account verification process

2. **Get API Keys**:
   - Go to Stripe Dashboard → Developers → API Keys
   - Copy your **Publishable Key** and **Secret Key**
   - For production, use the live keys (starts with `pk_live_` and `sk_live_`)

3. **Create Products and Prices**:
   - Go to Stripe Dashboard → Products
   - Create three products:
     - **Starter Plan**: $29/month
     - **Professional Plan**: $99/month  
     - **Enterprise Plan**: Custom pricing
   - Copy the Price IDs for each plan

### 2. Environment Configuration

1. **Backend Configuration** (add to your `.env` file):
   ```env
   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
   STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
   STRIPE_STARTER_PRICE_ID=price_starter_plan_id
   STRIPE_PROFESSIONAL_PRICE_ID=price_professional_plan_id
   STRIPE_ENTERPRISE_PRICE_ID=price_enterprise_plan_id
   ```

2. **Frontend Configuration** (add to `apps/web/.env.local`):
   ```env
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_STRIPE_STARTER_PRICE_ID=price_starter_plan_id
   NEXT_PUBLIC_STRIPE_PROFESSIONAL_PRICE_ID=price_professional_plan_id
   NEXT_PUBLIC_STRIPE_ENTERPRISE_PRICE_ID=price_enterprise_plan_id
   ```

### 3. Database Migration

Run the database migration to create the Stripe tables:

```bash
# For the API (SQLAlchemy)
cd apps/api
alembic upgrade head

# For the web app (Prisma)
cd apps/web
npx prisma db push
```

### 4. Install Dependencies

```bash
# Backend dependencies
cd apps/api
pip install -r requirements.txt

# Frontend dependencies
cd apps/web
npm install
```

## 🔧 API Endpoints

### Authentication Required
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Create Checkout Session
```http
POST /stripe/create-checkout-session
Content-Type: application/json

{
  "price_id": "price_1234567890",
  "success_url": "https://yourapp.com/success",
  "cancel_url": "https://yourapp.com/cancel"
}
```

### Create Customer Portal Session
```http
POST /stripe/create-portal-session
Content-Type: application/json

{
  "return_url": "https://yourapp.com/dashboard"
}
```

### Get Subscriptions
```http
GET /stripe/subscriptions
```

### Get Payment History
```http
GET /stripe/payments
```

### Cancel Subscription
```http
POST /stripe/cancel-subscription/{subscription_id}?at_period_end=true
```

### Webhook Endpoint
```http
POST /stripe/webhook
Content-Type: application/json
Stripe-Signature: <webhook-signature>

{
  "id": "evt_1234567890",
  "type": "customer.subscription.created",
  "data": { ... }
}
```

## 🎨 Frontend Components

### SubscriptionManager Component

The `SubscriptionManager` component provides a complete subscription management interface:

```tsx
import { SubscriptionManager } from '@/components/SubscriptionManager';

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <SubscriptionManager />
    </div>
  );
}
```

### Features:
- **Plan Selection**: Choose between Starter, Professional, and Enterprise plans
- **Current Subscription**: View active subscription details
- **Payment History**: See all past payments and invoices
- **Subscription Management**: Cancel or modify subscriptions
- **Customer Portal**: Access Stripe's customer portal for billing management

## 🔗 Webhook Setup

### 1. Create Webhook Endpoint

1. Go to Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Set URL to: `https://yourdomain.com/stripe/webhook`
4. Select these events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

### 2. Get Webhook Secret

1. After creating the webhook, click on it
2. Copy the "Signing secret" (starts with `whsec_`)
3. Add it to your environment variables

### 3. Test Webhooks

Use Stripe CLI for local testing:
```bash
stripe listen --forward-to localhost:8000/stripe/webhook
```

## 🧪 Testing

### Test Mode
- Use test API keys (starts with `sk_test_` and `pk_test_`)
- Use test card numbers: `4242 4242 4242 4242`
- Test webhooks using Stripe CLI

### Test Cards
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Requires Authentication**: `4000 0025 0000 3155`

## 🚀 Production Deployment

### 1. Switch to Live Keys
- Replace test keys with live keys
- Update webhook endpoint to production URL
- Test thoroughly in staging environment

### 2. Security Considerations
- Enable webhook signature verification
- Use HTTPS for all endpoints
- Implement rate limiting
- Monitor for suspicious activity

### 3. Monitoring
- Set up Stripe Dashboard alerts
- Monitor webhook delivery
- Track subscription metrics
- Set up error logging

## 📊 Pricing Plans

### Starter Plan - $29/month
- Up to 1,000 API calls/month
- Basic AI agents
- Email support
- Standard infrastructure

### Professional Plan - $99/month
- Up to 10,000 API calls/month
- Advanced AI agents
- Priority support
- Enhanced infrastructure
- Custom integrations

### Enterprise Plan - Custom Pricing
- Unlimited API calls
- Custom AI models
- Dedicated support
- Private infrastructure
- Custom integrations
- SLA guarantee

## 🔍 Troubleshooting

### Common Issues

1. **Webhook Not Receiving Events**:
   - Check webhook URL is accessible
   - Verify webhook secret is correct
   - Check Stripe Dashboard for delivery logs

2. **Checkout Session Creation Fails**:
   - Verify price IDs are correct
   - Check Stripe API key permissions
   - Ensure customer exists

3. **Customer Portal Not Working**:
   - Verify customer has active subscription
   - Check return URL is valid
   - Ensure customer portal is enabled in Stripe

### Debug Mode

Enable debug logging in the API:
```python
import logging
logging.getLogger('stripe').setLevel(logging.DEBUG)
```

## 📚 Additional Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe API Reference](https://stripe.com/docs/api)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Stripe Customer Portal](https://stripe.com/docs/billing/subscriptions/customer-portal)
