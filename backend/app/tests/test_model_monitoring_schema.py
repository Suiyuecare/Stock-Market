from datetime import date

from app.schemas import ModelMonitoringAlert, ModelMonitoringInput, ModelMonitoringResult, ModelMonitoringThresholds


def test_model_monitoring_input_schema_tracks_model_and_operations_metrics() -> None:
    inputs = ModelMonitoringInput(
        monitoring_date=date(2026, 6, 2),
        win_rate_20d=0.52,
        win_rate_60d=0.55,
        historical_win_rate_mean=0.56,
        historical_win_rate_std=0.04,
        average_return_20d=0.01,
        max_drawdown_20d=0.08,
        calibration_error=0.06,
        sector_win_rate_20d={"semiconductor": 0.5},
        historical_sector_win_rate={"semiconductor": 0.56},
        factor_contribution_20d={"technical": 0.2},
        historical_factor_contribution={"technical": 0.18},
        data_latency_minutes=10,
        api_failure_rate=0.02,
        news_parse_error_rate=0.03,
    )

    assert inputs.monitoring_date == date(2026, 6, 2)
    assert inputs.sector_win_rate_20d["semiconductor"] == 0.5


def test_model_monitoring_result_schema_tracks_alerts_and_signal_strength() -> None:
    alert = ModelMonitoringAlert(
        code="possible_model_decay",
        severity="critical",
        message="20-day win rate is too low.",
        recommended_action="Lower signal strength and review retraining.",
    )
    result = ModelMonitoringResult(
        monitoring_date=date(2026, 6, 2),
        health_status="critical",
        signal_strength_multiplier=0.5,
        metrics={"win_rate_20d": 0.4},
        alerts=[alert],
    )

    assert result.health_status == "critical"
    assert result.alerts[0].code == "possible_model_decay"


def test_model_monitoring_threshold_schema_can_adjust_alert_sensitivity() -> None:
    thresholds = ModelMonitoringThresholds(
        win_rate_std_alert_multiplier=1.5,
        calibration_error_threshold=0.05,
    )

    assert thresholds.win_rate_std_alert_multiplier == 1.5
    assert thresholds.calibration_error_threshold == 0.05
