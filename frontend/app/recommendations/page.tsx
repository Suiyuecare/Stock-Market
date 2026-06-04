import { AppShell } from "@/components/AppShell";
import { ScoreCard } from "@/components/ScoreCard";
import type { PredictionSignal, TaiwanPredictionToolResponse } from "@/lib/api";
import { fetchTaiwanPredictionTool, fetchTopProbabilityRanking } from "@/lib/api";
import { buildSignalIndustryScore, classifySignal } from "@/lib/industry-classification";
import { buildExternalAnalystTargetPrice, buildStockMetrics, buildTargetPriceRange, sanitizeDisplayText, scoreTone } from "@/lib/view-model";

type RecommendationRow = {
  signal: PredictionSignal;
  score: number;
  scores: HorizonScores;
  stockScores: HorizonScores;
  overheatPenalty: number;
  eventRiskPenalty: number;
  liquidityPassed: boolean;
  reason: string;
  themes: string[];
  themeFit: number;
  majorCategory: string;
  subcategories: string[];
  metrics: ReturnType<typeof buildStockMetrics>;
  targetRange: ReturnType<typeof buildTargetPriceRange>;
  externalTarget: ReturnType<typeof buildExternalAnalystTargetPrice>;
};

type RecommendationCategoryGroup = {
  majorCategory: string;
  averageScore: number;
  count: number;
  rows: RecommendationRow[];
  subcategories: Array<{ name: string; score: number; count: number }>;
};

type HorizonKey = "1d" | "5d" | "20d";

type HorizonScores = Record<HorizonKey, number>;

type FactorWeights = {
  technical: number;
  chip: number;
  usMarket: number;
  market: number;
  news: number;
  revenueIndustry: number;
  fundamental: number;
  valuation: number;
};

type MarketState = {
  score: number;
  label: string;
  action: string;
  multiplier: number;
  tone: "positive" | "negative" | "neutral";
  components: Array<{ label: string; value: number; detail: string }>;
};

const horizonWeights: Record<HorizonKey, FactorWeights> = {
  "1d": {
    technical: 25,
    chip: 22,
    usMarket: 18,
    market: 12,
    news: 10,
    revenueIndustry: 5,
    fundamental: 5,
    valuation: 3,
  },
  "5d": {
    technical: 22,
    chip: 22,
    usMarket: 13,
    market: 8,
    news: 5,
    revenueIndustry: 15,
    fundamental: 12,
    valuation: 3,
  },
  "20d": {
    technical: 15,
    chip: 18,
    usMarket: 8,
    market: 8,
    news: 2,
    revenueIndustry: 22,
    fundamental: 22,
    valuation: 5,
  },
};

