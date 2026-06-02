from typing import List

from app.schemas import (
    SignalSelectionBatchResult,
    SignalSelectionCandidate,
    SignalSelectionConfig,
    SignalSelectionInput,
    SignalSelectionResult,
    SignalSelectionThresholds,
)


class SignalSelectionLayer:
    """Filter probability outputs into research watchlist decisions."""

    def evaluate(
        self,
        signal: SignalSelectionInput,
        config: SignalSelectionConfig = SignalSelectionConfig(),
    ) -> SignalSelectionResult:
        reasons: List[str] = []
        warnings: List[str] = []
        risk_flags: List[str] = []

        if signal.probability_up < config.minimum_probability:
            reasons.append("Probability is below the signal threshold.")
            return self._result(signal, False, "excluded", 0, reasons, warnings, risk_flags)

        reasons.append("Probability passed the signal threshold.")

        if signal.liquidity_score < config.minimum_liquidity_score:
            reasons.append("Liquidity is below the minimum threshold.")
            risk_flags.append("insufficient_liquidity")
            return self._result(signal, False, "excluded", 0, reasons, warnings, risk_flags)

        if signal.has_major_negative_event:
            reasons.append("A major negative event is active.")
            risk_flags.append("major_negative_event")
            return self._result(signal, False, "excluded", 0, reasons, warnings, risk_flags)

        if signal.is_high_risk_event_window:
            reason = signal.event_window_reason or "High-risk event window is active."
            warnings.append(reason)
            risk_flags.append("high_risk_event_window")

        if signal.calibration_sample_count < config.minimum_sample_count:
            warnings.append("Historical sample count is below the confidence threshold.")
            risk_flags.append("insufficient_sample_count")

        if signal.confidence < config.minimum_confidence:
            warnings.append("Model confidence is below the selection threshold.")
            risk_flags.append("low_confidence")

        if signal.risk_score >= config.high_risk_threshold:
            warnings.append("RiskScore is too high for the primary watchlist.")
            risk_flags.append("high_risk_score")

        if signal.us_market_score >= config.us_positive_threshold and signal.chip_score < config.chip_weak_threshold:
            warnings.append("US linkage is positive, but Taiwan institutional/chip score is weak.")
            risk_flags.append("us_positive_chip_weak")

        if "high_risk_score" in risk_flags or "high_risk_event_window" in risk_flags:
            return self._result(signal, True, "high_risk_watchlist", 2, reasons, warnings, risk_flags)

        if "insufficient_sample_count" in risk_flags or "low_confidence" in risk_flags or "us_positive_chip_weak" in risk_flags:
            return self._result(signal, True, "low_confidence_watchlist", 1, reasons, warnings, risk_flags)

        return self._result(signal, True, "primary_watchlist", 3, reasons, warnings, risk_flags)

    def select_batch(
        self,
        candidates: List[SignalSelectionCandidate],
        thresholds: SignalSelectionThresholds = SignalSelectionThresholds(),
    ) -> SignalSelectionBatchResult:
        eligible: List[SignalSelectionCandidate] = []
        rejected: List[SignalSelectionResult] = []

        for candidate in candidates:
            result = self._evaluate_candidate(candidate, thresholds)
            if result.selected:
                eligible.append(candidate)
            else:
                rejected.append(result)

        ranked = sorted(
            eligible,
            key=lambda item: (item.risk_adjusted_score, item.expected_return_5d, item.probability_up_5d),
            reverse=True,
        )
        selected: List[SignalSelectionCandidate] = []
        industry_counts: dict[str, int] = {}
        for candidate in ranked:
            if len(selected) >= thresholds.top_k_per_day:
                rejected.append(
                    self._candidate_result(candidate, False, "excluded", ["Daily top-k limit reached."], [], ["top_k_limit"])
                )
                continue
            count = industry_counts.get(candidate.industry, 0)
            if count >= thresholds.max_per_industry:
                rejected.append(
                    self._candidate_result(candidate, False, "excluded", ["Industry daily limit reached."], [], ["industry_limit"])
                )
                continue
            selected.append(candidate)
            industry_counts[candidate.industry] = count + 1

        return SignalSelectionBatchResult(selected=selected, rejected=rejected, thresholds=thresholds)

    def _evaluate_candidate(
        self,
        candidate: SignalSelectionCandidate,
        thresholds: SignalSelectionThresholds,
    ) -> SignalSelectionResult:
        reasons: List[str] = []
        risk_flags: List[str] = []

        checks = [
            (candidate.probability_up_1d >= thresholds.min_probability_up_1d, "probability_up_1d_below_threshold"),
            (candidate.probability_up_5d >= thresholds.min_probability_up_5d, "probability_up_5d_below_threshold"),
            (candidate.probability_up_20d >= thresholds.min_probability_up_20d, "probability_up_20d_below_threshold"),
            (candidate.confidence >= thresholds.min_confidence, "confidence_below_threshold"),
            (candidate.risk_score <= thresholds.max_risk_score, "risk_score_above_threshold"),
            (candidate.bullish_score >= thresholds.min_bullish_score, "bullish_score_below_threshold"),
            (candidate.risk_adjusted_score >= thresholds.min_risk_adjusted_score, "risk_adjusted_score_below_threshold"),
            (candidate.expected_return_5d >= thresholds.min_expected_return_5d, "expected_return_5d_below_threshold"),
            (candidate.trade_sample_count >= thresholds.min_trade_sample_count, "sample_count_below_threshold"),
        ]
        for passed, code in checks:
            if not passed:
                risk_flags.append(code)

        if thresholds.require_positive_chip_score and candidate.chip_score <= 50:
            risk_flags.append("chip_score_not_positive")
        if thresholds.require_no_major_negative_news and candidate.has_major_negative_news:
            risk_flags.append("major_negative_news")

        if risk_flags:
            return self._candidate_result(candidate, False, "excluded", reasons, ["Signal failed selection thresholds."], risk_flags)

        reasons.append("Signal passed probability, quality, risk, and sample-count thresholds.")
        return self._candidate_result(candidate, True, "primary_watchlist", reasons, [], [])

    def _result(
        self,
        signal: SignalSelectionInput,
        selected: bool,
        decision: str,
        priority: int,
        reasons: List[str],
        warnings: List[str],
        risk_flags: List[str],
    ) -> SignalSelectionResult:
        return SignalSelectionResult(
            stock_id=signal.stock_id,
            signal_date=signal.signal_date,
            selected=selected,
            decision=decision,
            priority=priority,
            reasons=reasons,
            warnings=warnings,
            risk_flags=risk_flags,
        )

    def _candidate_result(
        self,
        candidate: SignalSelectionCandidate,
        selected: bool,
        decision: str,
        reasons: List[str],
        warnings: List[str],
        risk_flags: List[str],
    ) -> SignalSelectionResult:
        return SignalSelectionResult(
            stock_id=candidate.stock_id,
            signal_date=candidate.signal_date,
            selected=selected,
            decision=decision,
            priority=3 if selected else 0,
            reasons=reasons,
            warnings=warnings,
            risk_flags=risk_flags,
        )
