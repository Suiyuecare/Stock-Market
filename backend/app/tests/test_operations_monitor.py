import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import AlertEvent, Base, JobRun
from app.services.operations_monitor import OperationsMonitor


def _session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_operations_monitor_records_successful_job_run_and_readiness() -> None:
    monitor = OperationsMonitor()
    with _session() as session:
        result = monitor.run_job(session, "smoke-job", lambda: {"status": "completed", "updated_rows": 3})
        readiness = monitor.readiness(session)

        assert result["updated_rows"] == 3
        assert session.query(JobRun).count() == 1
        assert readiness.status == "ready"
        assert readiness.latest_job_runs[0].job_name == "smoke-job"
        assert readiness.open_alert_count == 0


def test_operations_monitor_records_failed_job_and_alert() -> None:
    monitor = OperationsMonitor()

    def failed_job() -> dict:
        raise RuntimeError("provider timeout")

    with _session() as session:
        with pytest.raises(RuntimeError):
            monitor.run_job(session, "provider-job", failed_job)
        readiness = monitor.readiness(session)
        alerts = monitor.list_open_alerts(session)

        assert session.query(JobRun).filter_by(status="failed").count() == 1
        assert session.query(AlertEvent).count() == 1
        assert readiness.status == "critical"
        assert alerts[0].code == "scheduled_job_failed"
        assert "provider timeout" in alerts[0].message


def test_operations_monitor_emits_manual_alert() -> None:
    monitor = OperationsMonitor()
    with _session() as session:
        alert = monitor.emit_alert(
            session,
            severity="warning",
            source="readiness",
            code="api_latency_high",
            message="API latency is above launch threshold.",
            recommended_action="Inspect runtime logs and provider response time.",
            context={"p95_ms": 1200},
        )

        assert alert.severity == "warning"
        assert session.query(AlertEvent).count() == 1
        assert monitor.readiness(session).open_alert_count == 1
