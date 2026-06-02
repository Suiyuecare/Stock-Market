import type { PredictionSignal } from "@/lib/api";
import { getFactorDisplayScore, sanitizeDisplayText } from "@/lib/view-model";

export function InstitutionalTradingPanel({ signal }: { signal: PredictionSignal }) {
  const score = getFactorDisplayScore(signal, "chip");
  const factor = signal.factor_scores.find((item) => item.category === "chip");

  return (
    <div className="stack">
      <div className="status-row">
        <span>法人籌碼摘要</span>
        <strong>{score}</strong>
      </div>
      <p className="muted-copy">{sanitizeDisplayText(factor?.explanation ?? "法人與成交量資料觀察中")}</p>
      <div className="pill-row">
        <span>外資連續性</span>
        <span>投信累積</span>
        <span>三大法人同步</span>
      </div>
    </div>
  );
}
