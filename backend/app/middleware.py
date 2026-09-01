import uuid
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.logging import request_id_ctx_var
import logging

logger = logging.getLogger(__name__)

class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Accept incoming or generate new request_id
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())
            
        # 2. Set the context variable
        token = request_id_ctx_var.set(request_id)
        
        start_time = time.time()
        
        try:
            # 3. Call the next middleware / route handler
            response = await call_next(request)
            
            # 4. Attach request_id to response headers
            response.headers["X-Request-ID"] = request_id
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Note: Do not log authorization headers or sensitive data.
            # We skip logging all requests here to avoid noise, but can log if needed.
            # logger.info(f"{request.method} {request.url.path} {response.status_code}", extra={"duration_ms": duration_ms})
            
            return response
            
        except Exception as e:
            # Re-raise exception for global error handler to catch
            raise e
        finally:
            # Clean up the context var
            request_id_ctx_var.reset(token)
