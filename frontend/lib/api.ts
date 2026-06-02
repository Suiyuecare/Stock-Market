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

export type StockInstrument = MarketSummary["instruments"][number];

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
  probability_up_1d?: number | null;
  probability_up_5d?: number | null;
  probability_up_20d?: number | null;
  confidence: number;
  composite_score: number;
  bullish_score?: number | null;
  risk_adjusted_score?: number | null;
  explanation?: {
    top_positive_factors?: string[];
    top_negative_factors?: string[];
    top_risk_factors?: string[];
    component_scores?: Record<string, number>;
  } | null;
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
  instrument: StockInstrument;
  signal: PredictionSignal;
  factor_history: Array<{ date: string; composite_score: number; risk_score: number }>;
};

export type StockListResponse = {
  disclaimer: string;
  stocks: StockInstrument[];
};

export type StockScoresResponse = {
  disclaimer: string;
  stock_id: string;
  stock_name: string;
  BullishScore: number | null;
  RiskScore: number;
  RiskAdjustedScore: number | null;
  probability_up_1d: number | null;
  probability_up_5d: number | null;
  probability_up_20d: number | null;
  factor_scores: FactorScore[];
  explanation: PredictionSignal["explanation"];
  confidence: number;
};

export type TechnicalSignalPayload = {
  state?: string;
  states?: string[];
  score_signal?: number;
  golden_cross?: boolean;
  death_cross?: boolean;
  bullish_divergence?: boolean;
  bearish_divergence?: boolean;
  dif?: number | null;
  dea?: number | null;
  macd_hist?: number | null;
  macd_bar_tw?: number | null;
  [key: string]: unknown;
};

export type StockTechnicalResponse = {
  disclaimer: string;
  stock_id: string;
  stock_name: string;
  latest_indicators: TechnicalIndicators;
  signals: Record<string, TechnicalSignalPayload>;
  technical_score: {
    score: number;
    positive_factors: string[];
    negative_factors: string[];
    risk_factors: string[];
    confidence: number;
    trend_score?: number;
    volume_price_score?: number;
    macd_score?: number;
    rsi_score?: number;
    kd_score?: number;
    breakout_score?: number;
  };
};

export type StockInstitutionalResponse = {
  disclaimer: string;
  stock_id: string;
  stock_name: string;
  chip_score: {
    score: number;
    positive_factors: string[];
    negative_factors: string[];
    risk_factors: string[];
    confidence: number;
    [key: string]: unknown;
  };
  summary: Record<string, number | boolean | null>;
};

export type StockNewsResponse = {
  disclaimer: string;
  stock_id: string;
  stock_name: string;
  news: PredictionSignal["news"];
};

export type InstitutionalRankingResponse = {
  disclaimer: string;
  ranking: Array<{
    stock_id: string;
    stock_name: string;
    score: number;
    institutional_net_ratio: number;
    positive_factors: string[];
    risk_factors: string[];
  }>;
};

export type MacdRankingResponse = {
  disclaimer: string;
  ranking: Array<{
    stock_id: string;
    stock_name: string;
    macd_golden_cross: boolean;
    macd_hist: number | null;
    dif: number | null;
    dea: number | null;
    technical_score: number;
  }>;
};

export type VolumePriceRankingResponse = {
  disclaimer: string;
  ranking: Array<{
    stock_id: string;
    stock_name: string;
    state: string;
    states: string[];
    bearish_divergence: boolean;
    bullish_divergence: boolean;
    score_signal: number;
  }>;
};

export type USMarketRadarResponse = {
  disclaimer: string;
  linkage: Record<string, number>;
  stocks: Array<{
    stock_id: string;
    stock_name: string;
    score: number;
    sensitivity_multiplier: number;
    positive_factors: string[];
    negative_factors: string[];
    risk_factors: string[];
  }>;
};

export type HighRiskResponse = {
  disclaimer: string;
  signals: Array<{
    stock_id: string;
    stock_name: string;
    risk_score: RiskScore;
    probability_up_1d: number | null;
    top_risk_factors: string[];
  }>;
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

export async function fetchStocks(): Promise<StockListResponse> {
  return getJson<StockListResponse>("/api/stocks");
}

export async function fetchRanking(): Promise<RankingResponse> {
  return getJson<RankingResponse>("/api/stocks/ranking");
}

export async function fetchTopProbabilityRanking(): Promise<RankingResponse> {
  return getJson<RankingResponse>("/api/rankings/top-probability");
}

export async function fetchInstitutionalBuyingRanking(): Promise<InstitutionalRankingResponse> {
  return getJson<InstitutionalRankingResponse>("/api/rankings/institutional-buying");
}

export async function fetchMacdGoldenCrossRanking(): Promise<MacdRankingResponse> {
  return getJson<MacdRankingResponse>("/api/rankings/macd-golden-cross");
}

export async function fetchVolumePriceDivergenceRanking(): Promise<VolumePriceRankingResponse> {
  return getJson<VolumePriceRankingResponse>("/api/rankings/volume-price-divergence");
}

export async function fetchStockDetail(symbol: string): Promise<StockDetailResponse> {
  return getJson<StockDetailResponse>(`/api/stocks/${symbol}`);
}

export async function fetchStockScores(symbol: string): Promise<StockScoresResponse> {
  return getJson<StockScoresResponse>(`/api/stocks/${symbol}/scores`);
}

export async function fetchStockTechnical(symbol: string): Promise<StockTechnicalResponse> {
  return getJson<StockTechnicalResponse>(`/api/stocks/${symbol}/technical`);
}

export async function fetchStockInstitutional(symbol: string): Promise<StockInstitutionalResponse> {
  return getJson<StockInstitutionalResponse>(`/api/stocks/${symbol}/institutional`);
}

export async function fetchStockNews(symbol: string): Promise<StockNewsResponse> {
  return getJson<StockNewsResponse>(`/api/stocks/${symbol}/news`);
}

export async function fetchUSMarketRadar(): Promise<USMarketRadarResponse> {
  return getJson<USMarketRadarResponse>("/api/us-market/radar");
}

export async function fetchHighRisk(): Promise<HighRiskResponse> {
  return getJson<HighRiskResponse>("/api/risk/high-risk");
}
