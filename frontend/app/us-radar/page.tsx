import { USMarketRadar } from "@/components/USMarketRadar";
import { fetchMarketSummary } from "@/lib/api";

export default async function USRadarPage() {
  const summary = await fetchMarketSummary();

  return (
    <main className="content standalone">
      <header className="topbar">
        <div>
          <p className="eyebrow">US Linkage</p>
          <h1>美股連動雷達</h1>
        </div>
        <div className="status">{summary.us_premarket_status}</div>
      </header>
      <div className="disclaimer">{summary.disclaimer}</div>
      <article className="panel">
        <USMarketRadar linkage={summary.us_linkage} />
      </article>
    </main>
  );
}
