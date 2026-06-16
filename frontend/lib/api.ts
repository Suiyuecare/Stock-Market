import { brokerResearchSymbols, getBrokerAnalystTargetPrice, getBrokerResearchEventsForInstrument, getBrokerResearchScore } from "@/lib/broker-research";
import { fetchLatestSupabaseAnalystTargetPrice, isSupabaseAnalystTargetReadConfigured, isSupabaseAnalystTargetWriteConfigured } from "@/lib/supabase-analyst-targets";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const twseListedCompanyUrl = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L";
const twseMonthlyRevenueUrl = "https://openapi.twse.com.tw/v1/opendata/t187ap05_L";
const twseDailyQuoteUrl = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL";
const twseStockDayUrl = "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY";
const twseValuationUrl = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL";
const twseMaterialNewsUrl = "https://openapi.twse.com.tw/v1/opendata/t187ap04_L";
const twseExchangeNewsUrl = "https://openapi.twse.com.tw/v1/news/newsList";
const twseExchangeEventsUrl = "https://openapi.twse.com.tw/v1/news/eventList";
const twseAttentionUrl = "https://openapi.twse.com.tw/v1/announcement/notice";
const twseDispositionUrl = "https://openapi.twse.com.tw/v1/announcement/punish";
const twseMarginUrl = "https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN";
const twseForeignHoldingUrl = "https://openapi.twse.com.tw/v1/fund/MI_QFIIS_sort_20";
const tpexQuoteUrl = "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes";
const tpexValuationUrl = "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_peratio_analysis";
const tdccOwnershipDistributionUrl = "https://smart.tdcc.com.tw/opendata/getOD.ashx?id=1-5";
const cnaFinanceRssUrl = "https://feeds.feedburner.com/rsscna/finance";
const cnaTechnologyRssUrl = "https://feeds.feedburner.com/rsscna/technology";
const fmpTargetPriceConsensusUrl = "https://financialmodelingprep.com/stable/price-target-consensus";
const analystProviderUrls = {
  factset: "https://developer.factset.com/api-catalog/factset-estimates-api",
  lseg: "https://developers.lseg.com/en/api-catalog/refinitiv-data-platform/estimates-API",
  bloomberg: "https://professional.bloomberg.com/products/data/data-management/data-license/",
  fmp: "https://financialmodelingprep.com/stable/price-target-consensus",
};

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
  data_source_status?: DataSourceStatus[];
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
    summary?: string;
    url?: string;
    image_url?: string;
    event_type?: string;
    source_url?: string;
    linkage_reason?: string;
  }>;
  quote?: TwseQuote | null;
  valuation?: TwseValuation | null;
  analyst_target_price?: AnalystTargetPrice | null;
  risk_flags?: ApiRiskFlag[];
  data_source_status?: DataSourceStatus[];
  sector?: string | null;
};

export type TwseQuote = {
  source: "TWSE OpenAPI" | "TWSE Official STOCK_DAY" | "TPEx OpenAPI";
  endpoint: string;
  date: string;
  symbol: string;
  name: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  change: number | null;
  trade_volume: number | null;
  trade_value: number | null;
  transaction_count: number | null;
};

export type TwseValuation = {
  source: "TWSE OpenAPI" | "TPEx OpenAPI";
  endpoint: string;
  date: string;
  symbol: string;
  name: string;
  pe_ratio: number | null;
  dividend_yield: number | null;
  pb_ratio: number | null;
  dividend_per_share?: number | null;
};

export type AnalystTargetPrice = {
  symbol: string;
  currency: string;
  target_price_mean: number | null;
  target_price_high: number | null;
  target_price_low: number | null;
  analyst_count?: number | null;
  broker?: string | null;
  rating?: string | null;
  source: string;
  source_type: "licensed_or_keyed_api" | "news_extracted" | "needs_license";
  source_url?: string;
  published_at?: string;
  confidence: number;
  provider_status: "configured" | "needs_key" | "extracted";
  note: string;
};

export type ApiRiskFlag = {
  source: string;
  endpoint: string;
  title: string;
  detail: string;
  severity: number;
  related_symbols: string[];
  url?: string;
};

export type DataSourceStatus = {
  name: string;
  status: "connected" | "configured" | "needs_key";
  detail: string;
  url: string;
  requires_key: boolean;
};

export type RankingResponse = {
  disclaimer: string;
  signals: PredictionSignal[];
  data_date?: string;
  candidate_count?: number;
  method?: string;
  freshness?: RecommendationFreshness;
};

export type RecommendationFreshness = {
  mode: "official_aggregate" | "per_stock_override" | "demo";
  label: string;
  summary: string;
  twse_stock_day_all_date?: string | null;
  twse_official_stock_day_date?: string | null;
  tpex_date?: string | null;
  market_study_baseline_date?: string | null;
};

export type StockDetailResponse = {
  disclaimer: string;
  instrument: StockInstrument;
  signal: PredictionSignal;
  factor_history: Array<{ date: string; composite_score: number; risk_score: number }>;
  growth_history: RevenueGrowthPoint[];
  growth_source: DataSourceReference;
};

export type RevenueGrowthPoint = {
  date: string;
  label: string;
  revenue_million_twd: number;
  revenue_yoy: number | null;
  revenue_mom: number | null;
  accumulated_yoy: number | null;
};

