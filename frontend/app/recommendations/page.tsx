import { AppShell } from "@/components/AppShell";
import { ScoreCard } from "@/components/ScoreCard";
import type { PredictionSignal, TaiwanPredictionToolResponse } from "@/lib/api";
import { fetchTaiwanPredictionTool, fetchTopProbabilityRanking } from "@/lib/api";
import { buildStockMetrics, sanitizeDisplayText, scoreTone } from "@/lib/view-model";

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
  metrics: ReturnType<typeof buildStockMetrics>;
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

const marketThemeProfiles: Record<string, { fit: number; themes: string[] }> = {
  "2330": { fit: 88, themes: ["半導體", "AI/HPC"] },
  "2454": { fit: 89, themes: ["IC 設計", "Edge AI"] },
  "3035": { fit: 89, themes: ["ASIC", "晶片設計服務"] },
  "3661": { fit: 89, themes: ["ASIC", "HPC"] },
  "2382": { fit: 90, themes: ["AI 伺服器", "雲端資料中心"] },
  "3231": { fit: 90, themes: ["AI 伺服器", "雲端資料中心"] },
  "6669": { fit: 90, themes: ["AI 伺服器", "雲端資料中心"] },
  "2317": { fit: 78, themes: ["EMS", "伺服器"] },
  "2308": { fit: 82, themes: ["電源管理", "資料中心"] },
  "2345": { fit: 80, themes: ["高速網通", "資料中心"] },
  "3017": { fit: 92, themes: ["散熱", "液冷"] },
  "3324": { fit: 92, themes: ["散熱", "液冷"] },
  "2383": { fit: 92, themes: ["CCL", "高速材料"] },
  "3037": { fit: 92, themes: ["ABF", "PCB/載板"] },
  "8046": { fit: 90, themes: ["ABF", "載板"] },
  "3711": { fit: 78, themes: ["封裝測試", "先進封裝"] },
  "1590": { fit: 74, themes: ["機器人", "氣動元件"] },
  "2049": { fit: 74, themes: ["機器人", "線性傳動"] },
  "2359": { fit: 74, themes: ["機器人", "AI 視覺"] },
  "1504": { fit: 76, themes: ["電機", "機器人/電動化"] },
  "1513": { fit: 78, themes: ["重電", "電網升級"] },
  "1519": { fit: 80, themes: ["重電", "變壓器"] },
  "1605": { fit: 72, themes: ["電線電纜", "電網"] },
  "2603": { fit: 63, themes: ["貨櫃航運", "景氣循環"] },
  "2609": { fit: 63, themes: ["貨櫃航運", "景氣循環"] },
  "2615": { fit: 63, themes: ["貨櫃航運", "景氣循環"] },
  "2618": { fit: 63, themes: ["航空", "旅運復甦"] },
  "2610": { fit: 63, themes: ["航空", "旅運復甦"] },
  "2634": { fit: 68, themes: ["航太", "國防"] },
  "2881": { fit: 66, themes: ["金融避險", "大型金控"] },
  "2882": { fit: 66, themes: ["金融避險", "大型金控"] },
  "2884": { fit: 66, themes: ["金融避險", "銀行"] },
  "2885": { fit: 66, themes: ["金融避險", "券商"] },
  "2886": { fit: 66, themes: ["金融避險", "銀行"] },
  "2891": { fit: 66, themes: ["金融避險", "大型金控"] },
  "5880": { fit: 66, themes: ["金融避險", "銀行"] },
  "5876": { fit: 66, themes: ["金融避險", "銀行"] },
  "1216": { fit: 56, themes: ["內需防禦", "食品通路"] },
  "2912": { fit: 56, themes: ["內需防禦", "零售通路"] },
  "2207": { fit: 43, themes: ["內需消費", "汽車"] },
  "6505": { fit: 68, themes: ["能源", "油品價差"] },
  "1301": { fit: 66, themes: ["塑化", "景氣循環"] },
  "1303": { fit: 66, themes: ["塑化", "景氣循環"] },
  "2002": { fit: 64, themes: ["鋼鐵", "景氣循環"] },
  "6446": { fit: 72, themes: ["生技醫療", "新藥"] },
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
  const averageRisk = Math.round(recommendations.reduce((sum, row) => sum + row.metrics.riskScore, 0) / Math.max(1, recommendations.length));
  const averageScore = Math.round(recommendations.reduce((sum, row) => sum + row.score, 0) / Math.max(1, recommendations.length));
  const averageOverheat = Math.round(recommendations.reduce((sum, row) => sum + row.overheatPenalty, 0) / Math.max(1, recommendations.length));

  return (
    <AppShell active="/recommendations">
      <header className="topbar">
        <div>
          <p className="eyebrow">明燈推薦 · 2026/03/01-06/03 研究版</p>
          <h1>今日前 20 檔研究觀察名單</h1>
        </div>
        <div className={`status ${marketState.tone === "positive" ? "ok" : marketState.tone === "negative" ? "risk" : ""}`}>市場狀態 {marketState.score} · {marketState.label}</div>
      </header>

      <section className="metric-grid">
        <ScoreCard label="市場狀態分數" value={`${marketState.score}`} detail={marketState.action} tone={marketState.tone} />
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
              </div>
              <em>{row.score}</em>
              <small>1D {row.scores["1d"]} · 5D {row.scores["5d"]} · 20D {row.scores["20d"]} · 過熱扣 {row.overheatPenalty} · 事件扣 {row.eventRiskPenalty}</small>
            </a>
          ))}
        </div>
        <p className="panel-note">排序預設看 5D 短線分數。分數不是上漲機率；真正的 probability_up_1d / 5d / 20d 需要用 2018 至今歷史分數分桶、Brier Score 與 walk-forward 回測校準後再顯示。</p>
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

