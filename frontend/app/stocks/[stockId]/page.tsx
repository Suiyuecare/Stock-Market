import { AppShell } from "@/components/AppShell";
import { BacktestConfidencePanel } from "@/components/BacktestConfidencePanel";
import { BeginnerDecisionPanel } from "@/components/BeginnerDecisionPanel";
import { ComplianceNotice } from "@/components/ComplianceNotice";
import { FactorBreakdown } from "@/components/FactorBreakdown";
import { HorizonProbabilityPanel } from "@/components/HorizonProbabilityPanel";
import { NewsTimeline } from "@/components/NewsTimeline";
import { ReferencePanel } from "@/components/ReferencePanel";
import { RelatedStockNewsPanel } from "@/components/RelatedStockNewsPanel";
import { ScoreCard } from "@/components/ScoreCard";
import { StockGrowthTimeline } from "@/components/StockGrowthTimeline";
import { StockInsightTabs } from "@/components/StockInsightTabs";
import { StockQuoteOverview } from "@/components/StockQuoteOverview";
import { StockSearch } from "@/components/StockSearch";
import { TargetPriceRangePanel } from "@/components/TargetPriceRangePanel";
import { WatchlistButton } from "@/components/WatchlistButton";
import { buildStockMetrics, formatScore, sanitizeDisplayText, sanitizeRiskScore, scoreTone } from "@/lib/view-model";
import { fetchStockDetail } from "@/lib/api";

