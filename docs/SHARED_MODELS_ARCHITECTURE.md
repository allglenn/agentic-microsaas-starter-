# 🏗️ Shared Models Architecture

## Overview

This project implements a **shared models architecture** to eliminate code duplication between services and maintain a single source of truth for all database models and connections.

## 🎯 Problem Solved

**Before**: Each service (`apps/api/`, `apps/agent/`) had duplicate model and database files:
- `apps/api/models.py` ❌
- `apps/api/database.py` ❌  
- `apps/agent/models.py` ❌
- `apps/agent/database.py` ❌

**After**: Single shared location for all models and database logic:
- `libs/shared/models.py` ✅
- `libs/shared/database.py` ✅

## 📁 Directory Structure

```
agentic-microsaas-starter-full-personalized/
├── libs/                           # Shared libraries
│   ├── __init__.py
│   └── shared/                     # Shared models and database
│       ├── __init__.py
│       ├── database.py             # Database connection & session
│       └── models.py               # All SQLAlchemy models
├── apps/
│   ├── api/                        # FastAPI service
│   │   ├── main.py                 # Updated imports
│   │   ├── stripe_service.py       # Updated imports
│   │   ├── email_service.py        # Updated imports
│   │   ├── team_service.py         # Updated imports
│   │   ├── storage_service.py      # Updated imports
│   │   └── middleware.py           # Updated imports
│   └── agent/                      # Celery agent service
│       ├── worker.py               # Updated imports
│       ├── tasks.py                # Updated imports
│       ├── simple_agent.py         # Updated imports
│       ├── enhanced_agents.py      # Updated imports
│       ├── monitoring.py           # Updated imports
│       └── agent_config.py         # Updated imports
└── setup.py                        # Package configuration
```

## 🔧 Implementation Details

### 1. Shared Database Connection (`libs/shared/database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/agentic_microsaas")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2. Shared Models (`libs/shared/models.py`)

Contains **20 SQLAlchemy models** organized by feature:

#### Core Models
- `User` - User accounts and authentication
- `Agent` - AI agents configuration
- `Task` - Task execution tracking
- `ApiCall` - API usage monitoring

#### Stripe Models
- `StripeCustomer` - Stripe customer data
- `Subscription` - Subscription management
- `Payment` - Payment tracking
- `WebhookEvent` - Stripe webhook events

#### Email Models
- `EmailTemplate` - Email templates
- `EmailNotification` - Email sending logs
- `EmailPreference` - User email preferences

#### Team Management Models
- `Team` - Team/organization data
- `Role` - Role definitions
- `TeamMembership` - User-team relationships
- `TeamInvitation` - Team invitation system
- `Permission` - Permission definitions

#### File Storage Models
- `File` - File metadata
- `FileShare` - File sharing permissions
- `FileUploadSession` - Chunked upload sessions
- `FileAccessLog` - File access tracking

### 3. Service Import Pattern

Each service uses this pattern to import shared models:

```python
import sys
import os

# Add project root to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from libs.shared.database import get_db, engine, Base
from libs.shared.models import User, Agent, Task, # ... other models
```

## 🚀 Benefits

### ✅ **Single Source of Truth**
- All models defined in one location
- Changes propagate to all services automatically
- No risk of model drift between services

### ✅ **DRY Principle**
- Eliminated duplicate model definitions
- Reduced codebase size by ~50%
- Easier maintenance and updates

### ✅ **Clean Architecture**
- Clear separation between shared libraries and services
- Services focus on business logic, not model definitions
- Better organization and discoverability

### ✅ **Deployment Ready**
- Both services can import from shared package
- Consistent model definitions across environments
- Simplified deployment and testing

## 🔄 Migration Process

The migration was completed in 8 steps:

1. **🏗️ Created libs directory structure**
2. **📁 Moved database connection to shared**
3. **🗃️ Moved all models to shared package**
4. **📦 Created setup.py for package installation**
5. **🔄 Updated API service imports**
6. **🔄 Updated Agent service imports**
7. **🗑️ Cleaned up duplicate files**
8. **🧪 Tested the new shared structure**

## 🧪 Testing

### Import Test
```bash
# Test shared models import
python3 -c "
import sys
sys.path.append('.')
from libs.shared.models import User, Agent, Task
from libs.shared.database import get_db, engine, Base
print('✅ Shared models import successfully!')
"
```

### Service Import Test
```bash
# Test API service imports
cd apps/api && python3 -c "
import sys, os
sys.path.append(os.path.join(os.getcwd(), '..', '..'))
from libs.shared.models import User, Agent, Task
print('✅ API service can import shared models!')
"

# Test Agent service imports  
cd apps/agent && python3 -c "
import sys, os
sys.path.append(os.path.join(os.getcwd(), '..', '..'))
from libs.shared.models import User, Agent, Task
print('✅ Agent service can import shared models!')
"
```

## 📋 Available Models

| Category | Models | Count |
|----------|--------|-------|
| **Core** | User, Agent, Task, ApiCall | 4 |
| **Stripe** | StripeCustomer, Subscription, Payment, WebhookEvent | 4 |
| **Email** | EmailTemplate, EmailNotification, EmailPreference | 3 |
| **Teams** | Team, Role, TeamMembership, TeamInvitation, Permission | 5 |
| **Files** | File, FileShare, FileUploadSession, FileAccessLog | 4 |
| **Total** | | **20** |

## 🔧 Development Workflow

### Adding New Models
1. Add model to `libs/shared/models.py`
2. Update relationships in existing models if needed
3. Run database migrations
4. Both services automatically have access to new model

### Updating Existing Models
1. Modify model in `libs/shared/models.py`
2. Changes automatically available to both services
3. Update database schema as needed
4. Test both services to ensure compatibility

### Service-Specific Logic
- Keep business logic in service files
- Import shared models as needed
- Use shared database connection
- Maintain service boundaries

## 🚨 Important Notes

### Path Management
- Each service adds project root to Python path
- This allows importing from `libs.shared`
- No need to install as package in development

### Database Migrations
- Use Alembic for database schema changes
- Run migrations from project root
- Both services share the same database schema

### Deployment Considerations
- Ensure `libs/` directory is included in deployment
- Both services need access to shared models
- Consider installing as package in production

## 🎯 Future Enhancements

- **Package Installation**: Install shared models as proper Python package
- **Version Management**: Track model versions and changes
- **API Documentation**: Auto-generate model documentation
- **Validation**: Add model validation and constraints
- **Testing**: Comprehensive model testing suite

---

## 📚 Related Documentation

- [API Documentation](apps/api/README.md)
- [Agent Documentation](apps/agent/README.md)
- [Deployment Guide](infra/README.md)
- [Database Schema](prisma/schema.prisma)

This shared models architecture provides a solid foundation for scalable microservices development! 🚀
