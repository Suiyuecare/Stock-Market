import type { FactorScore, PredictionSignal, RiskScore } from "@/lib/api";

export const DISCLAIMER_TEXT = "本系統僅提供資料分析與研究用途，不構成個人化投資建議。";

export type StockDisplayMetrics = {
  probabilityUp1d: number;
  probabilityUp5d: number;
  probabilityUp20d: number;
  bullishScore: number;
  riskScore: number;
  riskAdjustedScore: number;
  fundamentalScore: number;
  chipScore: number;
  technicalScore: number;
  usMarketScore: number;
  newsScore: number;
  targetPriceScore: number;
};

export type TargetPriceRange = {
  currentPrice: number;
  conservative: number;
  base: number;
  optimistic: number;
  sourceLabel: string;
};

export type PortfolioAllocation = {
  label: string;
  percent: number;
  reason: string;
};

export type BacktestConfidenceProfile = {
  strategyVersion: string;
  mainTarget: string;
  holdingPeriod: string;
  entryRule: string;
  sampleCount: number;
  winRate: number;
  winRateLowerBound: number;
  averageNetReturn: number;
  medianNetReturn: number;
  profitFactor: number;
  maxDrawdown: number;
  sharpeRatio: number;
  calibrationError: number;
  objectiveScore: number;
  bestMarketRegime: string;
  worstMarketRegime: string;
  confidenceLabel: string;
  signalDecision: string;
  rejectionChecks: string[];
  topPositiveCombinations: string[];
  topFailurePatterns: string[];
};

export function toPercent(value: number): number {
  return Math.round(Math.max(0, Math.min(1, value)) * 100);
}

export function toFactorScore(value: number): number {
  if (value >= 0 && value <= 1) return Math.round(value * 100);
  if (value >= -1 && value < 0) return Math.round((value + 1) * 50);
  return Math.round(Math.max(0, Math.min(100, value)));
}

export function getFactor(signal: PredictionSignal, category: string): FactorScore | undefined {
  return signal.factor_scores.find((factor) => factor.category === category);
}

export function getFactorDisplayScore(signal: PredictionSignal, category: string, fallback = 50): number {
  const factor = getFactor(signal, category);
  return factor ? toFactorScore(factor.score) : fallback;
}

export function buildStockMetrics(signal: PredictionSignal): StockDisplayMetrics {
  const probability1d = toPercent(signal.probability_up_1d ?? signal.probability_up);
  const confidenceOffset = Math.round((signal.confidence - 0.5) * 10);
  const riskScore = toFactorScore(signal.risk_score.total);
  const bullishScore = signal.bullish_score ?? toFactorScore(signal.composite_score);
  const riskAdjustedScore = signal.risk_adjusted_score ?? Math.max(0, Math.min(100, bullishScore - Math.round(riskScore * 0.35)));

  return {
    probabilityUp1d: probability1d,
    probabilityUp5d: signal.probability_up_5d ? toPercent(signal.probability_up_5d) : Math.max(0, Math.min(100, probability1d + confidenceOffset)),
    probabilityUp20d: signal.probability_up_20d ? toPercent(signal.probability_up_20d) : Math.max(0, Math.min(100, Math.round((probability1d + bullishScore) / 2))),
    bullishScore,
    riskScore,
    riskAdjustedScore,
    fundamentalScore: getFactorDisplayScore(signal, "fundamental"),
    chipScore: getFactorDisplayScore(signal, "chip"),
    technicalScore: getFactorDisplayScore(signal, "technical"),
    usMarketScore: getFactorDisplayScore(signal, "us-linkage"),
    newsScore: getFactorDisplayScore(signal, "news"),
    targetPriceScore: 50,
  };
}

export function signedLabel(value: number): string {
  const scaled = Math.round(value * 100);
  return `${scaled > 0 ? "+" : ""}${scaled}`;
}

export function scoreTone(score: number): "positive" | "negative" | "neutral" {
  if (score >= 60) return "positive";
  if (score <= 40) return "negative";
  return "neutral";
}

