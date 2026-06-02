import { AppShell } from "@/components/AppShell";
import { FactorBreakdown } from "@/components/FactorBreakdown";
import { NewsTimeline } from "@/components/NewsTimeline";
import { RiskPanel } from "@/components/RiskPanel";
import { ScoreCard } from "@/components/ScoreCard";
import { StockRankingTable } from "@/components/StockRankingTable";
import { TechnicalChart } from "@/components/TechnicalChart";
import { USMarketRadar } from "@/components/USMarketRadar";
import { buildStockMetrics, DISCLAIMER_TEXT, sanitizeRiskScore } from "@/lib/view-model";
import { fetchHighRisk, fetchMarketSummary, fetchStockDetail, fetchStocks, fetchTopProbabilityRanking, fetchUSMarketRadar } from "@/lib/api";

export default async function Home() {
  const [summary, stocks, ranking, detail, radar, highRisk] = await Promise.all([
    fetchMarketSummary(),
    fetchStocks(),
    fetchTopProbabilityRanking(),
    fetchStockDetail("2330"),
    fetchUSMarketRadar(),
    fetchHighRisk(),
  ]);
  const signals = ranking.signals;
  const selected = detail.signal;
  const metrics = buildStockMetrics(selected);
  const topRisk = highRisk.signals[0];

  return (
    <AppShell active="/">
      <header className="topbar">
        <div>
          <p className="eyebrow">每日盤後 + 美股開盤前</p>
          <h1>台美股因子分析儀表板</h1>
        </div>
        <div className="status">Research MVP</div>
      </header>

      <div className="disclaimer">{DISCLAIMER_TEXT}</div>

      <section className="metric-grid">
        <ScoreCard label="台股盤後狀態" value={summary.tw_status} detail={summary.session_date} />
        <ScoreCard label="美股連動狀態" value={summary.us_premarket_status} detail="開盤前觀察訊號" />
        <ScoreCard label="追蹤標的" value={`${stocks.stocks.length}`} detail="台股樣本池" />
        <ScoreCard label="2330 上漲機率" value={`${metrics.probabilityUp1d}%`} detail="1D probability-style signal" tone="positive" />
      </section>

      <section className="grid">
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Signal Trend</p>
              <h2>觀察訊號趨勢</h2>
            </div>
          </div>
          <TechnicalChart />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Ranking</p>
              <h2>台股因子排名</h2>
            </div>
            <a className="text-link" href="/ranking">完整排名</a>
          </div>
          <StockRankingTable signals={signals} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">US Linkage</p>
              <h2>美股連動雷達</h2>
            </div>
          </div>
          <USMarketRadar linkage={radar.linkage} stocks={radar.stocks} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Risk Monitor</p>
              <h2>{selected.symbol} 風險係數</h2>
            </div>
          </div>
          <RiskPanel risk={sanitizeRiskScore(selected.risk_score)} />
          {topRisk ? <p className="muted-copy">最高風險觀察：{topRisk.stock_id} {topRisk.stock_name}</p> : null}
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Factor Explanation</p>
              <h2>正向/負向因子</h2>
            </div>
          </div>
          <FactorBreakdown positiveDrivers={selected.positive_drivers} negativeDrivers={selected.negative_drivers} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">News Timeline</p>
              <h2>新聞/事件時間線</h2>
            </div>
            <a className="text-link" href="/news">全部事件</a>
          </div>
          <NewsTimeline news={selected.news} />
        </article>
      </section>
    </AppShell>
  );
}
