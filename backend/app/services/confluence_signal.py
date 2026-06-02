from typing import List, Tuple

from app.schemas import BullishConfluenceConfig, BullishConfluenceInput, BullishConfluenceResult


class BullishConfluenceEvaluator:
    """Evaluate whether a stock has multi-factor bullish confluence."""

    def evaluate(
        self,
        signal: BullishConfluenceInput,
        config: BullishConfluenceConfig = BullishConfluenceConfig(),
    ) -> BullishConfluenceResult:
        passed_conditions: List[str] = []
        failed_conditions: List[str] = []
        rejection_reasons: List[str] = []
        risk_flags: List[str] = []

        threshold_checks: List[Tuple[bool, str, str]] = [
            (
                signal.fundamental_score > config.min_fundamental_score,
                "FundamentalScore shows improvement.",
                "fundamental_score_below_confluence_threshold",
            ),
            (
                signal.chip_score > config.min_chip_score,
                "Institutional/chip score is bullish.",
                "chip_score_below_confluence_threshold",
            ),
            (
                signal.technical_score > config.min_technical_score,
                "Technical score is bullish.",
                "technical_score_below_confluence_threshold",
            ),
            (
                signal.us_market_score > config.min_us_market_score,
                "US market linkage is supportive.",
                "us_market_score_below_confluence_threshold",
            ),
            (
                signal.news_score > config.min_news_score,
                "News score has no material bearish drag.",
                "news_score_below_confluence_threshold",
            ),
            (
                signal.risk_score < config.max_risk_score,
                "RiskScore is below the high-risk threshold.",
                "risk_score_above_confluence_threshold",
            ),
            (
                signal.liquidity_score >= config.min_liquidity_score,
                "Liquidity is sufficient.",
                "liquidity_score_below_confluence_threshold",
            ),
        ]

        for passed, success, failure in threshold_checks:
            if passed:
                passed_conditions.append(success)
            else:
                failed_conditions.append(failure)

        blocking_checks = [
            (
                config.reject_macd_death_cross and signal.macd_death_cross,
                "MACD death cross is active.",
                "macd_death_cross",
            ),
            (
                config.reject_macd_bearish_divergence and signal.macd_bearish_divergence,
                "Bearish MACD divergence is active.",
                "macd_bearish_divergence",
            ),
            (
                config.reject_high_price_volume_divergence and signal.high_price_volume_divergence,
                "High-level price-volume divergence is active.",
                "high_price_volume_divergence",
            ),
            (
                config.reject_three_institutions_sync_sell and signal.three_institutions_sync_sell,
                "Three institutions are synchronously net selling.",
                "three_institutions_sync_sell",
            ),
            (
                config.reject_major_negative_news and signal.has_major_negative_news,
                "Major negative news is active.",
                "major_negative_news",
            ),
        ]
        for blocked, reason, flag in blocking_checks:
            if blocked:
                rejection_reasons.append(reason)
                risk_flags.append(flag)
            else:
                passed_conditions.append(f"No {flag.replace('_', ' ')}.")

        total_conditions = len(threshold_checks) + len(blocking_checks)
        confluence_score = round(len(passed_conditions) / total_conditions * 100, 4)
        passed = (
            len(passed_conditions) >= config.min_passed_conditions
            and not failed_conditions
            and not rejection_reasons
        )

        return BullishConfluenceResult(
            stock_id=signal.stock_id,
            signal_date=signal.signal_date,
            passed=passed,
            confluence_score=confluence_score,
            passed_conditions=passed_conditions,
            failed_conditions=failed_conditions,
            rejection_reasons=rejection_reasons,
            risk_flags=risk_flags,
        )
