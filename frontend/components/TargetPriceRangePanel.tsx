import type { PredictionSignal } from "@/lib/api";
import { buildExternalAnalystTargetPrice, buildTargetPriceRange } from "@/lib/view-model";

export function TargetPriceRangePanel({ signal }: { signal: PredictionSignal }) {
  const range = buildTargetPriceRange(signal);
  const externalTarget = buildExternalAnalystTargetPrice(signal);
  const quoteLabel = signal.quote?.source === "TPEx OpenAPI"
    ? "TWD · TPEx 盤後收盤價"
    : signal.quote?.source === "TWSE Official STOCK_DAY"
      ? "TWD · TWSE 官方日成交收盤價"
      : signal.quote?.source === "TWSE OpenAPI"
        ? "TWD · TWSE 盤後總表收盤價"
        : "TWD 估算現價";

  return (
    <div className="target-range">
      <div className="target-summary-grid">
        <div className="price-now">
          <span>現在金額</span>
          <strong>{formatPrice(range.currentPrice)}</strong>
          <small>{quoteLabel}</small>
        </div>
        <div className={`external-target-card ${externalTarget.isAvailable ? "available" : "pending"}`}>
          <span>外部法人目標價</span>
          <strong>{externalTarget.isAvailable ? formatPrice(externalTarget.targetPriceMean) : "待授權"}</strong>
          <small>{externalTarget.sourceLabel}</small>
          {externalTarget.isAvailable ? (
            <div className="external-target-meta">
              <b>低 {externalTarget.targetPriceLow ? formatPrice(externalTarget.targetPriceLow) : "未提供"}</b>
              <b>高 {externalTarget.targetPriceHigh ? formatPrice(externalTarget.targetPriceHigh) : "未提供"}</b>
              <b>{externalTarget.analystCount ? `${externalTarget.analystCount} 位` : externalTarget.brokerLabel}</b>
            </div>
          ) : (
            <div className="external-target-meta">
              <b>{externalTarget.statusLabel}</b>
              <b>FactSet</b>
              <b>LSEG / Bloomberg</b>
            </div>
          )}
        </div>
      </div>
      <div className="range-track" aria-label="模型估算目標區間">
        <div>
          <span>模型保守</span>
          <b>{formatPrice(range.conservative)}</b>
        </div>
        <div>
          <span>模型中性</span>
          <b>{formatPrice(range.base)}</b>
        </div>
        <div>
          <span>模型樂觀</span>
          <b>{formatPrice(range.optimistic)}</b>
        </div>
      </div>
      <p className="muted-copy">{externalTarget.note}</p>
      <p className="muted-copy">{range.sourceLabel}</p>
    </div>
  );
}

function formatPrice(value: number | null): string {
  if (typeof value !== "number") return "待授權";
  if (value >= 1000) return value.toLocaleString("zh-TW", { maximumFractionDigits: 0 });
  if (value >= 100) return value.toLocaleString("zh-TW", { maximumFractionDigits: 1 });
  return value.toLocaleString("zh-TW", { maximumFractionDigits: 2 });
}
