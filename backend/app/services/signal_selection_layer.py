from typing import List

from app.schemas import SignalSelectionConfig, SignalSelectionInput, SignalSelectionResult


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
