from datetime import date, datetime, timezone

from app.schemas import DataAvailabilityLedgerInput, SignalDataAvailabilityCheck


def test_data_availability_schema_tracks_signal_safe_timestamp() -> None:
    record = DataAvailabilityLedgerInput(
        source="MOPS",
        dataset_name="fundamental_monthly",
        symbol="2330",
        data_date=date(2026, 5, 31),
        published_at=datetime(2026, 6, 10, 10, 0, tzinfo=timezone.utc),
        ingested_at=datetime(2026, 6, 10, 10, 5, tzinfo=timezone.utc),
        available_for_signal_at=datetime(2026, 6, 10, 10, 10, tzinfo=timezone.utc),
        revision_number=1,
        checksum="sha256:example",
        raw_payload_path="raw/mops/fundamental_monthly/2026-05.json",
    )

    assert record.available_for_signal_at > datetime(2026, 6, 5, 9, 0, tzinfo=timezone.utc)
    assert record.revision_number == 1


def test_signal_data_availability_check_represents_backtest_cutoff() -> None:
    check = SignalDataAvailabilityCheck(
        dataset_name="fundamental_monthly",
        symbol="2330",
        signal_generated_at=datetime(2026, 6, 5, 9, 0, tzinfo=timezone.utc),
    )

    assert check.dataset_name == "fundamental_monthly"
    assert check.signal_generated_at.isoformat() == "2026-06-05T09:00:00+00:00"
