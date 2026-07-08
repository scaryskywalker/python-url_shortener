from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MerchantCreate(BaseModel):
    merchant_code: str = Field(..., min_length=1, max_length=100, examples=["AMAZON01"])
    name: str = Field(..., min_length=1, max_length=255, examples=["Amazon"])
    account_details: str | None = Field(default=None, examples=["Demo merchant account"])
    plan: str = Field(default="Free", examples=["Free"])


class MerchantResponse(BaseModel):
    merchant_id: str
    merchant_code: str
    name: str
    plan: str
    token_limit: int | None
    url_validity_days: int | None
    urls_created_count: int
    api_key: str


class MerchantProfile(BaseModel):
    merchant_id: str
    merchant_code: str
    name: str
    plan: str
    token_limit: int | None
    url_validity_days: int | None
    urls_created_count: int


class ApiKeyRotateResponse(BaseModel):
    merchant_id: str
    api_key: str


class MerchantRead(BaseModel):
    merchant_id: str
    merchant_code: str
    name: str
    account_details: str | None
    account_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
