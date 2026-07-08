import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MerchantConfig(Base):
    __tablename__ = "merchant_configs"

    config_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.merchant_id"), nullable=False, index=True)
    strategy_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shortening_strategies.strategy_id"), nullable=False, index=True
    )
    valid_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    merchant = relationship("Merchant", back_populates="configs")
    strategy = relationship("ShorteningStrategy", back_populates="configs")
    urls = relationship("Url", back_populates="config")