export type DataSourceReference = {
  name: string;
  url: string;
  dataset: string;
  published_at: string;
  note: string;
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

export type TaiwanPredictionToolResponse = {
  disclaimer: string;
  research: {
    research_window: {
      start: string;
      first_trading_day: string;
      end: string;
      trading_days: number;
    };
    market_summary: Record<string, number | string | boolean>;
    sector_rotation: Array<{
      name: string;
      score: number;
      return: number | null;
      role: string;
    }>;
    hard_filters: Record<string, number | boolean>;
    model_notes: string[];
    data_sources: Array<{ name: string; url: string; usage: string }>;
  };
  horizon_weights: Record<"1d" | "5d" | "20d", Record<string, number>>;
  market_state: {
    score: number;
    label: string;
    action: string;
    tone: "positive" | "negative" | "neutral";
    multiplier: number;
    components: Array<{ name: string; score: number; detail: string }>;
  };
  ranked_signals: Array<{
    symbol: string;
    name: string;
    score_1d: number;
    score_5d: number;
    score_20d: number;
    reason: string;
    overheat_penalty: number;
    event_risk_penalty: number;
    liquidity_passed: boolean;
  }>;
};

async function getJson<T>(path: string): Promise<T> {
  try {
    const response = await fetchWithTimeout(`${apiBaseUrl}${path}`, { cache: "no-store", timeoutMs: 1500 });
    if (response.ok) {
      return response.json() as Promise<T>;
    }
  } catch {
    // The production frontend can launch before the FastAPI service is deployed.
  }
  return (await mockResponse(path)) as T;
}

export async function fetchMarketSummary(): Promise<MarketSummary> {
  return getJson<MarketSummary>("/api/market/summary");
}

export async function fetchTaiwanPredictionTool(): Promise<TaiwanPredictionToolResponse> {
  return getJson<TaiwanPredictionToolResponse>("/api/market/taiwan-prediction-tool");
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
  const detail = await getJson<StockDetailResponse>(`/api/stocks/${symbol}`);
  const signalWithLatestMarketData = await attachTwseMarketData(detail.signal);
  return {
    ...detail,
    instrument: {
      ...detail.instrument,
      symbol: signalWithLatestMarketData.symbol,
      name: signalWithLatestMarketData.name,
      sector: signalWithLatestMarketData.sector ?? detail.instrument.sector,
      market: signalWithLatestMarketData.quote?.source === "TPEx OpenAPI" ? "TPEX" : detail.instrument.market,
      currency: "TWD",
    },
    signal: signalWithLatestMarketData,
  };
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
  const response = await getJson<StockNewsResponse>(`/api/stocks/${symbol}/news`);
  const instruments = await getFallbackInstruments();
  const normalized = symbol.toUpperCase();
  const instrument = instruments.find((item) => item.symbol === normalized) ?? {
    symbol: normalized,
    name: response.stock_name,
    market: "TW",
    sector: null,
    currency: "TWD",
  };
  const officialNews = await getNewsForInstrument(instrument);
  return {
    ...response,
    stock_id: instrument.symbol,
    stock_name: instrument.name,
    news: dedupeNews([...officialNews, ...response.news])
      .sort((a, b) => Date.parse(b.published_at) - Date.parse(a.published_at))
      .slice(0, 12),
  };
}

export async function fetchUSMarketRadar(): Promise<USMarketRadarResponse> {
  return getJson<USMarketRadarResponse>("/api/us-market/radar");
}

export async function fetchHighRisk(): Promise<HighRiskResponse> {
  return getJson<HighRiskResponse>("/api/risk/high-risk");
}

const disclaimer = "本系統僅提供資料整理、研究分析與教育用途，不構成個人化投資建議、投資顧問服務、交易指示、獲利保證或招攬買賣；MVP Beta 期間部分資料可能延遲、估算或仍為示範資料。";

const seedInstruments: StockInstrument[] = [
  { symbol: "1101", market: "TW", name: "台泥", sector: "水泥工業", currency: "TWD" },
  { symbol: "1102", market: "TW", name: "亞泥", sector: "水泥工業", currency: "TWD" },
  { symbol: "1216", market: "TW", name: "統一", sector: "食品工業", currency: "TWD" },
  { symbol: "1301", market: "TW", name: "台塑", sector: "塑膠工業", currency: "TWD" },
  { symbol: "1303", market: "TW", name: "南亞", sector: "塑膠工業", currency: "TWD" },
  { symbol: "1326", market: "TW", name: "台化", sector: "塑膠工業", currency: "TWD" },
  { symbol: "1402", market: "TW", name: "遠東新", sector: "紡織纖維", currency: "TWD" },
  { symbol: "1590", market: "TW", name: "亞德客-KY", sector: "電機機械", currency: "TWD" },
  { symbol: "2002", market: "TW", name: "中鋼", sector: "鋼鐵工業", currency: "TWD" },
  { symbol: "2207", market: "TW", name: "和泰車", sector: "汽車工業", currency: "TWD" },
  { symbol: "2301", market: "TW", name: "光寶科", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2303", market: "TW", name: "聯電", sector: "半導體", currency: "TWD" },
  { symbol: "2308", market: "TW", name: "台達電", sector: "電源管理", currency: "TWD" },
  { symbol: "2317", market: "TW", name: "鴻海", sector: "電子代工", currency: "TWD" },
  { symbol: "2324", market: "TW", name: "仁寶", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2330", market: "TW", name: "台積電", sector: "半導體", currency: "TWD" },
  { symbol: "2345", market: "TW", name: "智邦", sector: "通信網路", currency: "TWD" },
  { symbol: "2357", market: "TW", name: "華碩", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2379", market: "TW", name: "瑞昱", sector: "半導體", currency: "TWD" },
  { symbol: "2382", market: "TW", name: "廣達", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2395", market: "TW", name: "研華", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2408", market: "TW", name: "南亞科", sector: "半導體", currency: "TWD" },
  { symbol: "2059", market: "TW", name: "川湖", sector: "伺服器導軌", currency: "TWD" },
  { symbol: "2376", market: "TW", name: "技嘉", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2377", market: "TW", name: "微星", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2455", market: "TW", name: "全新", sector: "光通訊", currency: "TWD" },
  { symbol: "2458", market: "TW", name: "義隆", sector: "半導體", currency: "TWD" },
  { symbol: "3017", market: "TW", name: "奇鋐", sector: "散熱", currency: "TWD" },
  { symbol: "3324", market: "TPEX", name: "雙鴻", sector: "散熱", currency: "TWD" },
  { symbol: "2383", market: "TW", name: "台光電", sector: "CCL", currency: "TWD" },
  { symbol: "3037", market: "TW", name: "欣興", sector: "PCB/載板", currency: "TWD" },
  { symbol: "3081", market: "TPEX", name: "聯亞", sector: "光通訊", currency: "TWD" },
  { symbol: "3189", market: "TW", name: "景碩", sector: "PCB/載板", currency: "TWD" },
  { symbol: "3260", market: "TPEX", name: "威剛", sector: "記憶體模組", currency: "TWD" },
  { symbol: "3515", market: "TPEX", name: "華擎", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "3653", market: "TW", name: "健策", sector: "散熱", currency: "TWD" },
  { symbol: "3665", market: "TW", name: "貿聯-KY", sector: "高速連接器", currency: "TWD" },
  { symbol: "3710", market: "TPEX", name: "連展投控", sector: "光通訊/連接器", currency: "TWD" },
  { symbol: "4971", market: "TPEX", name: "IET-KY", sector: "光通訊", currency: "TWD" },
  { symbol: "4991", market: "TPEX", name: "環宇-KY", sector: "光通訊", currency: "TWD" },
  { symbol: "5274", market: "TPEX", name: "信驊", sector: "半導體", currency: "TWD" },
  { symbol: "6197", market: "TW", name: "佳必琪", sector: "連接器", currency: "TWD" },
  { symbol: "6274", market: "TW", name: "台燿", sector: "CCL", currency: "TWD" },
  { symbol: "6442", market: "TW", name: "光聖", sector: "光通訊", currency: "TWD" },
  { symbol: "6510", market: "TPEX", name: "精測", sector: "半導體", currency: "TWD" },
  { symbol: "8210", market: "TW", name: "勤誠", sector: "伺服器機殼", currency: "TWD" },
  { symbol: "2049", market: "TW", name: "上銀", sector: "機器人/自動化", currency: "TWD" },
  { symbol: "2359", market: "TW", name: "所羅門", sector: "機器人/AI 視覺", currency: "TWD" },
  { symbol: "1504", market: "TW", name: "東元", sector: "電機機械", currency: "TWD" },
  { symbol: "1513", market: "TW", name: "中興電", sector: "重電", currency: "TWD" },
  { symbol: "1519", market: "TW", name: "華城", sector: "重電", currency: "TWD" },
  { symbol: "1605", market: "TW", name: "華新", sector: "電線電纜", currency: "TWD" },
  { symbol: "2618", market: "TW", name: "長榮航", sector: "航空", currency: "TWD" },
  { symbol: "2610", market: "TW", name: "華航", sector: "航空", currency: "TWD" },
  { symbol: "2634", market: "TW", name: "漢翔", sector: "航太/國防", currency: "TWD" },
  { symbol: "2912", market: "TW", name: "統一超", sector: "貿易百貨", currency: "TWD" },
  { symbol: "6446", market: "TPEX", name: "藥華藥", sector: "生技醫療", currency: "TWD" },
  { symbol: "2330", market: "TW", name: "台積電", sector: "半導體", currency: "TWD" },
  { symbol: "2454", market: "TW", name: "聯發科", sector: "半導體", currency: "TWD" },
  { symbol: "2603", market: "TW", name: "長榮", sector: "航運業", currency: "TWD" },
  { symbol: "2609", market: "TW", name: "陽明", sector: "航運業", currency: "TWD" },
  { symbol: "2615", market: "TW", name: "萬海", sector: "航運業", currency: "TWD" },
  { symbol: "2880", market: "TW", name: "華南金", sector: "金融保險", currency: "TWD" },
  { symbol: "2881", market: "TW", name: "富邦金", sector: "金融保險", currency: "TWD" },
  { symbol: "2882", market: "TW", name: "國泰金", sector: "金融保險", currency: "TWD" },
  { symbol: "2884", market: "TW", name: "玉山金", sector: "金融保險", currency: "TWD" },
  { symbol: "2885", market: "TW", name: "元大金", sector: "金融保險", currency: "TWD" },
  { symbol: "2886", market: "TW", name: "兆豐金", sector: "金融保險", currency: "TWD" },
  { symbol: "2891", market: "TW", name: "中信金", sector: "金融保險", currency: "TWD" },
  { symbol: "3008", market: "TW", name: "大立光", sector: "光電業", currency: "TWD" },
  { symbol: "3034", market: "TW", name: "聯詠", sector: "半導體", currency: "TWD" },
  { symbol: "3035", market: "TW", name: "智原", sector: "半導體", currency: "TWD" },
  { symbol: "3231", market: "TW", name: "緯創", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "3661", market: "TW", name: "世芯-KY", sector: "半導體", currency: "TWD" },
  { symbol: "3711", market: "TW", name: "日月光投控", sector: "半導體", currency: "TWD" },
  { symbol: "4904", market: "TW", name: "遠傳", sector: "通信網路", currency: "TWD" },
  { symbol: "4938", market: "TW", name: "和碩", sector: "電子代工", currency: "TWD" },
  { symbol: "5871", market: "TW", name: "中租-KY", sector: "金融保險", currency: "TWD" },
  { symbol: "5876", market: "TW", name: "上海商銀", sector: "金融保險", currency: "TWD" },
  { symbol: "5880", market: "TW", name: "合庫金", sector: "金融保險", currency: "TWD" },
  { symbol: "6505", market: "TW", name: "台塑化", sector: "油電燃氣", currency: "TWD" },
  { symbol: "6669", market: "TW", name: "緯穎", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "8046", market: "TW", name: "南電", sector: "電子零組件", currency: "TWD" },
];

let twseInstrumentCache: StockInstrument[] | null = null;
const revenueGrowthCache = new Map<string, { history: RevenueGrowthPoint[]; source: DataSourceReference }>();
let twseQuoteCache: Map<string, TwseQuote> | null = null;
let twseQuoteCacheLoadedAt = 0;
let twseValuationCache: Map<string, TwseValuation> | null = null;
let tpexQuoteCache: Map<string, TwseQuote> | null = null;
let tpexQuoteCacheLoadedAt = 0;
let tpexValuationCache: Map<string, TwseValuation> | null = null;
let apiRiskFlagCache: Map<string, ApiRiskFlag[]> | null = null;
let officialNewsCache: NewsItem[] | null = null;
let officialNewsCacheLoadedAt = 0;
let fallbackSignalsCache: PredictionSignal[] | null = null;
let fallbackRecommendationSignalsCache: PredictionSignal[] | null = null;
let fallbackRecommendationSignalsCacheLoadedAt = 0;
let fallbackRecommendationDataDate = "資料日期待確認";
let fallbackRecommendationCandidateCount = 0;
let fallbackRecommendationFreshness: RecommendationFreshness = {
  mode: "demo",
  label: "資料日期待確認",
  summary: "官方來源日期尚未確認，頁面可能顯示示範資料或延遲資料。",
  twse_stock_day_all_date: null,
  twse_official_stock_day_date: null,
  tpex_date: null,
  market_study_baseline_date: "2026-06-03",
};
let twseQuoteCachePromise: Promise<Map<string, TwseQuote>> | null = null;
let twseValuationCachePromise: Promise<Map<string, TwseValuation>> | null = null;
let tpexQuoteCachePromise: Promise<Map<string, TwseQuote>> | null = null;
let tpexValuationCachePromise: Promise<Map<string, TwseValuation>> | null = null;
let apiRiskFlagCachePromise: Promise<Map<string, ApiRiskFlag[]>> | null = null;
let officialNewsCachePromise: Promise<NewsItem[]> | null = null;
let fallbackSignalsCachePromise: Promise<PredictionSignal[]> | null = null;
let fallbackRecommendationSignalsCachePromise: Promise<PredictionSignal[]> | null = null;
const analystTargetCache = new Map<string, { loadedAt: number; value: AnalystTargetPrice }>();

type NewsItem = PredictionSignal["news"][number] & {
  stock_id?: string | null;
  related_industry?: string | null;
};

const industryCodeMap: Record<string, string> = {
  "01": "水泥工業",
  "02": "食品工業",
  "03": "塑膠工業",
  "04": "紡織纖維",
  "05": "電機機械",
  "06": "電器電纜",
  "08": "玻璃陶瓷",
  "09": "造紙工業",
  "10": "鋼鐵工業",
  "11": "橡膠工業",
  "12": "汽車工業",
  "14": "建材營造",
  "15": "航運業",
  "16": "觀光餐旅",
  "17": "金融保險",
  "18": "貿易百貨",
  "20": "其他",
  "21": "化學工業",
  "22": "生技醫療",
  "23": "油電燃氣",
  "24": "半導體",
  "25": "電腦及週邊",
  "26": "光電業",
  "27": "通信網路",
  "28": "電子零組件",
  "29": "電子通路",
  "30": "資訊服務",
  "31": "其他電子",
  "32": "文化創意",
  "33": "農業科技",
  "34": "電子商務",
  "35": "綠能環保",
  "36": "數位雲端",
  "37": "運動休閒",
  "38": "居家生活",
};

async function getFallbackInstruments(): Promise<StockInstrument[]> {
  if (twseInstrumentCache) return twseInstrumentCache;
  const normalized: StockInstrument[] = [];
  try {
    const response = await fetch(twseListedCompanyUrl, { next: { revalidate: 60 * 60 * 6 } });
    if (response.ok) {
      const rows = (await response.json()) as Array<Record<string, string>>;
      normalized.push(...rows
        .map((row) => {
          const symbol = String(row["公司代號"] ?? "").trim();
          const name = String(row["公司簡稱"] || row["公司名稱"] || symbol).trim();
          const industryCode = String(row["產業別"] ?? "").trim();
          if (!/^\d{4}$/.test(symbol) || !name) return null;
          const sector = industryCodeMap[industryCode] ?? (industryCode || "未分類");
          const instrument: StockInstrument = {
            symbol,
            market: "TW",
            name,
            sector,
            currency: "TWD",
          };
          return instrument;
        })
        .filter((item): item is StockInstrument => item !== null));
    }
  } catch {
    // Keep the frontend resilient when TWSE is temporarily unavailable.
  }
  try {
    const tpexQuoteMap = await getTpexQuoteMap();
    normalized.push(...Array.from(tpexQuoteMap.values()).map((quote) => ({
      symbol: quote.symbol,
      market: "TPEX",
      name: quote.name,
      sector: "上櫃",
      currency: "TWD",
    } satisfies StockInstrument)));
  } catch {
    // TPEx data is additive; the TWSE/seed pool keeps the app usable.
  }
  twseInstrumentCache = uniqueInstruments(normalized.length > 0 ? normalized : seedInstruments);
  return twseInstrumentCache;
}

function uniqueInstruments(items: StockInstrument[]): StockInstrument[] {
  const seen = new Set<string>();
  return items.filter((item) => {
    if (seen.has(item.symbol)) return false;
    seen.add(item.symbol);
    return true;
  });
}

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

const recommendationCoverageSymbols = Array.from(new Set([
  ...brokerResearchSymbols,
  "2330", "2454", "3035", "3661", "2382", "3231", "6669", "2317", "2308", "2345",
  "3017", "3324", "2383", "3037", "8046", "3711", "1590", "2049", "2359", "1504",
  "1513", "1519", "1605", "2603", "2609", "2615", "2618", "2610", "2634", "2881",
  "2882", "2884", "2885", "2886", "2891", "5880", "5876", "1216", "2912", "2207",
  "6505", "1301", "1303", "2002", "6446", "5871", "4904", "3008", "2408", "2357",
]));

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

function symbolSeed(symbol: string): number {
  return symbol.split("").reduce((sum, char, index) => sum + char.charCodeAt(0) * (index + 3), 0);
}

function bounded(seed: number, min: number, max: number, salt = 0): number {
  const raw = Math.abs(Math.sin(seed * 12.9898 + salt * 78.233) * 43758.5453);
  return min + (raw - Math.floor(raw)) * (max - min);
}

function parseTwseNumber(value: string | undefined): number | null {
  if (!value) return null;
  const numeric = Number(String(value).replaceAll(",", "").trim());
  return Number.isFinite(numeric) ? numeric : null;
}

function parseTwseDate(value: string | undefined): string {
  const trimmed = String(value ?? "").trim();
  if (!/^\d{7}$/.test(trimmed)) return "資料日期待確認";
  const year = Number(trimmed.slice(0, 3)) + 1911;
  return `${year}-${trimmed.slice(3, 5)}-${trimmed.slice(5, 7)}`;
}

function parseTwseSlashDate(value: string | undefined): string {
  const trimmed = String(value ?? "").trim();
  const match = /^(\d{3})\/(\d{2})\/(\d{2})$/.exec(trimmed);
  if (!match) return "資料日期待確認";
  const year = Number(match[1]) + 1911;
  return `${year}-${match[2]}-${match[3]}`;
}

function taipeiDateKey(date = new Date()): string {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Taipei",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(date);
  const values = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return `${values.year}${values.month}${values.day}`;
}

function taipeiIsoDate(date = new Date()): string {
  const key = taipeiDateKey(date);
  return `${key.slice(0, 4)}-${key.slice(4, 6)}-${key.slice(6, 8)}`;
}

function taipeiMarketRefreshWindowStarted(date = new Date()): boolean {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Taipei",
    weekday: "short",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).formatToParts(date);
  const values = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  const weekday = values.weekday ?? "";
  if (weekday === "Sat" || weekday === "Sun") return false;
  const minutes = Number(values.hour) * 60 + Number(values.minute);
  return minutes >= 13 * 60 + 30;
}

function pickLatestQuote(...quotes: Array<TwseQuote | null | undefined>): TwseQuote | null {
  return quotes.reduce<TwseQuote | null>((latest, quote) => {
    if (!quote?.close) return latest;
    if (!latest) return quote;
    return quote.date > latest.date ? quote : latest;
  }, null);
}

function isTradableCommonStock(symbol: string): boolean {
  return /^\d{4}$/.test(symbol) && !symbol.startsWith("0");
}

function shouldRefreshTwsePerStockQuotes(quotes: TwseQuote[]): boolean {
  if (!taipeiMarketRefreshWindowStarted()) return false;
  const latestTwseDate = quotes
    .filter((quote) => quote.source === "TWSE OpenAPI")
    .map((quote) => quote.date)
    .sort()
    .at(-1);
  return Boolean(latestTwseDate && latestTwseDate !== "資料日期待確認" && latestTwseDate < taipeiIsoDate());
}

function dateBehindToday(date: string): boolean {
  return Boolean(taipeiMarketRefreshWindowStarted() && date && date !== "資料日期待確認" && date < taipeiIsoDate());
}

function quoteMapBehindToday(map: Map<string, TwseQuote>): boolean {
  const latestDate = latestQuoteDateFromQuotes(Array.from(map.values()));
  return latestDate ? dateBehindToday(latestDate) : false;
}

function latestQuoteDateFromQuotes(quotes: Array<TwseQuote | null | undefined>): string | null {
  return quotes
    .map((quote) => quote?.date)
    .filter((date): date is string => Boolean(date && date !== "資料日期待確認"))
    .sort()
    .at(-1) ?? null;
}

function latestQuoteDateFromMap(map: Map<string, TwseQuote>): string | null {
  return latestQuoteDateFromQuotes(Array.from(map.values()));
}

function buildRecommendationFreshness(params: {
  twseStockDayAllDate: string | null;
  twseOfficialStockDayDate: string | null;
  tpexDate: string | null;
}): RecommendationFreshness {
  const marketStudyBaselineDate = "2026-06-03";
  const { twseStockDayAllDate, twseOfficialStockDayDate, tpexDate } = params;
  if (twseOfficialStockDayDate && twseStockDayAllDate && twseOfficialStockDayDate > twseStockDayAllDate) {
    return {
      mode: "per_stock_override",
      label: `個股官方補最新至 ${twseOfficialStockDayDate}`,
      summary: `TWSE STOCK_DAY_ALL 仍停在 ${twseStockDayAllDate}；推薦池已改用 TWSE 個股 STOCK_DAY 補到 ${twseOfficialStockDayDate}，TPEx 盤後資料 ${tpexDate ?? "待確認"}。市場研究快照與 sector rotation 仍沿用 ${marketStudyBaselineDate} 基準。`,
      twse_stock_day_all_date: twseStockDayAllDate,
      twse_official_stock_day_date: twseOfficialStockDayDate,
      tpex_date: tpexDate,
      market_study_baseline_date: marketStudyBaselineDate,
    };
  }
  if (twseStockDayAllDate || tpexDate) {
    const displayedDate = [twseStockDayAllDate, tpexDate].filter((date): date is string => Boolean(date)).sort().at(-1) ?? "資料日期待確認";
    return {
      mode: "official_aggregate",
      label: `官方盤後資料 ${displayedDate}`,
      summary: `推薦池目前以官方盤後總表更新：TWSE STOCK_DAY_ALL ${twseStockDayAllDate ?? "待確認"}、TPEx ${tpexDate ?? "待確認"}。市場研究快照與 sector rotation 仍沿用 ${marketStudyBaselineDate} 基準。`,
      twse_stock_day_all_date: twseStockDayAllDate,
      twse_official_stock_day_date: twseOfficialStockDayDate,
      tpex_date: tpexDate,
      market_study_baseline_date: marketStudyBaselineDate,
    };
  }
  return {
    mode: "demo",
    label: "官方資料待確認",
    summary: `尚未取得新的官方盤後日期，暫維持既有資料。市場研究快照基準為 ${marketStudyBaselineDate}。`,
    twse_stock_day_all_date: twseStockDayAllDate,
    twse_official_stock_day_date: twseOfficialStockDayDate,
    tpex_date: tpexDate,
    market_study_baseline_date: marketStudyBaselineDate,
  };
}

async function mapWithConcurrency<T, R>(items: T[], limit: number, mapper: (item: T, index: number) => Promise<R>): Promise<R[]> {
  const results = new Array<R>(items.length);
  let cursor = 0;
  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (cursor < items.length) {
      const index = cursor;
      cursor += 1;
      results[index] = await mapper(items[index], index);
    }
  });
  await Promise.all(workers);
  return results;
}

function quoteChangePercent(quote: TwseQuote | null | undefined): number {
  if (!quote?.close || quote.change === null || quote.change === undefined) return 0;
  const previousClose = quote.close - quote.change;
  if (!Number.isFinite(previousClose) || previousClose <= 0) return 0;
  return quote.change / previousClose;
}

function quoteRangePositionScore(quote: TwseQuote | null | undefined): number {
  if (!quote?.close || !quote.high || !quote.low || quote.high <= quote.low) return 50;
  return clamp(((quote.close - quote.low) / (quote.high - quote.low)) * 100, 0, 100);
}

function quoteTradeValueScore(quote: TwseQuote | null | undefined): number {
  const tradeValue = quote?.trade_value ?? 0;
  if (tradeValue <= 0) return 0;
  return clamp(45 + Math.log10(Math.max(1, tradeValue / 30_000_000)) * 18, 0, 100);
}

function quoteAmplitudeRisk(quote: TwseQuote | null | undefined): number {
  if (!quote?.close || !quote.high || !quote.low) return 38;
  return clamp(((quote.high - quote.low) / quote.close) * 650, 12, 88);
}

function valuationQualityScore(valuation: TwseValuation | null | undefined): number {
  const pe = valuation?.pe_ratio ?? null;
  const pb = valuation?.pb_ratio ?? null;
  let score = 55;
  if (typeof pe === "number" && pe > 0) {
    if (pe >= 12 && pe <= 28) score += 12;
    else if (pe > 28 && pe <= 45) score += 4;
    else if (pe > 60) score -= 12;
    else if (pe < 8) score -= 4;
  }
  if (typeof pb === "number" && pb > 0) {
    if (pb <= 2.5) score += 6;
    else if (pb >= 6) score -= 8;
  }
  return clamp(score, 25, 82);
}

function topicFitScore(instrument: StockInstrument): number {
  const text = `${instrument.symbol} ${instrument.name} ${instrument.sector ?? ""}`;
  const rules: Array<[RegExp, number]> = [
    [/CCL|PCB|載板|ABF|散熱|液冷|封裝|先進封裝/, 82],
    [/光通訊|CPO|互連|連接器|導軌|機櫃|BMC|測試介面|探針卡/, 80],
    [/機器人|自動化|電機|電器電纜|重電|電網|變壓器/, 72],
    [/半導體|IC|晶片|電子零組件|電腦及週邊|通信網路|其他電子|資訊服務|數位雲端/, 68],
    [/金融|金控|銀行|保險|證券/, 64],
    [/航運|航空|貨櫃|航太|國防/, 62],
    [/油電|塑膠|化學|鋼鐵|水泥|原物料/, 58],
    [/食品|貿易百貨|觀光|居家|運動休閒|內需/, 56],
    [/生技|醫療|汽車|建材營造/, 46],
  ];
  const brokerScore = getBrokerResearchScore(instrument.symbol);
  const ruleScore = rules.find(([pattern]) => pattern.test(text))?.[1] ?? 54;
  return brokerScore ? Math.max(ruleScore, brokerScore) : ruleScore;
}

function replaceScoreFactor(factors: FactorScore[], category: string, score: number, weight: number, direction = "positive"): FactorScore[] {
  const factorNameByCategory: Record<string, string> = {
    fundamental: "FundamentalScore",
    chip: "ChipScore",
    technical: "TechnicalScore",
    "us-linkage": "USMarketScore",
    news: "NewsScore",
    target_price: "TargetPriceScore",
  };
  const next = factor(factorNameByCategory[category] ?? category, category, score, weight, direction);
  const found = factors.some((item) => item.category === category);
  if (!found) return [...factors, next];
  return factors.map((item) => (item.category === category ? next : item));
}

function applyDynamicQuoteScores(
  signalPayload: PredictionSignal,
  quote: TwseQuote | null,
  valuation: TwseValuation | null,
  instrument: StockInstrument,
): PredictionSignal {
  const componentScores = signalPayload.explanation?.component_scores ?? {};
  const changePct = quoteChangePercent(quote);
  const rangePosition = quoteRangePositionScore(quote);
  const liquidityScore = quoteTradeValueScore(quote);
  const amplitudeRisk = quoteAmplitudeRisk(quote);
  const topicScore = topicFitScore(instrument);
  const valuationScore = valuationQualityScore(valuation);
  const momentumScore = clamp(50 + changePct * 520 + (rangePosition - 50) * 0.22, 18, 92);
  const technicalScore = Math.round(clamp((componentScores.TechnicalScore ?? 55) * 0.34 + momentumScore * 0.42 + rangePosition * 0.14 + liquidityScore * 0.1, 20, 92));
  const chipScore = Math.round(clamp((componentScores.ChipScore ?? 55) * 0.42 + liquidityScore * 0.34 + Math.max(0, momentumScore - 45) * 0.24, 18, 90));
  const fundamentalScore = Math.round(clamp((componentScores.FundamentalScore ?? 55) * 0.56 + topicScore * 0.22 + valuationScore * 0.22, 20, 88));
  const usMarketScore = Math.round(clamp((componentScores.USMarketScore ?? 52) * 0.5 + topicScore * 0.32 + Math.max(45, momentumScore) * 0.18, 22, 88));
  const newsScore = Math.round(clamp((componentScores.NewsScore ?? 50) * 0.7 + topicScore * 0.18 + momentumScore * 0.12, 25, 82));
  const bullishScore = Math.round(clamp(
    fundamentalScore * 0.2
    + chipScore * 0.22
    + technicalScore * 0.23
    + usMarketScore * 0.13
    + newsScore * 0.07
    + valuationScore * 0.05
    + liquidityScore * 0.1,
    20,
    90,
  ));
  const totalRisk = clamp(
    signalPayload.risk_score.total
    + Math.max(0, amplitudeRisk - 45) / 260
    - Math.max(0, liquidityScore - 55) / 420
    + (changePct < -0.03 ? 0.08 : 0),
    0.12,
    0.9,
  );
  const riskAdjustedScore = Math.round(clamp(bullishScore - totalRisk * 35, 20, 86));
  const probabilityBase = clamp(0.46 + riskAdjustedScore / 260 + Math.max(-0.05, Math.min(0.06, changePct)) * 0.55, 0.42, 0.76);
  let factors = signalPayload.factor_scores;
  factors = replaceScoreFactor(factors, "fundamental", fundamentalScore, 0.2, fundamentalScore >= 58 ? "positive" : "neutral");
  factors = replaceScoreFactor(factors, "chip", chipScore, 0.22, chipScore >= 58 ? "positive" : chipScore <= 42 ? "negative" : "neutral");
  factors = replaceScoreFactor(factors, "technical", technicalScore, 0.23, technicalScore >= 58 ? "positive" : technicalScore <= 42 ? "negative" : "neutral");
  factors = replaceScoreFactor(factors, "us-linkage", usMarketScore, 0.13, usMarketScore >= 58 ? "positive" : "neutral");
  factors = replaceScoreFactor(factors, "news", newsScore, 0.07, newsScore >= 58 ? "positive" : "neutral");
  factors = replaceScoreFactor(factors, "target_price", valuationScore, 0.05, valuationScore >= 62 ? "positive" : valuationScore <= 45 ? "negative" : "neutral");

  return {
    ...signalPayload,
    name: quote?.name || instrument.name,
    sector: instrument.sector,
    signal_date: quote?.date ?? signalPayload.signal_date,
    quote,
    valuation,
    probability_up: probabilityBase,
    probability_up_1d: clamp(probabilityBase + (technicalScore - 60) / 600, 0.4, 0.78),
    probability_up_5d: clamp(probabilityBase + (chipScore - 60) / 650, 0.4, 0.78),
    probability_up_20d: clamp(probabilityBase + (fundamentalScore - 60) / 700, 0.38, 0.76),
    confidence: clamp(0.54 + liquidityScore / 360 + (quote ? 0.06 : 0), 0.52, 0.86),
    composite_score: bullishScore / 100,
    bullish_score: bullishScore,
    risk_adjusted_score: riskAdjustedScore,
    factor_scores: factors,
    positive_drivers: factors.filter((item) => item.direction === "positive").slice(0, 3),
    negative_drivers: factors.filter((item) => item.direction === "negative").slice(0, 3),
    risk_score: {
      ...signalPayload.risk_score,
      total: totalRisk,
      volatility: clamp(amplitudeRisk / 100, 0.12, 0.9),
      liquidity: clamp(1 - liquidityScore / 100, 0.05, 0.85),
      explanation: "Risk now includes latest official quote amplitude and liquidity from TWSE/TPEx daily quote feeds.",
    },
    technicals: {
      ...signalPayload.technicals,
      ma_5: quote?.close ? Number((quote.close * (1 - changePct * 0.35)).toFixed(2)) : signalPayload.technicals.ma_5,
      ma_20: quote?.close ? Number((quote.close * (1 - changePct * 0.75)).toFixed(2)) : signalPayload.technicals.ma_20,
      rsi_14: Math.round(clamp(48 + changePct * 520 + (rangePosition - 50) * 0.2, 20, 82)),
    },
    explanation: {
      ...signalPayload.explanation,
      top_positive_factors: [
        `最新${quote?.source ?? "官方"}報價納入：${quote?.date ?? "日期待確認"}`,
        `成交值流動性分數 ${Math.round(liquidityScore)}`,
        `產業/題材相對分數 ${Math.round(topicScore)}`,
        ...(signalPayload.explanation?.top_positive_factors ?? []),
      ].slice(0, 5),
      component_scores: {
        ...(signalPayload.explanation?.component_scores ?? {}),
        FundamentalScore: fundamentalScore,
        ChipScore: chipScore,
        TechnicalScore: technicalScore,
        USMarketScore: usMarketScore,
        NewsScore: newsScore,
        TargetPriceScore: valuationScore,
      },
    },
  };
}

function dynamicRecommendationScore(signalPayload: PredictionSignal): number {
  const scores = signalPayload.explanation?.component_scores ?? {};
  const riskScore = (signalPayload.risk_score.total ?? 0.5) * 100;
  const liquidityScore = quoteTradeValueScore(signalPayload.quote);
  const brokerCoverageScore = getBrokerResearchScore(signalPayload.symbol) ?? 0;
  return clamp(
    (scores.TechnicalScore ?? 50) * 0.22
    + (scores.ChipScore ?? 50) * 0.22
    + (scores.FundamentalScore ?? 50) * 0.15
    + (scores.USMarketScore ?? 50) * 0.11
    + (scores.NewsScore ?? 50) * 0.06
    + (scores.TargetPriceScore ?? 50) * 0.04
    + liquidityScore * 0.12
    + quoteRangePositionScore(signalPayload.quote) * 0.08
    + Math.max(0, brokerCoverageScore - 62) * 0.16
    - Math.max(0, riskScore - 45) * 0.18,
    0,
    100,
  );
}

async function getTwseQuoteMap(): Promise<Map<string, TwseQuote>> {
  const cacheAgeMs = Date.now() - twseQuoteCacheLoadedAt;
  if (twseQuoteCache && cacheAgeMs < 10 * 60 * 1000) return twseQuoteCache;
  if (twseQuoteCachePromise) return twseQuoteCachePromise;
  twseQuoteCachePromise = loadTwseQuoteMap();
  return twseQuoteCachePromise;
}

async function loadTwseQuoteMap(): Promise<Map<string, TwseQuote>> {
  const map = new Map<string, TwseQuote>();
  try {
    const response = await fetchWithTimeout(twseDailyQuoteUrl, { cache: "no-store", timeoutMs: 6000 });
    if (response.ok) {
      const rows = (await response.json()) as Array<Record<string, string>>;
      rows.forEach((row) => {
        const symbol = String(row.Code ?? "").trim();
        if (!/^\d{4}$/.test(symbol)) return;
        map.set(symbol, {
          source: "TWSE OpenAPI",
          endpoint: twseDailyQuoteUrl,
          date: parseTwseDate(row.Date),
          symbol,
          name: String(row.Name ?? symbol).trim(),
          open: parseTwseNumber(row.OpeningPrice),
          high: parseTwseNumber(row.HighestPrice),
          low: parseTwseNumber(row.LowestPrice),
          close: parseTwseNumber(row.ClosingPrice),
          change: parseTwseNumber(row.Change),
          trade_volume: parseTwseNumber(row.TradeVolume),
          trade_value: parseTwseNumber(row.TradeValue),
          transaction_count: parseTwseNumber(row.Transaction),
        });
      });
    }
  } catch {
    // Keep the frontend resilient when TWSE is temporarily unavailable.
  }
  twseQuoteCache = map;
  twseQuoteCacheLoadedAt = Date.now();
  twseQuoteCachePromise = null;
  return map;
}

async function getLatestTwseStockDayQuote(symbol: string, fallbackName?: string): Promise<TwseQuote | null> {
  if (!/^\d{4}$/.test(symbol)) return null;
  const endpoint = `${twseStockDayUrl}?date=${taipeiDateKey()}&stockNo=${symbol}&response=json`;
  try {
    const response = await fetchWithTimeout(endpoint, { cache: "no-store", timeoutMs: 6000 });
    if (!response.ok) return null;
    const payload = (await response.json()) as {
      stat?: string;
      title?: string;
      data?: string[][];
    };
    if (payload.stat !== "OK" || !Array.isArray(payload.data) || payload.data.length === 0) return null;
    const latestRow = [...payload.data].reverse().find((row) => parseTwseNumber(row[6]) !== null);
    if (!latestRow) return null;
    const titleName = / \d{4}\s+(.+?)\s+各日成交資訊/.exec(payload.title ?? "")?.[1]?.trim();
    return {
      source: "TWSE Official STOCK_DAY",
      endpoint,
      date: parseTwseSlashDate(latestRow[0]),
      symbol,
      name: titleName || fallbackName || symbol,
      open: parseTwseNumber(latestRow[3]),
      high: parseTwseNumber(latestRow[4]),
      low: parseTwseNumber(latestRow[5]),
      close: parseTwseNumber(latestRow[6]),
      change: parseTwseNumber(latestRow[7]),
      trade_volume: parseTwseNumber(latestRow[1]),
      trade_value: parseTwseNumber(latestRow[2]),
      transaction_count: parseTwseNumber(latestRow[8]),
    };
  } catch {
    return null;
  }
}

async function getLatestOfficialQuoteDate(): Promise<string> {
  const [twseQuoteMap, tpexQuoteMap] = await Promise.all([
    getTwseQuoteMap(),
    getTpexQuoteMap(),
  ]);
  const dates = [
    ...Array.from(twseQuoteMap.values()).map((quote) => quote.date),
    ...Array.from(tpexQuoteMap.values()).map((quote) => quote.date),
  ].filter((date) => date && date !== "資料日期待確認");
  if (taipeiMarketRefreshWindowStarted()) {
    const latestBellwetherQuote = await getLatestTwseStockDayQuote("2330", "台積電");
    if (latestBellwetherQuote?.date && latestBellwetherQuote.date !== "資料日期待確認") {
      dates.push(latestBellwetherQuote.date);
    }
  }
  return dates.sort().at(-1) ?? "資料日期待確認";
}

async function getTwseValuationMap(): Promise<Map<string, TwseValuation>> {
  if (twseValuationCache) return twseValuationCache;
  if (twseValuationCachePromise) return twseValuationCachePromise;
  twseValuationCachePromise = loadTwseValuationMap();
  return twseValuationCachePromise;
}

async function loadTwseValuationMap(): Promise<Map<string, TwseValuation>> {
  const map = new Map<string, TwseValuation>();
  try {
    const response = await fetchWithTimeout(twseValuationUrl, { next: { revalidate: 60 * 30 }, timeoutMs: 6000 });
    if (response.ok) {
      const rows = (await response.json()) as Array<Record<string, string>>;
      rows.forEach((row) => {
        const symbol = String(row.Code ?? "").trim();
        if (!/^\d{4}$/.test(symbol)) return;
        map.set(symbol, {
          source: "TWSE OpenAPI",
          endpoint: twseValuationUrl,
          date: parseTwseDate(row.Date),
          symbol,
          name: String(row.Name ?? symbol).trim(),
          pe_ratio: parseTwseNumber(row.PEratio),
          dividend_yield: parseTwseNumber(row.DividendYield),
          pb_ratio: parseTwseNumber(row.PBratio),
        });
      });
    }
  } catch {
    // Keep the frontend resilient when TWSE is temporarily unavailable.
  }
  twseValuationCache = map;
  return map;
}

async function getTpexQuoteMap(): Promise<Map<string, TwseQuote>> {
  const cacheAgeMs = Date.now() - tpexQuoteCacheLoadedAt;
  if (tpexQuoteCache && cacheAgeMs < 10 * 60 * 1000 && !quoteMapBehindToday(tpexQuoteCache)) return tpexQuoteCache;
  if (tpexQuoteCachePromise) return tpexQuoteCachePromise;
  tpexQuoteCachePromise = loadTpexQuoteMap();
  return tpexQuoteCachePromise;
}

async function loadTpexQuoteMap(): Promise<Map<string, TwseQuote>> {
  const map = new Map<string, TwseQuote>();
  try {
    const response = await fetchWithTimeout(tpexQuoteUrl, { cache: "no-store", timeoutMs: 6000 });
    if (response.ok) {
      const rows = (await response.json()) as Array<Record<string, string>>;
      rows.forEach((row) => {
        const symbol = String(row.SecuritiesCompanyCode ?? "").trim();
        if (!/^\d{4}$/.test(symbol)) return;
        map.set(symbol, {
          source: "TPEx OpenAPI",
          endpoint: tpexQuoteUrl,
          date: parseTwseDate(row.Date),
          symbol,
          name: String(row.CompanyName ?? symbol).trim(),
          open: parseTwseNumber(row.Open),
          high: parseTwseNumber(row.High),
          low: parseTwseNumber(row.Low),
          close: parseTwseNumber(row.Close),
          change: parseTwseNumber(row.Change),
          trade_volume: parseTwseNumber(row.TradingShares),
          trade_value: parseTwseNumber(row.TransactionAmount),
          transaction_count: parseTwseNumber(row.TransactionNumber),
        });
      });
    }
  } catch {
    // Keep the frontend resilient when TPEx is temporarily unavailable.
  }
  tpexQuoteCache = map;
  tpexQuoteCacheLoadedAt = Date.now();
  tpexQuoteCachePromise = null;
  return map;
}

async function getTpexValuationMap(): Promise<Map<string, TwseValuation>> {
  if (tpexValuationCache) return tpexValuationCache;
  if (tpexValuationCachePromise) return tpexValuationCachePromise;
  tpexValuationCachePromise = loadTpexValuationMap();
  return tpexValuationCachePromise;
}

async function loadTpexValuationMap(): Promise<Map<string, TwseValuation>> {
  const map = new Map<string, TwseValuation>();
  try {
    const response = await fetchWithTimeout(tpexValuationUrl, { cache: "no-store", timeoutMs: 6000 });
    if (response.ok) {
      const rows = (await response.json()) as Array<Record<string, string>>;
      rows.forEach((row) => {
        const symbol = String(row.SecuritiesCompanyCode ?? "").trim();
        if (!/^\d{4}$/.test(symbol)) return;
        map.set(symbol, {
          source: "TPEx OpenAPI",
          endpoint: tpexValuationUrl,
          date: parseTwseDate(row.Date),
          symbol,
          name: String(row.CompanyName ?? symbol).trim(),
          pe_ratio: parseTwseNumber(row.PriceEarningRatio),
          dividend_yield: parseTwseNumber(row.YieldRatio),
          pb_ratio: parseTwseNumber(row.PriceBookRatio),
          dividend_per_share: parseTwseNumber(row.DividendPerShare),
        });
      });
    }
  } catch {
    // Keep the frontend resilient when TPEx is temporarily unavailable.
  }
  tpexValuationCache = map;
  return map;
}

async function getOfficialNewsPool(): Promise<NewsItem[]> {
  const cacheAgeMs = Date.now() - officialNewsCacheLoadedAt;
  if (officialNewsCache && cacheAgeMs < 60 * 1000) return officialNewsCache;
  if (officialNewsCachePromise) return officialNewsCachePromise;
  officialNewsCachePromise = loadOfficialNewsPool();
  return officialNewsCachePromise;
}

async function loadOfficialNewsPool(): Promise<NewsItem[]> {
  const events: NewsItem[] = [];
  const settled = await Promise.allSettled([
    fetchWithTimeout(twseMaterialNewsUrl, { next: { revalidate: 60 }, timeoutMs: 6000 }),
    fetchWithTimeout(twseExchangeNewsUrl, { next: { revalidate: 60 }, timeoutMs: 6000 }),
    fetchWithTimeout(twseExchangeEventsUrl, { next: { revalidate: 60 }, timeoutMs: 6000 }),
    fetchWithTimeout(cnaFinanceRssUrl, { next: { revalidate: 60 }, timeoutMs: 6000 }),
    fetchWithTimeout(cnaTechnologyRssUrl, { next: { revalidate: 60 }, timeoutMs: 6000 }),
  ]);

  const [material, exchangeNews, exchangeEvents, cnaFinance, cnaTechnology] = settled;
  if (material.status === "fulfilled" && material.value.ok) {
    const rows = (await material.value.json()) as Array<Record<string, string>>;
    events.push(...rows.map(normalizeMaterialNews).filter((item): item is NewsItem => item !== null));
  }
  if (exchangeNews.status === "fulfilled" && exchangeNews.value.ok) {
    const rows = (await exchangeNews.value.json()) as Array<Record<string, string>>;
    events.push(...rows.map(normalizeTwseExchangeNews).filter((item): item is NewsItem => item !== null));
  }
  if (exchangeEvents.status === "fulfilled" && exchangeEvents.value.ok) {
    const rows = (await exchangeEvents.value.json()) as Array<Record<string, string>>;
    events.push(...rows.map(normalizeTwseExchangeEvent).filter((item): item is NewsItem => item !== null));
  }
  if (cnaFinance.status === "fulfilled" && cnaFinance.value.ok) {
    events.push(...parseRssNews(await cnaFinance.value.text(), "CNA 財經 RSS", cnaFinanceRssUrl));
  }
  if (cnaTechnology.status === "fulfilled" && cnaTechnology.value.ok) {
    events.push(...parseRssNews(await cnaTechnology.value.text(), "CNA 科技 RSS", cnaTechnologyRssUrl));
  }

  officialNewsCache = dedupeNews(events).sort((a, b) => Date.parse(b.published_at) - Date.parse(a.published_at)).slice(0, 260);
  officialNewsCacheLoadedAt = Date.now();
  officialNewsCachePromise = null;
  return officialNewsCache;
}

function normalizeMaterialNews(row: Record<string, string>): NewsItem | null {
  const symbol = String(row["公司代號"] ?? "").trim();
  const companyName = String(row["公司名稱"] ?? "").trim();
  const title = String(row["主旨 "] ?? row["主旨"] ?? "").trim();
  const summary = String(row["說明"] ?? "").trim();
  if (!/^\d{4}$/.test(symbol) || !title) return null;
  const publishedAt = buildTwseDateTime(row["發言日期"], row["發言時間"]);
  const sentiment = classifyNewsSentiment(`${title}\n${summary}`);
  return {
    title: `${companyName}：${title}`,
    source: "TWSE/MOPS 重大訊息",
    source_url: twseMaterialNewsUrl,
    published_at: publishedAt,
    sentiment: sentiment.label,
    impact_score: sentiment.impact,
    related_symbols: [symbol],
    stock_id: symbol,
    summary: summary || title,
    event_type: inferEventType(`${title}\n${summary}`),
    linkage_reason: "公司代號直接命中公開資訊觀測站重大訊息",
  };
}

function normalizeTwseExchangeNews(row: Record<string, string>): NewsItem | null {
  const title = String(row.Title ?? "").trim();
  if (!title) return null;
  const sentiment = classifyNewsSentiment(title);
  return {
    title,
    source: "TWSE 證交所新聞",
    source_url: twseExchangeNewsUrl,
    published_at: parseTwseDate(row.Date),
    sentiment: sentiment.label,
    impact_score: sentiment.impact,
    related_symbols: [],
    summary: title,
    url: String(row.Url ?? "").trim(),
    event_type: inferEventType(title),
    linkage_reason: "交易所市場新聞，作為市場背景事件",
  };
}

function normalizeTwseExchangeEvent(row: Record<string, string>): NewsItem | null {
  const title = String(row.Title ?? "").trim();
  if (!title) return null;
  return {
    title,
    source: "TWSE 活動訊息",
    source_url: twseExchangeEventsUrl,
    published_at: new Date().toISOString(),
    sentiment: "neutral",
    impact_score: 0.02,
    related_symbols: [],
    summary: title,
    url: String(row.Details ?? "").trim(),
    event_type: "market_event",
    linkage_reason: "交易所活動與法人說明會資訊，作為事件行事曆",
  };
}

function parseRssNews(xml: string, source: string, sourceUrl: string): NewsItem[] {
  const items = xml.match(/<item>[\s\S]*?<\/item>/g) ?? [];
  const parsed: Array<NewsItem | null> = items.map((item) => {
      const title = decodeXml(readRssTag(item, "title"));
      const description = decodeXml(readRssTag(item, "description"));
      const summary = stripTags(description);
      if (!title) return null;
      const sentiment = classifyNewsSentiment(`${title}\n${summary}`);
      return {
        title,
        source,
        source_url: sourceUrl,
        published_at: parseRssDate(readRssTag(item, "pubDate")),
        sentiment: sentiment.label,
        impact_score: sentiment.impact,
        related_symbols: inferRelatedSymbols(`${title}\n${summary}`),
        summary: summary || title,
        url: decodeXml(readRssTag(item, "link")),
        image_url: extractRssImageUrl(item, description),
        event_type: inferEventType(`${title}\n${summary}`),
        linkage_reason: "CNA 財經/科技新聞依公司名稱、產業與供應鏈關鍵字連動",
      } satisfies NewsItem;
    });
  return parsed.filter((item): item is NewsItem => item !== null);
}

function readRssTag(item: string, tag: string): string {
  const match = item.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`, "i"));
  return match?.[1]?.replace("<![CDATA[", "").replace("]]>", "").trim() ?? "";
}

function readRssAttribute(item: string, tag: string, attribute: string): string {
  const match = item.match(new RegExp(`<${tag}[^>]*\\s${attribute}=["']([^"']+)["'][^>]*\\/?>`, "i"));
  return match?.[1]?.trim() ?? "";
}

function extractRssImageUrl(item: string, description: string): string | undefined {
  const candidates = [
    readRssAttribute(item, "media:content", "url"),
    readRssAttribute(item, "media:thumbnail", "url"),
    readRssAttribute(item, "enclosure", "url"),
    readRssAttribute(description, "img", "src"),
  ];
  return candidates.find((candidate) => /^https?:\/\//i.test(candidate));
}

function decodeXml(value: string): string {
  return value
    .replaceAll("&amp;", "&")
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">")
    .replaceAll("&quot;", "\"")
    .replaceAll("&#39;", "'");
}

function stripTags(value: string): string {
  return value.replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
}

function parseRssDate(value: string): string {
  const parsed = Date.parse(value);
  return Number.isFinite(parsed) ? new Date(parsed).toISOString() : new Date().toISOString();
}

function buildTwseDateTime(dateValue: string | undefined, timeValue: string | undefined): string {
  const date = parseTwseDate(dateValue);
  if (date === "資料日期待確認") return new Date().toISOString();
  const digits = String(timeValue ?? "").replace(/\D/g, "").padStart(6, "0").slice(-6);
  return `${date}T${digits.slice(0, 2)}:${digits.slice(2, 4)}:${digits.slice(4, 6)}+08:00`;
}

function classifyNewsSentiment(text: string): { label: string; impact: number } {
  const content = text.toLowerCase();
  const negative = ["違約", "裁罰", "駭客", "資安", "虧損", "下修", "衰退", "停工", "訴訟", "處分", "利空", "賣超", "重訊說明", "風險"];
  const positive = ["創高", "成長", "買超", "配息", "股利", "擴產", "得標", "強漲", "看好", "需求", "ai", "輝達", "法說會", "營收增加"];
  const negativeHits = negative.filter((word) => content.includes(word)).length;
  const positiveHits = positive.filter((word) => content.includes(word)).length;
  if (negativeHits > positiveHits) return { label: "cautious", impact: Math.max(-0.45, -0.12 - negativeHits * 0.07) };
  if (positiveHits > negativeHits) return { label: "positive", impact: Math.min(0.45, 0.1 + positiveHits * 0.05) };
  return { label: "neutral", impact: 0.03 };
}

function inferEventType(text: string): string {
  if (/營收|月營收|revenue/i.test(text)) return "revenue";
  if (/法說|法人說明會|guidance|展望/i.test(text)) return "guidance";
  if (/股利|配息|除息|除權/i.test(text)) return "dividend";
  if (/資安|駭客|裁罰|違約|訴訟|風險/i.test(text)) return "risk";
  if (/AI|輝達|晶片|半導體|COMPUTEX|供應鏈/i.test(text)) return "supply_chain";
  return "industry";
}

function inferRelatedSymbols(text: string): string[] {
  const mapping: Array<[string, string]> = [
    ["台積電", "2330"],
    ["聯電", "2303"],
    ["聯發科", "2454"],
    ["鴻海", "2317"],
    ["廣達", "2382"],
    ["緯創", "3231"],
    ["緯穎", "6669"],
    ["台達電", "2308"],
    ["智邦", "2345"],
    ["華碩", "2357"],
    ["南亞科", "2408"],
    ["智原", "3035"],
    ["聯詠", "3034"],
    ["世芯", "3661"],
    ["日月光", "3711"],
    ["頎邦", "6147"],
    ["萬潤", "6187"],
    ["旺矽", "6223"],
    ["環球晶", "6488"],
    ["元太", "8069"],
    ["輝達", "NVDA"],
    ["NVIDIA", "NVDA"],
    ["超微", "AMD"],
    ["AMD", "AMD"],
    ["蘋果", "AAPL"],
    ["Apple", "AAPL"],
    ["博通", "AVGO"],
    ["Broadcom", "AVGO"],
    ["美光", "MU"],
    ["Micron", "MU"],
  ];
  return Array.from(new Set(mapping.filter(([keyword]) => text.includes(keyword)).map(([, symbol]) => symbol)));
}

function deriveNewsKeywords(instrument: StockInstrument): string[] {
  const keywords = [instrument.symbol, instrument.name, instrument.sector ?? ""].filter(Boolean);
  const sector = instrument.sector ?? "";
  if (/半導體|電子|電腦|週邊|通信|零組件|光電/.test(sector)) keywords.push("AI", "輝達", "晶片", "半導體", "COMPUTEX", "供應鏈", "伺服器", "台積電");
  if (/金融/.test(sector)) keywords.push("金融", "金控", "利率", "外資", "殖利率");
  if (/航運/.test(sector)) keywords.push("航運", "運價", "貨櫃");
  if (/水泥|塑膠|鋼鐵|油電|化學/.test(sector)) keywords.push("原物料", "能源", "景氣", "報價");
  return Array.from(new Set(keywords.filter(Boolean)));
}

function deriveRelatedStockSymbols(instrument: StockInstrument): string[] {
  const sector = instrument.sector ?? "";
  const base = [instrument.symbol];
  if (/半導體|晶片|IC|電子零組件/.test(sector)) {
    base.push("2330", "2303", "2454", "3034", "3035", "3661", "3711", "6147", "6223", "6488", "2408");
  }
  if (/電腦|週邊|電子代工|電源|通信|AI|伺服器/.test(sector)) {
    base.push("2317", "2324", "2356", "2376", "2377", "2382", "3231", "6669", "2308", "2345", "2357", "4938", "8210", "6187");
  }
  if (/散熱|液冷|水冷|導軌|機櫃/.test(sector)) base.push("2059", "3017", "3324", "3653", "8210", "2308");
  if (/光通訊|CPO|互連|連接器/.test(sector)) base.push("2455", "3081", "3665", "3710", "4971", "4991", "6197", "6442");
  if (/PCB|CCL|載板|ABF/.test(sector)) base.push("2383", "3037", "3189", "6274", "8046");
  if (/金融/.test(sector)) base.push("2881", "2882", "2884", "2885", "2886", "2891", "5880");
  if (/航運/.test(sector)) base.push("2603", "2609", "2615");
  if (/光電/.test(sector)) base.push("3008", "8069", "2409");
  return Array.from(new Set(base.filter((symbol) => symbol !== instrument.symbol))).slice(0, 10);
}

async function getNewsForInstrument(instrument: StockInstrument): Promise<NewsItem[]> {
  const pool = await getOfficialNewsPool();
  const keywords = deriveNewsKeywords(instrument);
  const relatedStockSymbols = deriveRelatedStockSymbols(instrument);
  const direct = pool.filter((event) => event.stock_id === instrument.symbol || event.related_symbols.includes(instrument.symbol));
  const brokerResearch = getBrokerResearchEventsForInstrument(instrument);
  const contextual = pool.filter((event) => {
    if (direct.includes(event)) return false;
    const haystack = `${event.title}\n${event.summary ?? ""}`;
    return keywords.some((keyword) => keyword && haystack.includes(keyword));
  });
  const marketBackground = pool.filter((event) => event.source.startsWith("TWSE") || event.source.startsWith("CNA")).slice(0, 4);
  const selected = dedupeNews([...brokerResearch, ...direct, ...contextual, ...marketBackground]).slice(0, 10);
  return selected.map((event) => ({
    ...event,
    related_symbols: Array.from(new Set([
      ...event.related_symbols,
      instrument.symbol,
      ...(event.stock_id === instrument.symbol || contextual.includes(event) ? relatedStockSymbols.slice(0, 6) : []),
    ])),
  }));
}

function analystEstimateApiKey(): string | undefined {
  return process.env.FMP_API_KEY || process.env.FINANCIAL_MODELING_PREP_API_KEY;
}

function configuredCommercialAnalystProviders(): string[] {
  return [
    process.env.FACTSET_API_KEY ? "FactSet" : "",
    process.env.LSEG_API_KEY ? "LSEG I/B/E/S" : "",
    process.env.BLOOMBERG_API_KEY ? "Bloomberg" : "",
    analystEstimateApiKey() ? "FMP" : "",
  ].filter(Boolean);
}

function buildAnalystSymbolCandidates(instrument: StockInstrument): string[] {
  const suffix = instrument.market === "TPEX" ? ".TWO" : ".TW";
  return Array.from(new Set([
    instrument.symbol,
    `${instrument.symbol}${suffix}`,
    `${instrument.symbol}.TW`,
    `${instrument.symbol}.TWO`,
  ]));
}

async function getExternalAnalystTargetPrice(instrument: StockInstrument, news: NewsItem[]): Promise<AnalystTargetPrice> {
  const cacheKey = `${instrument.symbol}:${news.map((item) => item.title).join("|").slice(0, 240)}`;
  const cached = analystTargetCache.get(cacheKey);
  if (cached && Date.now() - cached.loadedAt < 60 * 1000) return cached.value;

  const supabaseTarget = await fetchLatestSupabaseAnalystTargetPrice(instrument);
  const brokerTarget = getBrokerAnalystTargetPrice(instrument);
  const extractedTarget = supabaseTarget ?? brokerTarget ?? extractAnalystTargetFromNews(instrument, news);
  const value = extractedTarget ?? buildPendingAnalystTarget(instrument);
  analystTargetCache.set(cacheKey, { loadedAt: Date.now(), value });
  return value;
}

async function fetchFmpTargetPriceConsensus(instrument: StockInstrument): Promise<AnalystTargetPrice | null> {
  const apiKey = analystEstimateApiKey();
  if (!apiKey) return null;
  for (const symbol of buildAnalystSymbolCandidates(instrument)) {
    const endpoint = `${fmpTargetPriceConsensusUrl}?symbol=${encodeURIComponent(symbol)}&apikey=${encodeURIComponent(apiKey)}`;
    try {
      const response = await fetchWithTimeout(endpoint, { next: { revalidate: 60 * 60 * 6 }, timeoutMs: 6000 });
      if (!response.ok) continue;
      const payload = await response.json();
      const row = Array.isArray(payload) ? payload[0] : payload;
      const normalized = normalizeFmpTargetPrice(instrument.symbol, row);
      if (normalized?.target_price_mean) return normalized;
    } catch {
      // Try the next symbol candidate; Taiwan tickers vary by provider suffix.
    }
  }
  return null;
}

function normalizeFmpTargetPrice(symbol: string, row: unknown): AnalystTargetPrice | null {
  if (!row || typeof row !== "object") return null;
  const item = row as Record<string, unknown>;
  const mean = parseProviderNumber(item.targetConsensus ?? item.targetPrice ?? item.target_price_mean);
  if (typeof mean !== "number") return null;
  return {
    symbol,
    currency: String(item.currency ?? "USD"),
    target_price_mean: mean,
    target_price_high: parseProviderNumber(item.targetHigh ?? item.target_price_high),
    target_price_low: parseProviderNumber(item.targetLow ?? item.target_price_low),
    analyst_count: parseProviderNumber(item.numberOfAnalystOpinions ?? item.analystCount ?? item.analyst_count),
    source: "FMP price target consensus",
    source_type: "licensed_or_keyed_api",
    source_url: analystProviderUrls.fmp,
    published_at: typeof item.date === "string" ? item.date : new Date().toISOString(),
    confidence: 0.72,
    provider_status: "configured",
    note: "外部 keyed API 回傳的法人/分析師目標價共識；正式商用仍需確認該 provider 的台股涵蓋率與 redisplay 權利。",
  };
}

type TargetPriceMention = {
  targetPrice: number;
  targetPriceLow?: number;
  targetPriceHigh?: number;
  broker?: string | null;
  rating?: string | null;
  confidence: number;
};

function extractAnalystTargetFromNews(instrument: StockInstrument, news: NewsItem[]): AnalystTargetPrice | null {
  const candidates = news.flatMap((event) => {
    const mentions = extractTargetPriceMentions(`${event.title}\n${event.summary ?? ""}`);
    return mentions.map((mention) => ({ mention, event }));
  });
  const best = candidates
    .filter(({ mention }) => typeof mention.targetPrice === "number")
    .sort((left, right) => {
      const confidenceDelta = right.mention.confidence - left.mention.confidence;
      if (Math.abs(confidenceDelta) > 0.001) return confidenceDelta;
      return Date.parse(right.event.published_at) - Date.parse(left.event.published_at);
    })[0];
  if (!best) return null;

  return {
    symbol: instrument.symbol,
    currency: "TWD",
    target_price_mean: best.mention.targetPrice,
    target_price_high: best.mention.targetPriceHigh ?? null,
    target_price_low: best.mention.targetPriceLow ?? null,
    analyst_count: null,
    broker: best.mention.broker ?? null,
    rating: best.mention.rating ?? null,
    source: best.mention.broker ? `${best.event.source} / ${best.mention.broker}` : best.event.source,
    source_type: "news_extracted",
    source_url: best.event.url || best.event.source_url,
    published_at: best.event.published_at,
    confidence: best.mention.confidence,
    provider_status: "extracted",
    note: "新聞文字明確提到的券商/法人目標價，非正式法人共識；應點開原文確認報告日期、評等與適用假設。",
  };
}

function extractTargetPriceMentions(text: string): TargetPriceMention[] {
  const brokerPattern = /(摩根士丹利|高盛|花旗|麥格理|里昂|大摩|小摩|美銀|瑞銀|野村|元大|富邦|國泰|群益|凱基|統一|永豐|玉山|中信|法人|投顧|券商)/i;
  const ratingPattern = /(買進|中立|加碼|減碼|優於大盤|劣於大盤|持有|Buy|Hold|Neutral|Overweight|Underweight)/i;
  const pricePattern = /(?:目標價|合理價|上看|喊到|調升至|調降至)\s*(?:新台幣|台幣|NT\$|\$)?\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:元)?/gi;
  const rangePattern = /(?:區間|目標區間)\s*(?:新台幣|台幣|NT\$|\$)?\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:至|-|~)\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:元)?/gi;
  const mentions: TargetPriceMention[] = [];
  let match: RegExpExecArray | null;

  while ((match = pricePattern.exec(text)) !== null) {
    const window = text.slice(Math.max(0, match.index - 32), Math.min(text.length, match.index + match[0].length + 32));
    const broker = brokerPattern.exec(window)?.[1] ?? null;
    const rating = ratingPattern.exec(window)?.[1] ?? null;
    const targetPrice = parseProviderNumber(match[1]);
    if (typeof targetPrice !== "number") continue;
    mentions.push({
      targetPrice,
      broker,
      rating,
      confidence: broker ? 0.58 : 0.42,
    });
  }

  while ((match = rangePattern.exec(text)) !== null) {
    const low = parseProviderNumber(match[1]);
    const high = parseProviderNumber(match[2]);
    if (typeof low !== "number" || typeof high !== "number") continue;
    mentions.push({
      targetPrice: Number(((low + high) / 2).toFixed(2)),
      targetPriceLow: Math.min(low, high),
      targetPriceHigh: Math.max(low, high),
      confidence: 0.5,
    });
  }

  return mentions;
}

function buildPendingAnalystTarget(instrument: StockInstrument): AnalystTargetPrice {
  const configured = configuredCommercialAnalystProviders();
  return {
    symbol: instrument.symbol,
    currency: "TWD",
    target_price_mean: null,
    target_price_high: null,
    target_price_low: null,
    analyst_count: null,
    source: configured.length > 0 ? configured.join(" / ") : "FactSet / LSEG I/B/E/S / Bloomberg / FMP",
    source_type: "needs_license",
    source_url: configured.includes("FactSet") ? analystProviderUrls.factset : analystProviderUrls.lseg,
    confidence: 0,
    provider_status: configured.length > 0 ? "configured" : "needs_key",
    note: configured.length > 0
      ? "外部法人資料授權變數已設定，但仍需要依合約欄位完成 provider mapping 後才顯示正式共識目標價。"
      : "尚未設定外部法人目標價授權。請提供 FactSet、LSEG I/B/E/S、Bloomberg 或 FMP 的 API key 與 redisplay 權限後啟用。",
  };
}

function parseProviderNumber(value: unknown): number | null {
  if (value === null || value === undefined) return null;
  const numeric = Number(String(value).replaceAll(",", "").replace("%", "").trim());
  return Number.isFinite(numeric) ? numeric : null;
}

function dedupeNews(events: NewsItem[]): NewsItem[] {
  const seen = new Set<string>();
  return events.filter((event) => {
    const key = `${event.url || event.title}-${event.source}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function applyNewsSignal(signalPayload: PredictionSignal, news: NewsItem[]): PredictionSignal {
  if (news.length === 0) return signalPayload;
  const averageImpact = news.reduce((sum, event) => sum + event.impact_score, 0) / news.length;
  const negativeCount = news.filter((event) => event.impact_score < -0.05).length;
  const positiveCount = news.filter((event) => event.impact_score > 0.08).length;
  const newsScore = Math.round(clamp(50 + averageImpact * 85 + positiveCount * 2 - negativeCount * 4, 20, 85));
  const oldNewsScore = signalPayload.explanation?.component_scores?.NewsScore ?? 50;
  const bullishScore = Math.round(clamp((signalPayload.bullish_score ?? 55) + (newsScore - oldNewsScore) * 0.12, 20, 90));
  const eventRisk = clamp(signalPayload.risk_score.event + Math.max(0, -averageImpact) * 0.45 + negativeCount * 0.03, 0.05, 0.95);
  const riskAdjustedScore = Math.round(clamp(bullishScore - signalPayload.risk_score.total * 35 - Math.max(0, negativeCount - positiveCount) * 2, 20, 85));
  const updatedNewsFactor = factor("NewsScore", "news", newsScore, 0.12, newsScore >= 58 ? "positive" : newsScore <= 42 ? "negative" : "neutral");
  const factorScores = signalPayload.factor_scores.map((item) => (item.category === "news" ? updatedNewsFactor : item));
  const topPositive = news.filter((event) => event.impact_score > 0.08).map((event) => `新聞正向：${event.title}`).slice(0, 2);
  const topRisk = news.filter((event) => event.impact_score < -0.05).map((event) => `新聞風險：${event.title}`).slice(0, 2);

  return {
    ...signalPayload,
    news,
    composite_score: bullishScore / 100,
    bullish_score: bullishScore,
    risk_adjusted_score: riskAdjustedScore,
    factor_scores: factorScores,
    positive_drivers: factorScores.filter((item) => item.direction === "positive").slice(0, 3),
    risk_score: {
      ...signalPayload.risk_score,
      event: eventRisk,
      explanation: "Event risk now incorporates official TWSE/MOPS material information, TWSE news, and CNA finance/technology RSS context.",
    },
    explanation: {
      ...signalPayload.explanation,
      top_positive_factors: [...topPositive, ...(signalPayload.explanation?.top_positive_factors ?? [])].slice(0, 4),
      top_risk_factors: [...topRisk, ...(signalPayload.explanation?.top_risk_factors ?? [])].slice(0, 4),
      component_scores: {
        ...(signalPayload.explanation?.component_scores ?? {}),
        NewsScore: newsScore,
      },
    },
  };
}

function addRiskFlag(map: Map<string, ApiRiskFlag[]>, symbol: string, flag: ApiRiskFlag): void {
  if (!/^\d{4}$/.test(symbol)) return;
  const current = map.get(symbol) ?? [];
  current.push(flag);
  map.set(symbol, current);
}

async function getApiRiskFlagMap(): Promise<Map<string, ApiRiskFlag[]>> {
  if (apiRiskFlagCache) return apiRiskFlagCache;
  if (apiRiskFlagCachePromise) return apiRiskFlagCachePromise;
  apiRiskFlagCachePromise = loadApiRiskFlagMap();
  return apiRiskFlagCachePromise;
}

async function loadApiRiskFlagMap(): Promise<Map<string, ApiRiskFlag[]>> {
  const map = new Map<string, ApiRiskFlag[]>();
  const settled = await Promise.allSettled([
    fetchWithTimeout(twseAttentionUrl, { next: { revalidate: 60 * 30 }, timeoutMs: 6000 }),
    fetchWithTimeout(twseDispositionUrl, { next: { revalidate: 60 * 30 }, timeoutMs: 6000 }),
    fetchWithTimeout(twseMarginUrl, { next: { revalidate: 60 * 30 }, timeoutMs: 6000 }),
    fetchWithTimeout(twseForeignHoldingUrl, { next: { revalidate: 60 * 60 }, timeoutMs: 6000 }),
    fetchWithTimeout(tdccOwnershipDistributionUrl, { cache: "no-store", timeoutMs: 3500 }),
  ]);

  const [attention, disposition, margin, foreignHolding, tdccOwnership] = settled;
  if (attention.status === "fulfilled" && attention.value.ok) {
    const rows = (await attention.value.json()) as Array<Record<string, string>>;
    rows.forEach((row) => {
      const symbol = String(row.Code ?? "").trim();
      const count = parseTwseNumber(row.NumberOfAnnouncement);
      if (!/^\d{4}$/.test(symbol) || !count) return;
      addRiskFlag(map, symbol, {
        source: "TWSE 注意股票",
        endpoint: twseAttentionUrl,
        title: "交易所注意股票公告",
        detail: `${row.Name ?? symbol} 近期有 ${count} 筆注意公告，需閱讀交易所原始原因。`,
        severity: 0.55,
        related_symbols: [symbol],
        url: twseAttentionUrl,
      });
    });
  }
  if (disposition.status === "fulfilled" && disposition.value.ok) {
    const rows = (await disposition.value.json()) as Array<Record<string, string>>;
    rows.forEach((row) => {
      const symbol = String(row.Code ?? "").trim();
      if (!/^\d{4}$/.test(symbol)) return;
      addRiskFlag(map, symbol, {
        source: "TWSE 處置股票",
        endpoint: twseDispositionUrl,
        title: "交易所處置公告",
        detail: `${row.Name ?? symbol}：${row.ReasonsOfDisposition ?? "處置原因請以交易所公告為準"}；期間 ${row.DispositionPeriod ?? "待確認"}`,
        severity: 0.85,
        related_symbols: [symbol],
        url: twseDispositionUrl,
      });
    });
  }
  if (margin.status === "fulfilled" && margin.value.ok) {
    const rows = (await margin.value.json()) as Array<Record<string, string>>;
    rows.forEach((row) => {
      const symbol = String(row["股票代號"] ?? "").trim();
      if (!/^\d{4}$/.test(symbol)) return;
      const marginYesterday = parseTwseNumber(row["融資前日餘額"]) ?? 0;
      const marginToday = parseTwseNumber(row["融資今日餘額"]) ?? 0;
      const shortYesterday = parseTwseNumber(row["融券前日餘額"]) ?? 0;
      const shortToday = parseTwseNumber(row["融券今日餘額"]) ?? 0;
      const marginDelta = marginToday - marginYesterday;
      const shortDelta = shortToday - shortYesterday;
      if (Math.abs(marginDelta) < 1200 && Math.abs(shortDelta) < 300) return;
      addRiskFlag(map, symbol, {
        source: "TWSE 融資融券",
        endpoint: twseMarginUrl,
        title: "融資融券餘額異動",
        detail: `${row["股票名稱"] ?? symbol} 融資變動 ${marginDelta.toLocaleString()}、融券變動 ${shortDelta.toLocaleString()}，作為槓桿/軋空風險 reference。`,
        severity: shortDelta > 0 || marginDelta > 0 ? 0.35 : 0.18,
        related_symbols: [symbol],
        url: twseMarginUrl,
      });
    });
  }
  if (foreignHolding.status === "fulfilled" && foreignHolding.value.ok) {
    const rows = (await foreignHolding.value.json()) as Array<Record<string, string>>;
    rows.forEach((row) => {
      const symbol = String(row.Code ?? "").trim();
      if (!/^\d{4}$/.test(symbol)) return;
      addRiskFlag(map, symbol, {
        source: "TWSE 外資持股",
        endpoint: twseForeignHoldingUrl,
        title: "外資持股比例參考",
        detail: `${row.Name ?? symbol} 外資持股比 ${row.SharesHeldPer ?? "待確認"}%，排名 ${row.Rank ?? "待確認"}。`,
        severity: 0.08,
        related_symbols: [symbol],
        url: twseForeignHoldingUrl,
      });
    });
  }
  if (tdccOwnership.status === "fulfilled" && tdccOwnership.value.ok) {
    parseTdccOwnership(await tdccOwnership.value.text()).forEach((flag) => addRiskFlag(map, flag.related_symbols[0], flag));
  }

  apiRiskFlagCache = map;
  return map;
}

function parseTdccOwnership(csv: string): ApiRiskFlag[] {
  const [headerLine, ...lines] = csv.replace(/^\uFEFF/, "").split(/\r?\n/).filter(Boolean);
  const headers = splitCsvLine(headerLine);
  const symbolIndex = headers.indexOf("證券代號");
  const bucketIndex = headers.indexOf("持股分級");
  const peopleIndex = headers.indexOf("人數");
  const shareIndex = headers.indexOf("股數");
  const ratioIndex = headers.indexOf("占集保庫存數比例%");
  if (symbolIndex < 0 || bucketIndex < 0 || ratioIndex < 0) return [];
  const bySymbol = new Map<string, { ratio: number; people: number; shares: number }>();
  lines.forEach((line) => {
    const cells = splitCsvLine(line);
    const symbol = String(cells[symbolIndex] ?? "").trim();
    const bucket = Number(cells[bucketIndex]);
    if (!/^\d{4}$/.test(symbol) || bucket < 15) return;
    const current = bySymbol.get(symbol) ?? { ratio: 0, people: 0, shares: 0 };
    current.ratio += parseTwseNumber(cells[ratioIndex]) ?? 0;
    current.people += parseTwseNumber(cells[peopleIndex]) ?? 0;
    current.shares += parseTwseNumber(cells[shareIndex]) ?? 0;
    bySymbol.set(symbol, current);
  });
  return Array.from(bySymbol.entries())
    .filter(([, value]) => value.ratio >= 35)
    .slice(0, 500)
    .map(([symbol, value]) => ({
      source: "TDCC 集保股權分散",
      endpoint: tdccOwnershipDistributionUrl,
      title: "大額持股集中度參考",
      detail: `持股分級 15 以上合計約 ${value.ratio.toFixed(2)}%，人數 ${value.people.toLocaleString()}；此為股權集中度 reference。`,
      severity: value.ratio >= 65 ? 0.32 : 0.18,
      related_symbols: [symbol],
      url: tdccOwnershipDistributionUrl,
    }));
}

function splitCsvLine(line: string): string[] {
  const values: string[] = [];
  let current = "";
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === "\"") {
      if (quoted && line[index + 1] === "\"") {
        current += "\"";
        index += 1;
      } else {
        quoted = !quoted;
      }
    } else if (char === "," && !quoted) {
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }
  values.push(current);
  return values.map((value) => value.trim());
}

function applyApiRiskFlags(signalPayload: PredictionSignal, riskFlags: ApiRiskFlag[]): PredictionSignal {
  if (riskFlags.length === 0) return { ...signalPayload, risk_flags: [] };
  const severeFlags = riskFlags.filter((flag) => flag.severity >= 0.5);
  const averageSeverity = riskFlags.reduce((sum, flag) => sum + flag.severity, 0) / riskFlags.length;
  const eventRisk = clamp(signalPayload.risk_score.event + averageSeverity * 0.18 + severeFlags.length * 0.08, 0.05, 0.95);
  const totalRisk = clamp(signalPayload.risk_score.total + averageSeverity * 0.08 + severeFlags.length * 0.04, 0.1, 0.95);
  const bullishScore = signalPayload.bullish_score ?? Math.round(signalPayload.composite_score * 100);
  const riskAdjustedScore = Math.round(clamp(bullishScore - totalRisk * 35, 20, 85));
  const topRisk = riskFlags.map((flag) => `${flag.source}：${flag.title}`).slice(0, 3);

  return {
    ...signalPayload,
    risk_flags: riskFlags,
    risk_adjusted_score: riskAdjustedScore,
    risk_score: {
      ...signalPayload.risk_score,
      total: totalRisk,
      event: eventRisk,
      explanation: `${signalPayload.risk_score.explanation} Official TWSE/TDCC reference flags are attached for risk review.`,
    },
    explanation: {
      ...signalPayload.explanation,
      top_risk_factors: [...topRisk, ...(signalPayload.explanation?.top_risk_factors ?? [])].slice(0, 5),
    },
  };
}

function getDataSourceStatus(): DataSourceStatus[] {
  const supabaseTargetReadConfigured = isSupabaseAnalystTargetReadConfigured();
  const supabaseTargetWriteConfigured = isSupabaseAnalystTargetWriteConfigured();
  const keyedProviders: Array<[string, string | string[], string]> = [
    ["OpenAI 新聞解析", "OPENAI_API_KEY", "https://platform.openai.com/docs/api-reference"],
    ["Finnhub 美股/新聞", "FINNHUB_API_KEY", "https://finnhub.io/docs/api"],
    ["Polygon/Massive 美股", "POLYGON_API_KEY", "https://massive.com/docs"],
    ["Alpha Vantage 技術指標", "ALPHA_VANTAGE_API_KEY", "https://www.alphavantage.co/documentation/"],
    ["FRED 美國總經", "FRED_API_KEY", "https://fred.stlouisfed.org/docs/api/fred/"],
    ["TEJ 商業台股資料", "TEJ_API_KEY", "https://api.tej.com.tw/"],
    ["FMP 法人目標價", ["FMP_API_KEY", "FINANCIAL_MODELING_PREP_API_KEY"], analystProviderUrls.fmp],
    ["FactSet 法人共識", "FACTSET_API_KEY", analystProviderUrls.factset],
    ["LSEG I/B/E/S 法人共識", "LSEG_API_KEY", analystProviderUrls.lseg],
    ["Bloomberg 法人/估值資料", "BLOOMBERG_API_KEY", analystProviderUrls.bloomberg],
  ];
  return [
    { name: "TWSE OpenAPI", status: "connected", detail: "上市總表、估值、重大訊息、注意/處置、融資融券、外資持股；個股頁另接 TWSE 官方日成交資訊", url: "https://openapi.twse.com.tw/", requires_key: false },
    { name: "TPEx OpenAPI", status: "connected", detail: "上櫃行情與本益比/殖利率/股價淨值比", url: "https://www.tpex.org.tw/openapi/", requires_key: false },
    { name: "TDCC OpenData", status: "connected", detail: "股權分散與大額持股集中度 reference", url: tdccOwnershipDistributionUrl, requires_key: false },
    { name: "CNA RSS", status: "connected", detail: "財經與科技新聞 RSS，新聞池與前台畫面每 1 分鐘同步", url: cnaFinanceRssUrl, requires_key: false },
    { name: "本機券商研究報告", status: "connected", detail: "已匯入富邦、合庫、中信、國泰、元大 Computex/AI factory PDF 摘要、供應鏈事件與部分目標價；正式商用需確認轉載與 redisplay 權利", url: "https://stock.suiyuecare.com/news", requires_key: false },
    {
      name: "Supabase 新聞法人目標價",
      status: supabaseTargetReadConfigured ? "configured" : "needs_key",
      detail: supabaseTargetWriteConfigured
        ? "每兩天由公開新聞/RSS 擷取法人目標價並寫入 Supabase，前台優先讀取最新紀錄"
        : "前台可讀設定尚未完整，或缺少 server-side SUPABASE_SERVICE_ROLE_KEY，暫時無法由 Cron 寫入新目標價",
      url: "https://supabase.com/docs/guides/api",
      requires_key: true,
    },
    ...keyedProviders.map(([name, envName, url]) => {
      const envNames = Array.isArray(envName) ? envName : [envName];
      const configured = envNames.some((item) => process.env[item]);
      return {
      name,
      status: configured ? "configured" as const : "needs_key" as const,
      detail: configured ? `${envNames.join(" / ")} 已設定，可進入正式 provider 串接` : `${envNames.join(" / ")} 尚未設定，前台先顯示免授權資料與保留欄位`,
      url,
      requires_key: true,
    };
    }),
  ];
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

async function attachTwseMarketData(signalPayload: PredictionSignal): Promise<PredictionSignal> {
  const [quoteMap, valuationMap, tpexQuoteMap, tpexValuationMap, riskFlagMap] = await Promise.all([
    getTwseQuoteMap(),
    getTwseValuationMap(),
    getTpexQuoteMap(),
    getTpexValuationMap(),
    getApiRiskFlagMap(),
  ]);
  const valuation = valuationMap.get(signalPayload.symbol) ?? tpexValuationMap.get(signalPayload.symbol) ?? null;
  const twseQuote = quoteMap.get(signalPayload.symbol) ?? null;
  const shouldTryLatestTwseQuote = Boolean(twseQuote || valuation?.source === "TWSE OpenAPI");
  const latestTwseQuote = shouldTryLatestTwseQuote ? await getLatestTwseStockDayQuote(signalPayload.symbol, twseQuote?.name || valuation?.name) : null;
  const quote = pickLatestQuote(latestTwseQuote, twseQuote) ?? tpexQuoteMap.get(signalPayload.symbol) ?? null;
  const market = quote?.source === "TPEx OpenAPI" || valuation?.source === "TPEx OpenAPI" ? "TPEX" : "TW";
  const instrument: StockInstrument = {
    symbol: signalPayload.symbol,
    name: quote?.name || valuation?.name || signalPayload.name,
    sector: signalPayload.sector ?? null,
    market,
    currency: "TWD",
  };
  const news = await getNewsForInstrument(instrument);
  const analystTargetPrice = await getExternalAnalystTargetPrice(instrument, news);
  const withMarketData = applyNewsSignal({
    ...signalPayload,
    name: instrument.name,
    quote,
    valuation,
    analyst_target_price: analystTargetPrice,
    data_source_status: getDataSourceStatus(),
  }, news);
  return applyApiRiskFlags(withMarketData, riskFlagMap.get(signalPayload.symbol) ?? []);
}

async function fetchWithTimeout(url: string, init: RequestInit & { next?: { revalidate?: number }; timeoutMs?: number } = {}): Promise<Response> {
  const { timeoutMs = 8000, ...fetchInit } = init;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...fetchInit, signal: controller.signal });
  } finally {
    clearTimeout(timeout);
  }
}

