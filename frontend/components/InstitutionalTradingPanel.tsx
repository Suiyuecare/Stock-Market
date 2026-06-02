import type { PredictionSignal, StockInstitutionalResponse } from "@/lib/api";
import { formatRatio, getFactorDisplayScore, sanitizeDisplayText } from "@/lib/view-model";

export function InstitutionalTradingPanel({
  signal,
  institutional,
}: {
  signal: PredictionSignal;
  institutional?: StockInstitutionalResponse;
}) {
  const score = institutional?.chip_score.score ?? getFactorDisplayScore(signal, "chip");
  const factor = signal.factor_scores.find((item) => item.category === "chip");
  const summary = institutional?.summary;
  const factors = institutional?.chip_score.positive_factors.length
    ? institutional.chip_score.positive_factors
    : ["外資連續性", "投信累積", "三大法人同步"];

  return (
    <div className="stack">
      <div className="status-row">
        <span>法人籌碼摘要</span>
        <strong>{Math.round(score)}</strong>
      </div>
      <p className="muted-copy">{sanitizeDisplayText(factor?.explanation ?? "法人與成交量資料觀察中")}</p>
      {summary ? (
        <div className="mini-metrics">
          <div>
            <span>外資比率</span>
            <b>{formatRatio(summary.foreign_net_ratio)}</b>
          </div>
          <div>
            <span>投信比率</span>
            <b>{formatRatio(summary.investment_trust_net_ratio)}</b>
          </div>
          <div>
            <span>自營商比率</span>
            <b>{formatRatio(summary.dealer_net_ratio)}</b>
          </div>
          <div>
            <span>法人合計</span>
            <b>{formatRatio(summary.institutional_net_ratio)}</b>
          </div>
        </div>
      ) : null}
      <div className="pill-row">
        {factors.slice(0, 4).map((factorText) => (
          <span key={factorText}>{sanitizeDisplayText(factorText)}</span>
        ))}
      </div>
    </div>
  );
}
