"""Add feature store daily.

Revision ID: 0003_feature_store_daily
Revises: 0002_data_availability_ledger
Create Date: 2026-06-02
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_feature_store_daily"
down_revision = "0002_data_availability_ledger"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feature_store_daily",
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column("stock_id", sa.String(), nullable=False),
        sa.Column("feature_group", sa.String(), nullable=False),
        sa.Column("feature_name", sa.String(), nullable=False),
        sa.Column("feature_value", sa.Numeric(24, 8), nullable=False),
        sa.Column("feature_version", sa.String(), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("available_for_signal_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["stock_id"], ["stock_master.stock_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("trade_date", "stock_id", "feature_group", "feature_name", "feature_version"),
    )
    op.create_index(
        "ix_feature_store_signal_time",
        "feature_store_daily",
        ["stock_id", "trade_date", "available_for_signal_at"],
    )
    op.create_index(
        "ix_feature_store_feature_lookup",
        "feature_store_daily",
        ["feature_group", "feature_name", "feature_version"],
    )


def downgrade() -> None:
    op.drop_index("ix_feature_store_feature_lookup", table_name="feature_store_daily")
    op.drop_index("ix_feature_store_signal_time", table_name="feature_store_daily")
    op.drop_table("feature_store_daily")