function formatTwseMonth(month: string): string {
  const trimmed = month.trim();
  if (!/^\d{5}$/.test(trimmed)) return "2026-04";
  const year = Number(trimmed.slice(0, 3)) + 1911;
  return `${year}-${trimmed.slice(3, 5)}`;
}

function formatTwseDate(date: string): string {
  const trimmed = date.trim();
  if (!/^\d{7}$/.test(trimmed)) return "2026-05-17";
  const year = Number(trimmed.slice(0, 3)) + 1911;
  return `${year}-${trimmed.slice(3, 5)}-${trimmed.slice(5, 7)}`;
}

function shiftMonth(date: string, offset: number): string {
  const [yearText, monthText] = date.split("-");
  const dateValue = new Date(Number(yearText), Number(monthText) - 1 + offset, 1);
  return `${dateValue.getFullYear()}-${String(dateValue.getMonth() + 1).padStart(2, "0")}`;
}

function fallbackGrowthHistory(symbol: string): { history: RevenueGrowthPoint[]; source: DataSourceReference } {
  const seed = symbolSeed(symbol);
  const baseRevenue = bounded(seed, 1800, 90000, 60);
  const history = Array.from({ length: 8 }, (_, index) => {
    const month = shiftMonth("2026-04", index - 7);
    const momentum = 1 + (index - 3) * 0.018 + Math.sin(seed + index) * 0.025;
    const revenue = Math.max(120, baseRevenue * momentum);
    return {
      date: month,
      label: month,
      revenue_million_twd: Number(revenue.toFixed(0)),
      revenue_yoy: Number(bounded(seed, -8, 24, 70 + index).toFixed(1)),
      revenue_mom: Number(bounded(seed, -5, 12, 80 + index).toFixed(1)),
      accumulated_yoy: Number(bounded(seed, -6, 18, 90 + index).toFixed(1)),
    };
  });
  return {
    history,
    source: {
      name: "TWSE OpenAPI",
      url: twseMonthlyRevenueUrl,
      dataset: "上市公司每月營業收入彙總表 /opendata/t187ap05_L",
      published_at: "示範資料",
      note: "若官方 API 暫時無法取得，前台會使用示範曲線維持閱讀體驗。",
    },
  };
}

