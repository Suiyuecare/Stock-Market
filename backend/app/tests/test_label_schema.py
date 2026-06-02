from datetime import date, datetime, timezone
from decimal import Decimal

from app.schemas import LabelEngineRequest, LabelResult


def test_label_result_schema_tracks_multiple_label_fields() -> None:
    result = LabelResult(
        trade_date=date(2026, 6, 4),
        stock_id="2330",
        label_name="up_5d_relative",
        label_value=1,
        horizon_days=5,
        label_version="label-v1",
        forward_return=Decimal("0.05"),
        benchmark_return=Decimal("0.01"),
        excess_return=Decimal("0.04"),
        max_favorable_excursion=Decimal("0.05"),
        max_adverse_excursion=Decimal("0"),
        transaction_cost=Decimal("0.001"),
        minimum_excess_return=Decimal("0.002"),
        calculated_at=datetime(2026, 6, 11, 15, 0, tzinfo=timezone.utc),
        available_for_signal_at=datetime(2026, 6, 11, 15, 5, tzinfo=timezone.utc),
    )

    assert result.label_name == "up_5d_relative"
    assert result.excess_return == Decimal("0.04")


def test_label_engine_request_can_choose_optimization_target_inputs() -> None:
    request = LabelEngineRequest(
        trade_date=date(2026, 6, 4),
        stock_id="2330",
        closes=[Decimal("100"), Decimal("105")],
        benchmark_closes=[Decimal("100"), Decimal("101")],
        horizon_days=1,
        transaction_cost=Decimal("0.001"),
        minimum_excess_return=Decimal("0.002"),
        take_profit=Decimal("0.03"),
        stop_loss=Decimal("0.02"),
        available_for_signal_at=datetime(2026, 6, 5, 15, 5, tzinfo=timezone.utc),
    )

    assert request.horizon_days == 1
    assert request.take_profit == Decimal("0.03")