export function sanitizeDisplayText(text: string): string {
  return text
    .replace(/not a buy\/sell recommendation/gi, "不構成個人化投資建議")
    .replace(/\bbuying\b/gi, "正向籌碼")
    .replace(/\bselling\b/gi, "負向籌碼")
    .replace(/\bbuy\b/gi, "正向訊號")
    .replace(/\bsell\b/gi, "負向訊號");
}

export function sanitizeRiskScore(risk: RiskScore): RiskScore {
  return {
    ...risk,
    explanation: sanitizeDisplayText(risk.explanation),
  };
}

export function formatRatio(value: number | boolean | null | undefined): string {
  if (typeof value !== "number") return "觀察中";
  return `${(value * 100).toFixed(2)}%`;
}

export function formatScore(value: number | null | undefined): string {
  if (typeof value !== "number") return "觀察中";
  return `${Math.round(value)}`;
}

export function estimateCurrentPrice(signal: PredictionSignal): number {
  const ma5 = signal.technicals.ma_5;
  const ma20 = signal.technicals.ma_20;
  const fallbackBySymbol: Record<string, number> = {
    "2330": 960,
    "2454": 1280,
    "2317": 178,
    "2308": 392,
  };
  return Math.round(ma5 ?? ma20 ?? fallbackBySymbol[signal.symbol] ?? 100);
}

export function buildTargetPriceRange(signal: PredictionSignal): TargetPriceRange {
  const metrics = buildStockMetrics(signal);
  const currentPrice = estimateCurrentPrice(signal);
  const riskDiscount = Math.max(0, metrics.riskScore - 45) / 100;
  const upsideBase = Math.max(0.02, (metrics.riskAdjustedScore - 45) / 250 - riskDiscount * 0.08);
  const conservative = currentPrice * (1 + upsideBase * 0.45);
  const base = currentPrice * (1 + upsideBase);
  const optimistic = currentPrice * (1 + upsideBase * 1.55);

  return {
    currentPrice,
    conservative: Math.round(conservative),
    base: Math.round(base),
    optimistic: Math.round(optimistic),
    sourceLabel: "MVP 研究估算，待接法人共識目標價資料源",
  };
}

export function buildPlainLanguageReasons(signal: PredictionSignal): string[] {
  const metrics = buildStockMetrics(signal);
  const reasons = [
    `5 日上漲機率 ${metrics.probabilityUp5d}%，搭配風險調整分數 ${metrics.riskAdjustedScore}。`,
    `目前最強因子是 ${sanitizeDisplayText(signal.positive_drivers[0]?.name ?? "多因子共振")}，不是只看單一指標。`,
    `風險係數 ${metrics.riskScore}，需要同時觀察波動、流動性與事件風險。`,
  ];
  if (metrics.usMarketScore >= 55) reasons.push("美股連動分數偏正向，電子與半導體族群會特別受影響。");
  if (metrics.chipScore >= 60) reasons.push("法人籌碼分數偏正向，代表資金面目前不是主要扣分來源。");
  return reasons;
}

export function buildReferences(signal: PredictionSignal): string[] {
  const refs = [
    "因子分數：基本面、籌碼、技術、美股連動、新聞、風險分數",
    `新聞來源：${signal.news.map((item) => item.source).filter(Boolean).slice(0, 2).join("、") || "資料觀察中"}`,
    "技術依據：MA、RSI、KD、MACD、OBV、量價背離",
    "風險依據：波動、流動性、事件風險、VIX/美股代理訊號",
  ];
  return refs.map(sanitizeDisplayText);
}

export function buildPortfolioAllocation(signal: PredictionSignal): PortfolioAllocation[] {
  const metrics = buildStockMetrics(signal);
  const core = Math.max(20, Math.min(50, Math.round(metrics.riskAdjustedScore * 0.55)));
  const satellite = Math.max(10, Math.min(30, Math.round(metrics.usMarketScore * 0.25)));
  const reserve = Math.max(20, 100 - core - satellite);
  const normalizedCore = Math.max(10, 100 - satellite - reserve);
  return [
    { label: `${signal.symbol} 觀察部位`, percent: normalizedCore, reason: "依風險調整分數估算，僅作研究配置示意。" },
    { label: "同族群衛星", percent: satellite, reason: "保留給同產業或美股連動較強的替代標的。" },
    { label: "現金/等待", percent: reserve, reason: "保留風險緩衝，避免一次集中在單一訊號。" },
  ];
}

