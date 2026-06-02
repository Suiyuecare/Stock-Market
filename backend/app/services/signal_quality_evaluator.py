from app.schemas import SignalQualityInput, SignalQualityResult, SignalQualityThresholds


class SignalQualityEvaluator:
    """Evaluate signal quality beyond raw win rate."""

    def evaluate(
        self,
        metrics: SignalQualityInput,
        thresholds: SignalQualityThresholds = SignalQualityThresholds(),
    ) -> SignalQualityResult:
        reasons = []
        warnings = []

        if metrics.win_rate >= thresholds.minimum_win_rate:
            reasons.append("Win rate meets the minimum threshold.")
        else:
            warnings.append("Win rate is below the minimum threshold.")

        if metrics.expectancy > thresholds.minimum_expectancy:
            reasons.append("Expectancy is positive after costs.")
        else:
            warnings.append("Expectancy is not positive after costs.")

        if metrics.average_return > thresholds.minimum_average_return:
            reasons.append("Average return remains positive after costs.")
        else:
            warnings.append("Average return is not positive after costs.")

        if metrics.trade_count >= thresholds.minimum_trade_count:
            reasons.append("Sample count is sufficient.")
        else:
            warnings.append("Sample count is too small to trust the signal.")

        if abs(metrics.max_drawdown) <= thresholds.maximum_drawdown:
            reasons.append("Max drawdown is within the acceptable threshold.")
        else:
            warnings.append("Max drawdown exceeds the acceptable threshold.")

        if metrics.profit_factor >= thresholds.minimum_profit_factor:
            reasons.append("Profit Factor is above the minimum threshold.")
        else:
            warnings.append("Profit Factor is below the minimum threshold.")

        quality_score = self._quality_score(metrics, thresholds)
        passed = not warnings and quality_score >= 70
        return SignalQualityResult(
            passed=passed,
            quality_grade=self._grade(quality_score, passed),
            quality_score=quality_score,
            reasons=reasons,
            warnings=warnings,
            metrics={
                "win_rate": metrics.win_rate,
                "trade_count": float(metrics.trade_count),
                "average_return": metrics.average_return,
                "expectancy": metrics.expectancy,
                "max_drawdown": metrics.max_drawdown,
                "profit_factor": metrics.profit_factor,
                "max_single_loss": metrics.max_single_loss,
                "transaction_cost": metrics.transaction_cost,
                "slippage": metrics.slippage,
            },
        )

    def _quality_score(self, metrics: SignalQualityInput, thresholds: SignalQualityThresholds) -> float:
        win_rate_score = min(metrics.win_rate / thresholds.minimum_win_rate, 1.4) / 1.4 * 25
        expectancy_score = 25 if metrics.expectancy > thresholds.minimum_expectancy else 0
        sample_score = min(metrics.trade_count / thresholds.minimum_trade_count, 1.0) * 15
        drawdown_score = max(0.0, 1 - abs(metrics.max_drawdown) / thresholds.maximum_drawdown) * 15
        average_return_score = 10 if metrics.average_return > thresholds.minimum_average_return else 0
        profit_factor_score = min(metrics.profit_factor / thresholds.minimum_profit_factor, 1.3) / 1.3 * 10
        return round(win_rate_score + expectancy_score + sample_score + drawdown_score + average_return_score + profit_factor_score, 4)

    def _grade(self, quality_score: float, passed: bool) -> str:
        if not passed:
            return "rejected"
        if quality_score >= 85:
            return "excellent"
        if quality_score >= 70:
            return "acceptable"
        return "watch"
