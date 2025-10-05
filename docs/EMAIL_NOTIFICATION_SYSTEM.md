# 📧 Email Notification System

This document explains how to set up and use the email notification system in the Agentic MicroSaaS platform using SendGrid.

## 🚀 Features

- **SendGrid Integration**: Reliable email delivery with SendGrid
- **Template System**: Jinja2-based email templates with variable substitution
- **Email Preferences**: User-controlled email subscription management
- **Notification Tracking**: Complete email delivery and status tracking
- **Multiple Email Types**: Welcome, password reset, billing, marketing, and more
- **HTML & Text Support**: Both HTML and plain text email formats

## 📋 Setup Instructions

### 1. SendGrid Account Setup

1. **Create a SendGrid Account**:
   - Go to [sendgrid.com](https://sendgrid.com) and create an account
   - Complete the account verification process

2. **Get API Key**:
   - Go to SendGrid Dashboard → Settings → API Keys
   - Click "Create API Key"
   - Choose "Full Access" or "Restricted Access" (recommended)
   - Copy the API key (starts with `SG.`)

3. **Verify Sender Identity**:
   - Go to Settings → Sender Authentication
   - Verify a single sender email or domain
   - This will be your "from" email address

### 2. Environment Configuration

1. **Backend Configuration** (add to your `.env` file):
   ```env
   SENDGRID_API_KEY=SG.your_sendgrid_api_key_here
   SENDGRID_FROM_EMAIL=noreply@yourapp.com
   SENDGRID_FROM_NAME=Your App Name
   FRONTEND_URL=http://localhost:3000
   ```

2. **Frontend Configuration** (add to `apps/web/.env.local`):
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

### 3. Database Migration

Run the database migration to create the email tables:

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

### 5. Initialize Email Templates

The system will automatically create default email templates on first run. You can also create them manually:

```python
from email_service import EmailService
from database import get_db

# Initialize default templates
db = next(get_db())
EmailService.create_default_templates(db)
```

## 🔧 API Endpoints

### Authentication Required
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Send Custom Email
```http
POST /email/send
Content-Type: application/json

{
  "to_email": "user@example.com",
  "subject": "Your Subject",
  "html_content": "<h1>Hello World</h1>",
  "text_content": "Hello World"
}
```

### Send Template Email
```http
POST /email/send-template/{template_name}
Content-Type: application/json

{
  "to_email": "user@example.com",
  "variables": {
    "user_name": "John Doe",
    "app_name": "My App"
  }
}
```

### Get Email Templates
```http
GET /email/templates
```

### Get Email Notifications
```http
GET /email/notifications
```

### Get Email Preferences
```http
GET /email/preferences
```

### Update Email Preferences
```http
PUT /email/preferences
Content-Type: application/json

{
  "marketing_emails": true,
  "transactional_emails": true,
  "product_updates": false,
  "security_alerts": true,
  "billing_notifications": true,
  "weekly_digest": false
}
```

### Send Test Welcome Email
```http
POST /email/test-welcome
```

## 🎨 Frontend Components

### EmailPreferences Component

The `EmailPreferences` component provides a complete email preference management interface:

```tsx
import { EmailPreferences } from '@/components/EmailPreferences';

export default function Settings() {
  return (
    <div>
      <h1>Settings</h1>
      <EmailPreferences />
    </div>
  );
}
```

### Features:
- **Preference Toggle**: Enable/disable different email types
- **Required Emails**: Some emails (security, billing) cannot be disabled
- **Test Email**: Send test welcome email
- **Real-time Updates**: Changes are saved immediately
- **Visual Feedback**: Success/error messages for all actions

## 📧 Email Templates

### Default Templates

The system includes several default email templates:

1. **Welcome Email** (`welcome`)
   - Sent when a new user registers
   - Variables: `user_name`, `user_email`, `app_name`, `dashboard_url`

2. **Password Reset** (`password_reset`)
   - Sent when user requests password reset
   - Variables: `user_name`, `reset_url`, `app_name`

3. **Subscription Confirmation** (`subscription_confirmation`)
   - Sent when user subscribes to a plan
   - Variables: `user_name`, `plan_name`, `amount`, `currency`, `billing_url`

4. **Payment Failed** (`payment_failed`)
   - Sent when payment fails
   - Variables: `user_name`, `plan_name`, `amount`, `currency`, `billing_url`

5. **Weekly Digest** (`weekly_digest`)
   - Sent weekly with user activity summary
   - Variables: `user_name`, `week_start`, `week_end`, `api_calls`, `tasks_completed`

### Creating Custom Templates

1. **Add to Database**:
   ```python
   template = EmailTemplate(
       name="custom_template",
       subject="Custom Subject - {{ user_name }}",
       html_content="<h1>Hello {{ user_name }}</h1>",
       text_content="Hello {{ user_name }}",
       variables=["user_name", "custom_var"]
   )
   db.add(template)
   db.commit()
   ```

2. **Use in Code**:
   ```python
   EmailService.send_template_email(
       template_name="custom_template",
       to_email="user@example.com",
       variables={"user_name": "John", "custom_var": "value"},
       user_id=user.id,
       db=db
   )
   ```

## 🔔 Email Types and Preferences

### Email Types

- **Welcome**: New user registration
- **Password Reset**: Account security
- **Subscription Confirmation**: Billing notifications
- **Payment Failed**: Billing notifications
- **Weekly Digest**: User engagement
- **Product Updates**: Feature announcements
- **Marketing**: Promotional content
- **Security**: Security alerts

### User Preferences

Users can control which emails they receive:

- **Marketing Emails**: Promotional content (can be disabled)
- **Transactional Emails**: Account-related emails (required)
- **Product Updates**: Feature announcements (can be disabled)
- **Security Alerts**: Security notifications (required)
- **Billing Notifications**: Payment and subscription emails (required)
- **Weekly Digest**: Activity summaries (can be disabled)

## 🧪 Testing

### Test Mode
- Use SendGrid's test mode for development
- Test emails are sent but not delivered
- Check SendGrid dashboard for delivery logs

### Test Email Endpoints
- Use `/email/test-welcome` to send test welcome emails
- Check email delivery in SendGrid dashboard
- Verify email preferences are working correctly

### Email Validation
- SendGrid validates email addresses automatically
- Invalid emails are marked as "failed" in the database
- Bounced emails are tracked and can be handled

## 🚀 Production Deployment

### 1. SendGrid Configuration
- Switch to production API key
- Verify your domain for better deliverability
- Set up dedicated IP (recommended for high volume)
- Configure webhook events for delivery tracking

### 2. Email Templates
- Customize templates with your branding
- Test all templates before going live
- Ensure mobile-responsive design
- Include unsubscribe links where required

### 3. Monitoring
- Set up SendGrid dashboard alerts
- Monitor bounce rates and spam complaints
- Track email engagement metrics
- Set up error logging for failed sends

### 4. Compliance
- Include unsubscribe links in marketing emails
- Respect user preferences
- Follow CAN-SPAM and GDPR requirements
- Maintain email preference records

## 📊 Email Analytics

### Tracking Metrics
- **Delivery Rate**: Percentage of emails successfully delivered
- **Open Rate**: Percentage of emails opened by recipients
- **Click Rate**: Percentage of emails with clicked links
- **Bounce Rate**: Percentage of emails that bounced
- **Unsubscribe Rate**: Percentage of users who unsubscribed

### SendGrid Dashboard
- Real-time email activity
- Delivery statistics
- Bounce and spam reports
- Email performance analytics

## 🔍 Troubleshooting

### Common Issues

1. **Emails Not Sending**:
   - Check SendGrid API key is correct
   - Verify sender email is authenticated
   - Check SendGrid account status
   - Review error logs

2. **Template Not Found**:
   - Ensure template exists in database
   - Check template name spelling
   - Verify template is active

3. **User Preferences Not Working**:
   - Check user has email preferences record
   - Verify preference update logic
   - Check email type mapping

4. **High Bounce Rate**:
   - Verify email addresses are valid
   - Check sender reputation
   - Review email content for spam triggers

### Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger('sendgrid').setLevel(logging.DEBUG)
logging.getLogger('email_service').setLevel(logging.DEBUG)
```

## 📚 Additional Resources

- [SendGrid Documentation](https://docs.sendgrid.com/)
- [SendGrid API Reference](https://docs.sendgrid.com/api-reference/)
- [Email Best Practices](https://docs.sendgrid.com/for-developers/sending-email/best-practices)
- [Jinja2 Template Documentation](https://jinja.palletsprojects.com/)
- [CAN-SPAM Act Compliance](https://www.ftc.gov/tips-advice/business-center/guidance/can-spam-act-compliance-guide-business)
