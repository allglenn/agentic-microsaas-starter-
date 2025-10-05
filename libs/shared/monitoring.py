"""
Shared Monitoring Utilities
Task execution monitoring, API call monitoring, performance metrics, and health status checking
"""
import time
import functools
import asyncio
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .database import get_db
from .models import ApiCall, Task, User
from .logging_config import get_shared_logger
from .utils import timing_decorator

# Optional import for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Initialize logger
logger = get_shared_logger()

class TaskMonitor:
    """Monitor task execution with decorators and metrics collection"""
    
    @staticmethod
    def monitor_task_execution(task_name: str, user_id: Optional[str] = None):
        """Decorator to monitor task execution with metrics"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"
                error_message = None
                
                try:
                    logger.info(f"Starting task execution: {task_name}", task_name=task_name, user_id=user_id)
                    result = func(*args, **kwargs)
                    logger.info(f"Task execution completed: {task_name}", task_name=task_name, user_id=user_id)
                    return result
                    
                except Exception as e:
                    status = "failed"
                    error_message = str(e)
                    logger.error(f"Task execution failed: {task_name}", task_name=task_name, user_id=user_id, error=str(e))
                    raise
                    
                finally:
                    duration_ms = int((time.time() - start_time) * 1000)
                    TaskMonitor._log_task_metrics(task_name, status, duration_ms, user_id, error_message)
            
            return wrapper
        return decorator
    
    @staticmethod
    def monitor_async_task_execution(task_name: str, user_id: Optional[str] = None):
        """Decorator to monitor async task execution with metrics"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                status = "success"
                error_message = None
                
                try:
                    logger.info(f"Starting async task execution: {task_name}", task_name=task_name, user_id=user_id)
                    result = await func(*args, **kwargs)
                    logger.info(f"Async task execution completed: {task_name}", task_name=task_name, user_id=user_id)
                    return result
                    
                except Exception as e:
                    status = "failed"
                    error_message = str(e)
                    logger.error(f"Async task execution failed: {task_name}", task_name=task_name, user_id=user_id, error=str(e))
                    raise
                    
                finally:
                    duration_ms = int((time.time() - start_time) * 1000)
                    TaskMonitor._log_task_metrics(task_name, status, duration_ms, user_id, error_message)
            
            return wrapper
        return decorator
    
    @staticmethod
    def _log_task_metrics(task_name: str, status: str, duration_ms: int, user_id: Optional[str], error_message: Optional[str]):
        """Log task metrics to database"""
        try:
            db = next(get_db())
            
            # Create task record if it doesn't exist
            task = db.query(Task).filter(Task.title == task_name).first()
            if not task:
                task = Task(
                    title=task_name,
                    description=f"Monitored task: {task_name}",
                    status=status,
                    user_id=user_id or "system"
                )
                db.add(task)
            else:
                task.status = status
                task.updated_at = datetime.utcnow()
            
            # Update task result
            if error_message:
                task.result = f"Error: {error_message}"
            else:
                task.result = f"Completed in {duration_ms}ms"
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log task metrics: {e}")

