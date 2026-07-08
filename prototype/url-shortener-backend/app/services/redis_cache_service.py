import json
from datetime import datetime, timezone
from typing import Any

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings


def ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def short_url_cache_key(short_code: str) -> str:
    return f"shorturl:{short_code}"


def rate_limit_key(api_key_hash: str) -> str:
    return f"rate_limit:{api_key_hash}"


def cache_short_url(redis_client: Redis, short_code: str, payload: dict[str, Any], valid_until: datetime) -> None:
    settings = get_settings()
    expires_at = ensure_aware(valid_until)
    ttl_until_expiry = int((expires_at - datetime.now(timezone.utc)).total_seconds())
    ttl = min(settings.redis_short_url_cache_seconds, ttl_until_expiry)
    if ttl > 0:
        try:
            redis_client.setex(short_url_cache_key(short_code), ttl, json.dumps(payload, default=str))
        except RedisError:
            return


def get_cached_short_url(redis_client: Redis, short_code: str) -> dict[str, Any] | None:
    try:
        cached = redis_client.get(short_url_cache_key(short_code))
    except RedisError:
        return None
    if not cached:
        return None
    try:
        return json.loads(cached)
    except json.JSONDecodeError:
        return None


def check_rate_limit(redis_client: Redis, api_key_hash: str) -> bool:
    settings = get_settings()
    key = rate_limit_key(api_key_hash)
    try:
        count = redis_client.incr(key)
        if count == 1:
            redis_client.expire(key, 60)
        return count <= settings.api_rate_limit_per_minute
    except RedisError:
        return True