async function getRevenueGrowth(symbol: string): Promise<{ history: RevenueGrowthPoint[]; source: DataSourceReference }> {
  if (revenueGrowthCache.has(symbol)) return revenueGrowthCache.get(symbol)!;
  try {
    const response = await fetch(twseMonthlyRevenueUrl, { next: { revalidate: 60 * 60 * 6 } });
    if (response.ok) {
      const rows = (await response.json()) as Array<Record<string, string>>;
      const row = rows.find((item) => String(item["公司代號"] ?? "").trim() === symbol);
      if (row) {
        const currentMonth = formatTwseMonth(String(row["資料年月"] ?? ""));
        const currentRevenue = parseTwseNumber(row["營業收入-當月營收"]);
        const previousRevenue = parseTwseNumber(row["營業收入-上月營收"]);
        const lastYearRevenue = parseTwseNumber(row["營業收入-去年當月營收"]);
        const mom = parseTwseNumber(row["營業收入-上月比較增減(%)"]);
        const yoy = parseTwseNumber(row["營業收入-去年同月增減(%)"]);
        const accumulatedYoy = parseTwseNumber(row["累計營業收入-前期比較增減(%)"]);
        const history = [
          {
            date: shiftMonth(currentMonth, -12),
            label: "去年同月",
            revenue_million_twd: Number(((lastYearRevenue ?? currentRevenue ?? 0) / 1000).toFixed(0)),
            revenue_yoy: null,
            revenue_mom: null,
            accumulated_yoy: null,
          },
          {
            date: shiftMonth(currentMonth, -1),
            label: "上月",
            revenue_million_twd: Number(((previousRevenue ?? currentRevenue ?? 0) / 1000).toFixed(0)),
            revenue_yoy: null,
            revenue_mom: null,
            accumulated_yoy: null,
          },
          {
            date: currentMonth,
            label: "本月",
            revenue_million_twd: Number(((currentRevenue ?? 0) / 1000).toFixed(0)),
            revenue_yoy: yoy,
            revenue_mom: mom,
            accumulated_yoy: accumulatedYoy,
          },
        ];
        const result = {
          history,
          source: {
            name: "TWSE OpenAPI",
            url: twseMonthlyRevenueUrl,
            dataset: "上市公司每月營業收入彙總表 /opendata/t187ap05_L",
            published_at: formatTwseDate(String(row["出表日期"] ?? "")),
            note: "此 API 提供最新月營收、上月、去年同月、MoM、YoY 與累計 YoY，可作為成長曲線與基本面因子 reference。",
          },
        };
        revenueGrowthCache.set(symbol, result);
        return result;
      }
    }
  } catch {
    // Keep the page readable if TWSE is temporarily unavailable.
  }
  const fallback = fallbackGrowthHistory(symbol);
  revenueGrowthCache.set(symbol, fallback);
  return fallback;
}

