# Agent Service (Celery Worker)

Background task processing service using Celery with AI agent capabilities and OpenAI integration.

## 🚀 Features

- **Celery Workers** for background task processing
- **OpenAI Integration** with LangChain
- **Task Queue Management** with Redis
- **Performance Monitoring** and metrics
- **Error Handling** with retry logic
- **Database Integration** for task tracking

## 🛠️ Development

### Prerequisites

- Python 3.11+
- Redis server
- PostgreSQL database
- OpenAI API key

### Setup

1. **Install dependencies**:
   ```bash
   cd apps/agent
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start Redis server**:
   ```bash
   redis-server
   ```

4. **Start Celery worker**:
   ```bash
   celery -A worker worker --loglevel=info
   ```

## 📁 Project Structure

```
apps/agent/
├── worker.py           # Celery application and tasks
├── tasks.py            # Task processing logic
├── database.py         # Database configuration
├── models.py           # Database models
├── monitoring.py       # Performance monitoring
└── requirements.txt    # Python dependencies
```

## 🤖 AI Agent Capabilities

### Task Processing

The agent service processes various types of tasks:

- **Natural Language Processing**: Text analysis and generation
- **Decision Making**: Context-based decision processing
- **API Integration**: External service interactions
- **Data Processing**: Structured data manipulation

### OpenAI Integration

```python
# Example agent task processing
def process_task(task: Task, agent: Agent) -> str:
    llm = OpenAI(temperature=0.7, max_tokens=1000)
    prompt_template = PromptTemplate(
        input_variables=["task_title", "task_description", "agent_prompt"],
        template="Agent prompt: {agent_prompt}\nTask: {task_title}\nDescription: {task_description}"
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)
    result = chain.run(
        task_title=task.title,
        task_description=task.description,
        agent_prompt=agent.prompt
    )
    return result
```

## 🔧 Celery Configuration

### Worker Configuration

```python
celery_app = Celery(
    'agentic_worker',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)
```

### Task Definition

```python
@celery_app.task(bind=True)
def process_agent_task(self, task_id: str):
    """Process a task using an AI agent"""
    try:
        # Get task and agent from database
        # Process task with AI
        # Update task status
        return {"status": "completed", "result": result}
    except Exception as e:
        # Handle errors and update status
        return {"status": "error", "message": str(e)}
```

## 📊 Monitoring & Metrics

### Task Execution Monitoring

```python
@monitor_task_execution("agent_task")
def process_agent_task(task_id: str):
    # Task processing logic
    pass
```

### Performance Metrics

- **Task Duration**: Execution time tracking
- **Success Rate**: Task completion statistics
- **Error Rate**: Failure tracking and analysis
- **Queue Length**: Pending task monitoring

### Logging

```python
logger.info(f"Starting task processing for task_id: {task_id}")
logger.info(f"Task completed successfully: {task_id}")
logger.error(f"Task failed: {task_id} - {error_message}")
```

## 🗄️ Database Integration

### Task Status Updates

```python
def update_task_status(task_id: str, status: str):
    """Update task status in database"""
    db = next(get_db())
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = status
        db.commit()
```

### Task Creation

```python
def create_agent_task(task_data: Dict[str, Any]) -> str:
    """Create a new agent task and queue it for processing"""
    db = next(get_db())
    task = Task(
        title=task_data["title"],
        description=task_data.get("description"),
        agent_id=task_data["agent_id"],
        user_id=task_data["user_id"],
        status="pending"
    )
    db.add(task)
    db.commit()
    
    # Queue task for processing
    process_agent_task.delay(task.id)
    return task.id
```

## 🔧 Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agentic_microsaas

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Celery Settings

```python
# Task routing
task_routes = {
    'worker.process_agent_task': {'queue': 'agent_tasks'},
    'worker.health_check': {'queue': 'system'},
}

# Task serialization
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'

# Time limits
task_time_limit = 30 * 60  # 30 minutes
task_soft_time_limit = 25 * 60  # 25 minutes
```

## 🚀 Deployment

### Local Development

```bash
# Start Celery worker
celery -A worker worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A worker beat --loglevel=info

# Start Celery flower (monitoring)
celery -A worker flower
```

### Production

```bash
# Start multiple workers
celery -A worker worker --loglevel=info --concurrency=4

# Start with supervisor
supervisord -c supervisord.conf
```

### Docker

```bash
docker build -t agent-service .
docker run agent-service
```

## 🧪 Testing

```bash
# Run tests
pytest

# Test specific task
python -c "from worker import process_agent_task; process_agent_task.delay('test_task_id')"
```

## 📈 Performance Optimization

### Worker Scaling

- **Horizontal Scaling**: Multiple worker processes
- **Vertical Scaling**: Increased worker concurrency
- **Queue Partitioning**: Separate queues for different task types

### Task Optimization

- **Batch Processing**: Process multiple tasks together
- **Caching**: Cache frequently used data
- **Connection Pooling**: Optimize database connections

## 🔄 Task Lifecycle

1. **Task Creation**: Task created in database with "pending" status
2. **Queue Submission**: Task queued in Redis for processing
3. **Worker Pickup**: Celery worker picks up task from queue
4. **Processing**: AI agent processes the task
5. **Status Update**: Task status updated to "completed" or "failed"
6. **Result Storage**: Task result stored in database

## 🐛 Error Handling

### Retry Logic

```python
@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def process_agent_task(self, task_id: str):
    try:
        # Task processing
        pass
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### Error Recovery

- **Automatic Retries**: Failed tasks are automatically retried
- **Dead Letter Queue**: Permanently failed tasks moved to DLQ
- **Error Notifications**: Alerts for critical failures

## 🔍 Monitoring Tools

### Celery Flower

Web-based monitoring tool for Celery:

```bash
celery -A worker flower
# Access at http://localhost:5555
```

### Custom Monitoring

```python
# Task execution metrics
def log_agent_performance(agent_id: str, task_count: int, avg_duration: float):
    logger.info(f"Agent performance - ID: {agent_id}, Tasks: {task_count}, Avg Duration: {avg_duration}ms")
```

## 🔒 Security

- **API Key Management**: Secure OpenAI API key handling
- **Database Security**: Connection encryption and access control
- **Task Isolation**: Worker process isolation
- **Input Validation**: Task data validation and sanitization
