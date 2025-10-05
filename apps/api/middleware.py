import time
import os
import sys
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session

# Add project root to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from libs.shared.database import get_db
from libs.shared.models import ApiCall
from libs.shared.logging_config import get_api_logger
from libs.shared.monitoring import APIMonitor

# Initialize logger
logger = get_api_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        
        # Log API call using shared monitoring
        try:
            db = next(get_db())
            api_call = ApiCall(
                endpoint=str(request.url.path),
                method=request.method,
                status=response.status_code,
                duration=duration
            )
            db.add(api_call)
            db.commit()
        except Exception as e:
            logger.error(f"Error logging API call: {e}")
        finally:
            db.close()
        
        # Log request using structured logging
        logger.log_api_call(
            endpoint=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            duration_ms=duration
        )
        
        return response