function signal(symbol: string, name: string, index: number, sector: string | null = null): PredictionSignal {
  const seed = symbolSeed(symbol);
  const base = bounded(seed, 0.53, 0.72, 1);
  const riskTotal = bounded(seed, 0.24, 0.58, 2);
  const fundamentalScore = Math.round(bounded(seed, 48, 82, 3));
  const chipScore = Math.round(bounded(seed, 42, 80, 4));
  const technicalScore = Math.round(bounded(seed, 45, 84, 5));
  const usMarketScore = Math.round(bounded(seed, sector?.includes("半導體") ? 58 : 38, sector?.includes("半導體") ? 86 : 70, 6));
  const newsScore = Math.round(bounded(seed, 45, 72, 7));
  const bullishScore = Math.round(0.2 * fundamentalScore + 0.18 * chipScore + 0.17 * technicalScore + 0.15 * usMarketScore + 0.12 * newsScore + 16);
  const riskAdjustedScore = Math.round(Math.max(35, Math.min(78, bullishScore - riskTotal * 35)));
  const factorScores = [
    factor("FundamentalScore", "fundamental", fundamentalScore, 0.2),
    factor("ChipScore", "chip", chipScore, 0.18),
    factor("TechnicalScore", "technical", technicalScore, 0.17),
    factor("USMarketScore", "us-linkage", usMarketScore, 0.15),
    factor("NewsScore", "news", newsScore, 0.12),
    factor("TargetPriceScore", "target_price", 50, 0.05, "neutral"),
  ];

  return {
    symbol,
    name,
    sector,
    signal_date: "2026-06-02",
    horizon: "1D/5D/20D",
    probability_up: base,
    probability_up_1d: base,
    probability_up_5d: base - 0.03,
    probability_up_20d: base - 0.06,
    confidence: bounded(seed, 0.58, 0.78, 8),
    composite_score: bullishScore / 100,
    bullish_score: bullishScore,
    risk_adjusted_score: riskAdjustedScore,
    explanation: {
      top_positive_factors: [`${sector ?? "產業"} 因子資料已納入觀察`, "Technical trend remains above medium averages"],
      top_negative_factors: ["正式財報/法人資料仍待後端排程寫入", "Valuation sensitivity remains elevated"],
      top_risk_factors: ["VIX change", "Event risk", "Liquidity and volatility watch"],
      component_scores: {
        FundamentalScore: fundamentalScore,
        ChipScore: chipScore,
        TechnicalScore: technicalScore,
        USMarketScore: usMarketScore,
        NewsScore: newsScore,
        TargetPriceScore: 50,
      },
    },
    risk_score: {
      total: riskTotal,
      volatility: bounded(seed, 0.22, 0.62, 9),
      liquidity: bounded(seed, 0.16, 0.48, 10),
      concentration: bounded(seed, 0.2, 0.56, 11),
      event: bounded(seed, 0.18, 0.55, 12),
      explanation: "MVP fallback risk score combining volatility, liquidity, concentration, and event risk.",
    },
    technicals: {
      ma_5: Math.round(bounded(seed, 18, 1200, 13)),
      ma_20: Math.round(bounded(seed, 18, 1180, 14)),
      ma_60: Math.round(bounded(seed, 16, 1120, 15)),
      rsi_14: Math.round(bounded(seed, 42, 68, 16)),
      k_9: Math.round(bounded(seed, 38, 72, 17)),
      d_9: Math.round(bounded(seed, 36, 70, 18)),
      macd: Number(bounded(seed, -1.2, 3.2, 19).toFixed(2)),
      macd_signal: Number(bounded(seed, -1.1, 2.8, 20).toFixed(2)),
      macd_histogram: Number(bounded(seed, -0.6, 0.9, 21).toFixed(2)),
      obv: Math.round(bounded(seed, 120000, 2600000, 22)),
      volume_price_divergence: Number(bounded(seed, -0.35, 0.35, 23).toFixed(2)),
    },
    factor_scores: factorScores,
    positive_drivers: factorScores.filter((item) => item.direction === "positive").slice(0, 3),
    negative_drivers: [factor("FX volatility", "macro", 42, 0.08, "negative"), factor("Event risk", "risk", 38, 0.1, "negative")],
    news: mockNews(symbol),
  };
}

