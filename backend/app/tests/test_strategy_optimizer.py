from app.schemas import (
    BacktestResult,
    StrategyOptimizationCandidate,
    StrategyOptimizationConfig,
    StrategyParameterSet,
)
from app.services.strategy_optimizer import StrategyOptimizer


def _result(
    win_rate: float,
    trade_count: int,
    average_return: float = 0.018,
    profit_factor: float = 1.6,
    max_drawdown: float = -0.08,
) -> BacktestResult:
    return BacktestResult(
        win_rate=win_rate,
        trade_count=trade_count,
        average_return=average_return,
        median_return=average_return / 2,
        expectancy=average_return,
        max_drawdown=max_drawdown,
        profit_factor=profit_factor,
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


def _candidate(strategy_version: str, result: BacktestResult, confidence: float = 0.75) -> StrategyOptimizationCandidate:
    return StrategyOptimizationCandidate(
        parameters=StrategyParameterSet(strategy_version=strategy_version),
        backtest_result=result,
        calibration_error=0.04,
        stability_score=0.82,
        confidence=confidence,
    )


def test_strategy_optimizer_rejects_small_samples_even_with_high_raw_win_rate() -> None:
    optimization = StrategyOptimizer().optimize(
        [
            _candidate("tiny-high-win", _result(0.9, 12)),
            _candidate("robust-validated", _result(0.62, 700)),
        ],
        StrategyOptimizationConfig(min_total_trades=500),
    )

    assert optimization.best_strategy_version == "robust-validated"
    assert optimization.best_parameters.strategy_version == "robust-validated"
    assert optimization.ranked_results[0].passed_constraints is True
    assert optimization.rejected_results[0].strategy_version == "tiny-high-win"
    assert "Trade count is below the minimum total sample requirement." in optimization.rejected_results[0].rejection_reasons


def test_strategy_optimizer_applies_return_profit_factor_drawdown_and_confidence_constraints() -> None:
    optimization = StrategyOptimizer().optimize(
        [
            _candidate("negative-return", _result(0.65, 800, average_return=-0.001)),
            _candidate("weak-profit-factor", _result(0.65, 800, profit_factor=1.05)),
            _candidate("large-drawdown", _result(0.65, 800, max_drawdown=-0.35)),
            _candidate("low-confidence", _result(0.65, 800), confidence=0.4),
        ],
        StrategyOptimizationConfig(min_total_trades=500, max_drawdown_limit=0.2),
    )

    assert optimization.best_strategy_version is None
    assert len(optimization.ranked_results) == 0
    assert len(optimization.rejected_results) == 4
    reasons = {reason for result in optimization.rejected_results for reason in result.rejection_reasons}
    assert "Average net return is not positive after costs." in reasons
    assert "Profit factor is below the configured threshold." in reasons
    assert "Maximum drawdown is above the configured risk limit." in reasons
    assert "Signal confidence is below the configured threshold." in reasons


def test_strategy_optimizer_ranks_by_objective_after_constraints() -> None:
    optimization = StrategyOptimizer().optimize(
        [
            _candidate("stable-base", _result(0.61, 900, average_return=0.014, profit_factor=1.45)),
            _candidate("stronger-edge", _result(0.64, 900, average_return=0.022, profit_factor=1.9)),
        ],
        StrategyOptimizationConfig(min_total_trades=500),
    )

    assert optimization.best_strategy_version == "stronger-edge"
    assert optimization.best_objective_score > optimization.ranked_results[1].objective.objective_score
    assert optimization.ranked_results[0].objective.trade_count == 900
