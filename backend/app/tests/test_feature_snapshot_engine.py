from datetime import date, datetime, timezone
from decimal import Decimal

from app.schemas import FeatureSnapshotRequest
from app.services.feature_snapshot_engine import FeatureSnapshotEngine


def test_feature_snapshot_engine_builds_point_in_time_records() -> None:
    calculated_at = datetime(2026, 6, 4, 15, 0, tzinfo=timezone.utc)
    available_at = datetime(2026, 6, 4, 15, 5, tzinfo=timezone.utc)

    result = FeatureSnapshotEngine().build_snapshot(
        FeatureSnapshotRequest(
            trade_date=date(2026, 6, 4),
            stock_id="2330",
            feature_group="technical",
            feature_version="technical-v1",
            calculated_at=calculated_at,
            available_for_signal_at=available_at,
            features={
                "macd_hist": Decimal("1.25"),
                "rsi14": Decimal("61.5"),
                "volume_price_score": Decimal("72"),
            },
        )
    )

    assert [record.feature_name for record in result.records] == ["macd_hist", "rsi14", "volume_price_score"]
    assert all(record.stock_id == "2330" for record in result.records)
    assert all(record.feature_group == "technical" for record in result.records)
    assert all(record.feature_version == "technical-v1" for record in result.records)
    assert all(record.available_for_signal_at == available_at for record in result.records)
