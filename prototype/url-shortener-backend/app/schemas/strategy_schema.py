from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StrategyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["BASE62_8"])
    output_length: int = Field(..., ge=1, le=255, examples=[8])
    description: str | None = Field(default=None, examples=["Base62 short code with 8 characters"])


class StrategyResponse(BaseModel):
    strategy_id: str
    name: str
    output_length: int
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
