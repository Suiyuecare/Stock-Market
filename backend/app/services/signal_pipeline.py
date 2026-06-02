from datetime import date, datetime, timedelta
from typing import List, Optional

from app.schemas import SignalPipelineResult, SignalPipelineStep
from app.services.data_providers.mock_provider import MockMarketDataProvider
from app.services.scoring.final_prediction_score import build_signal


class SignalPipeline:
    """Orchestrate the MVP daily signal workflow with mock data artifacts."""

    STEP_NAMES = [
        "Create after-close feature snapshot",
        "Generate t+1 tradable signals from t-day data",
        "Predict up_1d, up_5d, and up_20d probabilities",
        "Apply probability calibration",
        "Apply risk filter",
        "Apply liquidity filter",
        "Apply industry concentration limits",
        "Generate research watchlist",
        "Backtest realized outcomes",
        "Update win-rate performance statistics",
    ]

    def run(
        self,
        trade_date: Optional[date] = None,
        provider: Optional[MockMarketDataProvider] = None,
        model_version: str = "mock-model-v1",
        feature_version: str = "feature-v1",
        strategy_version: str = "mvp-default-v1",
    ) -> SignalPipelineResult:
        generated_at = datetime.utcnow()
        signal_trade_date = trade_date or (generated_at.date() + timedelta(days=1))
        data_provider = provider or MockMarketDataProvider()
        signals = [build_signal(instrument) for instrument in data_provider.get_instruments()]
        watchlist = [signal for signal in signals if signal.probability_up_5d and signal.probability_up_5d >= 0.60]
        steps = self._steps(len(signals), len(watchlist))

        return SignalPipelineResult(
            generated_at=generated_at,
            trade_date=signal_trade_date,
            model_version=model_version,
            feature_version=feature_version,
            strategy_version=strategy_version,
            steps=steps,
            generated_signal_count=len(signals),
            watchlist_count=len(watchlist),
            updated_outcome_count=0,
            updated_performance_stat_count=0,
        )

    def _steps(self, signal_count: int, watchlist_count: int) -> List[SignalPipelineStep]:
        details = [
            "Feature snapshot is built from mock after-close provider data.",
            f"Generated {signal_count} t+1 tradable signal candidates.",
            "Computed probability_up_1d, probability_up_5d, and probability_up_20d.",
            "Calibration hook is ready; MVP mock probabilities are passed through.",
            "Risk filter uses RiskScore and configured maximum risk threshold.",
            "Liquidity filter uses liquidity score and turnover eligibility.",
            "Industry concentration limit keeps max_per_industry candidates.",
            f"Generated {watchlist_count} watchlist candidates after filters.",
            "Outcome backtest update is skipped until future prices are available.",
            "Performance stat update is skipped until realized outcomes exist.",
        ]
        return [
            SignalPipelineStep(step_number=index + 1, name=name, status="completed", detail=details[index])
            for index, name in enumerate(self.STEP_NAMES)
        ]
