from app.schemas import BacktestResult, ObjectiveScoreRequest
from app.services.objective_score_engine import ObjectiveScoreEngine


def _result(win_rate: float, trade_count: int) -> BacktestResult:
    return BacktestResult(
        win_rate=win_rate,
        trade_count=trade_count,
        average_return=0.018,
        median_return=0.01,
        expectancy=0.012,
        max_drawdown=-0.08,
        profit_factor=1.8,
        sharpe_ratio=1.2,
        sortino_ratio=1.5,
        max_single_loss=-0.05,
        max_consecutive_losses=3,
        average_holding_days=5,
        turnover=2,
        win_rate_by_sector={"semiconductor": win_rate},
        win_rate_by_market_state={"bull": win_rate},
        trades=[],
    )


def test_wilson_lower_bound_discounts_small_high_win_sample() -> None:
    engine = ObjectiveScoreEngine()
    small_sample = engine.evaluate(ObjectiveScoreRequest(backtest_result=_result(0.9, 10)))
    large_sample = engine.evaluate(ObjectiveScoreRequest(backtest_result=_result(0.62, 1000)))

    assert small_sample.raw_win_rate - small_sample.win_rate_lower_bound > 0.25
    assert large_sample.raw_win_rate - large_sample.win_rate_lower_bound < 0.05
    assert small_sample.raw_win_rate > large_sample.raw_win_rate
    assert "Trade sample is below the preferred fold-level minimum." in small_sample.risk_factors


def test_objective_score_combines_return_profit_factor_calibration_and_stability() -> None:
    result = ObjectiveScoreEngine().evaluate(
        ObjectiveScoreRequest(
            backtest_result=_result(0.64, 800),
            calibration_score=0.85,
            stability_score=0.80,
        )
    )

    assert result.objective_score > 50
    assert result.average_net_return_score == 0.6
    assert result.profit_factor_score == 0.8
    assert result.calibration_score == 0.85
    assert result.stability_score == 0.8
    assert result.positive_factors


def test_objective_score_penalizes_drawdown_and_negative_expectancy() -> None:
    backtest = _result(0.55, 200)
    backtest.average_return = -0.01
    backtest.profit_factor = 0.8
    backtest.max_drawdown = -0.30

    result = ObjectiveScoreEngine().evaluate(ObjectiveScoreRequest(backtest_result=backtest))

    assert result.max_drawdown_penalty == 1.0
    assert "Average net return is not positive after costs." in result.negative_factors
    assert "Profit factor is below 1, so losses exceed gains." in result.negative_factors
    assert result.risk_factors


def test_objective_score_flags_low_trade_count_as_risk() -> None:
    result = ObjectiveScoreEngine().evaluate(ObjectiveScoreRequest(backtest_result=_result(0.7, 50)))

    assert "Trade sample is below the preferred fold-level minimum." in result.risk_factors
