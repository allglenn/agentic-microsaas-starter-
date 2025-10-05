import stripe
import os
import sys
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import logging

# Add project root to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from libs.shared.models import User, StripeCustomer, Subscription, Payment, WebhookEvent

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class StripeService:
    """Service class for handling Stripe operations"""
    
    @staticmethod
    def create_customer(user: User, db: Session) -> StripeCustomer:
        """Create a Stripe customer for a user"""
        try:
            # Create customer in Stripe
            stripe_customer = stripe.Customer.create(
                email=user.email,
                name=user.name,
                metadata={
                    "user_id": user.id,
                    "app_name": "agentic-microsaas"
                }
            )
            
            # Create customer record in database
            db_customer = StripeCustomer(
                user_id=user.id,
                stripe_customer_id=stripe_customer.id,
                email=user.email,
                name=user.name
            )
            
            db.add(db_customer)
            db.commit()
            db.refresh(db_customer)
            
            logger.info(f"Created Stripe customer {stripe_customer.id} for user {user.id}")
            return db_customer
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating customer: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            raise
    
    @staticmethod
    def get_or_create_customer(user: User, db: Session) -> StripeCustomer:
        """Get existing customer or create new one"""
        # Check if customer already exists
        existing_customer = db.query(StripeCustomer).filter(
            StripeCustomer.user_id == user.id
        ).first()
        
        if existing_customer:
            return existing_customer
        
        return StripeService.create_customer(user, db)
    
    @staticmethod
    def create_checkout_session(
        user: User, 
        price_id: str, 
        success_url: str, 
        cancel_url: str,
        db: Session
    ) -> str:
        """Create a Stripe checkout session for subscription"""
        try:
            customer = StripeService.get_or_create_customer(user, db)
            
            session = stripe.checkout.Session.create(
                customer=customer.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": user.id,
                    "app_name": "agentic-microsaas"
                }
            )
            
            logger.info(f"Created checkout session {session.id} for user {user.id}")
            return session.url
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating checkout session: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            raise
    
    @staticmethod
    def create_portal_session(user: User, return_url: str) -> str:
        """Create a Stripe customer portal session"""
        try:
            customer = stripe.Customer.retrieve(user.stripe_customer.stripe_customer_id)
            
            session = stripe.billing_portal.Session.create(
                customer=customer.id,
                return_url=return_url,
            )
            
            logger.info(f"Created portal session for customer {customer.id}")
            return session.url
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating portal session: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating portal session: {e}")
            raise
    
    @staticmethod
    def get_subscription(subscription_id: str) -> Optional[Dict[str, Any]]:
        """Get subscription details from Stripe"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error retrieving subscription: {e}")
            return None
    
    @staticmethod
    def cancel_subscription(subscription_id: str, at_period_end: bool = True) -> bool:
        """Cancel a subscription"""
        try:
            if at_period_end:
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                stripe.Subscription.delete(subscription_id)
            
            logger.info(f"Canceled subscription {subscription_id}")
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error canceling subscription: {e}")
            return False
    
    @staticmethod
    def handle_webhook(event_data: Dict[str, Any], db: Session) -> bool:
        """Handle Stripe webhook events"""
        try:
            event_type = event_data.get('type')
            event_id = event_data.get('id')
            
            # Check if event already processed
            existing_event = db.query(WebhookEvent).filter(
                WebhookEvent.stripe_event_id == event_id
            ).first()
            
            if existing_event:
                logger.info(f"Event {event_id} already processed")
                return True
            
            # Store event
            webhook_event = WebhookEvent(
                stripe_event_id=event_id,
                event_type=event_type,
                data=event_data,
                processed=False
            )
            db.add(webhook_event)
            db.commit()
            
            # Process event based on type
            if event_type == 'customer.subscription.created':
                StripeService._handle_subscription_created(event_data, db)
            elif event_type == 'customer.subscription.updated':
                StripeService._handle_subscription_updated(event_data, db)
            elif event_type == 'customer.subscription.deleted':
                StripeService._handle_subscription_deleted(event_data, db)
            elif event_type == 'invoice.payment_succeeded':
                StripeService._handle_payment_succeeded(event_data, db)
            elif event_type == 'invoice.payment_failed':
                StripeService._handle_payment_failed(event_data, db)
            
            # Mark as processed
            webhook_event.processed = True
            webhook_event.processed_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Processed webhook event {event_id} of type {event_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return False
    
    @staticmethod
    def _handle_subscription_created(event_data: Dict[str, Any], db: Session):
        """Handle subscription created event"""
        subscription_data = event_data['data']['object']
        customer_id = subscription_data['customer']
        
        # Find customer in database
        stripe_customer = db.query(StripeCustomer).filter(
            StripeCustomer.stripe_customer_id == customer_id
        ).first()
        
        if not stripe_customer:
            logger.error(f"Customer {customer_id} not found for subscription")
            return
        
        # Create subscription record
        subscription = Subscription(
            user_id=stripe_customer.user_id,
            stripe_customer_id=stripe_customer.id,
            stripe_subscription_id=subscription_data['id'],
            stripe_price_id=subscription_data['items']['data'][0]['price']['id'],
            status=subscription_data['status'],
            current_period_start=datetime.fromtimestamp(subscription_data['current_period_start']),
            current_period_end=datetime.fromtimestamp(subscription_data['current_period_end']),
            trial_start=datetime.fromtimestamp(subscription_data['trial_start']) if subscription_data.get('trial_start') else None,
            trial_end=datetime.fromtimestamp(subscription_data['trial_end']) if subscription_data.get('trial_end') else None,
        )
        
        db.add(subscription)
        db.commit()
    
    @staticmethod
    def _handle_subscription_updated(event_data: Dict[str, Any], db: Session):
        """Handle subscription updated event"""
        subscription_data = event_data['data']['object']
        
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_data['id']
        ).first()
        
        if subscription:
            subscription.status = subscription_data['status']
            subscription.current_period_start = datetime.fromtimestamp(subscription_data['current_period_start'])
            subscription.current_period_end = datetime.fromtimestamp(subscription_data['current_period_end'])
            subscription.cancel_at_period_end = subscription_data['cancel_at_period_end']
            subscription.canceled_at = datetime.fromtimestamp(subscription_data['canceled_at']) if subscription_data.get('canceled_at') else None
            subscription.updated_at = datetime.utcnow()
            
            db.commit()
    
    @staticmethod
    def _handle_subscription_deleted(event_data: Dict[str, Any], db: Session):
        """Handle subscription deleted event"""
        subscription_data = event_data['data']['object']
        
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_data['id']
        ).first()
        
        if subscription:
            subscription.status = 'canceled'
            subscription.canceled_at = datetime.utcnow()
            subscription.updated_at = datetime.utcnow()
            
            db.commit()
    
    @staticmethod
    def _handle_payment_succeeded(event_data: Dict[str, Any], db: Session):
        """Handle payment succeeded event"""
        invoice_data = event_data['data']['object']
        subscription_id = invoice_data.get('subscription')
        
        if subscription_id:
            subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_id
            ).first()
            
            if subscription:
                # Create payment record
                payment = Payment(
                    user_id=subscription.user_id,
                    stripe_payment_intent_id=invoice_data['payment_intent'],
                    amount=invoice_data['amount_paid'] / 100,  # Convert from cents
                    currency=invoice_data['currency'],
                    status='succeeded',
                    description=f"Payment for subscription {subscription_id}",
                    metadata={
                        "subscription_id": subscription_id,
                        "invoice_id": invoice_data['id']
                    }
                )
                
                db.add(payment)
                db.commit()
    
    @staticmethod
    def _handle_payment_failed(event_data: Dict[str, Any], db: Session):
        """Handle payment failed event"""
        invoice_data = event_data['data']['object']
        subscription_id = invoice_data.get('subscription')
        
        if subscription_id:
            subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_id
            ).first()
            
            if subscription:
                # Create payment record
                payment = Payment(
                    user_id=subscription.user_id,
                    stripe_payment_intent_id=invoice_data['payment_intent'],
                    amount=invoice_data['amount_due'] / 100,  # Convert from cents
                    currency=invoice_data['currency'],
                    status='failed',
                    description=f"Failed payment for subscription {subscription_id}",
                    metadata={
                        "subscription_id": subscription_id,
                        "invoice_id": invoice_data['id']
                    }
                )
                
                db.add(payment)
                db.commit()
