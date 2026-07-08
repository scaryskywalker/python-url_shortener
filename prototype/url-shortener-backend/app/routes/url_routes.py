from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from redis import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.core.plans import get_plan
from app.core.redis import get_redis_client
from app.database.mysql import get_db
from app.dependencies.auth import get_current_merchant
from app.models.merchant import Merchant
from app.models.merchant_config import MerchantConfig
from app.models.url import Url
from app.schemas.url_schema import UrlRead, UrlShortenRequest, UrlShortenResponse, UrlValidationResponse
from app.services.redis_cache_service import cache_short_url, ensure_aware
from app.services.short_code_service import generate_unique_short_code
from app.services.validation_service import build_cache_payload, log_access, validate_short_url

api_router = APIRouter(prefix="/api/v1/urls", tags=["URLs"])
public_router = APIRouter(tags=["Redirect"])


def _validation_error_status(reason: str) -> int:
    if reason == "Short URL not found":
        return status.HTTP_404_NOT_FOUND
    return status.HTTP_403_FORBIDDEN


def _url_status(url: Url) -> tuple[bool, str]:
    if not url.config or not url.config.is_active:
        return False, "Inactive plan"
    if ensure_aware(url.config.valid_until) <= datetime.now(timezone.utc):
        return False, "Strategy expired"
    if url.valid_until and ensure_aware(url.valid_until) <= datetime.now(timezone.utc):
        return False, "Expired"
    return True, "Valid"


def _short_url(short_code: str) -> str:
    return f"{get_settings().public_base_url}/{short_code}"


@api_router.post("/shorten", response_model=UrlShortenResponse, status_code=status.HTTP_201_CREATED)
def shorten_url(
    payload: UrlShortenRequest,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client),
) -> UrlShortenResponse:
    config = (
        db.query(MerchantConfig)
        .options(joinedload(MerchantConfig.strategy))
        .filter(MerchantConfig.config_id == payload.config_id)
        .first()
    )
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found")
    if config.merchant_id != merchant.merchant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Configuration does not belong to merchant")
    if not config.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Configuration is inactive")
    if ensure_aware(config.valid_until) <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Configuration has expired")
    plan = get_plan(merchant.plan)
    if plan.token_limit is not None and merchant.urls_created_count >= plan.token_limit:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Plan token limit reached")

    original_url = str(payload.original_url)
    try:
        short_code = generate_unique_short_code(db, config.strategy, original_url)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    url = Url(
        short_code=short_code,
        original_url=original_url,
        merchant_id=merchant.merchant_id,
        config_id=config.config_id,
        valid_until=config.valid_until,
    )
    db.add(url)
    merchant.urls_created_count += 1
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="short_code already exists") from exc
    db.refresh(url)
    url.merchant = merchant
    url.config = config
    cache_short_url(redis_client, short_code, build_cache_payload(url), config.valid_until)

    return UrlShortenResponse(
        url_id=url.url_id,
        short_code=short_code,
        short_url=_short_url(short_code),
        original_url=original_url,
        valid_until=url.valid_until,
    )


@api_router.get("", response_model=list[UrlRead])
def list_urls(
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
) -> list[UrlRead]:
    urls = (
        db.query(Url)
        .options(joinedload(Url.config))
        .filter(Url.merchant_id == merchant.merchant_id)
        .order_by(Url.created_at.desc())
        .all()
    )
    rows = []
    for url in urls:
        is_valid, status_text = _url_status(url)
        rows.append(
            UrlRead(
                url_id=url.url_id,
                short_code=url.short_code,
                short_url=_short_url(url.short_code),
                original_url=url.original_url,
                merchant_id=url.merchant_id,
                config_id=url.config_id,
                valid_until=url.valid_until or (url.config.valid_until if url.config else None),
                is_valid=is_valid,
                status=status_text,
                created_at=url.created_at,
                updated_at=url.updated_at,
            )
        )
    return rows


@api_router.get("/{short_code}/validate", response_model=UrlValidationResponse)
def validate_url(
    short_code: str,
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client),
) -> dict:
    return validate_short_url(db, redis_client, short_code)


@api_router.delete("/{url_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_url(
    url_id: str,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client),
):
    url = db.query(Url).filter(Url.url_id == url_id, Url.merchant_id == merchant.merchant_id).first()
    if not url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    redis_client.delete(f"shorturl:{url.short_code}")
    db.delete(url)
    merchant.urls_created_count = max(merchant.urls_created_count - 1, 0)
    db.commit()
    return None


@public_router.get("/{short_code}")
def redirect_short_url(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client),
) -> RedirectResponse:
    result = validate_short_url(db, redis_client, short_code)
    if not result["is_valid"]:
        raise HTTPException(status_code=_validation_error_status(result["reason"]), detail=result["reason"])

    url = db.query(Url).filter(Url.short_code == short_code).first()
    if url:
        log_access(
            db,
            url.url_id,
            short_code,
            request.client.host if request.client else None,
            request.headers.get("user-agent"),
        )
    return RedirectResponse(url=result["original_url"], status_code=status.HTTP_302_FOUND)
