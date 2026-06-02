import type { RiskScore } from "@/lib/api";
import { ScoreCard } from "@/components/ScoreCard";

export function RiskPanel({ risk }: { risk: RiskScore }) {
  return (
    <div className="detail-grid">
      <ScoreCard label="Total risk" value={`${Math.round(risk.total * 100)}`} detail={risk.explanation} tone="risk" />
      <ScoreCard label="Volatility" value={`${Math.round(risk.volatility * 100)}`} detail="technical volatility component" />
      <ScoreCard label="Liquidity" value={`${Math.round(risk.liquidity * 100)}`} detail="liquidity component" />
      <ScoreCard label="Event" value={`${Math.round(risk.event * 100)}`} detail="news and VIX event proxy" />
    </div>
  );
}
