import logging
from typing import cast
from fastapi import HTTPException, Request, status
import redis
from services.cache_service import redis_client

logger = logging.getLogger(__name__)


def rate_limit_login(
    request: Request,
    max_requests: int = 5,
    window_seconds: int = 60,
) -> None:
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:login:{client_ip}"

    try:
        current_count = cast(int, redis_client.incr(key))

        if current_count == 1:
            redis_client.expire(key, window_seconds)

        if current_count > max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
            )
    except redis.RedisError as exc:
        logger.warning(f"Rate limiter failed for IP '{client_ip}': {exc}")
        return
