from datetime import date, datetime, timezone
from decimal import Decimal

from app.schemas import TargetVariableConfig, TargetVariableRequest, TargetVariableResult


def test_target_variable_config_declares_primary_model_target() -> None:
    config = TargetVariableConfig()

    assert config.horizons == [1, 5, 20]
    assert config.primary_target == "y_rel_5d"
    assert config.entry_price_type == "next_open"


def test_target_variable_request_tracks_signal_time_entry_and_exit_prices() -> None:
    request = TargetVariableRequest(
        signal_date=date(2026, 6, 2),
        signal_time=datetime(2026, 6, 2, 15, 5, tzinfo=timezone.utc),
        stock_id="2330",
        entry_price=Decimal("100"),
        exit_prices=[Decimal("101"), Decimal("102")],
    )

    assert request.signal_time.isoformat() == "2026-06-02T15:05:00+00:00"
    assert request.entry_price == Decimal("100")


def test_target_variable_result_schema_keeps_net_return_and_costs() -> None:
    result = TargetVariableResult(
        signal_date=date(2026, 6, 2),
        signal_time=datetime(2026, 6, 2, 15, 5, tzinfo=timezone.utc),
        stock_id="2330",
        target_name="y_rel_5d",
        horizon_days=5,
        target_value=1,
        net_return=Decimal("0.057"),
        benchmark_return=Decimal("0.01"),
        excess_return=Decimal("0.047"),
        entry_price=Decimal("100"),
        exit_price=Decimal("106"),
        total_cost=Decimal("0.003"),
        target_version="target-v1",
    )

    assert result.target_name == "y_rel_5d"
    assert result.total_cost == Decimal("0.003")
