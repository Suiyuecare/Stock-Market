import math
from typing import List

from app.schemas import ObjectiveScoreRequest, ObjectiveScoreResult


class ObjectiveScoreEngine:
    """Score strategy quality with sample-size-aware win rate and risk penalties."""

    def evaluate(self, request: ObjectiveScoreRequest) -> ObjectiveScoreResult:
        result = request.backtest_result
        config = request.config
        win_rate_lower_bound = self.wilson_lower_bound(result.win_rate, result.trade_count, config.z_score)
        average_net_return_score = self._positive_score(result.average_return, config.average_return_scale)
        profit_factor_score = self._positive_score(result.profit_factor - 1, config.profit_factor_scale - 1)
        calibration_score = self._clip(request.calibration_score)
        stability_score = self._clip(request.stability_score)
        max_drawdown_penalty = self._positive_score(abs(result.max_drawdown), config.max_drawdown_scale)

        objective_score = (
            config.win_rate_lower_bound_weight * win_rate_lower_bound
            + config.average_net_return_weight * average_net_return_score
            + config.profit_factor_weight * profit_factor_score
            + config.calibration_weight * calibration_score
            + config.stability_weight * stability_score
            - config.max_drawdown_penalty_weight * max_drawdown_penalty
        )
        adjusted_win_score = (
            win_rate_lower_bound
            + average_net_return_score
            + profit_factor_score
            - max_drawdown_penalty
            - self._turnover_penalty(result.turnover)
        )

        return ObjectiveScoreResult(
            objective_score=round(self._clip(objective_score) * 100, 4),
            win_rate_lower_bound=round(win_rate_lower_bound, 6),
            raw_win_rate=result.win_rate,
            average_net_return_score=round(average_net_return_score, 6),
            profit_factor_score=round(profit_factor_score, 6),
            calibration_score=round(calibration_score, 6),
            stability_score=round(stability_score, 6),
            max_drawdown_penalty=round(max_drawdown_penalty, 6),
            adjusted_win_score=round(adjusted_win_score, 6),
            trade_count=result.trade_count,
            positive_factors=self._positive_factors(
                win_rate_lower_bound,
                average_net_return_score,
                profit_factor_score,
                calibration_score,
                stability_score,
            ),
            negative_factors=self._negative_factors(result, win_rate_lower_bound),
            risk_factors=self._risk_factors(result, max_drawdown_penalty),
        )

    def wilson_lower_bound(self, win_rate: float, trade_count: int, z_score: float = 1.96) -> float:
        if trade_count <= 0:
            return 0.0
        p = self._clip(win_rate)
        denominator = 1 + z_score * z_score / trade_count
        centre = p + z_score * z_score / (2 * trade_count)
        margin = z_score * math.sqrt((p * (1 - p) + z_score * z_score / (4 * trade_count)) / trade_count)
        return self._clip((centre - margin) / denominator)

    def _positive_score(self, value: float, scale: float) -> float:
        if scale <= 0:
            return 0.0
        return self._clip(value / scale)

    def _turnover_penalty(self, turnover: float) -> float:
        return self._clip(turnover / 20)

    def _positive_factors(
        self,
        win_rate_lower_bound: float,
        average_net_return_score: float,
        profit_factor_score: float,
        calibration_score: float,
        stability_score: float,
    ) -> List[str]:
        factors: List[str] = []
        if win_rate_lower_bound >= 0.55:
            factors.append("Wilson lower-bound win rate is above the research threshold.")
        if average_net_return_score >= 0.5:
            factors.append("Average net return contributes positively after costs.")
        if profit_factor_score >= 0.5:
            factors.append("Profit factor indicates gains meaningfully exceed losses.")
        if calibration_score >= 0.7:
            factors.append("Predicted probabilities are well aligned with realized outcomes.")
        if stability_score >= 0.7:
            factors.append("Performance is stable across validation segments.")
        return factors

    def _negative_factors(self, result: object, win_rate_lower_bound: float) -> List[str]:
        factors: List[str] = []
        if win_rate_lower_bound < getattr(result, "win_rate"):
            factors.append("Win rate is discounted by sample-size uncertainty.")
        if getattr(result, "average_return") <= 0:
            factors.append("Average net return is not positive after costs.")
        if getattr(result, "profit_factor") < 1:
            factors.append("Profit factor is below 1, so losses exceed gains.")
        return factors

    def _risk_factors(self, result: object, max_drawdown_penalty: float) -> List[str]:
        factors: List[str] = []
        if max_drawdown_penalty >= 0.5:
            factors.append("Maximum drawdown creates a material objective-score penalty.")
        if getattr(result, "trade_count") < 100:
            factors.append("Trade sample is below the preferred fold-level minimum.")
        if getattr(result, "turnover") > 10:
            factors.append("High turnover can reduce realized edge after costs and slippage.")
        return factors

    def _clip(self, value: float) -> float:
        return max(0.0, min(1.0, value))
