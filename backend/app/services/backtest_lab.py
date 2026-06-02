import math
from statistics import mean, median, pstdev
from typing import Dict, Iterable, List

from app.schemas import (
    BacktestConfig,
    BacktestObservation,
    BacktestResult,
    BacktestTrade,
    TimeSeriesSplitWindow,
)


class BacktestLab:
    """Independent backtest engine for point-in-time signal observations."""

    def run(self, observations: List[BacktestObservation], config: BacktestConfig) -> BacktestResult:
        trades = [self._to_trade(observation, config) for observation in observations if self._eligible(observation, config)]
        returns = [trade.net_return for trade in trades]

        return BacktestResult(
            win_rate=self._win_rate(returns),
            trade_count=len(trades),
            average_return=round(mean(returns), 6) if returns else 0.0,
            median_return=round(median(returns), 6) if returns else 0.0,
            expectancy=self._expectancy(returns),
            max_drawdown=self._max_drawdown(returns),
            profit_factor=self._profit_factor(returns),
            sharpe_ratio=self._sharpe_ratio(returns),
            sortino_ratio=self._sortino_ratio(returns),
            max_single_loss=round(min(returns), 6) if returns else 0.0,
            max_consecutive_losses=self._max_consecutive_losses(returns),
            average_holding_days=round(mean([trade.holding_days for trade in trades]), 4) if trades else 0.0,
            turnover=self._turnover(trades),
            win_rate_by_sector=self._group_win_rate(trades, "sector"),
            win_rate_by_market_state=self._group_win_rate(trades, "market_state"),
            trades=trades,
        )

    def time_series_split(self, observations: List[BacktestObservation], n_splits: int = 3) -> List[TimeSeriesSplitWindow]:
        dates = sorted({observation.trade_date for observation in observations})
        if n_splits <= 0 or len(dates) < n_splits + 1:
            return []

        test_size = max(1, len(dates) // (n_splits + 1))
        windows: List[TimeSeriesSplitWindow] = []
        for split_index in range(n_splits):
            train_end_index = len(dates) - test_size * (n_splits - split_index)
            test_start_index = train_end_index
            test_end_index = min(len(dates) - 1, test_start_index + test_size - 1)
            if train_end_index <= 0 or test_start_index >= len(dates):
                continue
            windows.append(
                TimeSeriesSplitWindow(
                    train_start=dates[0],
                    train_end=dates[train_end_index - 1],
                    test_start=dates[test_start_index],
                    test_end=dates[test_end_index],
                )
            )
        return windows

    def _eligible(self, observation: BacktestObservation, config: BacktestConfig) -> bool:
        if observation.holding_days != config.holding_days:
            return False
        if observation.probability < config.entry_probability_threshold:
            return False
        if config.market_state and observation.market_state != config.market_state:
            return False
        if config.sector and observation.sector != config.sector:
            return False
        if config.market_cap_bucket and observation.market_cap_bucket != config.market_cap_bucket:
            return False
        if config.liquidity_bucket and observation.liquidity_bucket != config.liquidity_bucket:
            return False
        return True

    def _to_trade(self, observation: BacktestObservation, config: BacktestConfig) -> BacktestTrade:
        gross_return = observation.forward_return
        exit_reason = "horizon"
        if config.stop_loss is not None and observation.max_adverse_excursion is not None:
            if observation.max_adverse_excursion <= -abs(config.stop_loss):
                gross_return = -abs(config.stop_loss)
                exit_reason = "stop_loss"
        if exit_reason == "horizon" and config.take_profit is not None and observation.max_favorable_excursion is not None:
            if observation.max_favorable_excursion >= config.take_profit:
                gross_return = config.take_profit
                exit_reason = "take_profit"

        net_return = gross_return - config.transaction_cost - config.slippage
        return BacktestTrade(
            trade_date=observation.trade_date,
            stock_id=observation.stock_id,
            holding_days=observation.holding_days,
            gross_return=round(gross_return, 6),
            net_return=round(net_return, 6),
            exit_reason=exit_reason,
            sector=observation.sector,
            market_state=observation.market_state,
            market_cap_bucket=observation.market_cap_bucket,
            liquidity_bucket=observation.liquidity_bucket,
        )

    def _win_rate(self, returns: Iterable[float]) -> float:
        values = list(returns)
        if not values:
            return 0.0
        return round(sum(1 for value in values if value > 0) / len(values), 6)

    def _expectancy(self, returns: List[float]) -> float:
        if not returns:
            return 0.0
        wins = [value for value in returns if value > 0]
        losses = [value for value in returns if value <= 0]
        win_rate = len(wins) / len(returns)
        loss_rate = 1 - win_rate
        average_win = mean(wins) if wins else 0.0
        average_loss = abs(mean(losses)) if losses else 0.0
        return round(win_rate * average_win - loss_rate * average_loss, 6)

    def _max_drawdown(self, returns: List[float]) -> float:
        equity = 1.0
        peak = 1.0
        max_drawdown = 0.0
        for value in returns:
            equity *= 1 + value
            peak = max(peak, equity)
            max_drawdown = min(max_drawdown, equity / peak - 1)
        return round(max_drawdown, 6)

    def _profit_factor(self, returns: List[float]) -> float:
        gains = sum(value for value in returns if value > 0)
        losses = abs(sum(value for value in returns if value < 0))
        if losses == 0:
            return round(gains, 6) if gains else 0.0
        return round(gains / losses, 6)

    def _sharpe_ratio(self, returns: List[float]) -> float:
        if len(returns) < 2:
            return 0.0
        volatility = pstdev(returns)
        if volatility == 0:
            return 0.0
        return round(mean(returns) / volatility * math.sqrt(len(returns)), 6)

    def _sortino_ratio(self, returns: List[float]) -> float:
        downside = [value for value in returns if value < 0]
        if not downside:
            return 0.0
        downside_deviation = math.sqrt(mean([value * value for value in downside]))
        if downside_deviation == 0:
            return 0.0
        return round(mean(returns) / downside_deviation * math.sqrt(len(returns)), 6)

    def _max_consecutive_losses(self, returns: List[float]) -> int:
        current = 0
        max_losses = 0
        for value in returns:
            if value <= 0:
                current += 1
                max_losses = max(max_losses, current)
            else:
                current = 0
        return max_losses

    def _turnover(self, trades: List[BacktestTrade]) -> float:
        if not trades:
            return 0.0
        unique_dates = {trade.trade_date for trade in trades}
        return round(len(trades) / len(unique_dates), 6)

    def _group_win_rate(self, trades: List[BacktestTrade], field: str) -> Dict[str, float]:
        grouped: Dict[str, List[float]] = {}
        for trade in trades:
            key = getattr(trade, field) or "unknown"
            grouped.setdefault(key, []).append(trade.net_return)
        return {key: self._win_rate(values) for key, values in grouped.items()}
