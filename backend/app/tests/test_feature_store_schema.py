from datetime import date, datetime, timezone
from decimal import Decimal

from app.schemas import FeatureStoreDailyInput, FeatureStoreQuery


def test_feature_store_schema_tracks_versioned_feature_value() -> None:
    feature = FeatureStoreDailyInput(
        trade_date=date(2026, 6, 4),
        stock_id="2330",
        feature_group="technical",
        feature_name="rsi14",
        feature_value=Decimal("61.25000000"),
        feature_version="technical-v1",
        calculated_at=datetime(2026, 6, 4, 15, 0, tzinfo=timezone.utc),
        available_for_signal_at=datetime(2026, 6, 4, 15, 5, tzinfo=timezone.utc),
    )

    assert feature.feature_value == Decimal("61.25000000")
    assert feature.feature_version == "technical-v1"


def test_feature_store_query_represents_point_in_time_cutoff() -> None:
    query = FeatureStoreQuery(
        stock_id="2330",
        trade_date=date(2026, 6, 4),
        signal_generated_at=datetime(2026, 6, 5, 9, 0, tzinfo=timezone.utc),
        feature_group="technical",
    )

    assert query.feature_group == "technical"
    assert query.signal_generated_at.isoformat() == "2026-06-05T09:00:00+00:00"
