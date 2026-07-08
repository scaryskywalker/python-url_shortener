"""initial schema

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-07-07 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "merchants",
        sa.Column("merchant_id", sa.String(length=36), nullable=False),
        sa.Column("merchant_code", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("account_details", sa.Text(), nullable=True),
        sa.Column("account_status", sa.String(length=50), server_default="active", nullable=False),
        sa.Column("api_key_hash", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("merchant_id"),
    )
    op.create_index(op.f("ix_merchants_api_key_hash"), "merchants", ["api_key_hash"], unique=False)
    op.create_index(op.f("ix_merchants_merchant_code"), "merchants", ["merchant_code"], unique=True)

    op.create_table(
        "shortening_strategies",
        sa.Column("strategy_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("output_length", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("strategy_id"),
    )
    op.create_index(op.f("ix_shortening_strategies_name"), "shortening_strategies", ["name"], unique=True)

    op.create_table(
        "merchant_configs",
        sa.Column("config_id", sa.String(length=36), nullable=False),
        sa.Column("merchant_id", sa.String(length=36), nullable=False),
        sa.Column("strategy_id", sa.String(length=36), nullable=False),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.merchant_id"]),
        sa.ForeignKeyConstraint(["strategy_id"], ["shortening_strategies.strategy_id"]),
        sa.PrimaryKeyConstraint("config_id"),
    )
    op.create_index(op.f("ix_merchant_configs_merchant_id"), "merchant_configs", ["merchant_id"], unique=False)
    op.create_index(op.f("ix_merchant_configs_strategy_id"), "merchant_configs", ["strategy_id"], unique=False)

    op.create_table(
        "urls",
        sa.Column("url_id", sa.String(length=36), nullable=False),
        sa.Column("short_code", sa.String(length=255), nullable=False),
        sa.Column("original_url", sa.Text(), nullable=False),
        sa.Column("merchant_id", sa.String(length=36), nullable=False),
        sa.Column("config_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["config_id"], ["merchant_configs.config_id"]),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.merchant_id"]),
        sa.PrimaryKeyConstraint("url_id"),
    )
    op.create_index(op.f("ix_urls_config_id"), "urls", ["config_id"], unique=False)
    op.create_index(op.f("ix_urls_merchant_id"), "urls", ["merchant_id"], unique=False)
    op.create_index(op.f("ix_urls_short_code"), "urls", ["short_code"], unique=True)

    op.create_table(
        "url_access_logs",
        sa.Column("log_id", sa.String(length=36), nullable=False),
        sa.Column("url_id", sa.String(length=36), nullable=False),
        sa.Column("short_code", sa.String(length=255), nullable=False),
        sa.Column("ip_address", sa.String(length=100), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("accessed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["url_id"], ["urls.url_id"]),
        sa.PrimaryKeyConstraint("log_id"),
    )
    op.create_index(op.f("ix_url_access_logs_short_code"), "url_access_logs", ["short_code"], unique=False)
    op.create_index(op.f("ix_url_access_logs_url_id"), "url_access_logs", ["url_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_url_access_logs_url_id"), table_name="url_access_logs")
    op.drop_index(op.f("ix_url_access_logs_short_code"), table_name="url_access_logs")
    op.drop_table("url_access_logs")
    op.drop_index(op.f("ix_urls_short_code"), table_name="urls")
    op.drop_index(op.f("ix_urls_merchant_id"), table_name="urls")
    op.drop_index(op.f("ix_urls_config_id"), table_name="urls")
    op.drop_table("urls")
    op.drop_index(op.f("ix_merchant_configs_strategy_id"), table_name="merchant_configs")
    op.drop_index(op.f("ix_merchant_configs_merchant_id"), table_name="merchant_configs")
    op.drop_table("merchant_configs")
    op.drop_index(op.f("ix_shortening_strategies_name"), table_name="shortening_strategies")
    op.drop_table("shortening_strategies")
    op.drop_index(op.f("ix_merchants_merchant_code"), table_name="merchants")
    op.drop_index(op.f("ix_merchants_api_key_hash"), table_name="merchants")
    op.drop_table("merchants")
