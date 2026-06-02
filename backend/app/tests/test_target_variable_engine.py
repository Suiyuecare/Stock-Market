from datetime import date, datetime, timezone
from decimal import Decimal

from app.schemas import TargetVariableConfig, TargetVariableRequest
from app.services.target_variable_engine import TargetVariableEngine


def _request(**overrides: object) -> TargetVariableRequest:
    values = {
        "signal_date": date(2026, 6, 2),
        "signal_time": datetime(2026, 6, 2, 15, 5, tzinfo=timezone.utc),
        "stock_id": "2330",
        "entry_price": Decimal("100"),
        "exit_prices": [Decimal("101"), Decimal("102"), Decimal("103"), Decimal("104"), Decimal("106")],
        "benchmark_entry_price": Decimal("100"),
        "benchmark_exit_prices": [Decimal("100.2"), Decimal("100.4"), Decimal("100.6"), Decimal("100.8"), Decimal("101")],
        "config": TargetVariableConfig(
            horizons=[1, 5],
            fee_rate=Decimal("0.001"),
            transaction_tax_rate=Decimal("0.001"),
            slippage=Decimal("0.001"),
            cost_buffer=Decimal("0.001"),
            minimum_excess_return=Decimal("0.002"),
        ),
    }
    values.update(overrides)
    return TargetVariableRequest(**values)


def _target(results, name: str):
    return next(result for result in results if result.target_name == name)


def test_target_variable_engine_builds_absolute_relative_and_tp_sl_targets() -> None:
    results = TargetVariableEngine().build(_request())

    assert _target(results, "y_abs_5d").target_value == 1
    assert _target(results, "y_rel_5d").target_value == 1
    assert _target(results, "y_tp_sl_5d").target_value == 1
    assert _target(results, "y_abs_5d").net_return == Decimal("0.057")
    assert _target(results, "y_rel_5d").benchmark_return == Decimal("0.01")


def test_target_variable_engine_relative_target_uses_benchmark_cost_and_excess_hurdle() -> None:
    request = _request(exit_prices=[Decimal("101"), Decimal("101"), Decimal("101"), Decimal("101"), Decimal("101.4")])
    results = TargetVariableEngine().build(request)

    assert _target(results, "y_abs_5d").target_value == 1
    assert _target(results, "y_rel_5d").target_value == 0


def test_target_variable_engine_primary_target_defaults_to_y_rel_5d() -> None:
    primary = TargetVariableEngine().primary_target(_request())

    assert primary is not None
    assert primary.target_name == "y_rel_5d"
    assert primary.horizon_days == 5


def test_target_variable_engine_tp_sl_respects_intraperiod_order() -> None:
    request = _request(
        intraperiod_highs=[Decimal("101"), Decimal("104"), Decimal("104"), Decimal("104"), Decimal("104")],
        intraperiod_lows=[Decimal("98"), Decimal("99"), Decimal("99"), Decimal("99"), Decimal("99")],
        config=TargetVariableConfig(horizons=[5], take_profit=Decimal("0.03"), stop_loss=Decimal("0.02")),
    )
    results = TargetVariableEngine().build(request)

    assert _target(results, "y_tp_sl_5d").target_value == 0
