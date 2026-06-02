from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_session
from app.schemas import AlertEventRecord, ReadinessResponse
from app.services.operations_monitor import OperationsMonitor

router = APIRouter()
monitor = OperationsMonitor()


@router.get("/monitoring/readiness", response_model=ReadinessResponse)
def readiness(session: Session = Depends(get_session)) -> ReadinessResponse:
    return monitor.readiness(session)


@router.get("/monitoring/alerts", response_model=List[AlertEventRecord])
def open_alerts(session: Session = Depends(get_session)) -> List[AlertEventRecord]:
    return monitor.list_open_alerts(session)
