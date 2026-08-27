import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000

        response.headers["X-Request-ID"] = request_id

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"Status: {response.status_code} - Duration: {duration_ms:.2f}ms"
        )

        return response