function buildRecommendation(signal: PredictionSignal, marketState: MarketState): RecommendationRow {
  const metrics = buildStockMetrics(signal);
  const marketProfile = getMarketProfile(signal);
  const factors = buildFactorInputs(signal, metrics, marketProfile, marketState);
  const stockScores = buildHorizonScores(factors);
  const overheatPenalty = calculateOverheatPenalty(signal, metrics);
  const eventRiskPenalty = calculateEventRiskPenalty(signal);
  const marketMultiplier = buildMarketMultiplier(marketState, marketProfile);
  const scores = mapHorizonScores(stockScores, (stockScore) => clampScore(stockScore * marketMultiplier - overheatPenalty - eventRiskPenalty));
  const score = scores["5d"];

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
    metrics,
  };
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
  const direct = marketThemeProfiles[signal.symbol];
  if (direct) return direct;
  const haystack = `${signal.name} ${signal.sector ?? ""}`;
  const themes: string[] = [];
  if (/半導體|IC|晶片|封裝|測試/.test(haystack)) themes.push("半導體");
  if (/電腦|週邊|伺服器|雲端|資料中心/.test(haystack)) themes.push("AI/雲端");
  if (/電機|機械|自動化|氣動|機器人/.test(haystack)) themes.push("機器人/自動化");
  if (/航運|航空|運輸|物流/.test(haystack)) themes.push("運輸");
  if (/金融|銀行|金控|保險|證券/.test(haystack)) themes.push("金融避險");
  if (/電線|電纜|重電|電力|能源|油電/.test(haystack)) themes.push("電力能源");
  if (/水泥|塑膠|鋼鐵|化學|原物料/.test(haystack)) themes.push("原物料循環");
  if (/食品|百貨|觀光|汽車|零售/.test(haystack)) themes.push("內需防禦");
  if (/生技|醫療|製藥/.test(haystack)) themes.push("生技醫療");
  const fit = themes.length ? 58 + Math.min(18, themes.length * 6) : 52;
  return { fit, themes: themes.length ? themes : ["一般產業"] };
}
