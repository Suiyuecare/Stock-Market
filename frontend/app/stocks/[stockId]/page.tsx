import { AppShell } from "@/components/AppShell";
import { BacktestConfidencePanel } from "@/components/BacktestConfidencePanel";
import { BeginnerDecisionPanel } from "@/components/BeginnerDecisionPanel";
import { FactorBreakdown } from "@/components/FactorBreakdown";
import { HorizonProbabilityPanel } from "@/components/HorizonProbabilityPanel";
import { NewsTimeline } from "@/components/NewsTimeline";
import { ReferencePanel } from "@/components/ReferencePanel";
import { RelatedStockNewsPanel } from "@/components/RelatedStockNewsPanel";
import { ScoreCard } from "@/components/ScoreCard";
import { StockAiSelector } from "@/components/StockAiSelector";
import { StockGrowthTimeline } from "@/components/StockGrowthTimeline";
import { StockInsightTabs } from "@/components/StockInsightTabs";
import { StockQuoteOverview } from "@/components/StockQuoteOverview";
import { TargetPriceRangePanel } from "@/components/TargetPriceRangePanel";
import { WatchlistButton } from "@/components/WatchlistButton";
import { buildStockMetrics, formatScore, sanitizeDisplayText, sanitizeRiskScore, scoreTone } from "@/lib/view-model";
import { fetchStockDetail, fetchStocks } from "@/lib/api";

export default async function StockDetailPage({ params }: { params: Promise<{ stockId: string }> }) {
  const { stockId } = await params;
  const [detail, stocks] = await Promise.all([fetchStockDetail(stockId), fetchStocks()]);
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
          <p className="eyebrow">STOCK SIGNAL GUIDE</p>
          <h1>{signal.symbol} {signal.name}</h1>
        </div>
        <div className="stock-header-actions">
          <WatchlistButton stock={{ symbol: signal.symbol, name: signal.name, sector: signal.sector ?? null }} />
          <div className="status ok">5D 觀察機率 {metrics.probabilityUp5d}%</div>
        </div>
      </header>

      <StockAiSelector signal={signal} stocks={stocks.stocks} />

      <StockQuoteOverview signal={signal} />

      <section className="metric-grid">
        <ScoreCard label="上漲機率 1D" value={`${metrics.probabilityUp1d}%`} detail="下一交易日觀察訊號" tone={scoreTone(metrics.probabilityUp1d)} />
        <ScoreCard label="上漲機率 5D" value={`${metrics.probabilityUp5d}%`} detail="主要觀察週期" tone={scoreTone(metrics.probabilityUp5d)} />
        <ScoreCard label="上漲機率 20D" value={`${metrics.probabilityUp20d}%`} detail="中期研究訊號" tone={scoreTone(metrics.probabilityUp20d)} />
        <ScoreCard label="扣風險後分數" value={formatScore(scores.RiskAdjustedScore)} detail="分數越高，研究條件越完整" />
      </section>

      <section className="grid">
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">K 線時間軸</p>
              <h2>像券商圖表一樣看價格、成交量與 KD</h2>
            </div>
            <span className="panel-tag">近 1 年</span>
          </div>
          <StockGrowthTimeline history={detail.growth_history} signal={signal} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">機率與區間</p>
              <h2>1D / 5D / 20D 的觀察機率與目標區間</h2>
            </div>
          </div>
          <HorizonProbabilityPanel signal={signal} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">深入資料</p>
              <h2>想看更細時，再切到行情、K線、法人與大戶</h2>
            </div>
          </div>
          <StockInsightTabs signal={signal} technical={technical} institutional={institutional} radar={radar} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">價格區間</p>
              <h2>現在金額與研究區間</h2>
            </div>
          </div>
          <TargetPriceRangePanel signal={signal} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">白話結論</p>
              <h2>這檔目前是否值得放入觀察</h2>
            </div>
          </div>
          <BeginnerDecisionPanel signal={signal} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">機率分析</p>
              <h2>每個分數如何加總成觀察機率</h2>
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
              <p className="eyebrow">原因拆解</p>
              <h2>加分、扣分與風險因子</h2>
            </div>
          </div>
          <FactorBreakdown positiveDrivers={signal.positive_drivers} negativeDrivers={signal.negative_drivers} riskFactors={riskFactors} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">歷史驗證</p>
              <h2>類似訊號過去有沒有站得住腳</h2>
            </div>
          </div>
          <BacktestConfidencePanel signal={signal} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">資料來源</p>
              <h2>這個判讀引用了哪些 Reference</h2>
            </div>
          </div>
          <ReferencePanel signal={signal} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">最新事件</p>
              <h2>新聞與相關股票怎麼連動</h2>
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
