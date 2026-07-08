from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session, joinedload

from app.models.access_log import UrlAccessLog
from app.models.url import Url
from app.services.redis_cache_service import cache_short_url, ensure_aware, get_cached_short_url


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return ensure_aware(parsed)


def build_cache_payload(url: Url) -> dict[str, Any]:
    valid_until = url.valid_until or url.config.valid_until
    return {
        "original_url": url.original_url,
        "merchant_id": url.merchant_id,
        "config_id": url.config_id,
        "valid_until": ensure_aware(valid_until).isoformat() if valid_until else None,
    }


def validate_cached_payload(short_code: str, payload: dict[str, Any]) -> dict[str, Any]:
    valid_until = _parse_datetime(payload["valid_until"]) if payload.get("valid_until") else None
    if valid_until and valid_until <= _now():
        return {"short_code": short_code, "is_valid": False, "reason": "URL has expired"}

    return {
        "short_code": short_code,
        "is_valid": True,
        "reason": "URL is valid",
        "original_url": payload["original_url"],
        "merchant_id": payload["merchant_id"],
        "config_id": payload["config_id"],
        "valid_until": valid_until,
    }


def validate_url_from_db(db: Session, short_code: str) -> dict[str, Any]:
    url = (
        db.query(Url)
        .options(joinedload(Url.merchant), joinedload(Url.config))
        .filter(Url.short_code == short_code)
        .first()
    )
    if not url:
        return {"short_code": short_code, "is_valid": False, "reason": "Short URL not found"}
    if not url.merchant:
        return {"short_code": short_code, "is_valid": False, "reason": "Merchant not found"}
    if url.merchant.account_status != "active":
        return {"short_code": short_code, "is_valid": False, "reason": "Merchant is inactive"}
    if not url.config:
        return {"short_code": short_code, "is_valid": False, "reason": "Configuration not found"}
    if not url.config.is_active:
        return {"short_code": short_code, "is_valid": False, "reason": "Configuration is inactive"}
    if ensure_aware(url.config.valid_until) <= _now():
        return {"short_code": short_code, "is_valid": False, "reason": "Configuration has expired"}
    valid_until = url.valid_until or url.config.valid_until
    if valid_until and ensure_aware(valid_until) <= _now():
        return {"short_code": short_code, "is_valid": False, "reason": "URL has expired"}

    return {
        "short_code": short_code,
        "is_valid": True,
        "reason": "URL is valid",
        "original_url": url.original_url,
        "merchant_id": url.merchant_id,
        "config_id": url.config_id,
        "valid_until": ensure_aware(valid_until) if valid_until else None,
        "url": url,
    }


def validate_short_url(db: Session, redis_client: Any, short_code: str) -> dict[str, Any]:
    cached = get_cached_short_url(redis_client, short_code)
    if cached:
        cached_result = validate_cached_payload(short_code, cached)
        if not cached_result["is_valid"]:
            return cached_result

    result = validate_url_from_db(db, short_code)
    url = result.pop("url", None)
    if result["is_valid"] and url is not None:
        cache_short_url(redis_client, short_code, build_cache_payload(url), url.valid_until or url.config.valid_until)
    return result


def log_access(db: Session, url_id: str, short_code: str, ip_address: str | None, user_agent: str | None) -> None:
    try:
        db.add(
            UrlAccessLog(
                url_id=url_id,
                short_code=short_code,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
