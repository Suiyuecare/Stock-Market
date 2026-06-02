import { AppShell } from "@/components/AppShell";
import { BeginnerDecisionPanel } from "@/components/BeginnerDecisionPanel";
import { FactorBreakdown } from "@/components/FactorBreakdown";
import { InstitutionalTradingPanel } from "@/components/InstitutionalTradingPanel";
import { MACDPanel } from "@/components/MACDPanel";
import { NewsTimeline } from "@/components/NewsTimeline";
import { PortfolioAllocationPanel } from "@/components/PortfolioAllocationPanel";
import { ReferencePanel } from "@/components/ReferencePanel";
import { RiskPanel } from "@/components/RiskPanel";
import { ScoreCard } from "@/components/ScoreCard";
import { TargetPriceRangePanel } from "@/components/TargetPriceRangePanel";
import { TechnicalChart } from "@/components/TechnicalChart";
import { USMarketRadar } from "@/components/USMarketRadar";
import { VolumePriceDivergenceBadge } from "@/components/VolumePriceDivergenceBadge";
import { buildStockMetrics, DISCLAIMER_TEXT, formatScore, sanitizeDisplayText, sanitizeRiskScore, scoreTone } from "@/lib/view-model";
import { fetchStockDetail, fetchStockInstitutional, fetchStockNews, fetchStockScores, fetchStockTechnical, fetchUSMarketRadar } from "@/lib/api";

