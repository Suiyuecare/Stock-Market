import { RiskPanel } from "@/components/RiskPanel";
import { fetchStockDetail } from "@/lib/api";

export default async function RiskPage() {
  const detail = await fetchStockDetail("2330");

  return (
    <main className="content standalone">
      <header className="topbar">
        <div>
          <p className="eyebrow">Risk</p>
          <h1>風險分數面板</h1>
        </div>
        <div className="status">{detail.signal.symbol}</div>
      </header>
      <div className="disclaimer">{detail.disclaimer}</div>
      <article className="panel">
        <RiskPanel risk={detail.signal.risk_score} />
      </article>
    </main>
  );
}
