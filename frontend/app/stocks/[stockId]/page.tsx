import { FactorBreakdown } from "@/components/FactorBreakdown";
import { NewsTimeline } from "@/components/NewsTimeline";
import { RiskPanel } from "@/components/RiskPanel";
import { fetchStockDetail } from "@/lib/api";

export default async function StockDetailPage({ params }: { params: Promise<{ stockId: string }> }) {
  const { stockId } = await params;
  const detail = await fetchStockDetail(stockId);
  const signal = detail.signal;

  return (
    <main className="content standalone">
      <header className="topbar">
        <div>
          <p className="eyebrow">Stock Detail</p>
          <h1>{signal.symbol} {signal.name}</h1>
        </div>
        <div className="status">{Math.round(signal.probability_up * 100)}%</div>
      </header>
      <div className="disclaimer">{detail.disclaimer}</div>
      <section className="grid">
        <article className="panel span-2">
          <h2>Risk score</h2>
          <RiskPanel risk={signal.risk_score} />
        </article>
        <article className="panel">
          <h2>Factor explanation</h2>
          <FactorBreakdown positiveDrivers={signal.positive_drivers} negativeDrivers={signal.negative_drivers} />
        </article>
        <article className="panel">
          <h2>News timeline</h2>
          <NewsTimeline news={signal.news} />
        </article>
      </section>
    </main>
  );
}
