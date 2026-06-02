import type { PredictionSignal } from "@/lib/api";
import { buildTargetPriceRange } from "@/lib/view-model";

export function TargetPriceRangePanel({ signal }: { signal: PredictionSignal }) {
  const range = buildTargetPriceRange(signal);

  return (
    <div className="target-range">
      <div className="price-now">
        <span>現在金額</span>
        <strong>{range.currentPrice}</strong>
        <small>TWD 估算現價</small>
      </div>
      <div className="range-track" aria-label="法人預測上看區間">
        <div>
          <span>保守</span>
          <b>{range.conservative}</b>
        </div>
        <div>
          <span>中性</span>
          <b>{range.base}</b>
        </div>
        <div>
          <span>樂觀</span>
          <b>{range.optimistic}</b>
        </div>
      </div>
      <p className="muted-copy">{range.sourceLabel}</p>
    </div>
  );
}