export default async function RecommendationsPage() {
  const [ranking, tool] = await Promise.all([
    fetchTopProbabilityRanking(),
    fetchTaiwanPredictionTool(),
  ]);
  const marketState = buildMarketState(tool);
  const recommendations = ranking.signals
    .map((signal) => buildRecommendation(signal, marketState))
    .filter((row) => row.liquidityPassed)
    .sort((left, right) => right.scores["5d"] - left.scores["5d"])
    .slice(0, 20);
  const top = recommendations[0];
  const dataDate = ranking.data_date ?? tool.research.research_window.end;
  const candidateCount = ranking.candidate_count ?? ranking.signals.length;
  const averageRisk = Math.round(recommendations.reduce((sum, row) => sum + row.metrics.riskScore, 0) / Math.max(1, recommendations.length));
  const averageScore = Math.round(recommendations.reduce((sum, row) => sum + row.score, 0) / Math.max(1, recommendations.length));
  const averageOverheat = Math.round(recommendations.reduce((sum, row) => sum + row.overheatPenalty, 0) / Math.max(1, recommendations.length));
  const recommendationGroups = buildRecommendationGroups(recommendations);

  return (
    <AppShell active="/recommendations">
      <header className="topbar">
        <div>
          <p className="eyebrow">明燈推薦 · {dataDate} 動態候選池</p>
          <h1>今日前 20 檔研究觀察名單</h1>
        </div>
        <div className={`status ${marketState.tone === "positive" ? "ok" : marketState.tone === "negative" ? "risk" : ""}`}>市場狀態 {marketState.score} · {marketState.label}</div>
      </header>

      <section className="metric-grid">
        <ScoreCard label="市場狀態分數" value={`${marketState.score}`} detail={marketState.action} tone={marketState.tone} />
        <ScoreCard label="資料日期" value={dataDate.replaceAll("-", "/")} detail="以官方最新盤後資料為準" tone="neutral" />
        <ScoreCard label="動態候選池" value={`${candidateCount}`} detail="通過股價與流動性篩選後再排名" tone="neutral" />
        <ScoreCard label="第一名" value={top?.signal.symbol ?? "-"} detail={top ? top.signal.name : "資料整理中"} tone="positive" />
        <ScoreCard label="平均 5D 分數" value={`${averageScore}`} detail="分數不是機率" tone={scoreTone(averageScore)} />
        <ScoreCard label="研究區間漲幅" value="+32.4%" detail="TAIEX 3/2 → 6/3" tone="positive" />
        <ScoreCard label="平均風險" value={`${averageRisk}`} detail="越低越保守" tone={averageRisk >= 55 ? "risk" : "neutral"} />
        <ScoreCard label="平均過熱扣分" value={`${averageOverheat}`} detail="最高扣 15 分" tone={averageOverheat >= 8 ? "risk" : "neutral"} />
      </section>

      <section className="panel market-state-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Market First</p>
            <h2>先判斷台股市場狀態</h2>
          </div>
          <span className="panel-tag">市場分數先決定部位強弱</span>
        </div>
        <div className="market-state-grid">
          {marketState.components.map((component) => (
            <div key={component.label}>
              <span>{component.label}</span>
              <strong>{component.value}</strong>
              <small>{component.detail}</small>
            </div>
          ))}
        </div>
        <p className="panel-note">MarketScore = 加權指數趨勢 30%、市場寬度 20%、大盤資金 20%、美股與 AI 外溢 15%、匯率 10%、波動風險 5%，再扣集中風險。3/1-6/3 的結論是強多但集中，所以可以挑股，但不能無腦追高。</p>
      </section>

      <section className="panel market-state-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Market Study</p>
            <h2>3/1-6/3 台股情形</h2>
          </div>
          <span className="panel-tag">官方 TWSE / MOPS 資料整理</span>
        </div>
        <div className="market-state-grid">
          <div>
            <span>TAIEX 區間</span>
            <strong>+32.4%</strong>
            <small>35,095.09 → 46,459.16，6/3 創區間高點。</small>
          </div>
          <div>
            <span>20D / 60D</span>
            <strong>+12.9% / +38.3%</strong>
            <small>站上 MA20 與 MA60，屬強趨勢。</small>
          </div>
          <div>
            <span>市場寬度</span>
            <strong>70%</strong>
            <small>6/3 上漲 763 檔、下跌 289 檔。</small>
          </div>
          <div>
            <span>最大回撤</span>
            <strong>-9.6%</strong>
            <small>強多裡仍有急跌風險，過熱扣分不可拿掉。</small>
          </div>
        </div>
        <div className="horizon-weight-grid">
          {tool.research.sector_rotation.slice(0, 6).map((sector) => (
            <div key={sector.name}>
              <span>{sector.name}</span>
              <strong>{sector.score}</strong>
              <small>{typeof sector.return === "number" ? `3/2-6/3 約 ${(sector.return * 100).toFixed(1)}%` : "用籌碼、技術與營收再決定是否入選"}</small>
            </div>
          ))}
        </div>
        <p className="panel-note">新工具不把 AI 當唯一答案。電子零組件、IC 設計、晶圓製造、AI 供應鏈確實是研究期主軸，但金融避險、航運、機器人、重電、內需股仍可靠同業相對強度、籌碼與基本面進入候選。</p>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">1D / 5D / 20D</p>
            <h2>不同週期使用不同權重</h2>
          </div>
          <span className="panel-tag">流動性是硬性過濾，不拿來加分</span>
        </div>
        <div className="horizon-weight-grid">
          <HorizonWeightCard horizon="1d" title="1D 隔日" detail="重視籌碼、技術與美股夜盤" />
          <HorizonWeightCard horizon="5d" title="5D 短線" detail="重視籌碼延續與相對強度" />
          <HorizonWeightCard horizon="20d" title="20D 波段" detail="重視月營收、產業景氣與獲利品質" />
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Category First</p>
            <h2>推薦也先選大分類，再看小分類</h2>
          </div>
          <span className="panel-tag">大分類依平均 5D 分數排序</span>
        </div>
        <div className="recommendation-category-grid">
          {recommendationGroups.map((group, index) => (
            <details className="recommendation-category-card" key={group.majorCategory} open={index === 0}>
              <summary>
                <b>{index + 1}</b>
                <div>
                  <strong>{group.majorCategory}</strong>
                  <span>{group.count} 檔入選 · 平均 {group.averageScore}</span>
                </div>
                <em>{group.averageScore}</em>
              </summary>
              <div className="recommendation-category-body">
                <div className="recommendation-categories">
                  {group.subcategories.map((subcategory) => (
                    <b key={`${group.majorCategory}-${subcategory.name}`}>
                      {subcategory.name} · {subcategory.score}
                    </b>
                  ))}
                </div>
                <div className="industry-stock-list">
                  {group.rows.slice(0, 5).map((row) => (
                    <a href={`/stocks/${row.signal.symbol}`} key={`${group.majorCategory}-${row.signal.symbol}`}>
                      {row.signal.symbol} {row.signal.name} · {row.score}
                    </a>
                  ))}
                </div>
              </div>
            </details>
          ))}
        </div>
        <p className="panel-note">這裡的分類不是固定偏 AI，而是依每檔股票的大分類、小分類、籌碼、技術、基本面、風險與市場狀態重新排序；同一大分類裡的小分類也會由好到不好排列。</p>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Top 20</p>
            <h2>明燈推薦清單</h2>
          </div>
          <span className="panel-tag">市場狀態 × 個股分數 - 扣分</span>
        </div>
        <div className="recommendation-list">
          {recommendations.map((row, index) => (
            <a className="recommendation-row" href={`/stocks/${row.signal.symbol}`} key={row.signal.symbol}>
              <b>{index + 1}</b>
              <div>
                <strong>{row.signal.symbol} {row.signal.name}</strong>
                <span>{row.reason}</span>
                <div className="recommendation-categories">
                  <b>{row.majorCategory}</b>
                  {row.subcategories.slice(0, 2).map((subcategory) => <b key={`${row.signal.symbol}-${subcategory}`}>{subcategory}</b>)}
                </div>
              </div>
              <div className="recommendation-price">
                <span>現價 / 外部法人</span>
                <strong>{formatPrice(row.targetRange.currentPrice)} → {row.externalTarget.isAvailable ? formatPrice(row.externalTarget.targetPriceMean) : "待授權"}</strong>
                <small>{formatQuoteDate(row.signal.quote?.date)} · {row.externalTarget.isAvailable ? row.externalTarget.sourceLabel : `模型估算 ${formatPrice(row.targetRange.base)}`}</small>
              </div>
              <em>{row.score}</em>
              <small>1D {row.scores["1d"]} · 5D {row.scores["5d"]} · 20D {row.scores["20d"]} · 過熱扣 {row.overheatPenalty} · 事件扣 {row.eventRiskPenalty}</small>
            </a>
          ))}
        </div>
        <p className="panel-note">排序預設看 5D 短線分數。候選池不再鎖固定 20 檔，會從 TWSE / TPEx 最新報價裡先過濾低價、低流動性與風險，再依 1D / 5D / 20D 權重重排。分數不是上漲機率；真正的 probability_up_1d / 5d / 20d 需要用 2018 至今歷史分數分桶、Brier Score 與 walk-forward 回測校準後再顯示。</p>
      </section>
    </AppShell>
  );
}

