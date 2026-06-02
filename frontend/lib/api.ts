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
  try {
    const response = await fetch(`${apiBaseUrl}${path}`, { cache: "no-store" });
    if (response.ok) {
      return response.json() as Promise<T>;
    }
  } catch {
    // The production frontend can launch before the FastAPI service is deployed.
  }
  return mockResponse(path) as T;
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

const disclaimer = "本系統僅提供資料分析與研究用途，不構成個人化投資建議。";

const instruments: StockInstrument[] = [
  { symbol: "2330", market: "TW", name: "台積電", sector: "半導體", currency: "TWD" },
  { symbol: "2454", market: "TW", name: "聯發科", sector: "半導體", currency: "TWD" },
  { symbol: "2317", market: "TW", name: "鴻海", sector: "電子代工", currency: "TWD" },
  { symbol: "2308", market: "TW", name: "台達電", sector: "電源管理", currency: "TWD" },
];

const linkage = {
  NASDAQ: 0.42,
  QQQ: 0.38,
  SOX: 0.55,
  SMH: 0.46,
  "S&P500": 0.24,
  VIX: -0.31,
  TSM_ADR: 0.48,
  TSM_ADR_PREMIUM: 0.08,
  NVDA: 0.62,
  AMD: 0.34,
  AAPL: 0.18,
  AVGO: 0.47,
  MU: 0.22,
  MSFT: 0.19,
  META: 0.12,
  GOOGL: 0.16,
  AMZN: 0.15,
};

function factor(name: string, category: string, score: number, weight: number, direction = "positive"): FactorScore {
  return {
    name,
    category,
    score,
    weight,
    direction,
    explanation: `${name} contributes an explainable research signal for this MVP.`,
  };
}

function signal(symbol: string, name: string, index: number): PredictionSignal {
  const base = 0.68 - index * 0.04;
  const riskTotal = 0.3 + index * 0.05;
  const factorScores = [
    factor("FundamentalScore", "fundamental", 72 - index * 3, 0.2),
    factor("ChipScore", "chip", 68 - index * 2, 0.18),
    factor("TechnicalScore", "technical", 74 - index * 2, 0.17),
    factor("USMarketScore", "us_market", 78 - index * 4, 0.15),
    factor("NewsScore", "news", 64 - index * 2, 0.12),
    factor("TargetPriceScore", "target_price", 50, 0.05, "neutral"),
  ];

  return {
    symbol,
    name,
    signal_date: "2026-06-02",
    horizon: "1D/5D/20D",
    probability_up: base,
    probability_up_1d: base,
    probability_up_5d: base - 0.03,
    probability_up_20d: base - 0.06,
    confidence: 0.72 - index * 0.03,
    composite_score: 0.58 - index * 0.04,
    bullish_score: 70 - index * 4,
    risk_adjusted_score: 58 - index * 5,
    explanation: {
      top_positive_factors: ["SOX and AI supply-chain linkage are constructive", "Technical trend remains above medium averages"],
      top_negative_factors: ["FX volatility can pressure exporters", "Valuation sensitivity remains elevated"],
      top_risk_factors: ["VIX change", "Event risk", "Liquidity and volatility watch"],
      component_scores: {
        FundamentalScore: 72 - index * 3,
        ChipScore: 68 - index * 2,
        TechnicalScore: 74 - index * 2,
        USMarketScore: 78 - index * 4,
        NewsScore: 64 - index * 2,
        TargetPriceScore: 50,
      },
    },
    risk_score: {
      total: riskTotal,
      volatility: 0.32 + index * 0.03,
      liquidity: 0.2 + index * 0.02,
      concentration: 0.28 + index * 0.04,
      event: 0.36 + index * 0.03,
      explanation: "Mock risk score combining volatility, liquidity, concentration, and event risk.",
    },
    technicals: {
      ma_5: 612 + index * 12,
      ma_20: 598 + index * 10,
      ma_60: 560 + index * 8,
      rsi_14: 61 - index * 2,
      k_9: 58 - index,
      d_9: 54 - index,
      macd: 2.4 - index * 0.2,
      macd_signal: 1.8 - index * 0.15,
      macd_histogram: 0.6 - index * 0.05,
      obv: 1260000 - index * 80000,
      volume_price_divergence: index === 2 ? -0.3 : 0.2,
    },
    factor_scores: factorScores,
    positive_drivers: factorScores.filter((item) => item.direction === "positive").slice(0, 3),
    negative_drivers: [factor("FX volatility", "macro", 42, 0.08, "negative"), factor("Event risk", "risk", 38, 0.1, "negative")],
    news: mockNews(symbol),
  };
}

