import math
from decimal import Decimal
from statistics import median
from typing import List

from app.schemas import PerformanceStatsInput, PerformanceStatsResult, SignalPerformanceStatsRecord
from app.services.objective_score_engine import ObjectiveScoreEngine


class PerformanceStatsEngine:
    """Aggregate backtest trades into auditable signal performance statistics."""

    def build_stats(self, request: PerformanceStatsInput) -> PerformanceStatsResult:
        result = request.backtest_result
        returns = [trade.net_return for trade in result.trades]
        wins = [value for value in returns if value > 0]
        losses = [value for value in returns if value < 0]
        trade_count = len(returns)
        win_rate = len(wins) / trade_count if trade_count else 0.0
        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = gross_profit / gross_loss if gross_loss else (gross_profit if gross_profit else 0.0)

        stats = SignalPerformanceStatsRecord(
            model_version=request.model_version,
            strategy_version=request.strategy_version,
            horizon_days=request.horizon_days,
            market_regime=request.market_regime,
            industry=request.industry,
            probability_bucket=request.probability_bucket,
            risk_bucket=request.risk_bucket,
            trade_count=trade_count,
            win_rate=self._decimal(win_rate),
            win_rate_lower_bound=self._decimal(ObjectiveScoreEngine().wilson_lower_bound(win_rate, trade_count)),
            avg_net_return=self._decimal(sum(returns) / trade_count if trade_count else 0.0),
            median_net_return=self._decimal(median(returns) if returns else 0.0),
            profit_factor=self._decimal(profit_factor),
            max_drawdown=self._decimal(self._max_drawdown(returns)),
            sharpe=self._decimal(self._sharpe(returns)),
            calibration_error=request.calibration_error,
        )
        return PerformanceStatsResult(stats=stats)

    def _max_drawdown(self, returns: List[float]) -> float:
        equity = 1.0
        peak = 1.0
        worst = 0.0
        for value in returns:
            equity *= 1 + value
            peak = max(peak, equity)
            worst = min(worst, equity / peak - 1)
        return worst

    def _sharpe(self, returns: List[float]) -> float:
        if len(returns) < 2:
            return 0.0
        avg = sum(returns) / len(returns)
        variance = sum((value - avg) ** 2 for value in returns) / (len(returns) - 1)
        std = math.sqrt(variance)
        if std == 0:
            return 0.0
        return avg / std * math.sqrt(252 / max(1, len(returns)))

    def _decimal(self, value: float) -> Decimal:
        return Decimal(str(round(value, 8)))
