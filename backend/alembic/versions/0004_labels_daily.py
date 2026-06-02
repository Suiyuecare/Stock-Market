"""Add labels daily.

Revision ID: 0004_labels_daily
Revises: 0003_feature_store_daily
Create Date: 2026-06-02
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_labels_daily"
down_revision = "0003_feature_store_daily"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "labels_daily",
        sa.Column("trade_date", sa.Date(), nullable=False),
        sa.Column("stock_id", sa.String(), nullable=False),
        sa.Column("label_name", sa.String(), nullable=False),
        sa.Column("label_value", sa.Numeric(10, 4), nullable=False),
        sa.Column("horizon_days", sa.Integer(), nullable=False),
        sa.Column("label_version", sa.String(), nullable=False),
        sa.Column("forward_return", sa.Numeric(18, 8), nullable=True),
        sa.Column("benchmark_return", sa.Numeric(18, 8), nullable=True),
        sa.Column("excess_return", sa.Numeric(18, 8), nullable=True),
        sa.Column("max_favorable_excursion", sa.Numeric(18, 8), nullable=True),
        sa.Column("max_adverse_excursion", sa.Numeric(18, 8), nullable=True),
        sa.Column("transaction_cost", sa.Numeric(10, 6), nullable=False),
        sa.Column("minimum_excess_return", sa.Numeric(10, 6), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("available_for_signal_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["stock_id"], ["stock_master.stock_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("trade_date", "stock_id", "label_name", "horizon_days", "label_version"),
    )
    op.create_index("ix_labels_daily_lookup", "labels_daily", ["stock_id", "trade_date", "label_name", "label_version"])
    op.create_index("ix_labels_daily_signal_time", "labels_daily", ["stock_id", "trade_date", "available_for_signal_at"])


def downgrade() -> None:
    op.drop_index("ix_labels_daily_signal_time", table_name="labels_daily")
    op.drop_index("ix_labels_daily_lookup", table_name="labels_daily")
    op.drop_table("labels_daily")
