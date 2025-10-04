# 👥 Team Management & RBAC System

This document explains how to set up and use the comprehensive team management and role-based access control (RBAC) system in the Agentic MicroSaaS platform.

## 🚀 Features

- **Team Management**: Create, manage, and organize teams
- **Role-Based Access Control (RBAC)**: Granular permissions system
- **User Invitations**: Email-based team invitations with expiration
- **Member Management**: Add, remove, and update member roles
- **Permission System**: Resource-based permissions (agents, tasks, billing, etc.)
- **Team Settings**: Customizable team configurations
- **Invitation Tracking**: Monitor pending and expired invitations

## 📋 Setup Instructions

### 1. Database Migration

Run the database migration to create the team management tables:

```bash
# For the API (SQLAlchemy)
cd apps/api
alembic upgrade head

# For the web app (Prisma)
cd apps/web
npx prisma db push
```

### 2. Initialize Default Roles

The system will automatically create default roles on first run. You can also create them manually:

```python
from team_service import TeamService
from database import get_db

# Initialize default roles
db = next(get_db())
TeamService.create_default_roles(db)
```

### 3. Install Dependencies

```bash
# Backend dependencies (already included)
cd apps/api
pip install -r requirements.txt

# Frontend dependencies (already included)
cd apps/web
npm install
```

## 🔧 API Endpoints

### Authentication Required
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Team Management

#### Create Team
```http
POST /teams
Content-Type: application/json

{
  "name": "My Team",
  "description": "Team description"
}
```

#### Get User Teams
```http
GET /teams
```

#### Get Team Details
```http
GET /teams/{team_id}
```

### Member Management

#### Get Team Members
```http
GET /teams/{team_id}/members
```

#### Update Member Role
```http
PUT /teams/{team_id}/members/role
Content-Type: application/json

{
  "user_id": "user_id_here",
  "role": "admin"
}
```

#### Remove Member
```http
DELETE /teams/{team_id}/members/{user_id}
```

### Invitation Management

#### Invite User to Team
```http
POST /teams/{team_id}/invite
Content-Type: application/json

{
  "email": "user@example.com",
  "role": "member"
}
```

#### Accept Invitation
```http
POST /teams/invitations/{token}/accept
```

#### Decline Invitation
```http
POST /teams/invitations/{token}/decline
```

#### Get Team Invitations
```http
GET /teams/{team_id}/invitations
```

### Role Management

#### Get Available Roles
```http
GET /roles
```

## 🎨 Frontend Components

### TeamManagement Component

The `TeamManagement` component provides a complete team management interface:

```tsx
import { TeamManagement } from '@/components/TeamManagement';

export default function Teams() {
  return (
    <div>
      <h1>Team Management</h1>
      <TeamManagement />
    </div>
  );
}
```

### Features:
- **Team Creation**: Create new teams with descriptions
- **Team Selection**: Switch between different teams
- **Member Management**: View, update roles, and remove members
- **User Invitations**: Send email invitations with specific roles
- **Invitation Tracking**: Monitor pending invitations
- **Role Management**: Update member roles with dropdown selection

## 🔐 Role-Based Access Control (RBAC)

### Default System Roles

#### 1. Owner
- **Description**: Team owner with full access
- **Permissions**: All permissions (`*`)
- **Can**: Everything including team deletion and ownership transfer

#### 2. Admin
- **Description**: Team administrator with most permissions
- **Permissions**:
  - `agents:create`, `agents:read`, `agents:update`, `agents:delete`
  - `tasks:create`, `tasks:read`, `tasks:update`, `tasks:delete`
  - `team:read`, `team:update`, `team:invite`, `team:manage_members`
  - `billing:read`, `billing:update`
- **Can**: Manage team members, invite users, manage resources

#### 3. Member
- **Description**: Team member with basic permissions
- **Permissions**:
  - `agents:create`, `agents:read`, `agents:update`
  - `tasks:create`, `tasks:read`, `tasks:update`
  - `team:read`
- **Can**: Create and manage their own resources, view team info

#### 4. Viewer
- **Description**: Team viewer with read-only access
- **Permissions**:
  - `agents:read`, `tasks:read`, `team:read`
- **Can**: View team resources but cannot modify

### Permission System

#### Permission Format
Permissions follow the format: `resource:action`

#### Available Resources
- **agents**: AI agents management
- **tasks**: Task management
- **team**: Team management
- **billing**: Billing and subscription management
- **users**: User management (future)

#### Available Actions
- **create**: Create new resources
- **read**: View resources
- **update**: Modify existing resources
- **delete**: Remove resources
- **invite**: Invite users to team
- **manage_members**: Manage team members