class APIMonitor:
    """Monitor API calls with metrics collection and performance tracking"""
    
    @staticmethod
    def monitor_api_call(endpoint: str, method: str, user_id: Optional[str] = None):
        """Decorator to monitor API calls with metrics"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                status_code = 200
                error_message = None
                
                try:
                    logger.info(f"API call started: {method} {endpoint}", endpoint=endpoint, method=method, user_id=user_id)
                    result = func(*args, **kwargs)
                    logger.info(f"API call completed: {method} {endpoint}", endpoint=endpoint, method=method, user_id=user_id)
                    return result
                    
                except Exception as e:
                    status_code = 500
                    error_message = str(e)
                    logger.error(f"API call failed: {method} {endpoint}", endpoint=endpoint, method=method, user_id=user_id, error=str(e))
                    raise
                    
                finally:
                    duration_ms = int((time.time() - start_time) * 1000)
                    APIMonitor._log_api_metrics(endpoint, method, status_code, duration_ms, user_id, error_message)
            
            return wrapper
        return decorator
    
    @staticmethod
    def monitor_async_api_call(endpoint: str, method: str, user_id: Optional[str] = None):
        """Decorator to monitor async API calls with metrics"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                status_code = 200
                error_message = None
                
                try:
                    logger.info(f"Async API call started: {method} {endpoint}", endpoint=endpoint, method=method, user_id=user_id)
                    result = await func(*args, **kwargs)
                    logger.info(f"Async API call completed: {method} {endpoint}", endpoint=endpoint, method=method, user_id=user_id)
                    return result
                    
                except Exception as e:
                    status_code = 500
                    error_message = str(e)
                    logger.error(f"Async API call failed: {method} {endpoint}", endpoint=endpoint, method=method, user_id=user_id, error=str(e))
                    raise
                    
                finally:
                    duration_ms = int((time.time() - start_time) * 1000)
                    APIMonitor._log_api_metrics(endpoint, method, status_code, duration_ms, user_id, error_message)
            
            return wrapper
        return decorator
    
    @staticmethod
    def _log_api_metrics(endpoint: str, method: str, status_code: int, duration_ms: int, user_id: Optional[str], error_message: Optional[str]):
        """Log API metrics to database"""
        try:
            db = next(get_db())
            
            api_call = ApiCall(
                endpoint=endpoint,
                method=method,
                status=status_code,
                duration=duration_ms,
                user_id=user_id
            )
            
            db.add(api_call)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log API metrics: {e}")

