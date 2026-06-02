from datetime import date
from decimal import Decimal

from app.schemas import TradeManagementConfig, TradeManagementRequest, TradeManagementResult


def test_trade_management_config_schema_tracks_default_rules() -> None:
    config = TradeManagementConfig()

    assert config.entry_method == "next_open"
    assert config.exit_method == "fixed_horizon_or_tp_sl"
    assert config.holding_days == [1, 5, 20]
    assert config.trailing_stop_enabled is True
    assert config.cooldown_days_after_loss == 3


def test_trade_management_request_schema_tracks_path_and_benchmark() -> None:
    request = TradeManagementRequest(
        signal_date=date(2026, 6, 2),
        stock_id="2330",
        entry_price=Decimal("100"),
        future_closes=[Decimal("101")],
        future_highs=[Decimal("102")],
        future_lows=[Decimal("99")],
        benchmark_entry_price=Decimal("100"),
        benchmark_future_closes=[Decimal("100.5")],
    )

    assert request.stock_id == "2330"
    assert request.benchmark_entry_price == Decimal("100")


def test_trade_management_result_schema_tracks_three_win_definitions() -> None:
    result = TradeManagementResult(
        stock_id="2330",
        signal_date=date(2026, 6, 2),
        horizon_days=5,
        entry_method="next_open",
        exit_method="fixed_horizon_or_tp_sl",
        exit_reason="take_profit",
        entry_price=Decimal("100"),
        exit_price=Decimal("105"),
        net_return=Decimal("0.047"),
        benchmark_return=Decimal("0.01"),
        fixed_horizon_win=1,
        tp_sl_win=1,
        relative_win=1,
        cooldown_active=False,
        applied_stop_loss_pct=Decimal("0.03"),
        applied_take_profit_pct=Decimal("0.05"),
    )

    assert result.fixed_horizon_win == 1
    assert result.tp_sl_win == 1
    assert result.relative_win == 1
