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
    .replace(/\bbuy\b/gi, "正向訊號")
    .replace(/\bsell\b/gi, "負向訊號");
}

export function sanitizeRiskScore(risk: RiskScore): RiskScore {
  return {
    ...risk,
    explanation: sanitizeDisplayText(risk.explanation),
  };
}
