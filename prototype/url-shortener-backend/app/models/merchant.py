import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Merchant(Base):
    __tablename__ = "merchants"

    merchant_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    account_status: Mapped[str] = mapped_column(String(50), nullable=False, default="active", server_default="active")
    plan: Mapped[str] = mapped_column(String(50), nullable=False, default="Free", server_default="Free")
    urls_created_count: Mapped[int] = mapped_column(default=0, server_default="0", nullable=False)
    api_key_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    configs = relationship("MerchantConfig", back_populates="merchant", cascade="all, delete-orphan")
    urls = relationship("Url", back_populates="merchant", cascade="all, delete-orphan")
