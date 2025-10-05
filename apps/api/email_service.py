import sys
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from jinja2 import Template, Environment, FileSystemLoader
import json

# Add project root to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from libs.shared.models import User, EmailTemplate, EmailNotification, EmailPreference
from libs.shared.config import get_sendgrid_config

logger = logging.getLogger(__name__)

# Configure SendGrid using shared config
sendgrid_config = get_sendgrid_config()
sendgrid_client = SendGridAPIClient(api_key=sendgrid_config["api_key"])

# Jinja2 environment for template rendering
template_env = Environment(loader=FileSystemLoader("templates"))

class EmailService:
    """Service class for handling email operations with SendGrid"""
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        user_id: Optional[str] = None,
        template_id: Optional[str] = None,
        db: Session = None
    ) -> bool:
        """Send an email using SendGrid"""
        try:
            from_email = from_email or os.getenv("SENDGRID_FROM_EMAIL", "noreply@yourapp.com")
            
            # Create SendGrid mail object
            mail = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            if text_content:
                mail.add_content(Content("text/plain", text_content))
            
            # Send email
            response = sendgrid_client.send(mail)
            
            # Log email notification if user_id provided
            if user_id and db and template_id:
                EmailService._log_email_notification(
                    user_id=user_id,
                    template_id=template_id,
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    status="sent",
                    provider_message_id=response.headers.get("X-Message-Id"),
                    db=db
                )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            
            # Log failed email notification
            if user_id and db and template_id:
                EmailService._log_email_notification(
                    user_id=user_id,
                    template_id=template_id,
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                    status="failed",
                    error_message=str(e),
                    db=db
                )
            
            return False
    
    @staticmethod
    def send_template_email(
        template_name: str,
        to_email: str,
        variables: Dict[str, Any],
        user_id: Optional[str] = None,
        db: Session = None
    ) -> bool:
        """Send an email using a template"""
        try:
            # Get template from database
            template = db.query(EmailTemplate).filter(
                EmailTemplate.name == template_name,
                EmailTemplate.is_active == True
            ).first()
            
            if not template:
                logger.error(f"Template {template_name} not found")
                return False
            
            # Render template with variables
            html_template = Template(template.html_content)
            text_template = Template(template.text_content) if template.text_content else None
            
            html_content = html_template.render(**variables)
            text_content = text_template.render(**variables) if text_template else None
            
            # Send email
            return EmailService.send_email(
                to_email=to_email,
                subject=template.subject,
                html_content=html_content,
                text_content=text_content,
                user_id=user_id,
                template_id=template.id,
                db=db
            )
            
        except Exception as e:
            logger.error(f"Failed to send template email {template_name}: {e}")
            return False
    
    @staticmethod
    def send_welcome_email(user: User, db: Session) -> bool:
        """Send welcome email to new user"""
        variables = {
            "user_name": user.name or "there",
            "user_email": user.email,
            "app_name": "Agentic MicroSaaS",
            "dashboard_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard"
        }
        
        return EmailService.send_template_email(
            template_name="welcome",
            to_email=user.email,
            variables=variables,
            user_id=user.id,
            db=db
        )
    
    @staticmethod
    def send_password_reset_email(user: User, reset_token: str, db: Session) -> bool:
        """Send password reset email"""
        reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={reset_token}"
        
        variables = {
            "user_name": user.name or "there",
            "reset_url": reset_url,
            "app_name": "Agentic MicroSaaS"
        }
        
        return EmailService.send_template_email(
            template_name="password_reset",
            to_email=user.email,
            variables=variables,
            user_id=user.id,
            db=db
        )
    
    @staticmethod
    def send_subscription_confirmation(user: User, subscription_data: Dict[str, Any], db: Session) -> bool:
        """Send subscription confirmation email"""
        variables = {
            "user_name": user.name or "there",
            "plan_name": subscription_data.get("plan_name", "Unknown Plan"),
            "amount": subscription_data.get("amount", 0),
            "currency": subscription_data.get("currency", "USD"),
            "billing_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard/billing",
            "app_name": "Agentic MicroSaaS"
        }
        
        return EmailService.send_template_email(
            template_name="subscription_confirmation",
            to_email=user.email,
            variables=variables,
            user_id=user.id,
            db=db
        )
    
    @staticmethod
    def send_payment_failed_email(user: User, subscription_data: Dict[str, Any], db: Session) -> bool:
        """Send payment failed email"""
        variables = {
            "user_name": user.name or "there",
            "plan_name": subscription_data.get("plan_name", "Unknown Plan"),
            "amount": subscription_data.get("amount", 0),
            "currency": subscription_data.get("currency", "USD"),
            "billing_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard/billing",
            "app_name": "Agentic MicroSaaS"
        }
        
        return EmailService.send_template_email(
            template_name="payment_failed",
            to_email=user.email,
            variables=variables,
            user_id=user.id,
            db=db
        )
    
    @staticmethod
    def send_weekly_digest(user: User, digest_data: Dict[str, Any], db: Session) -> bool:
        """Send weekly digest email"""
        variables = {
            "user_name": user.name or "there",
            "week_start": digest_data.get("week_start"),
            "week_end": digest_data.get("week_end"),
            "api_calls": digest_data.get("api_calls", 0),
            "tasks_completed": digest_data.get("tasks_completed", 0),
            "dashboard_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard",
            "app_name": "Agentic MicroSaaS"
        }
        
        return EmailService.send_template_email(
            template_name="weekly_digest",
            to_email=user.email,
            variables=variables,
            user_id=user.id,
            db=db
        )
    
    @staticmethod
    def get_user_email_preferences(user_id: str, db: Session) -> Optional[EmailPreference]:
        """Get user's email preferences"""
        return db.query(EmailPreference).filter(EmailPreference.user_id == user_id).first()
    
    @staticmethod
    def update_user_email_preferences(
        user_id: str,
        preferences: Dict[str, bool],
        db: Session
    ) -> EmailPreference:
        """Update user's email preferences"""
        email_prefs = db.query(EmailPreference).filter(EmailPreference.user_id == user_id).first()
        
        if not email_prefs:
            email_prefs = EmailPreference(user_id=user_id)
            db.add(email_prefs)
        
        # Update preferences
        for key, value in preferences.items():
            if hasattr(email_prefs, key):
                setattr(email_prefs, key, value)
        
        email_prefs.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(email_prefs)
        
        return email_prefs
    
    @staticmethod
    def can_send_email(user_id: str, email_type: str, db: Session) -> bool:
        """Check if user has opted in to receive this type of email"""
        preferences = EmailService.get_user_email_preferences(user_id, db)
        
        if not preferences:
            return True  # Default to allowing emails if no preferences set
        
        email_type_mapping = {
            "welcome": "transactional_emails",
            "password_reset": "transactional_emails",
            "subscription_confirmation": "billing_notifications",
            "payment_failed": "billing_notifications",
            "weekly_digest": "weekly_digest",
            "product_updates": "product_updates",
            "marketing": "marketing_emails",
            "security": "security_alerts"
        }
        
        preference_key = email_type_mapping.get(email_type, "transactional_emails")
        return getattr(preferences, preference_key, True)
    
    @staticmethod
    def _log_email_notification(
        user_id: str,
        template_id: str,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        status: str,
        provider_message_id: Optional[str] = None,
        error_message: Optional[str] = None,
        db: Session = None
    ):
        """Log email notification to database"""
        try:
            notification = EmailNotification(
                user_id=user_id,
                template_id=template_id,
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                status=status,
                provider_message_id=provider_message_id,
                error_message=error_message,
                sent_at=datetime.utcnow() if status == "sent" else None
            )
            
            db.add(notification)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log email notification: {e}")
    
    @staticmethod
    def create_default_templates(db: Session):
        """Create default email templates"""
        templates = [
            {
                "name": "welcome",
                "subject": "Welcome to {{ app_name }}!",
                "html_content": """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Welcome to {{ app_name }}</title>
                </head>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h1>Welcome to {{ app_name }}, {{ user_name }}!</h1>
                    <p>Thank you for joining us. We're excited to have you on board!</p>
                    <p>Get started by exploring your dashboard:</p>
                    <a href="{{ dashboard_url }}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go to Dashboard</a>
                    <p>If you have any questions, feel free to reach out to our support team.</p>
                    <p>Best regards,<br>The {{ app_name }} Team</p>
                </body>
                </html>
                """,
                "text_content": """
                Welcome to {{ app_name }}, {{ user_name }}!
                
                Thank you for joining us. We're excited to have you on board!
                
                Get started by exploring your dashboard: {{ dashboard_url }}
                
                If you have any questions, feel free to reach out to our support team.
                
                Best regards,
                The {{ app_name }} Team
                """,
                "variables": ["user_name", "user_email", "app_name", "dashboard_url"]
            },
            {
                "name": "password_reset",
                "subject": "Reset your {{ app_name }} password",
                "html_content": """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Reset Your Password</title>
                </head>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h1>Reset Your Password</h1>
                    <p>Hi {{ user_name }},</p>
                    <p>You requested to reset your password for {{ app_name }}.</p>
                    <p>Click the button below to reset your password:</p>
                    <a href="{{ reset_url }}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
                    <p>This link will expire in 1 hour for security reasons.</p>
                    <p>If you didn't request this password reset, please ignore this email.</p>
                    <p>Best regards,<br>The {{ app_name }} Team</p>
                </body>
                </html>
                """,
                "text_content": """
                Reset Your Password
                
                Hi {{ user_name }},
                
                You requested to reset your password for {{ app_name }}.
                
                Click the link below to reset your password: {{ reset_url }}
                
                This link will expire in 1 hour for security reasons.
                
                If you didn't request this password reset, please ignore this email.
                
                Best regards,
                The {{ app_name }} Team
                """,
                "variables": ["user_name", "reset_url", "app_name"]
            }
        ]
        
        for template_data in templates:
            existing = db.query(EmailTemplate).filter(EmailTemplate.name == template_data["name"]).first()
            if not existing:
                template = EmailTemplate(**template_data)
                db.add(template)
        
        db.commit()
        logger.info("Default email templates created")
