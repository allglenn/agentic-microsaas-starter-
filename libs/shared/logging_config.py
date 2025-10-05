"""
Shared Logging Configuration
Standardized logging across all services with structured logging for production
"""
import logging
import sys
import os
from typing import Optional, Dict, Any
from datetime import datetime
import json
from .config import get_api_config

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)

class ServiceLogger:
    """Service-specific logger with standardized configuration"""
    
    def __init__(self, service_name: str, log_level: str = "INFO"):
        self.service_name = service_name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logger with appropriate handlers and formatters"""
        logger = logging.getLogger(f"agentic_microsaas.{self.service_name}")
        logger.setLevel(self.log_level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        # Use structured formatter for production, simple formatter for development
        if os.getenv("ENVIRONMENT", "development") == "production":
            console_handler.setFormatter(StructuredFormatter())
        else:
            console_formatter = logging.Formatter(
                f'%(asctime)s - {self.service_name} - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
        
        logger.addHandler(console_handler)
        
        # File handler for persistent logging
        log_dir = os.getenv("LOG_DIR", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f"{self.service_name}.log")
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)
        
        # Prevent duplicate logs
        logger.propagate = False
        
        return logger
    
    def info(self, message: str, **kwargs):
        """Log info message with extra fields"""
        self.logger.info(message, extra={'extra_fields': kwargs})
    
    def warning(self, message: str, **kwargs):
        """Log warning message with extra fields"""
        self.logger.warning(message, extra={'extra_fields': kwargs})
    
    def error(self, message: str, **kwargs):
        """Log error message with extra fields"""
        self.logger.error(message, extra={'extra_fields': kwargs})
    
    def debug(self, message: str, **kwargs):
        """Log debug message with extra fields"""
        self.logger.debug(message, extra={'extra_fields': kwargs})
    
    def critical(self, message: str, **kwargs):
        """Log critical message with extra fields"""
        self.logger.critical(message, extra={'extra_fields': kwargs})
    
    def log_api_call(self, endpoint: str, method: str, status_code: int, duration_ms: int, user_id: Optional[str] = None):
        """Log API call with structured data"""
        self.info(
            f"API call: {method} {endpoint}",
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            duration_ms=duration_ms,
            user_id=user_id,
            event_type="api_call"
        )
    
    def log_task_execution(self, task_name: str, status: str, duration_ms: int, user_id: Optional[str] = None, error: Optional[str] = None):
        """Log task execution with structured data"""
        log_data = {
            "task_name": task_name,
            "status": status,
            "duration_ms": duration_ms,
            "user_id": user_id,
            "event_type": "task_execution"
        }
        
        if error:
            log_data["error"] = error
            self.error(f"Task execution failed: {task_name}", **log_data)
        else:
            self.info(f"Task execution completed: {task_name}", **log_data)
    
    def log_agent_interaction(self, agent_id: str, user_id: str, interaction_type: str, duration_ms: int, tokens_used: Optional[int] = None):
        """Log agent interaction with structured data"""
        self.info(
            f"Agent interaction: {interaction_type}",
            agent_id=agent_id,
            user_id=user_id,
            interaction_type=interaction_type,
            duration_ms=duration_ms,
            tokens_used=tokens_used,
            event_type="agent_interaction"
        )
    
    def log_database_operation(self, operation: str, table: str, duration_ms: int, user_id: Optional[str] = None):
        """Log database operation with structured data"""
        self.info(
            f"Database operation: {operation} on {table}",
            operation=operation,
            table=table,
            duration_ms=duration_ms,
            user_id=user_id,
            event_type="database_operation"
        )
    
    def log_security_event(self, event_type: str, user_id: Optional[str] = None, ip_address: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Log security event with structured data"""
        log_data = {
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "security_event": True
        }
        
        if details:
            log_data.update(details)
        
        self.warning(f"Security event: {event_type}", **log_data)

class LoggingManager:
    """Centralized logging management for all services"""
    
    def __init__(self):
        self.loggers = {}
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """Setup root logger configuration"""
        root_logger = logging.getLogger("agentic_microsaas")
        root_logger.setLevel(logging.INFO)
        
        # Prevent duplicate logs from propagating
        root_logger.propagate = False
    
    def get_logger(self, service_name: str, log_level: str = "INFO") -> ServiceLogger:
        """Get or create service-specific logger"""
        if service_name not in self.loggers:
            self.loggers[service_name] = ServiceLogger(service_name, log_level)
        return self.loggers[service_name]
    
    def get_api_logger(self) -> ServiceLogger:
        """Get API service logger"""
        return self.get_logger("api", os.getenv("API_LOG_LEVEL", "INFO"))
    
    def get_agent_logger(self) -> ServiceLogger:
        """Get Agent service logger"""
        return self.get_logger("agent", os.getenv("AGENT_LOG_LEVEL", "INFO"))
    
    def get_web_logger(self) -> ServiceLogger:
        """Get Web service logger"""
        return self.get_logger("web", os.getenv("WEB_LOG_LEVEL", "INFO"))
    
    def get_shared_logger(self) -> ServiceLogger:
        """Get shared services logger"""
        return self.get_logger("shared", os.getenv("SHARED_LOG_LEVEL", "INFO"))

# Global logging manager
logging_manager = LoggingManager()

# Convenience functions
def get_api_logger() -> ServiceLogger:
    """Get API service logger"""
    return logging_manager.get_api_logger()

def get_agent_logger() -> ServiceLogger:
    """Get Agent service logger"""
    return logging_manager.get_agent_logger()

def get_web_logger() -> ServiceLogger:
    """Get Web service logger"""
    return logging_manager.get_web_logger()

def get_shared_logger() -> ServiceLogger:
    """Get shared services logger"""
    return logging_manager.get_shared_logger()

def get_logger(service_name: str, log_level: str = "INFO") -> ServiceLogger:
    """Get service-specific logger"""
    return logging_manager.get_logger(service_name, log_level)

# Configure standard library logging
def configure_standard_logging():
    """Configure standard library logging to use our structured format"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

# Initialize standard logging
configure_standard_logging()
