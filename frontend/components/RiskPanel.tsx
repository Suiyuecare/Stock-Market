import type { RiskScore } from "@/lib/api";
import { ScoreCard } from "@/components/ScoreCard";
import { sanitizeDisplayText, toFactorScore } from "@/lib/view-model";

export function RiskPanel({ risk }: { risk: RiskScore }) {
  return (
    <div className="detail-grid">
      <ScoreCard label="風險係數" value={`${toFactorScore(risk.total)}`} detail={sanitizeDisplayText(risk.explanation)} tone="risk" />
      <ScoreCard label="波動風險" value={`${toFactorScore(risk.volatility)}`} detail="20 日波動與技術結構" />
      <ScoreCard label="流動性風險" value={`${toFactorScore(risk.liquidity)}`} detail="成交量與流動性觀察" />
      <ScoreCard label="事件風險" value={`${toFactorScore(risk.event)}`} detail="新聞事件與 VIX 代理訊號" />
    </div>
  );
}
