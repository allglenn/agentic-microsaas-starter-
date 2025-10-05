from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, BigInteger, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    agents = relationship("Agent", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    api_calls = relationship("ApiCall", back_populates="user")
    stripe_customer = relationship("StripeCustomer", back_populates="user", uselist=False)
    subscriptions = relationship("Subscription", back_populates="user")
    email_notifications = relationship("EmailNotification", back_populates="user")
    email_preferences = relationship("EmailPreference", back_populates="user", uselist=False)
    team_memberships = relationship("TeamMembership", back_populates="user")
    owned_teams = relationship("Team", back_populates="owner")
    invitations_sent = relationship("TeamInvitation", back_populates="invited_by")
    invitations_received = relationship("TeamInvitation", back_populates="invited_user", foreign_keys="TeamInvitation.invited_user_id")
    files = relationship("File", back_populates="user")
    file_shares = relationship("FileShare", back_populates="shared_by")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    prompt = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="agents")
    tasks = relationship("Task", back_populates="agent")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    result = Column(Text, nullable=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    agent = relationship("Agent", back_populates="tasks")
    user = relationship("User", back_populates="tasks")

class ApiCall(Base):
    __tablename__ = "api_calls"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)  # in milliseconds
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="api_calls")

# Stripe-related models
class StripeCustomer(Base):
    __tablename__ = "stripe_customers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    stripe_customer_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="stripe_customer")
    subscriptions = relationship("Subscription", back_populates="stripe_customer")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    stripe_customer_id = Column(String, ForeignKey("stripe_customers.id"), nullable=False)
    stripe_subscription_id = Column(String, unique=True, nullable=False, index=True)
    stripe_price_id = Column(String, nullable=False)
    status = Column(String, nullable=False)  # active, canceled, past_due, incomplete, etc.
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime, nullable=True)
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="subscriptions")
    stripe_customer = relationship("StripeCustomer", back_populates="subscriptions")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    stripe_payment_intent_id = Column(String, unique=True, nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)  # Amount in cents
    currency = Column(String, default="usd", nullable=False)
    status = Column(String, nullable=False)  # succeeded, failed, pending, etc.
    description = Column(Text, nullable=True)
    payment_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    stripe_event_id = Column(String, unique=True, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    processed = Column(Boolean, default=False)
    data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

# Email-related models
class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    subject = Column(String, nullable=False)
    html_content = Column(Text, nullable=False)
    text_content = Column(Text, nullable=True)
    variables = Column(JSON, nullable=True)  # Available template variables
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EmailNotification(Base):
    __tablename__ = "email_notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    template_id = Column(String, ForeignKey("email_templates.id"), nullable=False)
    to_email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    html_content = Column(Text, nullable=False)
    text_content = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, sent, failed, bounced
    provider_message_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="email_notifications")
    template = relationship("EmailTemplate")

class EmailPreference(Base):
    __tablename__ = "email_preferences"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    marketing_emails = Column(Boolean, default=True)
    transactional_emails = Column(Boolean, default=True)
    product_updates = Column(Boolean, default=True)
    security_alerts = Column(Boolean, default=True)
    billing_notifications = Column(Boolean, default=True)
    weekly_digest = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="email_preferences")

# Team and Role-based Access Control models
class Team(Base):
    __tablename__ = "teams"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, nullable=True)  # Team-specific settings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="owned_teams")
    memberships = relationship("TeamMembership", back_populates="team")
    invitations = relationship("TeamInvitation", back_populates="team")

class Role(Base):
    __tablename__ = "roles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    permissions = Column(JSON, nullable=True)  # List of permissions
    is_system_role = Column(Boolean, default=False)  # System roles cannot be deleted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    memberships = relationship("TeamMembership", back_populates="role")

class TeamMembership(Base):
    __tablename__ = "team_memberships"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role_id = Column(String, ForeignKey("roles.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    invited_by_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    team = relationship("Team", back_populates="memberships")
    user = relationship("User", back_populates="team_memberships")
    role = relationship("Role", back_populates="memberships")
    invited_by = relationship("User", foreign_keys=[invited_by_id])

    # Ensure unique user per team
    __table_args__ = (
        {"extend_existing": True},
    )

class TeamInvitation(Base):
    __tablename__ = "team_invitations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    invited_user_id = Column(String, ForeignKey("users.id"), nullable=True)  # If user exists
    invited_email = Column(String, nullable=False)  # Email to invite
    role_id = Column(String, ForeignKey("roles.id"), nullable=False)
    invited_by_id = Column(String, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, default="pending")  # pending, accepted, declined, expired
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    declined_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    team = relationship("Team", back_populates="invitations")
    invited_user = relationship("User", back_populates="invitations_received", foreign_keys=[invited_user_id])
    invited_by = relationship("User", back_populates="invitations_sent", foreign_keys=[invited_by_id])
    role = relationship("Role")

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    resource = Column(String, nullable=False)  # e.g., "agents", "tasks", "billing"
    action = Column(String, nullable=False)  # e.g., "create", "read", "update", "delete"
    created_at = Column(DateTime, default=datetime.utcnow)

    # Ensure unique permission per resource-action combination
    __table_args__ = (
        {"extend_existing": True},
    )

# File Storage models
class File(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)  # Optional team association
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # GCS path
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)  # For deduplication
    is_public = Column(Boolean, default=False)
    is_encrypted = Column(Boolean, default=False)
    file_metadata = Column(JSON, nullable=True)  # Additional file metadata
    tags = Column(JSON, nullable=True)  # File tags for organization
    download_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="files")
    team = relationship("Team")
    shares = relationship("FileShare", back_populates="file")

class FileShare(Base):
    __tablename__ = "file_shares"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String, ForeignKey("files.id"), nullable=False)
    shared_by_id = Column(String, ForeignKey("users.id"), nullable=False)
    shared_with_user_id = Column(String, ForeignKey("users.id"), nullable=True)  # If shared with specific user
    shared_with_team_id = Column(String, ForeignKey("teams.id"), nullable=True)  # If shared with team
    share_token = Column(String, unique=True, nullable=False, index=True)  # For public sharing
    permission = Column(String, default="read")  # read, write, admin
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    is_active = Column(Boolean, default=True)
    access_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    file = relationship("File", back_populates="shares")
    shared_by = relationship("User", back_populates="file_shares", foreign_keys=[shared_by_id])
    shared_with_user = relationship("User", foreign_keys=[shared_with_user_id])
    shared_with_team = relationship("Team")

class FileUploadSession(Base):
    __tablename__ = "file_upload_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_token = Column(String, unique=True, nullable=False, index=True)
    filename = Column(String, nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String, nullable=False)
    chunk_size = Column(Integer, default=1048576)  # 1MB default
    total_chunks = Column(Integer, nullable=False)
    uploaded_chunks = Column(JSON, nullable=True)  # Array of uploaded chunk numbers
    status = Column(String, default="pending")  # pending, uploading, completed, failed
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")

class FileAccessLog(Base):
    __tablename__ = "file_access_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(String, ForeignKey("files.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Null for anonymous access
    action = Column(String, nullable=False)  # upload, download, view, share, delete
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    access_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    file = relationship("File")
    user = relationship("User")