class PerformanceMonitor:
    """Monitor performance metrics and system health"""
    
    @staticmethod
    def get_performance_metrics(time_range_hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics from database"""
        try:
            db = next(get_db())
            since = datetime.utcnow() - timedelta(hours=time_range_hours)
            
            # API call metrics
            api_calls = db.query(ApiCall).filter(ApiCall.created_at >= since).all()
            
            total_api_calls = len(api_calls)
            successful_calls = len([call for call in api_calls if 200 <= call.status < 400])
            failed_calls = total_api_calls - successful_calls
            
            avg_response_time = sum(call.duration for call in api_calls) / total_api_calls if total_api_calls > 0 else 0
            
            # Task metrics
            tasks = db.query(Task).filter(Task.created_at >= since).all()
            
            total_tasks = len(tasks)
            completed_tasks = len([task for task in tasks if task.status == "completed"])
            failed_tasks = len([task for task in tasks if task.status == "failed"])
            
            # User metrics
            active_users = db.query(User).filter(User.updated_at >= since).count()
            
            return {
                "time_range_hours": time_range_hours,
                "api_calls": {
                    "total": total_api_calls,
                    "successful": successful_calls,
                    "failed": failed_calls,
                    "success_rate": (successful_calls / total_api_calls * 100) if total_api_calls > 0 else 0,
                    "avg_response_time_ms": avg_response_time
                },
                "tasks": {
                    "total": total_tasks,
                    "completed": completed_tasks,
                    "failed": failed_tasks,
                    "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                },
                "users": {
                    "active": active_users
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}
    
    @staticmethod
    def get_health_status() -> Dict[str, Any]:
        """Get system health status"""
        try:
            db = next(get_db())
            
            # Check database connection
            db.execute("SELECT 1")
            database_status = "healthy"
            
        except Exception as e:
            database_status = "unhealthy"
            logger.error(f"Database health check failed: {e}")
        
        # Check system resources (basic)
        if PSUTIL_AVAILABLE:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
        else:
            cpu_percent = 0
            memory_percent = 0
            disk_percent = 0
        
        # Determine overall health
        overall_health = "healthy"
        if database_status != "healthy":
            overall_health = "unhealthy"
        elif cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
            overall_health = "degraded"
        
        return {
            "status": overall_health,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": database_status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent
            }
        }
    
    @staticmethod
    def cleanup_old_metrics(days_to_keep: int = 30):
        """Clean up old metrics data"""
        try:
            db = next(get_db())
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Delete old API calls
            old_api_calls = db.query(ApiCall).filter(ApiCall.created_at < cutoff_date).count()
            db.query(ApiCall).filter(ApiCall.created_at < cutoff_date).delete()
            
            # Delete old completed tasks
            old_tasks = db.query(Task).filter(
                Task.created_at < cutoff_date,
                Task.status.in_(["completed", "failed"])
            ).count()
            db.query(Task).filter(
                Task.created_at < cutoff_date,
                Task.status.in_(["completed", "failed"])
            ).delete()
            
            db.commit()
            
            logger.info(f"Cleaned up {old_api_calls} old API calls and {old_tasks} old tasks")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")

class MetricsCollector:
    """Collect and aggregate metrics from various sources"""
    
    @staticmethod
    def collect_user_metrics(user_id: str, time_range_hours: int = 24) -> Dict[str, Any]:
        """Collect metrics for a specific user"""
        try:
            db = next(get_db())
            since = datetime.utcnow() - timedelta(hours=time_range_hours)
            
            # User's API calls
            api_calls = db.query(ApiCall).filter(
                ApiCall.user_id == user_id,
                ApiCall.created_at >= since
            ).all()
            
            # User's tasks
            tasks = db.query(Task).filter(
                Task.user_id == user_id,
                Task.created_at >= since
            ).all()
            
            return {
                "user_id": user_id,
                "time_range_hours": time_range_hours,
                "api_calls": {
                    "total": len(api_calls),
                    "avg_duration": sum(call.duration for call in api_calls) / len(api_calls) if api_calls else 0
                },
                "tasks": {
                    "total": len(tasks),
                    "completed": len([task for task in tasks if task.status == "completed"]),
                    "failed": len([task for task in tasks if task.status == "failed"])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to collect user metrics: {e}")
            return {}
    
    @staticmethod
    def collect_system_metrics() -> Dict[str, Any]:
        """Collect system-wide metrics"""
        try:
            db = next(get_db())
            
            # Total users
            total_users = db.query(User).count()
            
            # Recent activity (last 24 hours)
            since = datetime.utcnow() - timedelta(hours=24)
            recent_api_calls = db.query(ApiCall).filter(ApiCall.created_at >= since).count()
            recent_tasks = db.query(Task).filter(Task.created_at >= since).count()
            
            return {
                "total_users": total_users,
                "recent_activity": {
                    "api_calls_24h": recent_api_calls,
                    "tasks_24h": recent_tasks
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}

# Convenience functions
def monitor_task_execution(task_name: str, user_id: Optional[str] = None):
    """Monitor task execution with decorator"""
    return TaskMonitor.monitor_task_execution(task_name, user_id)

def monitor_async_task_execution(task_name: str, user_id: Optional[str] = None):
    """Monitor async task execution with decorator"""
    return TaskMonitor.monitor_async_task_execution(task_name, user_id)

def monitor_api_call(endpoint: str, method: str, user_id: Optional[str] = None):
    """Monitor API call with decorator"""
    return APIMonitor.monitor_api_call(endpoint, method, user_id)

def monitor_async_api_call(endpoint: str, method: str, user_id: Optional[str] = None):
    """Monitor async API call with decorator"""
    return APIMonitor.monitor_async_api_call(endpoint, method, user_id)

def get_performance_metrics(time_range_hours: int = 24) -> Dict[str, Any]:
    """Get performance metrics"""
    return PerformanceMonitor.get_performance_metrics(time_range_hours)

def get_health_status() -> Dict[str, Any]:
    """Get system health status"""
    return PerformanceMonitor.get_health_status()

def cleanup_old_metrics(days_to_keep: int = 30):
    """Clean up old metrics data"""
    return PerformanceMonitor.cleanup_old_metrics(days_to_keep)

def collect_user_metrics(user_id: str, time_range_hours: int = 24) -> Dict[str, Any]:
    """Collect metrics for a specific user"""
    return MetricsCollector.collect_user_metrics(user_id, time_range_hours)

def collect_system_metrics() -> Dict[str, Any]:
    """Collect system-wide metrics"""
    return MetricsCollector.collect_system_metrics()
