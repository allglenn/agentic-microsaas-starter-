import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from database import get_db
from models import ApiCall
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = int((time.time() - start_time) * 1000)  # Convert to milliseconds
        
        # Log API call
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
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {duration}ms"
        )
        
        return response
