from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from redis import Redis
from sqlalchemy.orm import Session

from app.core.redis import get_redis_client
from app.core.security import hash_api_key
from app.database.mysql import get_db
from app.models.merchant import Merchant
from app.services.redis_cache_service import check_rate_limit


def get_current_merchant(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client),
) -> Merchant:
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    api_key_hash = hash_api_key(x_api_key)
    merchant = db.query(Merchant).filter(Merchant.api_key_hash == api_key_hash).first()
    if not merchant:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    if merchant.account_status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Merchant is inactive")
    if not check_rate_limit(redis_client, api_key_hash):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    return merchant