### Checking Permissions

```python
# Check if user has permission in a team
has_permission = TeamService.has_permission(
    user_id="user_id",
    team_id="team_id", 
    permission="agents:create",
    db=db
)
```

## 📧 Email Integration

### Team Invitation Emails

The system automatically sends invitation emails using the email service:

- **Template**: `team_invitation`
- **Variables**: `team_name`, `inviter_name`, `invitation_url`, `role_name`, `expires_at`
- **Expiration**: 7 days by default
- **Status Tracking**: pending, accepted, declined, expired, cancelled

### Email Template Example

```html
<!DOCTYPE html>
<html>
<head>
    <title>Team Invitation</title>
</head>
<body>
    <h1>You're invited to join {{ team_name }}!</h1>
    <p>{{ inviter_name }} has invited you to join their team as a {{ role_name }}.</p>
    <p>Click the link below to accept the invitation:</p>
    <a href="{{ invitation_url }}">Accept Invitation</a>
    <p>This invitation expires on {{ expires_at }}.</p>
</body>
</html>
```

## 🏗️ Database Schema

### Teams Table
```sql
CREATE TABLE teams (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    owner_id VARCHAR NOT NULL REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    settings JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Roles Table
```sql
CREATE TABLE roles (
    id VARCHAR PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    permissions JSON,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Team Memberships Table
```sql
CREATE TABLE team_memberships (
    id VARCHAR PRIMARY KEY,
    team_id VARCHAR NOT NULL REFERENCES teams(id),
    user_id VARCHAR NOT NULL REFERENCES users(id),
    role_id VARCHAR NOT NULL REFERENCES roles(id),
    joined_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    invited_by_id VARCHAR REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);
```

### Team Invitations Table
```sql
CREATE TABLE team_invitations (
    id VARCHAR PRIMARY KEY,
    team_id VARCHAR NOT NULL REFERENCES teams(id),
    invited_user_id VARCHAR REFERENCES users(id),
    invited_email VARCHAR NOT NULL,
    role_id VARCHAR NOT NULL REFERENCES roles(id),
    invited_by_id VARCHAR NOT NULL REFERENCES users(id),
    token VARCHAR UNIQUE NOT NULL,
    status VARCHAR DEFAULT 'pending',
    expires_at TIMESTAMP NOT NULL,
    accepted_at TIMESTAMP,
    declined_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🧪 Testing

### Test Team Creation
```python
# Create a test team
team = TeamService.create_team(
    name="Test Team",
    description="A test team",
    owner=current_user,
    db=db
)
```

### Test User Invitation
```python
# Invite a user to team
invitation = TeamService.invite_user_to_team(
    team_id="team_id",
    invited_email="user@example.com",
    role_name="member",
    invited_by=current_user,
    db=db
)
```

### Test Permission Checking
```python
# Check permissions
can_create_agents = TeamService.has_permission(
    user_id="user_id",
    team_id="team_id",
    permission="agents:create",
    db=db
)
```

## 🚀 Production Deployment

### 1. Security Considerations
- **Token Security**: Use secure random tokens for invitations
- **Permission Validation**: Always validate permissions on sensitive operations
- **Email Verification**: Verify email addresses before sending invitations
- **Rate Limiting**: Implement rate limiting for invitation endpoints

### 2. Performance Optimization
- **Database Indexing**: Add indexes on frequently queried columns
- **Caching**: Cache role permissions for better performance
- **Pagination**: Implement pagination for large team member lists

### 3. Monitoring
- **Team Activity**: Track team creation and member changes
- **Invitation Metrics**: Monitor invitation acceptance rates
- **Permission Audits**: Log permission checks for security auditing

## 🔍 Troubleshooting

### Common Issues

1. **Permission Denied Errors**:
   - Check if user is a team member
   - Verify user has the required role
   - Ensure permission is correctly defined

2. **Invitation Not Working**:
   - Check email service configuration
   - Verify invitation token is valid
   - Check invitation expiration

3. **Role Update Fails**:
   - Ensure user has `team:manage_members` permission
   - Verify role exists in database
   - Check for unique constraint violations

### Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger('team_service').setLevel(logging.DEBUG)
```

## 📚 Additional Resources

- [RBAC Best Practices](https://en.wikipedia.org/wiki/Role-based_access_control)
- [Team Management UX Patterns](https://uxdesign.cc/team-management-ux-patterns-8b8c8c8c8c8c)
- [Database Design for Teams](https://www.postgresql.org/docs/current/ddl.html)
- [Email Template Design](https://mailchimp.com/developer/transactional/templates/)
