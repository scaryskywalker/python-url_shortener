import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Url(Base):
    __tablename__ = "urls"

    url_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    short_code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    merchant_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchants.merchant_id"), nullable=False, index=True)
    config_id: Mapped[str] = mapped_column(String(36), ForeignKey("merchant_configs.config_id"), nullable=False, index=True)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    merchant = relationship("Merchant", back_populates="urls")
    config = relationship("MerchantConfig", back_populates="urls")
    access_logs = relationship("UrlAccessLog", back_populates="url", cascade="all, delete-orphan")
