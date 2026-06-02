from typing import List

from app.schemas import (
    ObjectiveScoreRequest,
    StrategyOptimizationCandidate,
    StrategyOptimizationConfig,
    StrategyOptimizationResult,
    StrategyOptimizationSummary,
)
from app.services.objective_score_engine import ObjectiveScoreEngine


class StrategyOptimizer:
    """Rank strategy parameter sets by objective score after hard constraints."""

    def __init__(self) -> None:
        self.objective_engine = ObjectiveScoreEngine()

    def optimize(
        self,
        candidates: List[StrategyOptimizationCandidate],
        config: StrategyOptimizationConfig = StrategyOptimizationConfig(),
    ) -> StrategyOptimizationResult:
        ranked: List[StrategyOptimizationSummary] = []
        rejected: List[StrategyOptimizationSummary] = []

        for candidate in candidates:
            rejection_reasons = self._constraint_failures(candidate, config)
            if rejection_reasons:
                rejected.append(
                    StrategyOptimizationSummary(
                        strategy_version=candidate.parameters.strategy_version,
                        passed_constraints=False,
                        rejection_reasons=rejection_reasons,
                    )
                )
                continue

            objective = self.objective_engine.evaluate(
                ObjectiveScoreRequest(
                    backtest_result=candidate.backtest_result,
                    calibration_score=self._calibration_score(candidate, config),
                    stability_score=candidate.stability_score or config.default_stability_score,
                )
            )
            ranked.append(
                StrategyOptimizationSummary(
                    strategy_version=candidate.parameters.strategy_version,
                    passed_constraints=True,
                    rejection_reasons=[],
                    objective=objective,
                )
            )

        ranked.sort(key=lambda summary: summary.objective.objective_score if summary.objective else 0.0, reverse=True)
        best = self._find_candidate(candidates, ranked[0].strategy_version) if ranked else None

        return StrategyOptimizationResult(
            best_strategy_version=ranked[0].strategy_version if ranked else None,
            best_objective_score=ranked[0].objective.objective_score if ranked and ranked[0].objective else None,
            best_parameters=best.parameters if best else None,
            ranked_results=ranked,
            rejected_results=rejected,
        )

    def _constraint_failures(
        self,
        candidate: StrategyOptimizationCandidate,
        config: StrategyOptimizationConfig,
    ) -> List[str]:
        result = candidate.backtest_result
        failures: List[str] = []
        if result.trade_count < config.min_total_trades:
            failures.append("Trade count is below the minimum total sample requirement.")
        if result.trade_count < config.min_trades_per_fold:
            failures.append("Trade count is below the preferred fold-level minimum.")
        if result.average_return <= config.min_average_net_return:
            failures.append("Average net return is not positive after costs.")
        if result.profit_factor < config.min_profit_factor:
            failures.append("Profit factor is below the configured threshold.")
        if abs(result.max_drawdown) > config.max_drawdown_limit:
            failures.append("Maximum drawdown is above the configured risk limit.")
        if candidate.confidence < config.min_confidence:
            failures.append("Signal confidence is below the configured threshold.")
        return failures

    def _calibration_score(
        self,
        candidate: StrategyOptimizationCandidate,
        config: StrategyOptimizationConfig,
    ) -> float:
        if candidate.calibration_error <= 0:
            return config.default_calibration_score
        return max(0.0, min(1.0, 1 - candidate.calibration_error))

    def _find_candidate(
        self,
        candidates: List[StrategyOptimizationCandidate],
        strategy_version: str,
    ) -> StrategyOptimizationCandidate:
        for candidate in candidates:
            if candidate.parameters.strategy_version == strategy_version:
                return candidate
        raise ValueError(f"Unknown strategy version: {strategy_version}")
