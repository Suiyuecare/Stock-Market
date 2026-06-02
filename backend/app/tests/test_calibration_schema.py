from app.schemas import CalibrationBucket, CalibrationResult, CalibrationSample


def test_calibration_sample_schema_tracks_probability_and_label() -> None:
    sample = CalibrationSample(
        predicted_probability=0.72,
        actual_outcome=1,
        horizon_days=5,
        stock_id="2330",
        sector="semiconductor",
        market_state="bull",
    )

    assert sample.predicted_probability == 0.72
    assert sample.actual_outcome == 1
    assert sample.horizon_days == 5


def test_calibration_result_schema_exposes_probability_bucket_backtest() -> None:
    bucket = CalibrationBucket(
        lower_bound=0.7,
        upper_bound=0.75,
        sample_count=20,
        average_predicted_probability=0.72,
        actual_win_rate=0.69,
        calibration_error=0.03,
        brier_score=0.21,
        reliability_status="well_calibrated",
    )
    result = CalibrationResult(
        horizon_days=5,
        sample_count=20,
        brier_score=0.21,
        expected_calibration_error=0.03,
        max_calibration_error=0.03,
        buckets=[bucket],
    )

    assert result.buckets[0].lower_bound == 0.7
    assert result.buckets[0].actual_win_rate == 0.69
