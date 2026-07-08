from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MerchantConfigCreate(BaseModel):
    strategy_id: str = Field(..., examples=["uuid-here"])
    valid_until: datetime
    is_active: bool = True


class MerchantConfigResponse(BaseModel):
    config_id: str
    merchant_id: str
    strategy_id: str
    valid_until: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
