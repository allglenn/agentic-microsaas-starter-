from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel
from database import get_db, engine, Base
from models import User, Agent, Task, ApiCall, StripeCustomer, Subscription, Payment, EmailTemplate, EmailNotification, EmailPreference
from stripe_service import StripeService
from email_service import EmailService
import logging
# Workflow imports will be added inline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agentic MicroSaaS API",
    description="API for AI-powered microsaas platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    email: str
    name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    prompt: str
    agent_type: Optional[str] = "basic"
    model_type: Optional[str] = "gpt-3.5-turbo"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    specialties: Optional[List[str]] = []

class AgentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    prompt: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    agent_id: str

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    result: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Stripe Pydantic models
class CheckoutSessionRequest(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str

class CheckoutSessionResponse(BaseModel):
    url: str

class PortalSessionRequest(BaseModel):
    return_url: str

class PortalSessionResponse(BaseModel):
    url: str

class SubscriptionResponse(BaseModel):
    id: str
    stripe_subscription_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Email Pydantic models
class EmailTemplateResponse(BaseModel):
    id: str
    name: str
    subject: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class EmailNotificationResponse(BaseModel):
    id: str
    to_email: str
    subject: str
    status: str
    sent_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class EmailPreferenceRequest(BaseModel):
    marketing_emails: Optional[bool] = None
    transactional_emails: Optional[bool] = None
    product_updates: Optional[bool] = None
    security_alerts: Optional[bool] = None
    billing_notifications: Optional[bool] = None
    weekly_digest: Optional[bool] = None

class EmailPreferenceResponse(BaseModel):
    id: str
    marketing_emails: bool
    transactional_emails: bool
    product_updates: bool
    security_alerts: bool
    billing_notifications: bool
    weekly_digest: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SendEmailRequest(BaseModel):
    to_email: str
    subject: str
    html_content: str
    text_content: Optional[str] = None

# Auth functions
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, os.getenv("API_SECRET_KEY", "secret"), algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(user_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Routes
@app.get("/")
async def root():
    return {"message": "Agentic MicroSaaS API", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# User routes
@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Agent routes
@app.post("/agents", response_model=AgentResponse)
async def create_agent(agent: AgentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_agent = Agent(
        name=agent.name,
        description=agent.description,
        prompt=agent.prompt,
        user_id=current_user.id
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

# Get available agent types
@app.get("/agents/types")
async def get_agent_types():
    from agent_configs import get_available_agent_types, get_agent_config
    agent_types = get_available_agent_types()
    return {
        "agent_types": agent_types,
        "configs": {agent_type: get_agent_config(agent_type) for agent_type in agent_types}
    }

@app.get("/agents", response_model=List[AgentResponse])
async def get_agents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agents = db.query(Agent).filter(Agent.user_id == current_user.id).all()
    return agents

@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id, Agent.user_id == current_user.id).first()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

# Task routes
@app.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify agent belongs to user
    agent = db.query(Agent).filter(Agent.id == task.agent_id, Agent.user_id == current_user.id).first()
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db_task = Task(
        title=task.title,
        description=task.description,
        agent_id=task.agent_id,
        user_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    tasks = db.query(Task).filter(Task.user_id == current_user.id).order_by(Task.created_at.desc()).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Analytics routes
@app.get("/analytics/api-calls")
async def get_api_calls_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    since = datetime.utcnow() - timedelta(days=days)
    calls = db.query(ApiCall).filter(
        ApiCall.user_id == current_user.id,
        ApiCall.created_at >= since
    ).all()
    
    total_calls = len(calls)
    successful_calls = len([c for c in calls if 200 <= c.status < 300])
    avg_duration = sum(c.duration for c in calls) / total_calls if total_calls > 0 else 0
    
    return {
        "total_calls": total_calls,
        "successful_calls": successful_calls,
        "success_rate": (successful_calls / total_calls * 100) if total_calls > 0 else 0,
        "average_duration_ms": round(avg_duration, 2)
    }

# Stripe Payment Endpoints
@app.post("/stripe/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe checkout session for subscription"""
    try:
        url = StripeService.create_checkout_session(
            user=current_user,
            price_id=request.price_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            db=db
        )
        return CheckoutSessionResponse(url=url)
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

@app.post("/stripe/create-portal-session", response_model=PortalSessionResponse)
async def create_portal_session(
    request: PortalSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a Stripe customer portal session"""
    try:
        if not current_user.stripe_customer:
            raise HTTPException(status_code=404, detail="No Stripe customer found")
        
        url = StripeService.create_portal_session(
            user=current_user,
            return_url=request.return_url
        )
        return PortalSessionResponse(url=url)
    except Exception as e:
        logger.error(f"Error creating portal session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create portal session")

@app.get("/stripe/subscriptions", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's subscriptions"""
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).order_by(Subscription.created_at.desc()).all()
    return subscriptions

@app.get("/stripe/payments", response_model=List[PaymentResponse])
async def get_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's payment history"""
    payments = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).order_by(Payment.created_at.desc()).all()
    return payments

@app.post("/stripe/cancel-subscription/{subscription_id}")
async def cancel_subscription(
    subscription_id: str,
    at_period_end: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a subscription"""
    # Verify subscription belongs to user
    subscription = db.query(Subscription).filter(
        Subscription.id == subscription_id,
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    success = StripeService.cancel_subscription(
        subscription_id=subscription.stripe_subscription_id,
        at_period_end=at_period_end
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")
    
    return {"message": "Subscription canceled successfully"}

@app.post("/stripe/webhook")
async def stripe_webhook(request: dict, db: Session = Depends(get_db)):
    """Handle Stripe webhook events"""
    try:
        # In production, verify the webhook signature
        # stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        
        success = StripeService.handle_webhook(request, db)
        if success:
            return {"status": "success"}
        else:
            raise HTTPException(status_code=400, detail="Webhook processing failed")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")

# Email Notification Endpoints
@app.post("/email/send")
async def send_email(
    request: SendEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a custom email"""
    try:
        success = EmailService.send_email(
            to_email=request.to_email,
            subject=request.subject,
            html_content=request.html_content,
            text_content=request.text_content,
            user_id=current_user.id,
            db=db
        )
        
        if success:
            return {"message": "Email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

@app.post("/email/send-template/{template_name}")
async def send_template_email(
    template_name: str,
    to_email: str,
    variables: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send an email using a template"""
    try:
        success = EmailService.send_template_email(
            template_name=template_name,
            to_email=to_email,
            variables=variables,
            user_id=current_user.id,
            db=db
        )
        
        if success:
            return {"message": "Template email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send template email")
    except Exception as e:
        logger.error(f"Error sending template email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send template email")

@app.get("/email/templates", response_model=List[EmailTemplateResponse])
async def get_email_templates(db: Session = Depends(get_db)):
    """Get all email templates"""
    templates = db.query(EmailTemplate).filter(EmailTemplate.is_active == True).all()
    return templates

@app.get("/email/notifications", response_model=List[EmailNotificationResponse])
async def get_email_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's email notifications"""
    notifications = db.query(EmailNotification).filter(
        EmailNotification.user_id == current_user.id
    ).order_by(EmailNotification.created_at.desc()).limit(50).all()
    return notifications

@app.get("/email/preferences", response_model=EmailPreferenceResponse)
async def get_email_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's email preferences"""
    preferences = EmailService.get_user_email_preferences(current_user.id, db)
    
    if not preferences:
        # Create default preferences
        preferences = EmailService.update_user_email_preferences(
            user_id=current_user.id,
            preferences={},
            db=db
        )
    
    return preferences

@app.put("/email/preferences", response_model=EmailPreferenceResponse)
async def update_email_preferences(
    request: EmailPreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's email preferences"""
    try:
        # Convert request to dict, filtering out None values
        preferences_dict = {k: v for k, v in request.dict().items() if v is not None}
        
        preferences = EmailService.update_user_email_preferences(
            user_id=current_user.id,
            preferences=preferences_dict,
            db=db
        )
        
        return preferences
    except Exception as e:
        logger.error(f"Error updating email preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update email preferences")

@app.post("/email/test-welcome")
async def test_welcome_email(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a test welcome email"""
    try:
        success = EmailService.send_welcome_email(current_user, db)
        
        if success:
            return {"message": "Welcome email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send welcome email")
    except Exception as e:
        logger.error(f"Error sending welcome email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send welcome email")

# Workflow Endpoints
@app.post("/workflows/execute")
async def execute_workflow(
    workflow_id: str,
    variables: Optional[dict] = None,
    current_user: User = Depends(get_current_user)
):
    """Execute a workflow"""
    try:
        # Import workflow engine
        from workflow_agents import workflow_engine
        
        instance_id = await workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            variables=variables or {},
            user_id=str(current_user.id)
        )
        
        return {
            "message": "Workflow execution started",
            "instance_id": instance_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows/instances/{instance_id}/status")
async def get_workflow_status(instance_id: str):
    """Get workflow instance status"""
    try:
        from workflow_agents import workflow_engine
        
        instance = workflow_engine.get_workflow_status(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail="Workflow instance not found")
        
        # Calculate progress
        workflow = workflow_engine.workflows.get(instance.workflow_id)
        total_steps = len(workflow.steps) if workflow else 0
        completed_steps = len([r for r in instance.results.values() if r is not None])
        progress = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        return {
            "instance_id": instance.id,
            "status": instance.status.value,
            "current_step": instance.current_step,
            "progress": progress,
            "started_at": instance.started_at,
            "completed_at": instance.completed_at,
            "results": instance.results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflows/templates")
async def list_workflow_templates():
    """List available workflow templates"""
    try:
        templates = [
            {
                "id": "customer_support_workflow",
                "name": "Customer Support Workflow",
                "description": "Automated customer support with escalation",
                "category": "customer_service",
                "step_count": 4
            },
            {
                "id": "content_creation_workflow",
                "name": "Content Creation Workflow",
                "description": "Automated content creation with review process",
                "category": "content_marketing",
                "step_count": 5
            },
            {
                "id": "data_analysis_workflow",
                "name": "Data Analysis Workflow",
                "description": "Automated data analysis with insights generation",
                "category": "data_analytics",
                "step_count": 5
            }
        ]
        
        return templates
        
    except Exception as e:
        logger.error(f"Error listing workflow templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)