async function getFallbackSignals(limit?: number): Promise<PredictionSignal[]> {
  const allSignals = await getAllFallbackSignals();
  return typeof limit === "number" ? allSignals.slice(0, limit) : allSignals;
}

async function getAllFallbackSignals(): Promise<PredictionSignal[]> {
  if (fallbackSignalsCache) return fallbackSignalsCache;
  if (fallbackSignalsCachePromise) return fallbackSignalsCachePromise;
  fallbackSignalsCachePromise = loadAllFallbackSignals();
  return fallbackSignalsCachePromise;
}

async function getRecommendationFallbackSignals(): Promise<PredictionSignal[]> {
  const cacheAgeMs = Date.now() - fallbackRecommendationSignalsCacheLoadedAt;
  if (
    fallbackRecommendationSignalsCache
    && cacheAgeMs < 10 * 60 * 1000
    && !(dateBehindToday(fallbackRecommendationDataDate) && cacheAgeMs > 60 * 1000)
  ) {
    return fallbackRecommendationSignalsCache;
  }
  if (fallbackRecommendationSignalsCachePromise) return fallbackRecommendationSignalsCachePromise;
  fallbackRecommendationSignalsCachePromise = loadRecommendationFallbackSignals();
  return fallbackRecommendationSignalsCachePromise;
}

