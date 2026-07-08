from fastapi import APIRouter, Depends
from redis import Redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.redis import get_redis_client
from app.database.mysql import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db), redis_client: Redis = Depends(get_redis_client)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    redis_client.ping()
    return {"status": "ok", "mysql": "ok", "redis": "ok"}
