from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.models.base import Base


class JobRun(Base):
    """Operational audit row for each scheduled job execution."""

    __tablename__ = "job_runs"
    __table_args__ = (
        Index("ix_job_runs_name_started", "job_name", "started_at"),
        Index("ix_job_runs_status", "status"),
    )

    run_id: Mapped[str] = mapped_column(String, default=lambda: str(uuid4()), primary_key=True)
    job_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    error_message: Mapped[Optional[str]] = mapped_column(String)
    result_summary: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)


class AlertEvent(Base):
    """Operational alert emitted when jobs, providers, or APIs fail readiness checks."""

    __tablename__ = "alert_events"
    __table_args__ = (
        Index("ix_alert_events_created_at", "created_at"),
        Index("ix_alert_events_severity", "severity"),
        Index("ix_alert_events_resolved", "resolved_at"),
    )

    alert_id: Mapped[str] = mapped_column(String, default=lambda: str(uuid4()), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    recommended_action: Mapped[str] = mapped_column(String, nullable=False)
    context: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
