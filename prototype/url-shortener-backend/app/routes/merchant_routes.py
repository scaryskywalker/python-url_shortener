from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.mysql import get_db
from app.dependencies.auth import get_current_merchant
from app.core.plans import get_plan, plan_options
from app.models.merchant import Merchant
from app.schemas.merchant_schema import ApiKeyRotateResponse, MerchantCreate, MerchantProfile, MerchantResponse
from app.services.api_key_service import create_api_key_pair

router = APIRouter(prefix="/api/v1/merchants", tags=["Merchants"])


@router.post("", response_model=MerchantResponse, status_code=status.HTTP_201_CREATED)
def create_merchant(payload: MerchantCreate, db: Session = Depends(get_db)) -> MerchantResponse:
    plan = get_plan(payload.plan)
    api_key, api_key_hash = create_api_key_pair()
    merchant = Merchant(
        merchant_code=payload.merchant_code,
        name=payload.name,
        account_details=payload.account_details,
        plan=plan.name,
        api_key_hash=api_key_hash,
    )
    db.add(merchant)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="merchant_code already exists") from exc
    db.refresh(merchant)
    return MerchantResponse(
        merchant_id=merchant.merchant_id,
        merchant_code=merchant.merchant_code,
        name=merchant.name,
        plan=merchant.plan,
        token_limit=plan.token_limit,
        url_validity_days=plan.url_validity_days,
        urls_created_count=merchant.urls_created_count,
        api_key=api_key,
    )


@router.get("/plans")
def list_plans() -> list[dict[str, int | str | None]]:
    return plan_options()


@router.get("/me", response_model=MerchantProfile)
def read_current_merchant(current_merchant: Merchant = Depends(get_current_merchant)) -> MerchantProfile:
    plan = get_plan(current_merchant.plan)
    return MerchantProfile(
        merchant_id=current_merchant.merchant_id,
        merchant_code=current_merchant.merchant_code,
        name=current_merchant.name,
        plan=current_merchant.plan,
        token_limit=plan.token_limit,
        url_validity_days=plan.url_validity_days,
        urls_created_count=current_merchant.urls_created_count,
    )


@router.post("/{merchant_id}/rotate-api-key", response_model=ApiKeyRotateResponse)
def rotate_api_key(
    merchant_id: str,
    current_merchant: Merchant = Depends(get_current_merchant),
    db: Session = Depends(get_db),
) -> ApiKeyRotateResponse:
    if current_merchant.merchant_id != merchant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot rotate another merchant's API key")

    api_key, api_key_hash = create_api_key_pair()
    current_merchant.api_key_hash = api_key_hash
    db.commit()
    db.refresh(current_merchant)
    return ApiKeyRotateResponse(merchant_id=current_merchant.merchant_id, api_key=api_key)
