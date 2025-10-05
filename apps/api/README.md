# API Service (FastAPI)

High-performance REST API built with FastAPI, featuring async support, authentication, and comprehensive monitoring.

## 🚀 Features

- **FastAPI** with async/await support
- **Shared Models Architecture** - Uses `libs/shared/models.py` for all database models
- **SQLAlchemy** ORM with PostgreSQL
- **JWT Authentication** with Bearer tokens
- **Automatic API Documentation** (Swagger/OpenAPI)
- **Request/Response Logging** with performance metrics
- **CORS Support** for cross-origin requests
- **Input Validation** with Pydantic models
- **SaaS Features** - Stripe payments, email notifications, team management, file storage

## 🏗️ Shared Models Architecture

This API service uses the **shared models architecture** where all database models are defined in `libs/shared/models.py`:

```python
# Import pattern used in all API files
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from libs.shared.database import get_db, engine, Base
from libs.shared.models import User, Agent, Task, StripeCustomer, Subscription, # ... etc
```

### Available Models (20 total)
- **Core**: User, Agent, Task, ApiCall
- **Stripe**: StripeCustomer, Subscription, Payment, WebhookEvent  
- **Email**: EmailTemplate, EmailNotification, EmailPreference
- **Teams**: Team, Role, TeamMembership, TeamInvitation, Permission
- **Files**: File, FileShare, FileUploadSession, FileAccessLog

> **📋 [Complete Shared Models Documentation](../../SHARED_MODELS_ARCHITECTURE.md)**  
> **🏗️ [Shared Modules Architecture](../../SHARED_MODULES_ARCHITECTURE.md)** - Configuration, Authentication, and Agent modules

## 🛠️ Development

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Redis (for caching)

### Setup

1. **Install dependencies**:
   ```bash
   cd apps/api
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

4. **Start development server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at http://localhost:8000

## 📁 Project Structure

```
apps/api/
├── main.py              # FastAPI application
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── middleware.py        # Custom middleware
├── logging_config.py    # Logging configuration
└── requirements.txt     # Python dependencies
```

## 🧪 API Endpoints

### Authentication

- `POST /users` - Create a new user
- `GET /users/me` - Get current user information

### Agents

- `POST /agents` - Create a new AI agent
- `GET /agents` - List user's agents
- `GET /agents/{agent_id}` - Get specific agent details

### Tasks

- `POST /tasks` - Create a new task
- `GET /tasks` - List user's tasks
- `GET /tasks/{task_id}` - Get specific task details

### Analytics

- `GET /analytics/api-calls` - Get API usage analytics

### Health Check

- `GET /` - API status
- `GET /health` - Health check endpoint

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Token Generation**: Tokens are generated with user information
2. **Token Validation**: Middleware validates tokens on protected routes
3. **User Context**: Current user is available in route handlers

### Example Usage

```python
# Protected route
@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id}
```

## 🗄️ Database Models

### User
- `id`: Unique identifier
- `email`: User email address
- `name`: User display name
- `created_at`: Account creation timestamp

### Agent
- `id`: Unique identifier
- `name`: Agent name
- `description`: Agent description
- `prompt`: AI prompt template
- `is_active`: Active status
- `user_id`: Owner user ID

### Task
- `id`: Unique identifier
- `title`: Task title
- `description`: Task description
- `status`: Task status (pending, processing, completed, failed)
- `result`: Task result
- `agent_id`: Associated agent ID
- `user_id`: Owner user ID

### ApiCall
- `id`: Unique identifier
- `endpoint`: API endpoint
- `method`: HTTP method
- `status`: Response status code
- `duration`: Request duration in milliseconds
- `user_id`: Associated user ID

## 📊 Monitoring & Logging

### Request Logging

All API requests are automatically logged with:
- Request method and endpoint
- Response status code
- Request duration
- User information (if authenticated)

### Performance Metrics

- Response time tracking
- Error rate monitoring
- API usage analytics
- Database query performance

### Log Format

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "message": "GET /api/tasks - 200 - 150ms",
  "endpoint": "/api/tasks",
  "method": "GET",
  "status": 200,
  "duration": 150
}
```

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agentic_microsaas

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
API_SECRET_KEY=your_secret_key_here

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Environment
ENVIRONMENT=development
```

### Database Configuration

```python
# database.py
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## 🚀 Deployment

### Local Development

```bash
uvicorn main:app --reload
```

### Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker

```bash
docker build -t api-service .
docker run -p 8000:8000 api-service
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_users.py
```

## 📚 API Documentation

The API automatically generates interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **CORS Protection**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic model validation
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **Rate Limiting**: Configurable request rate limits

## 📈 Performance

- **Async/Await**: Non-blocking request handling
- **Connection Pooling**: Database connection optimization
- **Response Caching**: Redis-based response caching
- **Request Middleware**: Optimized request processing pipeline

## 🐛 Error Handling

The API includes comprehensive error handling:

- **HTTP Exceptions**: Standard HTTP status codes
- **Validation Errors**: Detailed input validation messages
- **Database Errors**: Graceful database error handling
- **Custom Exceptions**: Application-specific error types

## 🔄 Background Tasks

Integration with Celery for background task processing:

- Task creation and queuing
- Status tracking
- Result retrieval
- Error handling and retries
