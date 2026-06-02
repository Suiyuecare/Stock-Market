from typing import List, Tuple

from app.schemas import SignalAntiPatternConfig, SignalAntiPatternInput, SignalAntiPatternResult


class SignalAntiPatternGuard:
    """Reject signals that rely on a single misleading indicator or narrative."""

    def evaluate(
        self,
        signal: SignalAntiPatternInput,
        config: SignalAntiPatternConfig = SignalAntiPatternConfig(),
    ) -> SignalAntiPatternResult:
        quality_gates_passed: List[str] = []
        quality_gates_failed: List[str] = []
        warnings: List[str] = []

        gates: List[Tuple[bool, str, str]] = [
            (
                signal.probability_up >= config.min_probability_up,
                "Model probability is above the minimum threshold.",
                "model_probability_below_threshold",
            ),
            (
                signal.risk_score <= config.max_risk_score,
                "RiskScore is acceptable.",
                "risk_score_above_threshold",
            ),
            (
                signal.trade_sample_count >= config.min_trade_sample_count,
                "Historical sample count is sufficient.",
                "sample_count_below_threshold",
            ),
            (
                signal.factor_alignment_count >= config.min_factor_alignment_count,
                "Multiple independent factors are aligned.",
                "insufficient_multi_factor_alignment",
            ),
            (
                signal.net_expectancy_after_costs > config.min_net_expectancy_after_costs,
                "Expected value remains positive after transaction costs.",
                "expectancy_not_positive_after_costs",
            ),
            (
                signal.yearly_stability_score >= config.min_yearly_stability_score,
                "Signal remains stable across different years.",
                "yearly_stability_below_threshold",
            ),
            (
                signal.market_regime_stability_score >= config.min_market_regime_stability_score,
                "Signal does not materially fail across market regimes.",
                "market_regime_stability_below_threshold",
            ),
        ]

        for passed, success, failure in gates:
            if passed:
                quality_gates_passed.append(success)
            else:
                quality_gates_failed.append(failure)

        anti_patterns = self._anti_patterns(signal)
        if anti_patterns:
            warnings.append("Signal appears to rely on a single indicator or narrative.")

        passed = not quality_gates_failed and not anti_patterns
        return SignalAntiPatternResult(
            stock_id=signal.stock_id,
            signal_date=signal.signal_date,
            passed=passed,
            quality_gates_passed=quality_gates_passed,
            quality_gates_failed=quality_gates_failed,
            anti_patterns=anti_patterns,
            warnings=warnings,
        )

    def _anti_patterns(self, signal: SignalAntiPatternInput) -> List[str]:
        single_factor_flags = [
            ("single_macd_golden_cross", signal.has_macd_golden_cross),
            ("single_foreign_net_buy", signal.has_foreign_net_buy),
            ("single_nvda_spike", signal.has_nvda_spike),
            ("single_positive_news", signal.has_positive_news),
            ("single_technical_breakout", signal.has_technical_breakout),
            ("single_high_model_probability", signal.probability_up >= 0.70),
        ]
        active = [name for name, enabled in single_factor_flags if enabled]
        if len(active) == 1 and signal.factor_alignment_count <= 1:
            return active
        if "single_high_model_probability" in active and signal.factor_alignment_count < 2:
            return ["single_high_model_probability"]
        return []
