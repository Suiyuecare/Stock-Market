from datetime import date
from decimal import Decimal

from app.schemas import TradeManagementConfig, TradeManagementRequest
from app.schemas import CostModelRequest
from app.services.cost_model_engine import CostModelEngine
from app.services.trade_management_engine import TradeManagementEngine


def _request(**overrides: object) -> TradeManagementRequest:
    values = {
        "signal_date": date(2026, 6, 2),
        "stock_id": "2330",
        "entry_price": Decimal("100"),
        "future_closes": [Decimal("101"), Decimal("102"), Decimal("103"), Decimal("104"), Decimal("106")],
        "future_highs": [Decimal("101"), Decimal("102"), Decimal("104"), Decimal("105"), Decimal("106")],
        "future_lows": [Decimal("99"), Decimal("100"), Decimal("101"), Decimal("102"), Decimal("103")],
        "benchmark_entry_price": Decimal("100"),
        "benchmark_future_closes": [Decimal("100.2"), Decimal("100.4"), Decimal("100.6"), Decimal("100.8"), Decimal("101")],
        "config": TradeManagementConfig(
            holding_days=[1, 5],
            fee_rate=Decimal("0.001"),
            transaction_tax_rate=Decimal("0.001"),
            slippage=Decimal("0.001"),
            take_profit_pct_range=[Decimal("0.05"), Decimal("0.15")],
            stop_loss_pct_range=[Decimal("0.03"), Decimal("0.08")],
            trailing_stop_enabled=False,
        ),
    }
    values.update(overrides)
    return TradeManagementRequest(**values)


def test_trade_management_builds_fixed_tp_sl_and_relative_wins() -> None:
    results = TradeManagementEngine().evaluate(_request())
    five_day = next(result for result in results if result.horizon_days == 5)

    assert five_day.exit_reason == "take_profit"
    assert five_day.tp_sl_win == 1
    assert five_day.fixed_horizon_win == 1
    assert five_day.relative_win == 1
    assert five_day.net_return == Decimal("0.047")


def test_trade_management_stop_loss_wins_false_when_stop_touched_first() -> None:
    request = _request(
        future_closes=[Decimal("99"), Decimal("98"), Decimal("101"), Decimal("105"), Decimal("106")],
        future_highs=[Decimal("101"), Decimal("102"), Decimal("105"), Decimal("106"), Decimal("107")],
        future_lows=[Decimal("99"), Decimal("96"), Decimal("98"), Decimal("100"), Decimal("101")],
    )
    result = next(item for item in TradeManagementEngine().evaluate(request) if item.horizon_days == 5)

    assert result.exit_reason == "stop_loss"
    assert result.tp_sl_win == 0
    assert result.exit_price == Decimal("97.00")


def test_trade_management_relative_win_uses_benchmark_plus_cost_buffer() -> None:
    request = _request(
        future_closes=[Decimal("101"), Decimal("101"), Decimal("101"), Decimal("101"), Decimal("101.2")],
        future_highs=[Decimal("101"), Decimal("101"), Decimal("101"), Decimal("101"), Decimal("101.2")],
        future_lows=[Decimal("100"), Decimal("100"), Decimal("100"), Decimal("100"), Decimal("100")],
    )
    result = next(item for item in TradeManagementEngine().evaluate(request) if item.horizon_days == 5)

    assert result.fixed_horizon_win == 1
    assert result.relative_win == 0


def test_trade_management_applies_atr_stop_and_cooldown() -> None:
    request = _request(
        atr=Decimal("4"),
        recent_loss_dates=[date(2026, 6, 1)],
        config=TradeManagementConfig(holding_days=[5], trailing_stop_enabled=False, trailing_stop_atr=Decimal("1.5")),
    )
    result = TradeManagementEngine().evaluate(request)[0]

    assert result.applied_stop_loss_pct == Decimal("0.06")
    assert result.cooldown_active is True


def test_trade_management_trailing_stop_can_exit_before_horizon() -> None:
    request = _request(
        future_closes=[Decimal("101"), Decimal("102"), Decimal("101"), Decimal("100"), Decimal("99")],
        future_highs=[Decimal("102"), Decimal("104"), Decimal("104"), Decimal("103"), Decimal("100")],
        future_lows=[Decimal("100"), Decimal("102"), Decimal("100.5"), Decimal("99"), Decimal("98")],
        atr=Decimal("2"),
        config=TradeManagementConfig(holding_days=[5], trailing_stop_enabled=True, trailing_stop_atr=Decimal("1.5")),
    )
    result = TradeManagementEngine().evaluate(request)[0]

    assert result.exit_reason == "trailing_stop"


def test_trade_management_can_use_configurable_cost_model_rate() -> None:
    cost = CostModelEngine().calculate(
        CostModelRequest(
            buy_notional=Decimal("100000"),
            sell_notional=Decimal("100000"),
            market_cap_bucket="small_cap",
        )
    )
    request = _request(total_cost_rate=cost.total_cost_rate)
    result = next(item for item in TradeManagementEngine().evaluate(request) if item.horizon_days == 5)

    assert result.exit_reason == "take_profit"
    assert result.net_return == Decimal("0.05") - cost.total_cost_rate
