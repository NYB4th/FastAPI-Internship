import json
import logging
from typing import Any
import redis
from config import settings

logger = logging.getLogger(__name__)

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True,
    socket_connect_timeout=2,
)


def get_cache(key: str) -> Any | None:
    try:
        data = redis_client.get(key)
        if data is not None:
            return json.loads(data)  # pyright: ignore[reportArgumentType]
        return None
    except redis.RedisError as exc:
        logger.warning(f"Redis GET failed for key '{key}': {exc}")
        return None


def set_cache(
    key: str, value: Any, ttl: int = settings.REDIS_CACHE_TTL_SECONDS
) -> bool:
    try:
        serialized = json.dumps(value)
        redis_client.setex(name=key, time=ttl, value=serialized)
        return True
    except redis.RedisError as exc:
        logger.warning(f"Redis SET failed for key '{key}': {exc}")
        return False


def delete_cache(key: str) -> bool:
    try:
        redis_client.delete(key)
        return True
    except redis.RedisError as exc:
        logger.warning(f"Redis DELETE failed for key '{key}': {exc}")
        return False


def delete_cache_pattern(pattern: str) -> bool:
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)  # pyright: ignore[reportGeneralTypeIssues]
        return True
    except redis.RedisError as exc:
        logger.warning(f"Redis DELETE pattern failed for '{pattern}': {exc}")
        return False