function HorizonWeightCard({ horizon, title, detail }: { horizon: HorizonKey; title: string; detail: string }) {
  const weights = horizonWeights[horizon];
  return (
    <div>
      <span>{title}</span>
      <strong>{detail}</strong>
      <small>
        技術 {weights.technical}% · 籌碼 {weights.chip}% · 美股 {weights.usMarket}% · 市場 {weights.market}% · 新聞 {weights.news}% · 月營收 {weights.revenueIndustry}% · 基本面 {weights.fundamental}% · 估值 {weights.valuation}%
      </small>
    </div>
  );
}

function buildRecommendationGroups(rows: RecommendationRow[]): RecommendationCategoryGroup[] {
  const buckets = new Map<string, RecommendationRow[]>();
  rows.forEach((row) => {
    const bucket = buckets.get(row.majorCategory) ?? [];
    bucket.push(row);
    buckets.set(row.majorCategory, bucket);
  });

  return Array.from(buckets.entries())
    .map(([majorCategory, bucketRows]) => {
      const sortedRows = [...bucketRows].sort((left, right) => right.score - left.score);
      return {
        majorCategory,
        averageScore: Math.round(bucketRows.reduce((sum, row) => sum + row.score, 0) / Math.max(1, bucketRows.length)),
        count: bucketRows.length,
        rows: sortedRows,
        subcategories: buildRecommendationSubcategories(bucketRows),
      } satisfies RecommendationCategoryGroup;
    })
    .sort((left, right) => right.averageScore - left.averageScore || right.count - left.count);
}

