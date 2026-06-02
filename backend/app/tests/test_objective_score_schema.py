from app.schemas import BacktestResult, ObjectiveScoreConfig, ObjectiveScoreRequest, ObjectiveScoreResult


def _backtest_result() -> BacktestResult:
    return BacktestResult(
        win_rate=0.62,
        trade_count=1000,
        average_return=0.01,
        median_return=0.005,
        expectancy=0.008,
        max_drawdown=-0.08,
        profit_factor=1.5,
        sharpe_ratio=1.0,
        sortino_ratio=1.2,
        max_single_loss=-0.03,
        max_consecutive_losses=4,
        average_holding_days=5,
        turnover=3,
        win_rate_by_sector={},
        win_rate_by_market_state={},
        trades=[],
    )


def test_objective_score_config_defaults_match_formula_weights() -> None:
    config = ObjectiveScoreConfig()

    assert config.win_rate_lower_bound_weight == 0.40
    assert config.average_net_return_weight == 0.20
    assert config.profit_factor_weight == 0.15
    assert config.calibration_weight == 0.10
    assert config.stability_weight == 0.10
    assert config.max_drawdown_penalty_weight == 0.05


def test_objective_score_request_and_result_schema() -> None:
    request = ObjectiveScoreRequest(
        backtest_result=_backtest_result(),
        calibration_score=0.8,
        stability_score=0.75,
    )
    result = ObjectiveScoreResult(
        objective_score=61.2,
        win_rate_lower_bound=0.58,
        raw_win_rate=request.backtest_result.win_rate,
        average_net_return_score=0.4,
        profit_factor_score=0.5,
        calibration_score=request.calibration_score,
        stability_score=request.stability_score,
        max_drawdown_penalty=0.4,
        adjusted_win_score=1.08,
        trade_count=request.backtest_result.trade_count,
        positive_factors=["Stable validation result."],
        negative_factors=[],
        risk_factors=[],
    )

    assert result.objective_score == 61.2
    assert result.trade_count == 1000
