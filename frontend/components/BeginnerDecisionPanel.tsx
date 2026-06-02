import type { PredictionSignal } from "@/lib/api";
import { buildPlainLanguageReasons, buildStockMetrics, sanitizeDisplayText } from "@/lib/view-model";

export function BeginnerDecisionPanel({ signal }: { signal: PredictionSignal }) {
  const metrics = buildStockMetrics(signal);
  const reasons = buildPlainLanguageReasons(signal);
  const readyCount = [
    metrics.probabilityUp5d >= 60,
    metrics.riskScore <= 55,
    metrics.bullishScore >= 60,
    metrics.riskAdjustedScore >= 50,
  ].filter(Boolean).length;

  return (
    <div className="decision-panel">
      <div className="decision-main">
        <span>新手判讀</span>
        <strong>{readyCount >= 3 ? "可放入觀察名單" : "先保持觀察"}</strong>
        <small>這不是個人化投資建議，而是把資料轉成容易理解的研究結論。</small>
      </div>
      <div className="decision-steps">
        {reasons.map((reason) => (
          <div key={reason}>
            <b>依據</b>
            <span>{sanitizeDisplayText(reason)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
