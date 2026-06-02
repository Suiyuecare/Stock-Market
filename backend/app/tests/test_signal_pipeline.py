from datetime import date
from decimal import Decimal

from app.schemas import SignalOutcomeRecord, SignalPerformanceStatsRecord, SignalRecord
from app.services.signal_pipeline import SignalPipeline


def test_signal_pipeline_runs_ten_mvp_steps_with_mock_data() -> None:
    result = SignalPipeline().run(trade_date=date(2026, 6, 5))

    assert result.trade_date == date(2026, 6, 5)
    assert len(result.steps) == 10
    assert result.steps[0].name == "Create after-close feature snapshot"
    assert result.steps[-1].name == "Update win-rate performance statistics"
    assert result.generated_signal_count >= result.watchlist_count
    assert result.model_version == "mock-model-v1"
    assert result.strategy_version == "mvp-default-v1"


def test_signal_pipeline_schemas_match_signal_tables() -> None:
    signal = SignalRecord(
        signal_id="sig-1",
        generated_at=date(2026, 6, 4),
        trade_date=date(2026, 6, 5),
        stock_id="2330",
        horizon_days=5,
        probability_up=Decimal("0.64"),
        bullish_score=Decimal("72"),
        risk_score=Decimal("35"),
        risk_adjusted_score=Decimal("59.75"),
        confidence=Decimal("0.70"),
        signal_rank=1,
        selected_for_watchlist=True,
        model_version="model-v1",
        feature_version="feature-v1",
    )
    outcome = SignalOutcomeRecord(
        signal_id=signal.signal_id,
        entry_date=date(2026, 6, 5),
        entry_price=Decimal("100"),
        exit_date=date(2026, 6, 12),
        exit_price=Decimal("104"),
        gross_return=Decimal("0.04"),
        net_return=Decimal("0.035"),
        win_absolute=True,
        holding_days=5,
    )
    stats = SignalPerformanceStatsRecord(
        model_version="model-v1",
        strategy_version="mvp-default-v1",
        horizon_days=5,
        market_regime="bull_market",
        industry="semiconductor",
        probability_bucket="0.60-0.65",
        risk_bucket="30-40",
        trade_count=120,
        win_rate=Decimal("0.62"),
        win_rate_lower_bound=Decimal("0.53"),
        avg_net_return=Decimal("0.018"),
        median_net_return=Decimal("0.011"),
        profit_factor=Decimal("1.45"),
        max_drawdown=Decimal("-0.08"),
        sharpe=Decimal("1.2"),
        calibration_error=Decimal("0.03"),
    )

    assert signal.selected_for_watchlist is True
    assert outcome.win_absolute is True
    assert stats.win_rate_lower_bound == Decimal("0.53")
