import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from database import AsyncSessionLocal
from models import AnalyticsEvent

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health"] or request.url.path.startswith("/static"):
            return await call_next(request)
            
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.4f}s")
        
        if request.url.path == "/chat" and request.method == "POST":
            # Record analytics event
            async with AsyncSessionLocal() as session:
                event = AnalyticsEvent(
                    event_type="chat_request",
                    metadata_json=f'{{"duration": {duration}}}'
                )
                session.add(event)
                await session.commit()
                
        return response