export default async function StockDetailPage({ params }: { params: Promise<{ stockId: string }> }) {
  const { stockId } = await params;
  const [detail, scores, technical, institutional, stockNews, radar] = await Promise.all([
    fetchStockDetail(stockId),
    fetchStockScores(stockId),
    fetchStockTechnical(stockId),
    fetchStockInstitutional(stockId),
    fetchStockNews(stockId),
    fetchUSMarketRadar(),
  ]);
  const signal = {
    ...detail.signal,
    technicals: technical.latest_indicators,
    news: stockNews.news,
    risk_score: sanitizeRiskScore(detail.signal.risk_score),
  };
  const metrics = buildStockMetrics(signal);
  const macdSignal = technical.signals.macd;
  const volumePriceSignal = technical.signals.volume_price_divergence;
  const riskFactors = [
    `波動風險 ${Math.round(signal.risk_score.volatility * 100)}`,
    `流動性風險 ${Math.round(signal.risk_score.liquidity * 100)}`,
    `事件風險 ${Math.round(signal.risk_score.event * 100)}`,
    ...((scores.explanation?.top_risk_factors ?? []).map((factor) => sanitizeDisplayText(factor))),
  ];

  return (
    <AppShell active="/stocks/2330">
      <header className="topbar">
        <div>
          <p className="eyebrow">Stock Decision Workspace</p>
          <h1>{signal.symbol} {signal.name} 觀察說明書</h1>
        </div>
        <div className="status">5D 上漲機率 {metrics.probabilityUp5d}%</div>
      </header>
      <div className="disclaimer">{DISCLAIMER_TEXT}</div>

      <section className="metric-grid">
        <ScoreCard label="上漲機率 1D" value={`${metrics.probabilityUp1d}%`} detail="下一交易日觀察訊號" tone={scoreTone(metrics.probabilityUp1d)} />
        <ScoreCard label="上漲機率 5D" value={`${metrics.probabilityUp5d}%`} detail="短週期推估訊號" tone={scoreTone(metrics.probabilityUp5d)} />
        <ScoreCard label="上漲機率 20D" value={`${metrics.probabilityUp20d}%`} detail="中週期研究訊號" tone={scoreTone(metrics.probabilityUp20d)} />
        <ScoreCard label="風險調整分數" value={formatScore(scores.RiskAdjustedScore)} detail="BullishScore 扣除風險係數" />
      </section>

      <section className="grid">
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Plain Language</p>
              <h2>為什麼系統會選這檔</h2>
            </div>
          </div>
          <BeginnerDecisionPanel signal={signal} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Target Range</p>
              <h2>現在金額與上看區間</h2>
            </div>
          </div>
          <TargetPriceRangePanel signal={signal} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Portfolio</p>
              <h2>我的選股配置組合</h2>
            </div>
          </div>
          <PortfolioAllocationPanel signal={signal} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Reference</p>
              <h2>客觀依據與資料來源</h2>
            </div>
          </div>
          <ReferencePanel signal={signal} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Score Matrix</p>
              <h2>因子分數矩陣</h2>
            </div>
          </div>
          <div className="score-matrix">
            <ScoreCard label="BullishScore" value={formatScore(scores.BullishScore)} detail="多因子綜合研究分數" />
            <ScoreCard label="RiskScore" value={`${metrics.riskScore}`} detail="風險係數" tone="risk" />
            <ScoreCard label="FundamentalScore" value={`${metrics.fundamentalScore}`} detail="基本面因子分數" />
            <ScoreCard label="ChipScore" value={formatScore(institutional.chip_score.score)} detail="法人籌碼因子分數" />
            <ScoreCard label="TechnicalScore" value={formatScore(technical.technical_score.score)} detail="技術因子分數" />
            <ScoreCard label="USMarketScore" value={`${metrics.usMarketScore}`} detail="美股連動因子分數" />
            <ScoreCard label="NewsScore" value={`${metrics.newsScore}`} detail="新聞情緒因子分數" />
            <ScoreCard label="TargetPriceScore" value={`${metrics.targetPriceScore}`} detail="目標價資料待接入" />
          </div>
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Technical</p>
              <h2>技術結構</h2>
            </div>
          </div>
          <TechnicalChart />
          <div className="subscore-grid">
            <span>趨勢 {formatScore(technical.technical_score.trend_score)}</span>
            <span>量價 {formatScore(technical.technical_score.volume_price_score)}</span>
            <span>MACD {formatScore(technical.technical_score.macd_score)}</span>
            <span>RSI {formatScore(technical.technical_score.rsi_score)}</span>
            <span>KD {formatScore(technical.technical_score.kd_score)}</span>
            <span>突破 {formatScore(technical.technical_score.breakout_score)}</span>
          </div>
          <div className="two-column">
            <MACDPanel signal={signal} />
            <VolumePriceDivergenceBadge signal={signal} />
          </div>
          <div className="pill-row">
            <span>MACD 黃金交叉：{macdSignal.golden_cross ? "已觸發" : "觀察中"}</span>
            <span>MACD 死亡交叉：{macdSignal.death_cross ? "已觸發" : "未觸發"}</span>
            <span>量價狀態：{volumePriceSignal.state ?? "觀察中"}</span>
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Institutional</p>
              <h2>法人籌碼摘要</h2>
            </div>
          </div>
          <InstitutionalTradingPanel signal={signal} institutional={institutional} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Risk</p>
              <h2>風險係數</h2>
            </div>
          </div>
          <RiskPanel risk={sanitizeRiskScore(signal.risk_score)} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Drivers</p>
              <h2>Top positive / negative / risk factors</h2>
            </div>
          </div>
          <FactorBreakdown positiveDrivers={signal.positive_drivers} negativeDrivers={signal.negative_drivers} riskFactors={riskFactors} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">US Linkage</p>
              <h2>美股連動解釋</h2>
            </div>
          </div>
          <USMarketRadar linkage={radar.linkage} stocks={radar.stocks} />
          <p className="muted-copy">此區以 SOX、TSM ADR、NVDA、AAPL、VIX 與供應鏈標籤估算美股連動觀察訊號。</p>
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">News</p>
              <h2>新聞/事件時間線</h2>
            </div>
          </div>
          <NewsTimeline news={signal.news} />
        </article>
      </section>
    </AppShell>
  );
}
