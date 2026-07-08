from datetime import datetime

from pydantic import AnyUrl, BaseModel, Field


class UrlShortenRequest(BaseModel):
    original_url: AnyUrl = Field(..., examples=["https://example.com/products/mobile"])
    config_id: str = Field(..., examples=["uuid-here"])


class UrlShortenResponse(BaseModel):
    url_id: str
    short_code: str
    short_url: str
    original_url: str
    valid_until: datetime | None


class UrlValidationResponse(BaseModel):
    short_code: str
    is_valid: bool
    reason: str
    original_url: str | None = None
    merchant_id: str | None = None
    config_id: str | None = None
    valid_until: datetime | None = None


class UrlRead(BaseModel):
    url_id: str
    short_code: str
    short_url: str
    original_url: str
    merchant_id: str
    config_id: str
    valid_until: datetime | None
    is_valid: bool
    status: str
    created_at: datetime
    updated_at: datetime
