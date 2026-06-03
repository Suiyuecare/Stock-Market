import { AppShell } from "@/components/AppShell";
import { BacktestConfidencePanel } from "@/components/BacktestConfidencePanel";
import { BeginnerDecisionPanel } from "@/components/BeginnerDecisionPanel";
import { ComplianceNotice } from "@/components/ComplianceNotice";
import { FactorBreakdown } from "@/components/FactorBreakdown";
import { GrowthCurvePanel } from "@/components/GrowthCurvePanel";
import { NewsTimeline } from "@/components/NewsTimeline";
import { PortfolioAllocationPanel } from "@/components/PortfolioAllocationPanel";
import { ReferencePanel } from "@/components/ReferencePanel";
import { RiskPanel } from "@/components/RiskPanel";
import { ScoreCard } from "@/components/ScoreCard";
import { StockRankingTable } from "@/components/StockRankingTable";
import { TargetPriceRangePanel } from "@/components/TargetPriceRangePanel";
import { TechnicalChart } from "@/components/TechnicalChart";
import { USMarketRadar } from "@/components/USMarketRadar";
import { buildStockMetrics, sanitizeRiskScore } from "@/lib/view-model";
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
  const previewSignals = signals.slice(0, 12);
  const selected = detail.signal;
  const metrics = buildStockMetrics(selected);
  const topRisk = highRisk.signals[0];

  return (
    <AppShell active="/">
      <header className="topbar">
        <div>
          <p className="eyebrow">BEGINNER STOCK DASHBOARD</p>
          <h1>今天先看哪些股票？新手版訊號總覽</h1>
        </div>
        <div className="status ok">每 1 分鐘更新新聞 · 盤後同步官方行情</div>
      </header>

      <ComplianceNotice />

      <section className="guide-strip" aria-label="新手導覽">
        <div>
          <span>第 1 步</span>
          <strong>先看能不能列入觀察</strong>
          <small>系統先把 1D / 5D / 20D 機率整理好，讓你不用一開始就看一堆線圖。</small>
        </div>
        <div>
          <span>第 2 步</span>
          <strong>再看它為什麼被選到</strong>
          <small>基本面、籌碼、技術、美股連動與新聞都會拆成加分或扣分原因。</small>
        </div>
        <div>
          <span>第 3 步</span>
          <strong>最後看自己能不能承受</strong>
          <small>風險係數太高時，即使分數漂亮，也只適合放在高風險觀察區。</small>
        </div>
      </section>

      <section className="metric-grid">
        <ScoreCard label="台股資料狀態" value={summary.tw_status} detail={summary.session_date} />
        <ScoreCard label="美股風向" value={summary.us_premarket_status} detail="會影響電子與 AI 供應鏈" />
        <ScoreCard label="目前追蹤股票" value={`${stocks.stocks.length}`} detail="可搜尋、可放入關注名單" />
        <ScoreCard label="今日範例觀察" value={`${selected.symbol}`} detail={`${selected.name} · 5D ${metrics.probabilityUp5d}%`} tone="positive" />
      </section>

      {summary.data_source_status?.length ? (
        <section className="api-source-strip" aria-label="API 資料與授權狀態">
          {summary.data_source_status.slice(0, 8).map((source) => (
            <a className={`api-source-pill ${source.status}`} href={source.url} target="_blank" rel="noreferrer" key={source.name}>
              <span>{source.name}</span>
              <strong>{source.status === "connected" ? "已連動" : source.status === "configured" ? "已授權" : "待 API key"}</strong>
              <small>{source.detail}</small>
            </a>
          ))}
        </section>
      ) : null}

      <section className="grid">
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">新手解讀</p>
              <h2>這檔股票現在該怎麼理解</h2>
            </div>
            <a className="text-link" href={`/stocks/${selected.symbol}`}>看完整分析</a>
          </div>
          <BeginnerDecisionPanel signal={selected} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">成長曲線</p>
              <h2>公司最近成長有沒有變好</h2>
            </div>
            <a className="text-link" href="/stocks/2330">看個股完整曲線</a>
          </div>
          <GrowthCurvePanel history={detail.growth_history} source={detail.growth_source} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">價格區間</p>
              <h2>現在價格與研究區間</h2>
            </div>
          </div>
          <TargetPriceRangePanel signal={selected} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">配置概念</p>
              <h2>不要只看單一股票</h2>
            </div>
          </div>
          <PortfolioAllocationPanel signal={selected} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">客觀依據</p>
              <h2>這些分數引用了哪些資料</h2>
            </div>
          </div>
          <ReferencePanel signal={selected} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">歷史驗證</p>
              <h2>類似條件過去表現如何</h2>
            </div>
          </div>
          <BacktestConfidencePanel signal={selected} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">觀察排行</p>
              <h2>今天有哪些股票訊號比較整齊</h2>
            </div>
            <a className="text-link" href="/ranking">完整排名</a>
          </div>
          <StockRankingTable signals={previewSignals} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">趨勢圖</p>
              <h2>分數最近是變強還是變弱</h2>
            </div>
          </div>
          <TechnicalChart />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">美股影響</p>
              <h2>美股科技股會怎麼牽動台股</h2>
            </div>
          </div>
          <USMarketRadar linkage={radar.linkage} stocks={radar.stocks} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">風險提醒</p>
              <h2>{selected.symbol} 需要先注意什麼</h2>
            </div>
          </div>
          <RiskPanel risk={sanitizeRiskScore(selected.risk_score)} />
          {topRisk ? <p className="muted-copy">最高風險觀察：{topRisk.stock_id} {topRisk.stock_name}</p> : null}
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">原因拆解</p>
              <h2>哪些因素加分，哪些因素扣分</h2>
            </div>
          </div>
          <FactorBreakdown positiveDrivers={selected.positive_drivers} negativeDrivers={selected.negative_drivers} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">最新事件</p>
              <h2>新聞怎麼影響這檔股票</h2>
            </div>
            <a className="text-link" href="/news">全部事件</a>
          </div>
          <NewsTimeline news={selected.news} />
        </article>
      </section>
    </AppShell>
  );
}