const signals = instruments.map((item, index) => signal(item.symbol, item.name, index));

function mockNews(symbol: string): PredictionSignal["news"] {
  return [
    {
      title: `${symbol} supply-chain demand remains resilient`,
      source: "mock-news",
      published_at: "2026-06-02T08:30:00Z",
      sentiment: "positive",
      impact_score: 0.28,
      related_symbols: [symbol, "NVDA", "TSM_ADR"],
    },
    {
      title: "FX volatility remains a near-term risk for Taiwan exporters",
      source: "mock-macro",
      published_at: "2026-06-02T04:30:00Z",
      sentiment: "cautious",
      impact_score: -0.12,
      related_symbols: [symbol],
    },
  ];
}

function findSignal(symbol: string): PredictionSignal {
  return signals.find((item) => item.symbol === symbol.toUpperCase()) ?? signals[0];
}

function stockDetail(symbol: string): StockDetailResponse {
  const selected = findSignal(symbol);
  const instrument = instruments.find((item) => item.symbol === selected.symbol) ?? instruments[0];
  return {
    disclaimer,
    instrument,
    signal: selected,
    factor_history: [
      { date: "2026-05-27", composite_score: 0.18, risk_score: 0.34 },
      { date: "2026-05-28", composite_score: 0.22, risk_score: 0.33 },
      { date: "2026-05-29", composite_score: 0.26, risk_score: 0.31 },
      { date: "2026-06-01", composite_score: selected.composite_score, risk_score: selected.risk_score.total },
    ],
  };
}

function technicalResponse(symbol: string): StockTechnicalResponse {
  const selected = findSignal(symbol);
  return {
    disclaimer,
    stock_id: selected.symbol,
    stock_name: selected.name,
    latest_indicators: selected.technicals,
    signals: {
      macd: {
        golden_cross: true,
        death_cross: false,
        bullish_divergence: false,
        bearish_divergence: false,
        dif: selected.technicals.macd,
        dea: selected.technicals.macd_signal,
        macd_hist: selected.technicals.macd_histogram,
        macd_bar_tw: (selected.technicals.macd_histogram ?? 0) * 2,
      },
      volume_price_divergence: {
        state: "price up + volume up",
        states: ["price up + volume up", "OBV confirming"],
        score_signal: 0.2,
        bullish_divergence: false,
        bearish_divergence: false,
      },
    },
    technical_score: {
      score: selected.explanation?.component_scores?.TechnicalScore ?? 70,
      positive_factors: ["MA trend remains constructive", "MACD histogram is positive"],
      negative_factors: [],
      risk_factors: ["Watch volume confirmation"],
      confidence: selected.confidence,
      trend_score: 72,
      volume_price_score: 66,
      macd_score: 74,
      rsi_score: 62,
      kd_score: 60,
      breakout_score: 58,
    },
  };
}

function institutionalResponse(symbol: string): StockInstitutionalResponse {
  const selected = findSignal(symbol);
  return {
    disclaimer,
    stock_id: selected.symbol,
    stock_name: selected.name,
    chip_score: {
      score: selected.explanation?.component_scores?.ChipScore ?? 65,
      positive_factors: ["Foreign investor net buying for 3 consecutive days", "Institutional net ratio is positive"],
      negative_factors: [],
      risk_factors: ["Dealer hedge flow should be monitored"],
      confidence: 0.7,
      foreign_net_ratio: 0.08,
      investment_trust_net_ratio: 0.03,
      dealer_net_ratio: 0.01,
      institutional_net_ratio: 0.12,
      consecutive_foreign_net_buy_days: 3,
      consecutive_investment_trust_net_buy_days: 2,
    },
    summary: {
      foreign_net_ratio: 0.08,
      investment_trust_net_ratio: 0.03,
      dealer_net_ratio: 0.01,
      institutional_net_ratio: 0.12,
      consecutive_foreign_net_buy_days: 3,
      consecutive_investment_trust_net_buy_days: 2,
      synchronized_institutional_buying: true,
      synchronized_institutional_selling: false,
    },
  };
}

