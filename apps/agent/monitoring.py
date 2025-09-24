import logging
import time
from functools import wraps
from typing import Callable, Any
from database import get_db
from models import ApiCall
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def monitor_task_execution(task_name: str):
    """Decorator to monitor task execution with metrics"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            task_id = kwargs.get('task_id', 'unknown')
            
            logger.info(f"Starting task execution: {task_name} (ID: {task_id})")
            
            try:
                result = func(*args, **kwargs)
                duration = int((time.time() - start_time) * 1000)
                
                logger.info(f"Task completed successfully: {task_name} (ID: {task_id}) - {duration}ms")
                
                # Log success metrics
                _log_task_metrics(task_name, "success", duration, task_id)
                
                return result
                
            except Exception as e:
                duration = int((time.time() - start_time) * 1000)
                
                logger.error(f"Task failed: {task_name} (ID: {task_id}) - {str(e)} - {duration}ms")
                
                # Log failure metrics
                _log_task_metrics(task_name, "failed", duration, task_id, str(e))
                
                raise
                
        return wrapper
    return decorator

def _log_task_metrics(task_name: str, status: str, duration: int, task_id: str, error: str = None):
    """Log task execution metrics to database"""
    try:
        db = next(get_db())
        
        # Create a mock API call record for task metrics
        api_call = ApiCall(
            endpoint=f"/tasks/{task_name}",
            method="POST",
            status=200 if status == "success" else 500,
            duration=duration
        )
        
        db.add(api_call)
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to log task metrics: {e}")
    finally:
        db.close()

def log_agent_performance(agent_id: str, task_count: int, avg_duration: float):
    """Log agent performance metrics"""
    logger.info(f"Agent performance - ID: {agent_id}, Tasks: {task_count}, Avg Duration: {avg_duration}ms")
    
    # Here you could send metrics to external monitoring services
    # like Prometheus, DataDog, or Google Cloud Monitoring