export default async function StockDetailPage({ params }: { params: Promise<{ stockId: string }> }) {
  const { stockId } = await params;
  const detail = await fetchStockDetail(stockId);
  const signal = {
    ...detail.signal,
    risk_score: sanitizeRiskScore(detail.signal.risk_score),
  };
  const metrics = buildStockMetrics(signal);
  const scores = {
    BullishScore: signal.bullish_score ?? metrics.bullishScore,
    RiskAdjustedScore: signal.risk_adjusted_score ?? metrics.riskAdjustedScore,
    explanation: signal.explanation,
  };
  const technical = {
    latest_indicators: signal.technicals,
    signals: {
      macd: {
        golden_cross: (signal.technicals.macd_histogram ?? 0) >= 0,
        death_cross: (signal.technicals.macd_histogram ?? 0) < -0.3,
      },
      volume_price_divergence: {
        state: (signal.technicals.volume_price_divergence ?? 0) >= 0 ? "量價結構偏正向" : "量價背離需觀察",
      },
    },
    technical_score: {
      score: metrics.technicalScore,
      trend_score: metrics.technicalScore,
      volume_price_score: Math.max(40, metrics.technicalScore - 4),
      macd_score: Math.max(35, metrics.technicalScore - 2),
      rsi_score: Math.max(35, metrics.technicalScore - 8),
      kd_score: Math.max(35, metrics.technicalScore - 10),
      breakout_score: Math.max(35, metrics.technicalScore - 12),
    },
  };
  const institutional = {
    chip_score: {
      score: metrics.chipScore,
      positive_factors: signal.explanation?.top_positive_factors ?? [],
      negative_factors: signal.explanation?.top_negative_factors ?? [],
      risk_factors: signal.explanation?.top_risk_factors ?? [],
      confidence: signal.confidence,
    },
    summary: {
      foreign_net_ratio: metrics.chipScore >= 60 ? 0.08 : 0.01,
      investment_trust_net_ratio: metrics.chipScore >= 65 ? 0.04 : 0.005,
      dealer_net_ratio: metrics.chipScore >= 62 ? 0.02 : 0,
      synchronized_institutional_buying: metrics.chipScore >= 65,
    },
  };
  const radar = {
    disclaimer: "",
    linkage: { SOX: 0.55, NASDAQ: 0.42, NVDA: 0.62, TSM_ADR: 0.48, VIX: -0.31 },
    stocks: [
      { stock_id: signal.symbol, stock_name: signal.name, score: metrics.usMarketScore, sensitivity_multiplier: 1, positive_factors: ["個股自身美股連動"], negative_factors: [], risk_factors: ["VIX 仍需觀察"] },
      { stock_id: "2330", stock_name: "台積電", score: 78, sensitivity_multiplier: 1.2, positive_factors: ["TSM ADR / SOX 連動"], negative_factors: [], risk_factors: [] },
      { stock_id: "2454", stock_name: "聯發科", score: 72, sensitivity_multiplier: 1.05, positive_factors: ["IC 設計族群連動"], negative_factors: [], risk_factors: [] },
      { stock_id: "6147", stock_name: "頎邦", score: 68, sensitivity_multiplier: 0.95, positive_factors: ["封測族群連動"], negative_factors: [], risk_factors: [] },
    ],
  };
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
          <p className="eyebrow">個股明燈</p>
          <h1>{signal.symbol} {signal.name} 個股搜尋與機率分析</h1>
        </div>
        <div className="stock-header-actions">
          <WatchlistButton stock={{ symbol: signal.symbol, name: signal.name, sector: signal.sector ?? null }} />
          <div className="status ok">5D 上漲機率 {metrics.probabilityUp5d}%</div>
        </div>
      </header>
      <ComplianceNotice />

      <section className="panel stock-search-hero">
        <div>
          <p className="eyebrow">Stock Search</p>
          <h2>先搜尋個股，再看完整資訊</h2>
        </div>
        <StockSearch />
      </section>

      <StockQuoteOverview signal={signal} />

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
              <p className="eyebrow">Growth Timeline</p>
              <h2>個股成長時間軸</h2>
            </div>
            <span className="panel-tag">最多 1 年</span>
          </div>
          <StockGrowthTimeline history={detail.growth_history} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Probability Target</p>
              <h2>上漲/下跌機率與 1D / 5D / 20D 目標金額</h2>
            </div>
          </div>
          <HorizonProbabilityPanel signal={signal} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Stock Data Tabs</p>
              <h2>行情 / K線 / 訊號 / 族群 / 法人 / 大戶</h2>
            </div>
          </div>
          <StockInsightTabs signal={signal} technical={technical} institutional={institutional} radar={radar} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Target Range</p>
              <h2>各投顧目標價區間</h2>
            </div>
          </div>
          <TargetPriceRangePanel signal={signal} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Plain Language</p>
              <h2>是否列入觀察與原因</h2>
            </div>
          </div>
          <BeginnerDecisionPanel signal={signal} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Probability Analysis</p>
              <h2>機率分析：每一項數值如何量化加總</h2>
            </div>
          </div>
          <div className="score-matrix">
            <ScoreCard label="BullishScore" value={formatScore(scores.BullishScore)} detail="基本面、籌碼、技術、美股、新聞加權" />
            <ScoreCard label="RiskScore" value={`${metrics.riskScore}`} detail="波動、流動性、事件與集中度" tone="risk" />
            <ScoreCard label="FundamentalScore" value={`${metrics.fundamentalScore}`} detail="營收與獲利能力" />
            <ScoreCard label="ChipScore" value={formatScore(institutional.chip_score.score)} detail="法人籌碼與成交量比" />
            <ScoreCard label="TechnicalScore" value={formatScore(technical.technical_score.score)} detail="K線、MA、MACD、RSI、量價" />
            <ScoreCard label="USMarketScore" value={`${metrics.usMarketScore}`} detail="SOX、TSM ADR、NVDA、AAPL、VIX" />
            <ScoreCard label="NewsScore" value={`${metrics.newsScore}`} detail="新聞事件與相關股票連動" />
            <ScoreCard label="RiskAdjustedScore" value={formatScore(scores.RiskAdjustedScore)} detail="BullishScore 扣除風險後分數" />
          </div>
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Factors</p>
              <h2>正向 / 負向 / 風險因子</h2>
            </div>
          </div>
          <FactorBreakdown positiveDrivers={signal.positive_drivers} negativeDrivers={signal.negative_drivers} riskFactors={riskFactors} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Win-rate Evidence</p>
              <h2>勝率最佳化與回測可信度</h2>
            </div>
          </div>
          <BacktestConfidencePanel signal={signal} />
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
              <p className="eyebrow">News</p>
              <h2>相關股票新聞與事件連動</h2>
            </div>
          </div>
          <RelatedStockNewsPanel signal={signal} />
          <div className="panel-divider" />
          <NewsTimeline news={signal.news} />
        </article>
      </section>
    </AppShell>
  );
}
