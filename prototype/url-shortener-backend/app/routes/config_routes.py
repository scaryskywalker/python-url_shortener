from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.mysql import get_db
from app.dependencies.auth import get_current_merchant
from app.models.merchant import Merchant
from app.models.merchant_config import MerchantConfig
from app.models.strategy import ShorteningStrategy
from app.schemas.config_schema import MerchantConfigCreate, MerchantConfigResponse
from app.services.redis_cache_service import ensure_aware

router = APIRouter(prefix="/api/v1/configs", tags=["Merchant Configurations"])


@router.post("", response_model=MerchantConfigResponse, status_code=status.HTTP_201_CREATED)
def create_config(
    payload: MerchantConfigCreate,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
) -> MerchantConfig:
    strategy = db.query(ShorteningStrategy).filter(ShorteningStrategy.strategy_id == payload.strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")
    if ensure_aware(payload.valid_until) <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="valid_until must be in the future")

    # Prevent duplicates
    existing_config = db.query(MerchantConfig).filter(
        MerchantConfig.merchant_id == merchant.merchant_id,
        MerchantConfig.strategy_id == payload.strategy_id
    ).first()
    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have an active plan for this encryption strategy."
        )

    config = MerchantConfig(
        merchant_id=merchant.merchant_id,
        strategy_id=payload.strategy_id,
        valid_until=payload.valid_until,
        is_active=payload.is_active,
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.get("", response_model=list[MerchantConfigResponse])
def list_configs(
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
) -> list[MerchantConfig]:
    return (
        db.query(MerchantConfig)
        .filter(MerchantConfig.merchant_id == merchant.merchant_id)
        .order_by(MerchantConfig.created_at.desc())
        .all()
    )


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_config(
    config_id: str,
    merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
):
    config = db.query(MerchantConfig).filter(
        MerchantConfig.config_id == config_id,
        MerchantConfig.merchant_id == merchant.merchant_id
    ).first()
    
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found")
        
    db.delete(config)
    db.commit()
    return None
