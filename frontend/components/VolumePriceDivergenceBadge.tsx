import type { PredictionSignal } from "@/lib/api";

export function VolumePriceDivergenceBadge({ signal }: { signal: PredictionSignal }) {
  const value = signal.technicals.volume_price_divergence;
  const status = value === null ? "量價資料觀察中" : value >= 0 ? "量能支持價格結構" : "量價背離需追蹤";
  const tone = value === null ? "neutral" : value >= 0 ? "positive" : "negative";

  return (
    <div className={`badge-card ${tone}`}>
      <span>量價背離狀態</span>
      <strong>{status}</strong>
      <small>{value === null ? "等待更多成交量資料" : `背離值 ${value.toFixed(4)}`}</small>
    </div>
  );
}
