from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class DataAvailabilityLedgerInput(BaseModel):
    source: str
    dataset_name: str
    symbol: Optional[str] = None
    data_date: date
    published_at: datetime
    ingested_at: datetime
    available_for_signal_at: datetime
    revision_number: int = 1
    checksum: Optional[str] = None
    raw_payload_path: Optional[str] = None


class DataAvailabilityLedgerRecord(DataAvailabilityLedgerInput):
    id: str


class SignalDataAvailabilityCheck(BaseModel):
    dataset_name: str
    symbol: Optional[str] = None
    signal_generated_at: datetime
