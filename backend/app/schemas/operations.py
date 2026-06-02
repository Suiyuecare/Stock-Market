from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class JobRunRecord(BaseModel):
    run_id: str
    job_name: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    error_message: Optional[str] = None
    result_summary: Dict[str, object]


class AlertEventRecord(BaseModel):
    alert_id: str
    created_at: datetime
    severity: str
    source: str
    code: str
    message: str
    recommended_action: str
    context: Dict[str, object]
    resolved_at: Optional[datetime] = None


class ReadinessCheck(BaseModel):
    name: str
    status: str
    detail: str


class ReadinessResponse(BaseModel):
    status: str
    generated_at: datetime
    checks: List[ReadinessCheck]
    open_alert_count: int
    latest_job_runs: List[JobRunRecord]
