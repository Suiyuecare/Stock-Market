from datetime import date
from typing import Dict, List, Optional, Sequence

from app.schemas import BacktestObservation, ValidationConfig, ValidationFold, ValidationResult
from app.services.backtest_lab import BacktestLab


class ValidationEngine:
    """Build purged walk-forward validation folds for point-in-time signals."""

    def __init__(self, backtest_lab: Optional[BacktestLab] = None) -> None:
        self.backtest_lab = backtest_lab or BacktestLab()

    def validate(self, observations: List[BacktestObservation], config: ValidationConfig) -> ValidationResult:
        if config.split_method != "walk_forward":
            return self._empty_result(config, [f"Unsupported split_method: {config.split_method}"])

        ordered_dates = sorted({observation.trade_date for observation in observations})
        date_to_observations = self._group_by_date(observations)
        folds: List[ValidationFold] = []
        warnings: List[str] = []
        window_size = (
            config.train_window_days
            + config.embargo_days
            + config.validation_window_days
            + config.embargo_days
            + config.test_window_days
        )
        step_days = self._step_days(config.retrain_frequency)

        start_index = 0
        while start_index + window_size <= len(ordered_dates):
            train_dates = ordered_dates[start_index : start_index + config.train_window_days]
            validation_start_index = start_index + config.train_window_days + config.embargo_days
            validation_end_index = validation_start_index + config.validation_window_days
            validation_dates = ordered_dates[validation_start_index:validation_end_index]
            test_start_index = validation_end_index + config.embargo_days
            test_end_index = test_start_index + config.test_window_days
            test_dates = ordered_dates[test_start_index:test_end_index]

            validation_observations = self._observations_for_dates(date_to_observations, validation_dates)
            test_observations = self._observations_for_dates(date_to_observations, test_dates)
            validation_result = self.backtest_lab.run(validation_observations, config.backtest_config)
            test_result = self.backtest_lab.run(test_observations, config.backtest_config)
            passed_min_trades = (
                validation_result.trade_count >= config.min_trades_per_fold
                and test_result.trade_count >= config.min_trades_per_fold
            )

            if not passed_min_trades:
                warnings.append(f"Fold {len(folds)} has fewer trades than min_trades_per_fold.")

            folds.append(
                ValidationFold(
                    fold_index=len(folds),
                    train_start=train_dates[0],
                    train_end=train_dates[-1],
                    validation_start=validation_dates[0],
                    validation_end=validation_dates[-1],
                    test_start=test_dates[0],
                    test_end=test_dates[-1],
                    train_sample_count=sum(len(date_to_observations.get(item, [])) for item in train_dates),
                    validation_trade_count=validation_result.trade_count,
                    test_trade_count=test_result.trade_count,
                    passed_min_trades=passed_min_trades,
                    validation_result=validation_result,
                    test_result=test_result,
                )
            )
            start_index += step_days

        if not folds:
            warnings.append("Not enough chronological observations to create a full validation fold.")

        total_test_trades = sum(fold.test_trade_count for fold in folds)
        passed_min_total_trades = total_test_trades >= config.min_total_trades
        if not passed_min_total_trades:
            warnings.append("Total test trades are fewer than min_total_trades.")

        test_trades = [trade for fold in folds for trade in fold.test_result.trades]
        return ValidationResult(
            split_method=config.split_method,
            retrain_frequency=config.retrain_frequency,
            embargo_days=config.embargo_days,
            fold_count=len(folds),
            total_test_trades=total_test_trades,
            passed_min_total_trades=passed_min_total_trades,
            passed_all_folds=bool(folds) and all(fold.passed_min_trades for fold in folds) and passed_min_total_trades,
            folds=folds,
            win_rate_by_market_regime=self._segment_win_rate(test_trades, "market_state")
            if config.evaluate_by_market_regime
            else {},
            win_rate_by_industry=self._segment_win_rate(test_trades, "sector") if config.evaluate_by_industry else {},
            win_rate_by_liquidity_bucket=self._segment_win_rate(test_trades, "liquidity_bucket")
            if config.evaluate_by_liquidity_bucket
            else {},
            warnings=warnings,
        )

    def _empty_result(self, config: ValidationConfig, warnings: List[str]) -> ValidationResult:
        return ValidationResult(
            split_method=config.split_method,
            retrain_frequency=config.retrain_frequency,
            embargo_days=config.embargo_days,
            fold_count=0,
            total_test_trades=0,
            passed_min_total_trades=False,
            passed_all_folds=False,
            folds=[],
            win_rate_by_market_regime={},
            win_rate_by_industry={},
            win_rate_by_liquidity_bucket={},
            warnings=warnings,
        )

    def _group_by_date(self, observations: Sequence[BacktestObservation]) -> Dict[date, List[BacktestObservation]]:
        grouped: Dict[date, List[BacktestObservation]] = {}
        for observation in observations:
            grouped.setdefault(observation.trade_date, []).append(observation)
        return grouped

    def _observations_for_dates(
        self,
        date_to_observations: Dict[date, List[BacktestObservation]],
        dates: Sequence[date],
    ) -> List[BacktestObservation]:
        return [observation for item in dates for observation in date_to_observations.get(item, [])]

    def _step_days(self, retrain_frequency: str) -> int:
        if retrain_frequency == "daily":
            return 1
        if retrain_frequency == "weekly":
            return 5
        if retrain_frequency == "quarterly":
            return 63
        return 21

    def _segment_win_rate(self, trades: Sequence[object], field: str) -> Dict[str, float]:
        grouped: Dict[str, List[float]] = {}
        for trade in trades:
            key = getattr(trade, field) or "unknown"
            grouped.setdefault(key, []).append(getattr(trade, "net_return"))
        return {key: round(sum(1 for value in values if value > 0) / len(values), 6) for key, values in grouped.items()}
