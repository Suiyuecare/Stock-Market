import logging
from datetime import datetime, timezone
from time import perf_counter
from typing import Callable, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import desc, select, text
from sqlalchemy.orm import Session

from app.models import AlertEvent, JobRun
from app.schemas import AlertEventRecord, JobRunRecord, ReadinessCheck, ReadinessResponse

logger = logging.getLogger("stock_app.operations")


class OperationsMonitor:
    """Record operational health, job failures, and launch-readiness checks."""

    def run_job(self, session: Session, job_name: str, job: Callable[[], Dict[str, object]]) -> Dict[str, object]:
        started_at = datetime.now(timezone.utc)
        start = perf_counter()
        run_id = str(uuid4())
        logger.info("job_start", extra={"job_name": job_name, "run_id": run_id})
        try:
            result = job()
            completed_at = datetime.now(timezone.utc)
            job_run = JobRun(
                run_id=run_id,
                job_name=job_name,
                status="completed",
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=int((perf_counter() - start) * 1000),
                result_summary=self._summary(result),
            )
            session.add(job_run)
            session.commit()
            logger.info("job_completed", extra={"job_name": job_name, "run_id": run_id, "duration_ms": job_run.duration_ms})
            return result
        except Exception as exc:
            completed_at = datetime.now(timezone.utc)
            job_run = JobRun(
                run_id=run_id,
                job_name=job_name,
                status="failed",
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=int((perf_counter() - start) * 1000),
                error_message=str(exc),
                result_summary={},
            )
            session.add(job_run)
            self.emit_alert(
                session,
                severity="critical",
                source=job_name,
                code="scheduled_job_failed",
                message=f"{job_name} failed: {exc}",
                recommended_action="Check provider availability, database connectivity, and scheduler logs.",
                context={"run_id": run_id},
                commit=False,
            )
            session.commit()
            logger.exception("job_failed", extra={"job_name": job_name, "run_id": run_id})
            raise

    def emit_alert(
        self,
        session: Session,
        severity: str,
        source: str,
        code: str,
        message: str,
        recommended_action: str,
        context: Optional[Dict[str, object]] = None,
        commit: bool = True,
    ) -> AlertEventRecord:
        alert = AlertEvent(
            created_at=datetime.now(timezone.utc),
            severity=severity,
            source=source,
            code=code,
            message=message,
            recommended_action=recommended_action,
            context=context or {},
        )
        session.add(alert)
        if commit:
            session.commit()
            session.refresh(alert)
        else:
            session.flush()
        logger.warning("alert_emitted", extra={"severity": severity, "source": source, "code": code})
        return self._alert_record(alert)

    def readiness(self, session: Session) -> ReadinessResponse:
        checks = [self._database_check(session), self._jobs_check(session), self._alerts_check(session)]
        open_alert_count = session.query(AlertEvent).filter(AlertEvent.resolved_at.is_(None)).count()
        latest_runs = session.scalars(select(JobRun).order_by(desc(JobRun.started_at)).limit(10)).all()
        status = "ready" if all(check.status == "ok" for check in checks) else "degraded"
        if any(check.status == "critical" for check in checks):
            status = "critical"
        return ReadinessResponse(
            status=status,
            generated_at=datetime.now(timezone.utc),
            checks=checks,
            open_alert_count=open_alert_count,
            latest_job_runs=[self._job_run_record(run) for run in latest_runs],
        )

    def list_open_alerts(self, session: Session, limit: int = 50) -> List[AlertEventRecord]:
        alerts = session.scalars(
            select(AlertEvent).where(AlertEvent.resolved_at.is_(None)).order_by(desc(AlertEvent.created_at)).limit(limit)
        ).all()
        return [self._alert_record(alert) for alert in alerts]

    def _database_check(self, session: Session) -> ReadinessCheck:
        try:
            session.execute(text("select 1"))
            return ReadinessCheck(name="database", status="ok", detail="Database session is reachable.")
        except Exception as exc:
            return ReadinessCheck(name="database", status="critical", detail=f"Database check failed: {exc}")

    def _jobs_check(self, session: Session) -> ReadinessCheck:
        failed = session.query(JobRun).filter(JobRun.status == "failed").count()
        latest = session.scalar(select(JobRun).order_by(desc(JobRun.started_at)))
        if failed:
            return ReadinessCheck(name="scheduled_jobs", status="critical", detail=f"{failed} job failure(s) recorded.")
        if latest is None:
            return ReadinessCheck(name="scheduled_jobs", status="warning", detail="No scheduled job run has been recorded yet.")
        return ReadinessCheck(name="scheduled_jobs", status="ok", detail=f"Latest job {latest.job_name} completed with status {latest.status}.")

    def _alerts_check(self, session: Session) -> ReadinessCheck:
        open_alerts = session.query(AlertEvent).filter(AlertEvent.resolved_at.is_(None)).count()
        if open_alerts:
            return ReadinessCheck(name="alerts", status="warning", detail=f"{open_alerts} open operational alert(s).")
        return ReadinessCheck(name="alerts", status="ok", detail="No open operational alerts.")

    def _summary(self, result: Dict[str, object]) -> Dict[str, object]:
        return {
            key: value
            for key, value in result.items()
            if key not in {"stocks", "radar", "linkage"} and isinstance(value, (str, int, float, bool, dict))
        }

    def _job_run_record(self, run: JobRun) -> JobRunRecord:
        return JobRunRecord(
            run_id=run.run_id,
            job_name=run.job_name,
            status=run.status,
            started_at=run.started_at,
            completed_at=run.completed_at,
            duration_ms=run.duration_ms,
            error_message=run.error_message,
            result_summary=run.result_summary,
        )

    def _alert_record(self, alert: AlertEvent) -> AlertEventRecord:
        return AlertEventRecord(
            alert_id=alert.alert_id,
            created_at=alert.created_at,
            severity=alert.severity,
            source=alert.source,
            code=alert.code,
            message=alert.message,
            recommended_action=alert.recommended_action,
            context=alert.context,
            resolved_at=alert.resolved_at,
        )
