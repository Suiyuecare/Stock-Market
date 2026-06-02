import { AppShell } from "@/components/AppShell";
import { ComplianceNotice } from "@/components/ComplianceNotice";
import { ScoreCard } from "@/components/ScoreCard";
import { USMarketRadar } from "@/components/USMarketRadar";
import { formatScore, signedLabel } from "@/lib/view-model";
import { fetchMarketSummary, fetchUSMarketRadar } from "@/lib/api";

export default async function USRadarPage() {
  const [summary, radar] = await Promise.all([fetchMarketSummary(), fetchUSMarketRadar()]);
  const topLinked = radar.stocks[0];

  return (
    <AppShell active="/us-radar">
      <header className="topbar">
        <div>
          <p className="eyebrow">US Linkage Radar</p>
          <h1>美股連動雷達</h1>
        </div>
        <div className="status">{summary.us_premarket_status}</div>
      </header>
      <ComplianceNotice />
      <section className="metric-grid">
        <ScoreCard label="NASDAQ" value={signedLabel(radar.linkage.NASDAQ ?? 0)} detail="美股科技指數" />
        <ScoreCard label="SOX" value={signedLabel(radar.linkage.SOX ?? 0)} detail="半導體連動核心" />
        <ScoreCard label="NVDA" value={signedLabel(radar.linkage.NVDA ?? 0)} detail="AI 供應鏈觀察" />
        <ScoreCard label="最高連動標的" value={topLinked?.stock_id ?? "觀察中"} detail={topLinked ? `${topLinked.stock_name} · ${formatScore(topLinked.score)}` : "等待資料"} />
      </section>
      <section className="grid">
        <article className="panel span-2">
          <USMarketRadar linkage={radar.linkage} stocks={radar.stocks} />
        </article>
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Explanation</p>
              <h2>連動解釋</h2>
            </div>
          </div>
          <div className="explain-grid">
            <div><strong>半導體</strong><span>SOX、SMH、TSM ADR、NVDA、AMD、AVGO 權重較高。</span></div>
            <div><strong>AI Server</strong><span>NVDA、AMD、AVGO、雲端巨頭資本支出訊號較重要。</span></div>
            <div><strong>Apple 鏈</strong><span>AAPL 與 guidance 類事件會提高相關標的敏感度。</span></div>
            <div><strong>內需</strong><span>美股連動權重較低，主要作為市場情緒背景。</span></div>
          </div>
        </article>
      </section>
    </AppShell>
  );
}
