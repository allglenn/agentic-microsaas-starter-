import { loadStripe } from '@stripe/stripe-js';

// Initialize Stripe
export const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

// Stripe configuration
export const STRIPE_CONFIG = {
  publishableKey: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!,
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
};

// Pricing plans configuration
export const PRICING_PLANS = {
  starter: {
    id: 'starter',
    name: 'Starter',
    price: 29,
    priceId: process.env.NEXT_PUBLIC_STRIPE_STARTER_PRICE_ID!,
    features: [
      'Up to 1,000 API calls/month',
      'Basic AI agents',
      'Email support',
      'Standard infrastructure',
    ],
  },
  professional: {
    id: 'professional',
    name: 'Professional',
    price: 99,
    priceId: process.env.NEXT_PUBLIC_STRIPE_PROFESSIONAL_PRICE_ID!,
    features: [
      'Up to 10,000 API calls/month',
      'Advanced AI agents',
      'Priority support',
      'Enhanced infrastructure',
      'Custom integrations',
    ],
  },
  enterprise: {
    id: 'enterprise',
    name: 'Enterprise',
    price: 'Custom',
    priceId: process.env.NEXT_PUBLIC_STRIPE_ENTERPRISE_PRICE_ID!,
    features: [
      'Unlimited API calls',
      'Custom AI models',
      'Dedicated support',
      'Private infrastructure',
      'Custom integrations',
      'SLA guarantee',
    ],
  },
};

// API functions
export const stripeApi = {
  async createCheckoutSession(priceId: string, successUrl: string, cancelUrl: string) {
    const response = await fetch(`${STRIPE_CONFIG.apiUrl}/stripe/create-checkout-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${await getAuthToken()}`,
      },
      body: JSON.stringify({
        price_id: priceId,
        success_url: successUrl,
        cancel_url: cancelUrl,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to create checkout session');
    }

    return response.json();
  },

  async createPortalSession(returnUrl: string) {
    const response = await fetch(`${STRIPE_CONFIG.apiUrl}/stripe/create-portal-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${await getAuthToken()}`,
      },
      body: JSON.stringify({
        return_url: returnUrl,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to create portal session');
    }

    return response.json();
  },

  async getSubscriptions() {
    const response = await fetch(`${STRIPE_CONFIG.apiUrl}/stripe/subscriptions`, {
      headers: {
        'Authorization': `Bearer ${await getAuthToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch subscriptions');
    }

    return response.json();
  },

  async getPayments() {
    const response = await fetch(`${STRIPE_CONFIG.apiUrl}/stripe/payments`, {
      headers: {
        'Authorization': `Bearer ${await getAuthToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch payments');
    }

    return response.json();
  },

  async cancelSubscription(subscriptionId: string, atPeriodEnd: boolean = true) {
    const response = await fetch(`${STRIPE_CONFIG.apiUrl}/stripe/cancel-subscription/${subscriptionId}?at_period_end=${atPeriodEnd}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${await getAuthToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to cancel subscription');
    }

    return response.json();
  },
};

// Helper function to get auth token
async function getAuthToken(): Promise<string> {
  // This would typically get the token from your auth system
  // For now, we'll return a placeholder
  return 'your-auth-token-here';
}
