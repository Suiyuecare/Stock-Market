from typing import Dict, List

from app.schemas import (
    ModelMonitoringAlert,
    ModelMonitoringInput,
    ModelMonitoringResult,
    ModelMonitoringThresholds,
)


class ModelMonitoringEngine:
    """Monitor model performance and data quality for daily production operation."""

    def evaluate(
        self,
        inputs: ModelMonitoringInput,
        thresholds: ModelMonitoringThresholds = ModelMonitoringThresholds(),
    ) -> ModelMonitoringResult:
        alerts: List[ModelMonitoringAlert] = []
        alerts.extend(self._performance_alerts(inputs, thresholds))
        alerts.extend(self._calibration_alerts(inputs, thresholds))
        alerts.extend(self._sector_alerts(inputs, thresholds))
        alerts.extend(self._factor_drift_alerts(inputs, thresholds))
        alerts.extend(self._operations_alerts(inputs, thresholds))

        health_status = self._health_status(alerts)
        return ModelMonitoringResult(
            monitoring_date=inputs.monitoring_date,
            health_status=health_status,
            signal_strength_multiplier=self._signal_strength_multiplier(alerts),
            metrics=self._metrics(inputs),
            alerts=alerts,
        )

    def _performance_alerts(
        self,
        inputs: ModelMonitoringInput,
        thresholds: ModelMonitoringThresholds,
    ) -> List[ModelMonitoringAlert]:
        alerts: List[ModelMonitoringAlert] = []
        lower_bound = inputs.historical_win_rate_mean - thresholds.win_rate_std_alert_multiplier * inputs.historical_win_rate_std
        if inputs.win_rate_20d < lower_bound:
            alerts.append(
                ModelMonitoringAlert(
                    code="possible_model_decay",
                    severity="critical",
                    message="Recent 20-day win rate is below the historical mean by more than two standard deviations.",
                    recommended_action="Lower signal strength and review whether retraining or recalibration is required.",
                )
            )
        if inputs.max_drawdown_20d >= thresholds.max_drawdown_threshold:
            alerts.append(
                ModelMonitoringAlert(
                    code="drawdown_limit_breached",
                    severity="warning",
                    message="Recent 20-day max drawdown exceeds the monitoring threshold.",
                    recommended_action="Reduce simulated exposure and inspect recent losing signal clusters.",
                )
            )
        return alerts

    def _calibration_alerts(
        self,
        inputs: ModelMonitoringInput,
        thresholds: ModelMonitoringThresholds,
    ) -> List[ModelMonitoringAlert]:
        if inputs.calibration_error < thresholds.calibration_error_threshold:
            return []
        return [
            ModelMonitoringAlert(
                code="probability_calibration_drift",
                severity="warning",
                message="Prediction probability calibration error is above threshold.",
                recommended_action="Review bucket backtests and recalibrate probability mapping.",
            )
        ]

    def _sector_alerts(
        self,
        inputs: ModelMonitoringInput,
        thresholds: ModelMonitoringThresholds,
    ) -> List[ModelMonitoringAlert]:
        alerts: List[ModelMonitoringAlert] = []
        for sector, recent_rate in inputs.sector_win_rate_20d.items():
            baseline = inputs.historical_sector_win_rate.get(sector)
            if baseline is None:
                continue
            if baseline - recent_rate >= thresholds.sector_win_rate_drop_threshold:
                alerts.append(
                    ModelMonitoringAlert(
                        code=f"sector_win_rate_drop:{sector}",
                        severity="warning",
                        message=f"{sector} recent win rate dropped materially versus historical baseline.",
                        recommended_action="Lower sector exposure and inspect factor behavior for this segment.",
                    )
                )
        return alerts

    def _factor_drift_alerts(
        self,
        inputs: ModelMonitoringInput,
        thresholds: ModelMonitoringThresholds,
    ) -> List[ModelMonitoringAlert]:
        alerts: List[ModelMonitoringAlert] = []
        for factor, recent_contribution in inputs.factor_contribution_20d.items():
            baseline = inputs.historical_factor_contribution.get(factor)
            if baseline is None:
                continue
            if abs(recent_contribution - baseline) >= thresholds.factor_contribution_drift_threshold:
                alerts.append(
                    ModelMonitoringAlert(
                        code=f"factor_contribution_drift:{factor}",
                        severity="info",
                        message=f"{factor} contribution drifted from its historical baseline.",
                        recommended_action="Review whether the market regime or factor weighting has changed.",
                    )
                )
        return alerts

    def _operations_alerts(
        self,
        inputs: ModelMonitoringInput,
        thresholds: ModelMonitoringThresholds,
    ) -> List[ModelMonitoringAlert]:
        alerts: List[ModelMonitoringAlert] = []
        if inputs.data_latency_minutes >= thresholds.data_latency_minutes_threshold:
            alerts.append(
                ModelMonitoringAlert(
                    code="data_latency_high",
                    severity="warning",
                    message="Data latency is above the operational threshold.",
                    recommended_action="Check provider ingestion jobs and data availability ledger timestamps.",
                )
            )
        if inputs.api_failure_rate >= thresholds.api_failure_rate_threshold:
            alerts.append(
                ModelMonitoringAlert(
                    code="api_failure_rate_high",
                    severity="warning",
                    message="API failure rate is above the operational threshold.",
                    recommended_action="Inspect provider status, retries, and application logs.",
                )
            )
        if inputs.news_parse_error_rate >= thresholds.news_parse_error_rate_threshold:
            alerts.append(
                ModelMonitoringAlert(
                    code="news_parse_error_rate_high",
                    severity="warning",
                    message="News parsing error rate is above threshold.",
                    recommended_action="Review parser prompts, provider payload changes, and fallback logic.",
                )
            )
        return alerts

    def _health_status(self, alerts: List[ModelMonitoringAlert]) -> str:
        severities = {alert.severity for alert in alerts}
        if "critical" in severities:
            return "critical"
        if "warning" in severities:
            return "degraded"
        return "healthy"

    def _signal_strength_multiplier(self, alerts: List[ModelMonitoringAlert]) -> float:
        multiplier = 1.0
        for alert in alerts:
            if alert.code == "possible_model_decay":
                multiplier *= 0.5
            elif alert.severity == "warning":
                multiplier *= 0.85
        return round(max(0.2, multiplier), 4)

    def _metrics(self, inputs: ModelMonitoringInput) -> Dict[str, object]:
        return {
            "win_rate_20d": inputs.win_rate_20d,
            "win_rate_60d": inputs.win_rate_60d,
            "historical_win_rate_mean": inputs.historical_win_rate_mean,
            "historical_win_rate_std": inputs.historical_win_rate_std,
            "average_return_20d": inputs.average_return_20d,
            "max_drawdown_20d": inputs.max_drawdown_20d,
            "calibration_error": inputs.calibration_error,
            "sector_win_rate_20d": inputs.sector_win_rate_20d,
            "factor_contribution_20d": inputs.factor_contribution_20d,
            "data_latency_minutes": inputs.data_latency_minutes,
            "api_failure_rate": inputs.api_failure_rate,
            "news_parse_error_rate": inputs.news_parse_error_rate,
        }
