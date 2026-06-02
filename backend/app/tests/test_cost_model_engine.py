from decimal import Decimal

from app.schemas import CostModelConfig, CostModelRequest
from app.services.cost_model_engine import CostModelEngine


def test_cost_model_calculates_commission_tax_and_large_cap_slippage() -> None:
    result = CostModelEngine().calculate(
        CostModelRequest(
            buy_notional=Decimal("100000"),
            sell_notional=Decimal("105000"),
            market_cap_bucket="large_cap",
        )
    )

    assert result.commission_buy == Decimal("142.500000")
    assert result.commission_sell == Decimal("149.625000")
    assert result.transaction_tax == Decimal("315.000")
    assert result.slippage_buy == Decimal("30")
    assert result.slippage_sell == Decimal("31.5")
    assert result.total_cost == Decimal("668.625000")
    assert result.total_cost_rate == Decimal("0.00668625")


def test_cost_model_applies_minimum_fee_for_small_notional() -> None:
    result = CostModelEngine().calculate(
        CostModelRequest(
            buy_notional=Decimal("5000"),
            sell_notional=Decimal("5000"),
            market_cap_bucket="large_cap",
        )
    )

    assert result.commission_buy == Decimal("20")
    assert result.commission_sell == Decimal("20")


def test_cost_model_uses_higher_slippage_for_smaller_cap_buckets() -> None:
    engine = CostModelEngine()
    large = engine.calculate(CostModelRequest(buy_notional=Decimal("100000"), sell_notional=Decimal("100000")))
    mid = engine.calculate(
        CostModelRequest(buy_notional=Decimal("100000"), sell_notional=Decimal("100000"), market_cap_bucket="mid_cap")
    )
    small = engine.calculate(
        CostModelRequest(buy_notional=Decimal("100000"), sell_notional=Decimal("100000"), market_cap_bucket="small_cap")
    )

    assert large.slippage_buy == Decimal("30")
    assert mid.slippage_buy == Decimal("80")
    assert small.slippage_buy == Decimal("150")
    assert small.total_cost > mid.total_cost > large.total_cost


def test_cost_model_supports_configurable_etf_or_broker_costs() -> None:
    config = CostModelConfig(
        commission_rate_buy=Decimal("0.0005"),
        commission_rate_sell=Decimal("0.0005"),
        transaction_tax_rate=Decimal("0"),
        min_fee=Decimal("1"),
        instrument_type="etf",
        broker="custom-broker",
    )
    result = CostModelEngine().calculate(
        CostModelRequest(
            buy_notional=Decimal("100000"),
            sell_notional=Decimal("100000"),
            market_cap_bucket="large_cap",
            config=config,
        )
    )

    assert result.commission_buy == Decimal("50.0000")
    assert result.commission_sell == Decimal("50.0000")
    assert result.transaction_tax == Decimal("0")
    assert result.instrument_type == "etf"
    assert result.broker == "custom-broker"