async function loadAllFallbackSignals(): Promise<PredictionSignal[]> {
  const stocks = await getFallbackInstruments();
  const stockMap = new Map(stocks.map((item) => [item.symbol, item]));
  const coveredStocks = recommendationCoverageSymbols.map((symbol) => stockMap.get(symbol)).filter((item): item is StockInstrument => Boolean(item));
  const selected = uniqueInstruments([
    ...coveredStocks,
    ...stocks.filter((item) => !recommendationCoverageSymbols.includes(item.symbol)).slice(0, 140),
  ]).slice(0, Math.min(stocks.length, 180));
  fallbackSignalsCache = await Promise.all(selected.map((item, index) => attachTwseMarketData(signal(item.symbol, item.name, index, item.sector))));
  return fallbackSignalsCache;
}

async function loadRecommendationFallbackSignals(): Promise<PredictionSignal[]> {
  const [stocks, twseQuoteMap, tpexQuoteMap, valuationMap, tpexValuationMap, riskFlagMap] = await Promise.all([
    getFallbackInstruments(),
    getTwseQuoteMap(),
    getTpexQuoteMap(),
    getTwseValuationMap(),
    getTpexValuationMap(),
    getApiRiskFlagMap(),
  ]);
  const stockMap = new Map(stocks.map((item) => [item.symbol, item]));
  const quoteMap = new Map<string, TwseQuote>([...twseQuoteMap.entries(), ...tpexQuoteMap.entries()]);
  const tradableQuotes = Array.from(quoteMap.values())
    .filter((quote) => isTradableCommonStock(quote.symbol))
    .filter((quote) => (quote.close ?? 0) >= 10)
    .filter((quote) => (quote.trade_value ?? 0) >= 30_000_000);

  const buildCandidate = (quote: TwseQuote, index: number) => {
    const fallbackInstrument: StockInstrument = {
      symbol: quote.symbol,
      name: quote.name,
      market: quote.source === "TPEx OpenAPI" ? "TPEX" : "TW",
      sector: stockMap.get(quote.symbol)?.sector ?? null,
      currency: "TWD",
    };
    const instrument = stockMap.get(quote.symbol) ?? fallbackInstrument;
    const valuation = valuationMap.get(quote.symbol) ?? tpexValuationMap.get(quote.symbol) ?? null;
    const baseSignal = signal(instrument.symbol, instrument.name, index, instrument.sector);
    const scoredSignal = applyDynamicQuoteScores(baseSignal, quote, valuation, instrument);
    return {
      signal: scoredSignal,
      score: dynamicRecommendationScore(scoredSignal),
    };
  };
  const preliminaryCandidates = tradableQuotes
    .map(buildCandidate)
    .sort((left, right) => right.score - left.score);
  const shouldRefreshLatestQuotes = shouldRefreshTwsePerStockQuotes(tradableQuotes);
  const latestQuoteOverrides = shouldRefreshLatestQuotes
    ? await getLatestRecommendationQuoteOverrides(preliminaryCandidates, tradableQuotes)
    : new Map<string, TwseQuote>();
  fallbackRecommendationFreshness = buildRecommendationFreshness({
    twseStockDayAllDate: latestQuoteDateFromMap(twseQuoteMap),
    twseOfficialStockDayDate: latestQuoteDateFromMap(latestQuoteOverrides),
    tpexDate: latestQuoteDateFromMap(tpexQuoteMap),
  });
  const candidates = tradableQuotes
    .map((quote, index) => buildCandidate(latestQuoteOverrides.get(quote.symbol) ?? quote, index))
    .sort((left, right) => right.score - left.score);

  fallbackRecommendationCandidateCount = candidates.length;
  fallbackRecommendationDataDate = [
    ...candidates.map((candidate) => candidate.signal.quote?.date),
    ...Array.from(latestQuoteOverrides.values()).map((quote) => quote.date),
  ].filter((date): date is string => Boolean(date && date !== "資料日期待確認")).sort().at(-1) ?? candidates[0]?.signal.quote?.date ?? "資料日期待確認";

  const priorityCandidateSymbols = new Set(recommendationCoverageSymbols);
  const priorityCandidates = candidates.filter(({ signal: signalPayload }) => priorityCandidateSymbols.has(signalPayload.symbol));
  const enrichmentTargets = uniqueRecommendationTargets([...candidates.slice(0, 90), ...priorityCandidates]).slice(0, 140);
  const enriched = await Promise.all(enrichmentTargets.map(async ({ signal: signalPayload }) => {
    const instrument: StockInstrument = {
      symbol: signalPayload.symbol,
      name: signalPayload.name,
      market: signalPayload.quote?.source === "TPEx OpenAPI" ? "TPEX" : "TW",
      sector: signalPayload.sector ?? null,
      currency: "TWD",
    };
    const news = await getNewsForInstrument(instrument);
    const analystTargetPrice = await getExternalAnalystTargetPrice(instrument, news);
    const withNews = applyNewsSignal({
      ...signalPayload,
      analyst_target_price: analystTargetPrice,
      data_source_status: getDataSourceStatus(),
    }, news);
    return applyApiRiskFlags(withNews, riskFlagMap.get(signalPayload.symbol) ?? []);
  }));

  fallbackRecommendationSignalsCache = enriched
    .sort((left, right) => dynamicRecommendationScore(right) - dynamicRecommendationScore(left))
    .slice(0, 80);
  fallbackRecommendationSignalsCacheLoadedAt = Date.now();

  if (fallbackRecommendationSignalsCache.length === 0) {
    const seedMap = new Map(seedInstruments.map((item) => [item.symbol, item]));
    const selected = recommendationCoverageSymbols
      .map((symbol) => seedMap.get(symbol))
      .filter((item): item is StockInstrument => Boolean(item));
    fallbackRecommendationSignalsCache = selected.map((item, index) => signal(item.symbol, item.name, index, item.sector));
    fallbackRecommendationCandidateCount = fallbackRecommendationSignalsCache.length;
    fallbackRecommendationDataDate = "示範資料";
    fallbackRecommendationSignalsCacheLoadedAt = Date.now();
    fallbackRecommendationFreshness = {
      mode: "demo",
      label: "示範資料",
      summary: "官方來源暫時不可用，推薦頁暫退回示範候選池。",
      twse_stock_day_all_date: null,
      twse_official_stock_day_date: null,
      tpex_date: null,
      market_study_baseline_date: "2026-06-03",
    };
  }

  fallbackRecommendationSignalsCachePromise = null;
  return fallbackRecommendationSignalsCache;
}

