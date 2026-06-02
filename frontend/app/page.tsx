import { AppShell } from "@/components/AppShell";
import { BacktestConfidencePanel } from "@/components/BacktestConfidencePanel";
import { BeginnerDecisionPanel } from "@/components/BeginnerDecisionPanel";
import { FactorBreakdown } from "@/components/FactorBreakdown";
import { NewsTimeline } from "@/components/NewsTimeline";
import { PortfolioAllocationPanel } from "@/components/PortfolioAllocationPanel";
import { ReferencePanel } from "@/components/ReferencePanel";
import { RiskPanel } from "@/components/RiskPanel";
import { ScoreCard } from "@/components/ScoreCard";
import { StockRankingTable } from "@/components/StockRankingTable";
import { TargetPriceRangePanel } from "@/components/TargetPriceRangePanel";
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
          <p className="eyebrow">Finance Template Workspace</p>
          <h1>台美股入門觀察工作台</h1>
        </div>
        <div className="status">今天先看懂，再決定是否放入觀察</div>
      </header>

      <div className="disclaimer">{DISCLAIMER_TEXT}</div>

      <section className="metric-grid">
        <ScoreCard label="台股盤後狀態" value={summary.tw_status} detail={summary.session_date} />
        <ScoreCard label="美股連動狀態" value={summary.us_premarket_status} detail="開盤前觀察訊號" />
        <ScoreCard label="追蹤標的" value={`${stocks.stocks.length}`} detail="台股樣本池" />
        <ScoreCard label="入門首選觀察" value={`${selected.symbol}`} detail={`${selected.name} · 5D ${metrics.probabilityUp5d}%`} tone="positive" />
      </section>

      <section className="grid">
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Beginner Mode</p>
              <h2>為什麼今天先看這檔</h2>
            </div>
            <a className="text-link" href={`/stocks/${selected.symbol}`}>看完整分析</a>
          </div>
          <BeginnerDecisionPanel signal={selected} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Target Range</p>
              <h2>現價與上看區間</h2>
            </div>
          </div>
          <TargetPriceRangePanel signal={selected} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">My Portfolio</p>
              <h2>觀察配置示意</h2>
            </div>
          </div>
          <PortfolioAllocationPanel signal={selected} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">References</p>
              <h2>客觀依據與 Reference</h2>
            </div>
          </div>
          <ReferencePanel signal={selected} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Backtest Confidence</p>
              <h2>歷史相似訊號驗證</h2>
            </div>
          </div>
          <BacktestConfidencePanel signal={selected} />
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

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Signal Trend</p>
              <h2>觀察訊號趨勢</h2>
            </div>
          </div>
          <TechnicalChart />
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