function buildRecommendationSubcategories(rows: RecommendationRow[]): RecommendationCategoryGroup["subcategories"] {
  const buckets = new Map<string, RecommendationRow[]>();
  rows.forEach((row) => {
    row.subcategories.forEach((subcategory) => {
      const bucket = buckets.get(subcategory) ?? [];
      bucket.push(row);
      buckets.set(subcategory, bucket);
    });
  });

  return Array.from(buckets.entries())
    .map(([name, bucketRows]) => ({
      name,
      score: Math.round(bucketRows.reduce((sum, row) => sum + row.score, 0) / Math.max(1, bucketRows.length)),
      count: bucketRows.length,
    }))
    .sort((left, right) => right.score - left.score || right.count - left.count)
    .slice(0, 6);
}

function buildRecommendation(signal: PredictionSignal, marketState: MarketState): RecommendationRow {
  const metrics = buildStockMetrics(signal);
  const classification = classifySignal(signal);
  const marketProfile = getMarketProfile(signal);
  const factors = buildFactorInputs(signal, metrics, marketProfile, marketState);
  const stockScores = buildHorizonScores(factors);
  const overheatPenalty = calculateOverheatPenalty(signal, metrics);
  const eventRiskPenalty = calculateEventRiskPenalty(signal);
  const marketMultiplier = buildMarketMultiplier(marketState, marketProfile);
  const scores = mapHorizonScores(stockScores, (stockScore) => clampScore(stockScore * marketMultiplier - overheatPenalty - eventRiskPenalty));
  const score = scores["5d"];
  const targetRange = buildTargetPriceRange(signal);
  const externalTarget = buildExternalAnalystTargetPrice(signal);

  return {
    signal,
    score,
    scores,
    stockScores,
    overheatPenalty,
    eventRiskPenalty,
    liquidityPassed: passesLiquidityFilter(signal),
    reason: buildReason(signal, metrics, marketProfile, marketState, overheatPenalty),
    themes: marketProfile.themes,
    themeFit: marketProfile.fit,
    majorCategory: classification.major.name,
    subcategories: classification.subcategories,
    metrics,
    targetRange,
    externalTarget,
  };
}

function formatPrice(value: number | null): string {
  if (typeof value !== "number") return "待授權";
  if (value >= 1000) return value.toLocaleString("zh-TW", { maximumFractionDigits: 0 });
  if (value >= 100) return value.toLocaleString("zh-TW", { maximumFractionDigits: 1 });
  return value.toLocaleString("zh-TW", { maximumFractionDigits: 2 });
}

function formatQuoteDate(value: string | null | undefined): string {
  if (!value || value === "資料日期待確認") return "日期待確認";
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) return value;
  return `${Number(match[2])}/${Number(match[3])} 官價`;
}

function buildReason(
  signal: PredictionSignal,
  metrics: ReturnType<typeof buildStockMetrics>,
  marketProfile: { fit: number; themes: string[] },
  marketState: MarketState,
  overheatPenalty: number,
): string {
  const drivers = [
    marketProfile.themes.length ? `產業：${marketProfile.themes.slice(0, 2).join(" / ")}` : "",
    marketState.score >= 65 ? "市場狀態加分" : "",
    metrics.riskScore <= 45 ? "風險較低" : "",
    metrics.chipScore >= 65 ? "籌碼偏強" : "",
    metrics.technicalScore >= 65 ? "技術面偏強" : "",
    metrics.fundamentalScore >= 62 ? "基本面加分" : "",
    metrics.usMarketScore >= 60 ? "美股連動加分" : "",
    overheatPenalty >= 6 ? `過熱扣 ${overheatPenalty}` : "",
  ].filter(Boolean);
  const fallback = signal.explanation?.top_positive_factors?.[0] ?? "多因子條件相對完整";
  return sanitizeDisplayText(drivers.slice(0, 3).join(" · ") || fallback);
}

function buildMarketState(tool: TaiwanPredictionToolResponse): MarketState {
  return {
    score: tool.market_state.score,
    label: tool.market_state.label,
    action: tool.market_state.action,
    multiplier: tool.market_state.multiplier,
    tone: tool.market_state.tone,
    components: tool.market_state.components.map((component) => ({
      label: component.name,
      value: component.score,
      detail: component.detail,
    })),
  };
}