function usMarketRadar(): USMarketRadarResponse {
  return {
    disclaimer,
    linkage,
    stocks: signals.map((item, index) => ({
      stock_id: item.symbol,
      stock_name: item.name,
      score: item.explanation?.component_scores?.USMarketScore ?? 70,
      sensitivity_multiplier: 1.2 - index * 0.08,
      positive_factors: ["SOX and NVDA support AI/semiconductor linkage"],
      negative_factors: index === 2 ? ["Apple supply-chain guidance sensitivity"] : [],
      risk_factors: ["VIX remains a market risk factor"],
    })),
  };
}

function mockResponse(path: string): unknown {
  if (path === "/api/market/summary") {
    return {
      session_date: "2026-06-02",
      tw_status: "盤後資料就緒",
      us_premarket_status: "美股開盤前觀察",
      disclaimer,
      instruments,
      us_linkage: linkage,
    } satisfies MarketSummary;
  }
  if (path === "/api/stocks") {
    return { disclaimer, stocks: instruments } satisfies StockListResponse;
  }
  if (path === "/api/stocks/ranking" || path === "/api/rankings/top-probability") {
    return { disclaimer, signals } satisfies RankingResponse;
  }
  if (path === "/api/rankings/institutional-buying") {
    return {
      disclaimer,
      ranking: signals.map((item) => ({
        stock_id: item.symbol,
        stock_name: item.name,
        score: item.explanation?.component_scores?.ChipScore ?? 65,
        institutional_net_ratio: 0.12,
        positive_factors: ["Institutional net buying remains positive"],
        risk_factors: ["Flow can reverse quickly"],
      })),
    } satisfies InstitutionalRankingResponse;
  }
  if (path === "/api/rankings/macd-golden-cross") {
    return {
      disclaimer,
      ranking: signals.map((item) => ({
        stock_id: item.symbol,
        stock_name: item.name,
        macd_golden_cross: true,
        macd_hist: item.technicals.macd_histogram,
        dif: item.technicals.macd,
        dea: item.technicals.macd_signal,
        technical_score: item.explanation?.component_scores?.TechnicalScore ?? 70,
      })),
    } satisfies MacdRankingResponse;
  }
  if (path === "/api/rankings/volume-price-divergence") {
    return {
      disclaimer,
      ranking: signals.map((item) => ({
        stock_id: item.symbol,
        stock_name: item.name,
        state: "price up + volume up",
        states: ["price up + volume up", "OBV confirming"],
        bearish_divergence: false,
        bullish_divergence: false,
        score_signal: 0.2,
      })),
    } satisfies VolumePriceRankingResponse;
  }
  if (path === "/api/us-market/radar") {
    return usMarketRadar();
  }
  if (path === "/api/risk/high-risk") {
    return {
      disclaimer,
      signals: signals
        .slice()
        .sort((a, b) => b.risk_score.total - a.risk_score.total)
        .map((item) => ({
          stock_id: item.symbol,
          stock_name: item.name,
          risk_score: item.risk_score,
          probability_up_1d: item.probability_up_1d ?? null,
          top_risk_factors: item.explanation?.top_risk_factors ?? [],
        })),
    } satisfies HighRiskResponse;
  }

  const stockMatch = path.match(/^\/api\/stocks\/([^/]+)(?:\/([^/]+))?$/);
  if (stockMatch) {
    const symbol = stockMatch[1];
    const section = stockMatch[2];
    const selected = findSignal(symbol);
    if (section === "scores") {
      return {
        disclaimer,
        stock_id: selected.symbol,
        stock_name: selected.name,
        BullishScore: selected.bullish_score ?? null,
        RiskScore: selected.risk_score.total,
        RiskAdjustedScore: selected.risk_adjusted_score ?? null,
        probability_up_1d: selected.probability_up_1d ?? null,
        probability_up_5d: selected.probability_up_5d ?? null,
        probability_up_20d: selected.probability_up_20d ?? null,
        factor_scores: selected.factor_scores,
        explanation: selected.explanation,
        confidence: selected.confidence,
      } satisfies StockScoresResponse;
    }
    if (section === "technical") {
      return technicalResponse(symbol);
    }
    if (section === "institutional") {
      return institutionalResponse(symbol);
    }
    if (section === "news") {
      return { disclaimer, stock_id: selected.symbol, stock_name: selected.name, news: selected.news } satisfies StockNewsResponse;
    }
    return stockDetail(symbol);
  }

  return { disclaimer };
}
