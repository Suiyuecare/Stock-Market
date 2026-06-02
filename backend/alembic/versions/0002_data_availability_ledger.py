"""Add data availability ledger.

Revision ID: 0002_data_availability_ledger
Revises: 0001_initial_stock_schema
Create Date: 2026-06-02
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_data_availability_ledger"
down_revision = "0001_initial_stock_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "data_availability_ledger",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("dataset_name", sa.String(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=True),
        sa.Column("data_date", sa.Date(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("available_for_signal_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(), nullable=True),
        sa.Column("raw_payload_path", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source", "dataset_name", "symbol", "data_date", "revision_number", name="uq_data_availability_revision"),
    )
    op.create_index(
        "ix_data_availability_signal_time",
        "data_availability_ledger",
        ["dataset_name", "symbol", "available_for_signal_at"],
    )
    op.create_index(
        "ix_data_availability_source_date",
        "data_availability_ledger",
        ["source", "dataset_name", "data_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_data_availability_source_date", table_name="data_availability_ledger")
    op.drop_index("ix_data_availability_signal_time", table_name="data_availability_ledger")
    op.drop_table("data_availability_ledger")
