# 🔄 Migration Guide: Shared Models Architecture

## Overview

This guide helps developers understand and work with the new shared models architecture that eliminates duplicate models between services.

## 🚨 Breaking Changes

### ❌ **REMOVED FILES**
- `apps/api/models.py` - **DELETED**
- `apps/api/database.py` - **DELETED**  
- `apps/agent/models.py` - **DELETED**
- `apps/agent/database.py` - **DELETED**

### ✅ **NEW FILES**
- `libs/shared/models.py` - **All 20 SQLAlchemy models**
- `libs/shared/database.py` - **Database connection & session management**
- `setup.py` - **Package configuration**

## 🔧 Import Changes

### Before (Old Pattern)
```python
# ❌ OLD - Direct imports from local files
from models import User, Agent, Task
from database import get_db, engine, Base
```

### After (New Pattern)
```python
# ✅ NEW - Import from shared package
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from libs.shared.database import get_db, engine, Base
from libs.shared.models import User, Agent, Task, # ... other models
```

## 📁 File Structure Changes

### Before
```
apps/
├── api/
│   ├── models.py          # ❌ Duplicate models
│   ├── database.py        # ❌ Duplicate database
│   └── main.py
└── agent/
    ├── models.py          # ❌ Duplicate models  
    ├── database.py        # ❌ Duplicate database
    └── worker.py
```

### After
```
libs/
└── shared/
    ├── models.py          # ✅ Single source of truth
    └── database.py        # ✅ Single database connection

apps/
├── api/
│   └── main.py            # ✅ Updated imports
└── agent/
    └── worker.py          # ✅ Updated imports
```

## 🛠️ Development Workflow

### Adding New Models
1. **Add to shared models**: Edit `libs/shared/models.py`
2. **Update relationships**: Add foreign keys and relationships
3. **Run migrations**: Use Alembic to update database schema
4. **Test both services**: Ensure API and Agent can import new model

### Modifying Existing Models
1. **Edit shared model**: Make changes in `libs/shared/models.py`
2. **Update database**: Run Alembic migrations
3. **Test services**: Verify both API and Agent still work
4. **Update documentation**: Reflect changes in API docs

### Service-Specific Logic
- **Keep business logic** in service files (`apps/api/`, `apps/agent/`)
- **Import shared models** as needed
- **Use shared database** connection
- **Maintain service boundaries**

## 🧪 Testing Changes

### Test Shared Models Import
```bash
# Test from project root
python3 -c "
import sys
sys.path.append('.')
from libs.shared.models import User, Agent, Task
from libs.shared.database import get_db, engine, Base
print('✅ Shared models work!')
"
```

### Test Service Imports
```bash
# Test API service
cd apps/api && python3 -c "
import sys, os
sys.path.append(os.path.join(os.getcwd(), '..', '..'))
from libs.shared.models import User, Agent, Task
print('✅ API service imports work!')
"

# Test Agent service  
cd apps/agent && python3 -c "
import sys, os
sys.path.append(os.path.join(os.getcwd(), '..', '..'))
from libs.shared.models import User, Agent, Task
print('✅ Agent service imports work!')
"
```

## 🚀 Deployment Considerations

### Development
- **No changes needed** - Path manipulation handles imports
- **Both services** can import from shared package
- **Database migrations** work as before

### Production
- **Ensure `libs/` directory** is included in deployment
- **Both services** need access to shared models
- **Consider installing** as proper Python package

## 📋 Available Models

| Category | Models | Description |
|----------|--------|-------------|
| **Core** | User, Agent, Task, ApiCall | Basic application models |
| **Stripe** | StripeCustomer, Subscription, Payment, WebhookEvent | Payment processing |
| **Email** | EmailTemplate, EmailNotification, EmailPreference | Email system |
| **Teams** | Team, Role, TeamMembership, TeamInvitation, Permission | Team management |
| **Files** | File, FileShare, FileUploadSession, FileAccessLog | File storage |

## 🔍 Troubleshooting

### Import Errors
```python
# ❌ Error: ModuleNotFoundError: No module named 'libs'
# ✅ Solution: Add project root to Python path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
```

### Database Connection Issues
```python
# ❌ Error: Database connection failed
# ✅ Solution: Check DATABASE_URL in .env file
# Ensure both services use same database
```

### Model Relationship Errors
```python
# ❌ Error: Relationship not found
# ✅ Solution: Check model relationships in libs/shared/models.py
# Ensure foreign keys are properly defined
```

## 📚 Related Documentation

- [Shared Models Architecture](SHARED_MODELS_ARCHITECTURE.md) - Complete architecture guide
- [API Documentation](apps/api/README.md) - API service documentation  
- [Agent Documentation](apps/agent/README.md) - Agent service documentation
- [Main README](README.md) - Project overview

## 🎯 Benefits Achieved

✅ **Single Source of Truth** - All models in one place  
✅ **No Code Duplication** - DRY principle followed  
✅ **Easy Maintenance** - Change models once, affects all services  
✅ **Clean Architecture** - Clear separation of concerns  
✅ **Deployment Ready** - Both services import from shared package  

---

**This migration provides a solid foundation for scalable microservices development!** 🚀
