from app.services.indicators.kd import stochastic_kd
from app.services.indicators.macd import analyze_macd, ema, macd, macd_series
from app.services.indicators.moving_average import moving_average
from app.services.indicators.obv import obv, obv_series
from app.services.indicators.rsi import rsi
from app.services.indicators.volume_price_divergence import analyze_volume_price_divergence, volume_price_divergence

__all__ = [
    "analyze_macd",
    "analyze_volume_price_divergence",
    "build_technical_indicators",
    "ema",
    "macd",
    "macd_series",
    "moving_average",
    "obv",
    "obv_series",
    "rsi",
    "stochastic_kd",
    "volume_price_divergence",
]


def build_technical_indicators(highs, lows, closes, volumes) -> dict:
    close_series = list(closes)
    high_series = list(highs)
    low_series = list(lows)
    volume_series = list(volumes)
    k, d = stochastic_kd(high_series, low_series, close_series)
    macd_line, signal_line, histogram = macd(close_series)

    return {
        "ma_5": moving_average(close_series, 5),
        "ma_20": moving_average(close_series, 20),
        "ma_60": moving_average(close_series, 60),
        "rsi_14": rsi(close_series, 14),
        "k_9": k,
        "d_9": d,
        "macd": macd_line,
        "macd_signal": signal_line,
        "macd_histogram": histogram,
        "obv": obv(close_series, volume_series),
        "volume_price_divergence": volume_price_divergence(close_series, volume_series),
    }