function buildFactorInputs(
  signal: PredictionSignal,
  metrics: ReturnType<typeof buildStockMetrics>,
  marketProfile: { fit: number; themes: string[] },
  marketState: MarketState,
) {
  const revenueIndustry = clampScore(
    marketProfile.fit * 0.3
    + metrics.fundamentalScore * 0.32
    + metrics.chipScore * 0.12
    + metrics.technicalScore * 0.12
    + metrics.usMarketScore * 0.08
    + metrics.newsScore * 0.06,
  );
  const valuation = clampScore(
    metrics.targetPriceScore * 0.4
    + metrics.fundamentalScore * 0.28
    + metrics.riskAdjustedScore * 0.22
    + (100 - metrics.riskScore) * 0.1,
  );
  return {
    technical: metrics.technicalScore,
    chip: metrics.chipScore,
    usMarket: metrics.usMarketScore,
    market: marketState.score,
    news: metrics.newsScore,
    revenueIndustry,
    fundamental: metrics.fundamentalScore,
    valuation,
    confidence: Math.round(signal.confidence * 100),
  };
}

function buildHorizonScores(factors: ReturnType<typeof buildFactorInputs>): HorizonScores {
  return mapHorizonScores(horizonWeights, (weights) => clampScore(
    factors.technical * (weights.technical / 100)
    + factors.chip * (weights.chip / 100)
    + factors.usMarket * (weights.usMarket / 100)
    + factors.market * (weights.market / 100)
    + factors.news * (weights.news / 100)
    + factors.revenueIndustry * (weights.revenueIndustry / 100)
    + factors.fundamental * (weights.fundamental / 100)
    + factors.valuation * (weights.valuation / 100)
    + Math.max(0, factors.confidence - 60) * 0.04,
  ));
}

function mapHorizonScores<T>(source: Record<HorizonKey, T>, mapper: (value: T, horizon: HorizonKey) => number): HorizonScores {
  return {
    "1d": mapper(source["1d"], "1d"),
    "5d": mapper(source["5d"], "5d"),
    "20d": mapper(source["20d"], "20d"),
  };
}

function buildMarketMultiplier(marketState: MarketState, marketProfile: { themes: string[] }): number {
  const defensive = marketProfile.themes.some((theme) => /金融|內需|食品|零售/.test(theme));
  if (marketState.score < 50 && defensive) return Math.min(1, marketState.multiplier + 0.06);
  if (marketState.score >= 65 && defensive) return Math.min(1.01, marketState.multiplier);
  return marketState.multiplier;
}

function calculateOverheatPenalty(signal: PredictionSignal, metrics: ReturnType<typeof buildStockMetrics>): number {
  let penalty = 0;
  if ((signal.technicals.rsi_14 ?? 0) > 75) penalty += 4;
  if (signal.technicals.ma_60 && signal.quote?.close && signal.quote.close > signal.technicals.ma_60 * 1.2) penalty += 5;
  if (metrics.technicalScore >= 78 && metrics.riskScore >= 55) penalty += 3;
  if ((signal.valuation?.pe_ratio ?? 0) >= 40 && metrics.fundamentalScore < 58) penalty += 3;
  if (metrics.chipScore < 48 && metrics.technicalScore > 70) penalty += 4;
  return Math.min(15, Math.round(penalty));
}

function calculateEventRiskPenalty(signal: PredictionSignal): number {
  const eventRisk = toScore(signal.risk_score.event);
  const negativeNews = signal.news.filter((item) => item.sentiment === "negative" || item.impact_score < -0.35).length;
  const riskFlags = signal.risk_flags?.filter((flag) => flag.severity >= 3).length ?? 0;
  return Math.min(12, Math.round(Math.max(0, eventRisk - 55) * 0.12 + negativeNews * 1.5 + riskFlags * 2));
}

function passesLiquidityFilter(signal: PredictionSignal): boolean {
  const tradeValue = signal.quote?.trade_value;
  if (typeof tradeValue !== "number" || tradeValue <= 0) return true;
  return tradeValue >= 30_000_000;
}

function toScore(value: number): number {
  if (value >= 0 && value <= 1) return value * 100;
  return Math.max(0, Math.min(100, value));
}

function clampScore(value: number): number {
  return Math.round(Math.max(0, Math.min(100, value)));
}

function getMarketProfile(signal: PredictionSignal): { fit: number; themes: string[] } {
  const classification = classifySignal(signal);
  return {
    fit: buildSignalIndustryScore(signal),
    themes: [classification.major.shortName, ...classification.subcategories],
  };
}
