from celery import Celery
import os
from dotenv import load_dotenv
import logging
from tasks import process_task, update_task_status
from database import get_db
from models import Task, Agent
from sqlalchemy.orm import Session

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
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

@celery_app.task(bind=True)
def process_agent_task(self, task_id: str):
    """Process a task using an AI agent"""
    try:
        logger.info(f"Starting task processing for task_id: {task_id}")
        
        # Get database session
        db = next(get_db())
        
        # Get task and agent
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            logger.error(f"Task not found: {task_id}")
            return {"status": "error", "message": "Task not found"}
        
        agent = db.query(Agent).filter(Agent.id == task.agent_id).first()
        if not agent:
            logger.error(f"Agent not found for task: {task_id}")
            return {"status": "error", "message": "Agent not found"}
        
        # Update task status to processing
        update_task_status(task_id, "processing")
        
        # Process the task with configured agent system
        from agent_config import should_use_enhanced_agent
        use_enhanced = should_use_enhanced_agent()
        result = process_task(task, agent, use_enhanced=use_enhanced)
        
        # Update task with result
        task.status = "completed"
        task.result = result
        db.commit()
        
        logger.info(f"Task completed successfully: {task_id}")
        return {"status": "completed", "result": result}
        
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {str(e)}")
        
        # Update task status to failed
        try:
            update_task_status(task_id, "failed")
        except:
            pass
            
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()

@celery_app.task
def health_check():
    """Health check task"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == '__main__':
    celery_app.start()