async function getLatestRecommendationQuoteOverrides(
  preliminaryCandidates: Array<{ signal: PredictionSignal; score: number }>,
  tradableQuotes: TwseQuote[],
): Promise<Map<string, TwseQuote>> {
  const prioritySymbols = new Set(recommendationCoverageSymbols);
  const priorityQuotes = tradableQuotes
    .filter((quote) => prioritySymbols.has(quote.symbol))
    .map((quote) => ({ signal: { symbol: quote.symbol, name: quote.name, quote } as PredictionSignal, score: 100 }));
  const targets = uniqueRecommendationTargets([...priorityQuotes, ...preliminaryCandidates])
    .filter(({ signal: signalPayload }) => signalPayload.quote?.source === "TWSE OpenAPI")
    .slice(0, 160);
  const latestQuotes = await mapWithConcurrency(targets, 12, async ({ signal: signalPayload }) => {
    return getLatestTwseStockDayQuote(signalPayload.symbol, signalPayload.name);
  });
  return new Map(latestQuotes
    .filter((quote): quote is TwseQuote => Boolean(quote?.close && quote.date >= taipeiIsoDate()))
    .map((quote) => [quote.symbol, quote]));
}

function uniqueRecommendationTargets(
  targets: Array<{ signal: PredictionSignal; score: number }>,
): Array<{ signal: PredictionSignal; score: number }> {
  const seen = new Set<string>();
  return targets.filter(({ signal: signalPayload }) => {
    if (seen.has(signalPayload.symbol)) return false;
    seen.add(signalPayload.symbol);
    return true;
  });
}

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

async function findSignal(symbol: string): Promise<PredictionSignal> {
  const stocks = await getFallbackInstruments();
  const normalized = symbol.toUpperCase();
  const instrument = stocks.find((item) => item.symbol === normalized) ?? stocks[0];
  const index = Math.max(0, stocks.findIndex((item) => item.symbol === instrument.symbol));
  return attachTwseMarketData(signal(instrument.symbol, instrument.name, index, instrument.sector));
}

async function stockDetail(symbol: string): Promise<StockDetailResponse> {
  const selected = await findSignal(symbol);
  const stocks = await getFallbackInstruments();
  const instrument = stocks.find((item) => item.symbol === selected.symbol) ?? stocks[0];
  const growth = await getRevenueGrowth(selected.symbol);
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
    growth_history: growth.history,
    growth_source: growth.source,
  };
}

async function technicalResponse(symbol: string): Promise<StockTechnicalResponse> {
  const selected = await findSignal(symbol);
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

async function institutionalResponse(symbol: string): Promise<StockInstitutionalResponse> {
  const selected = await findSignal(symbol);
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

async function usMarketRadar(): Promise<USMarketRadarResponse> {
  const signals = await getFallbackSignals(80);
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

async function taiwanPredictionTool(): Promise<TaiwanPredictionToolResponse> {
  const signals = await getRecommendationFallbackSignals();
  const ranked = signals.slice(0, 20).map((item) => ({
    symbol: item.symbol,
    name: item.name,
    score_1d: Math.round((item.explanation?.component_scores?.TechnicalScore ?? 62) * 0.35 + (item.explanation?.component_scores?.ChipScore ?? 60) * 0.3 + 27),
    score_5d: Math.round((item.explanation?.component_scores?.TechnicalScore ?? 62) * 0.24 + (item.explanation?.component_scores?.ChipScore ?? 60) * 0.24 + (item.explanation?.component_scores?.FundamentalScore ?? 58) * 0.18 + 22),
    score_20d: Math.round((item.explanation?.component_scores?.FundamentalScore ?? 58) * 0.34 + (item.explanation?.component_scores?.ChipScore ?? 60) * 0.18 + 26),
    reason: "3/1-6/3 市場研究版 · 多因子共振 · 流動性硬篩",
    overheat_penalty: 0,
    event_risk_penalty: 0,
    liquidity_passed: true,
  }));
  return {
    disclaimer,
    research: {
      research_window: {
        start: "2026-03-01",
        first_trading_day: "2026-03-02",
        end: "2026-06-03",
        trading_days: 65,
      },
      market_summary: {
        taiex_start_close: 35095.09,
        taiex_end_close: 46459.16,
        taiex_period_return: 0.3238,
        taiex_20d_return: 0.1293,
        taiex_60d_return: 0.3827,
        taiex_high_date: "2026-06-03",
        taiex_high: 46552.16,
        taiex_low_date: "2026-03-09",
        taiex_low: 31529.36,
        max_drawdown: -0.0961,
        latest_breadth_ratio: 0.7,
        daily_volatility: 0.0197,
      },
      sector_rotation: [
        { name: "電子零組件", score: 92, return: 0.7598, role: "leader" },
        { name: "AI 供應鏈", score: 90, return: 0.7276, role: "leader" },
        { name: "IC 設計", score: 89, return: 0.7181, role: "leader" },
        { name: "晶圓製造", score: 88, return: 0.6984, role: "leader" },
        { name: "智慧移動與電動車", score: 86, return: 0.7291, role: "leader" },
        { name: "金融避險", score: 66, return: null, role: "defensive" },
        { name: "航運航空", score: 63, return: null, role: "cyclical" },
        { name: "內需防禦", score: 56, return: null, role: "defensive" },
        { name: "生技醫療", score: 40, return: -0.1062, role: "laggard" },
      ],
      hard_filters: {
        min_trade_value_twd: 30_000_000,
        exclude_attention_or_disposition: true,
        exclude_low_liquidity: true,
        exclude_extreme_event_risk: true,
      },
      model_notes: [
        "分數不是機率；probability_up 需要歷史分桶、Brier Score 與 walk-forward 校準。",
        "流動性不加分，直接作硬性過濾。",
        "所有產業都用同業百分位、籌碼、技術、營收與風險重新競爭，不只偏 AI。",
      ],
      data_sources: [
        { name: "TWSE TAIEX historical index", url: "https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST", usage: "TAIEX trend, return and drawdown." },
        { name: "TWSE daily market quotes", url: "https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY_ALL", usage: "Breadth and liquidity filters." },
        { name: "TWSE daily index tables", url: "https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX", usage: "Sector rotation." },
        { name: "MOPS monthly revenue", url: "https://mopsfin.twse.com.tw/opendata/t187ap05_L.csv", usage: "Revenue and industry cycle." },
      ],
    },
    horizon_weights: {
      "1d": { technical: 0.25, chip: 0.22, us_market: 0.18, market: 0.12, news: 0.1, revenue_industry: 0.05, fundamental: 0.05, valuation: 0.03 },
      "5d": { technical: 0.22, chip: 0.22, us_market: 0.13, market: 0.08, news: 0.05, revenue_industry: 0.15, fundamental: 0.12, valuation: 0.03 },
      "20d": { technical: 0.15, chip: 0.18, us_market: 0.08, market: 0.08, news: 0.02, revenue_industry: 0.22, fundamental: 0.22, valuation: 0.05 },
    },
    market_state: {
      score: 73,
      label: "強多但集中",
      action: "可積極挑股，但只收低過熱、高流動性、多因子共振的股票。",
      tone: "positive",
      multiplier: 1.03,
      components: [
        { name: "加權指數趨勢", score: 92, detail: "3/2 至 6/3 TAIEX +32.38%，6/3 創區間高點。" },
        { name: "市場寬度", score: 70, detail: "6/3 上漲家數 763 / 1090，最近 10 日約 70%。" },
        { name: "大盤資金", score: 64, detail: "暫用籌碼與成交值代理，待接法人總量。" },
        { name: "美股與 AI 外溢", score: 76, detail: "AI / ICT 出口與半導體供應鏈是背景，但不是唯一題材。" },
        { name: "匯率", score: 55, detail: "暫用中性，接央行匯率後校準。" },
        { name: "波動風險", score: 57, detail: "期間最大回撤約 -9.61%，日波動約 1.97%。" },
        { name: "集中風險扣分", score: -8, detail: "大盤市值加權集中，不能把大盤強直接視為全市場強。" },
      ],
    },
    ranked_signals: ranked,
  };
}

async function mockResponse(path: string): Promise<unknown> {
  if (path === "/api/market/summary") {
    const stocks = await getFallbackInstruments();
    const sessionDate = await getLatestOfficialQuoteDate();
    return {
      session_date: sessionDate,
      tw_status: "盤後資料就緒",
      us_premarket_status: "美股開盤前觀察",
      disclaimer,
      instruments: stocks,
      us_linkage: linkage,
      data_source_status: getDataSourceStatus(),
    } satisfies MarketSummary;
  }
  if (path === "/api/market/taiwan-prediction-tool") {
    return taiwanPredictionTool();
  }
  if (path === "/api/stocks") {
    const stocks = await getFallbackInstruments();
    return { disclaimer, stocks } satisfies StockListResponse;
  }
  if (path === "/api/rankings/top-probability") {
    const signals = await getRecommendationFallbackSignals();
    return {
      disclaimer,
      signals,
      data_date: fallbackRecommendationDataDate,
      candidate_count: fallbackRecommendationCandidateCount,
      method: "dynamic-twse-tpex-quote-pool",
      freshness: fallbackRecommendationFreshness,
    } satisfies RankingResponse;
  }
  if (path === "/api/stocks/ranking") {
    const signals = await getFallbackSignals();
    return { disclaimer, signals } satisfies RankingResponse;
  }
  if (path === "/api/rankings/institutional-buying") {
    const compactSignals = (await getFallbackSignals()).slice(0, 80);
    return {
      disclaimer,
      ranking: compactSignals.map((item) => ({
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
    const compactSignals = (await getFallbackSignals()).slice(0, 80);
    return {
      disclaimer,
      ranking: compactSignals.map((item) => ({
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
    const compactSignals = (await getFallbackSignals()).slice(0, 80);
    return {
      disclaimer,
      ranking: compactSignals.map((item) => ({
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
    const compactSignals = (await getFallbackSignals()).slice(0, 80);
    return {
      disclaimer,
      signals: compactSignals
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
    const selected = await findSignal(symbol);
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