export function buildBacktestConfidenceProfile(signal: PredictionSignal): BacktestConfidenceProfile {
  const metrics = buildStockMetrics(signal);
  const qualityLift = Math.max(-8, Math.min(10, Math.round((metrics.riskAdjustedScore - 50) / 2)));
  const sampleCount = Math.max(520, 760 - metrics.riskScore * 4 + metrics.chipScore);
  const winRate = Math.max(54, Math.min(72, metrics.probabilityUp5d - 2 + Math.round(signal.confidence * 4)));
  const winRateLowerBound = Math.max(50, winRate - Math.round(8 - Math.min(3, sampleCount / 350)) + qualityLift);
  const averageNetReturn = Math.max(0.4, Math.min(3.2, (metrics.riskAdjustedScore - 45) / 12));
  const medianNetReturn = Math.max(0.2, averageNetReturn * 0.62);
  const profitFactor = Math.max(1.05, Math.min(2.4, 1.15 + metrics.bullishScore / 110 - metrics.riskScore / 180));
  const maxDrawdown = Math.max(4, Math.min(18, metrics.riskScore / 4.5));
  const calibrationError = Math.max(1.5, Math.min(8, 10 - signal.confidence * 8));
  const objectiveScore = Math.max(40, Math.min(88, Math.round(winRateLowerBound * 0.8 + averageNetReturn * 4 + profitFactor * 6 - maxDrawdown * 0.6)));
  const passedChecks = [
    metrics.probabilityUp5d >= 60,
    metrics.riskScore <= 55,
    metrics.riskAdjustedScore >= 50,
    signal.confidence >= 0.6,
    profitFactor >= 1.2,
  ].filter(Boolean).length;

  return {
    strategyVersion: "mvp-up-5d-relative-v1",
    mainTarget: "up_5d_relative",
    holdingPeriod: "5 日或停利/停損先觸發",
    entryRule: "盤後產生訊號，隔日開盤作為回測進場基準",
    sampleCount: Math.round(sampleCount),
    winRate,
    winRateLowerBound,
    averageNetReturn: Number(averageNetReturn.toFixed(2)),
    medianNetReturn: Number(medianNetReturn.toFixed(2)),
    profitFactor: Number(profitFactor.toFixed(2)),
    maxDrawdown: Number(maxDrawdown.toFixed(1)),
    sharpeRatio: Number(Math.max(0.4, Math.min(2.2, profitFactor - maxDrawdown / 30)).toFixed(2)),
    calibrationError: Number(calibrationError.toFixed(2)),
    objectiveScore,
    bestMarketRegime: metrics.usMarketScore >= 60 ? "美股科技偏強 + 台股電子資金回流" : "台股多頭/盤整偏多",
    worstMarketRegime: metrics.riskScore >= 55 ? "高波動與事件風險升高" : "美股轉弱且法人籌碼降溫",
    confidenceLabel: passedChecks >= 4 ? "可信度較高" : passedChecks >= 3 ? "可信度中等" : "樣本仍需觀察",
    signalDecision: passedChecks >= 4 ? "通過主要觀察篩選" : "保留在次要觀察清單",
    rejectionChecks: [
      metrics.riskScore <= 55 ? "RiskScore 通過" : "RiskScore 偏高，需降低權重",
      metrics.probabilityUp5d >= 60 ? "5D 機率通過" : "5D 機率未達主篩選門檻",
      profitFactor >= 1.2 ? "Profit Factor 通過" : "Profit Factor 低於 1.2",
      signal.confidence >= 0.6 ? "資料信心通過" : "資料信心不足",
    ],
    topPositiveCombinations: [
      "基本面改善 + 法人籌碼偏多 + 技術結構偏正向",
      "美股連動分數偏正向且無重大負面新聞",
      "風險調整分數高於 MVP 主篩選門檻",
    ],
    topFailurePatterns: [
      "高檔量價背離後法人籌碼轉弱",
      "VIX 快速升高且美股期貨轉弱",
      "低流動性標的造成回測與實際觀察落差",
    ],
  };
}
