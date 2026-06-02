import { AppShell } from "@/components/AppShell";
import { FactorBreakdown } from "@/components/FactorBreakdown";
import { InstitutionalTradingPanel } from "@/components/InstitutionalTradingPanel";
import { MACDPanel } from "@/components/MACDPanel";
import { NewsTimeline } from "@/components/NewsTimeline";
import { RiskPanel } from "@/components/RiskPanel";
import { ScoreCard } from "@/components/ScoreCard";
import { TechnicalChart } from "@/components/TechnicalChart";
import { USMarketRadar } from "@/components/USMarketRadar";
import { VolumePriceDivergenceBadge } from "@/components/VolumePriceDivergenceBadge";
import { buildStockMetrics, DISCLAIMER_TEXT, sanitizeRiskScore, scoreTone } from "@/lib/view-model";
import { fetchMarketSummary, fetchStockDetail } from "@/lib/api";

export default async function StockDetailPage({ params }: { params: Promise<{ stockId: string }> }) {
  const { stockId } = await params;
  const [detail, summary] = await Promise.all([fetchStockDetail(stockId), fetchMarketSummary()]);
  const signal = {
    ...detail.signal,
    risk_score: sanitizeRiskScore(detail.signal.risk_score),
  };
  const metrics = buildStockMetrics(signal);
  const riskFactors = [
    `波動風險 ${Math.round(signal.risk_score.volatility * 100)}`,
    `流動性風險 ${Math.round(signal.risk_score.liquidity * 100)}`,
    `事件風險 ${Math.round(signal.risk_score.event * 100)}`,
  ];

  return (
    <AppShell active="/stocks/2330">
      <header className="topbar">
        <div>
          <p className="eyebrow">Individual Stock Detail</p>
          <h1>{signal.symbol} {signal.name}</h1>
        </div>
        <div className="status">上漲機率 {metrics.probabilityUp1d}%</div>
      </header>
      <div className="disclaimer">{DISCLAIMER_TEXT}</div>

      <section className="metric-grid">
        <ScoreCard label="上漲機率 1D" value={`${metrics.probabilityUp1d}%`} detail="下一交易日觀察訊號" tone={scoreTone(metrics.probabilityUp1d)} />
        <ScoreCard label="上漲機率 5D" value={`${metrics.probabilityUp5d}%`} detail="短週期推估訊號" tone={scoreTone(metrics.probabilityUp5d)} />
        <ScoreCard label="上漲機率 20D" value={`${metrics.probabilityUp20d}%`} detail="中週期研究訊號" tone={scoreTone(metrics.probabilityUp20d)} />
        <ScoreCard label="風險調整分數" value={`${metrics.riskAdjustedScore}`} detail="BullishScore 扣除風險係數" />
      </section>

      <section className="grid">
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Score Matrix</p>
              <h2>因子分數矩陣</h2>
            </div>
          </div>
          <div className="score-matrix">
            <ScoreCard label="BullishScore" value={`${metrics.bullishScore}`} detail="多因子綜合研究分數" />
            <ScoreCard label="RiskScore" value={`${metrics.riskScore}`} detail="風險係數" tone="risk" />
            <ScoreCard label="FundamentalScore" value={`${metrics.fundamentalScore}`} detail="基本面因子分數" />
            <ScoreCard label="ChipScore" value={`${metrics.chipScore}`} detail="法人籌碼因子分數" />
            <ScoreCard label="TechnicalScore" value={`${metrics.technicalScore}`} detail="技術因子分數" />
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
          <div className="two-column">
            <MACDPanel signal={signal} />
            <VolumePriceDivergenceBadge signal={signal} />
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Institutional</p>
              <h2>法人籌碼摘要</h2>
            </div>
          </div>
          <InstitutionalTradingPanel signal={signal} />
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
          <USMarketRadar linkage={summary.us_linkage} />
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
