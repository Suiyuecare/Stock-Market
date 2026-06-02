const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type MarketSummary = {
  session_date: string;
  tw_status: string;
  us_premarket_status: string;
  disclaimer: string;
  instruments: Array<{
    symbol: string;
    market: string;
    name: string;
    sector: string | null;
    currency: string;
  }>;
  us_linkage: Record<string, number>;
};

export type FactorScore = {
  name: string;
  category: string;
  score: number;
  weight: number;
  direction: string;
  explanation: string;
};

export type RiskScore = {
  total: number;
  volatility: number;
  liquidity: number;
  concentration: number;
  event: number;
  explanation: string;
};

export type TechnicalIndicators = {
  ma_5: number | null;
  ma_20: number | null;
  ma_60: number | null;
  rsi_14: number | null;
  k_9: number | null;
  d_9: number | null;
  macd: number | null;
  macd_signal: number | null;
  macd_histogram: number | null;
  obv: number | null;
  volume_price_divergence: number | null;
};

export type PredictionSignal = {
  symbol: string;
  name: string;
  signal_date: string;
  horizon: string;
  probability_up: number;
  confidence: number;
  composite_score: number;
  risk_score: RiskScore;
  technicals: TechnicalIndicators;
  factor_scores: FactorScore[];
  positive_drivers: FactorScore[];
  negative_drivers: FactorScore[];
  news: Array<{
    title: string;
    source: string;
    published_at: string;
    sentiment: string;
    impact_score: number;
    related_symbols: string[];
  }>;
};

export type RankingResponse = {
  disclaimer: string;
  signals: PredictionSignal[];
};

export type StockDetailResponse = {
  disclaimer: string;
  signal: PredictionSignal;
  factor_history: Array<{ date: string; composite_score: number; risk_score: number }>;
};

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`API request failed: ${path}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchMarketSummary(): Promise<MarketSummary> {
  return getJson<MarketSummary>("/api/market/summary");
}

export async function fetchRanking(): Promise<RankingResponse> {
  return getJson<RankingResponse>("/api/stocks/ranking");
}

export async function fetchStockDetail(symbol: string): Promise<StockDetailResponse> {
  return getJson<StockDetailResponse>(`/api/stocks/${symbol}`);
}
