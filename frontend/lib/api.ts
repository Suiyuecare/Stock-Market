const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const twseListedCompanyUrl = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L";
const twseMonthlyRevenueUrl = "https://openapi.twse.com.tw/v1/opendata/t187ap05_L";
const twseDailyQuoteUrl = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL";
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
    event_type?: string;
    source_url?: string;
    linkage_reason?: string;
  }>;
  quote?: TwseQuote | null;
  valuation?: TwseValuation | null;
  risk_flags?: ApiRiskFlag[];
  data_source_status?: DataSourceStatus[];
  sector?: string | null;
};

export type TwseQuote = {
  source: "TWSE OpenAPI" | "TPEx OpenAPI";
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
let twseValuationCache: Map<string, TwseValuation> | null = null;
let tpexQuoteCache: Map<string, TwseQuote> | null = null;
let tpexValuationCache: Map<string, TwseValuation> | null = null;
let apiRiskFlagCache: Map<string, ApiRiskFlag[]> | null = null;
let officialNewsCache: NewsItem[] | null = null;
let fallbackSignalsCache: PredictionSignal[] | null = null;
let twseQuoteCachePromise: Promise<Map<string, TwseQuote>> | null = null;
let twseValuationCachePromise: Promise<Map<string, TwseValuation>> | null = null;
let tpexQuoteCachePromise: Promise<Map<string, TwseQuote>> | null = null;
let tpexValuationCachePromise: Promise<Map<string, TwseValuation>> | null = null;
let apiRiskFlagCachePromise: Promise<Map<string, ApiRiskFlag[]>> | null = null;
let officialNewsCachePromise: Promise<NewsItem[]> | null = null;
let fallbackSignalsCachePromise: Promise<PredictionSignal[]> | null = null;

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

async function getTwseQuoteMap(): Promise<Map<string, TwseQuote>> {
  if (twseQuoteCache) return twseQuoteCache;
  if (twseQuoteCachePromise) return twseQuoteCachePromise;
  twseQuoteCachePromise = loadTwseQuoteMap();
  return twseQuoteCachePromise;
}

async function loadTwseQuoteMap(): Promise<Map<string, TwseQuote>> {
  const map = new Map<string, TwseQuote>();
  try {
    const response = await fetchWithTimeout(twseDailyQuoteUrl, { next: { revalidate: 60 * 30 }, timeoutMs: 6000 });
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
  return map;
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
  if (tpexQuoteCache) return tpexQuoteCache;
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
  if (officialNewsCache) return officialNewsCache;
  if (officialNewsCachePromise) return officialNewsCachePromise;
  officialNewsCachePromise = loadOfficialNewsPool();
  return officialNewsCachePromise;
}

async function loadOfficialNewsPool(): Promise<NewsItem[]> {
  const events: NewsItem[] = [];
  const settled = await Promise.allSettled([
    fetchWithTimeout(twseMaterialNewsUrl, { next: { revalidate: 60 * 15 } }),
    fetchWithTimeout(twseExchangeNewsUrl, { next: { revalidate: 60 * 15 } }),
    fetchWithTimeout(twseExchangeEventsUrl, { next: { revalidate: 60 * 60 } }),
    fetchWithTimeout(cnaFinanceRssUrl, { next: { revalidate: 60 * 15 } }),
    fetchWithTimeout(cnaTechnologyRssUrl, { next: { revalidate: 60 * 15 } }),
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
      const summary = stripTags(decodeXml(readRssTag(item, "description")));
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
    ["智原", "3035"],
    ["日月光", "3711"],
  ];
  return mapping.filter(([keyword]) => text.includes(keyword)).map(([, symbol]) => symbol);
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

async function getNewsForInstrument(instrument: StockInstrument): Promise<NewsItem[]> {
  const pool = await getOfficialNewsPool();
  const keywords = deriveNewsKeywords(instrument);
  const direct = pool.filter((event) => event.stock_id === instrument.symbol || event.related_symbols.includes(instrument.symbol));
  const contextual = pool.filter((event) => {
    if (direct.includes(event)) return false;
    const haystack = `${event.title}\n${event.summary ?? ""}`;
    return keywords.some((keyword) => keyword && haystack.includes(keyword));
  });
  const marketBackground = pool.filter((event) => event.source.startsWith("TWSE") || event.source.startsWith("CNA")).slice(0, 4);
  const selected = dedupeNews([...direct, ...contextual, ...marketBackground]).slice(0, 8);
  return selected.map((event) => ({
    ...event,
    related_symbols: event.related_symbols.includes(instrument.symbol) ? event.related_symbols : [...event.related_symbols, instrument.symbol],
  }));
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
  const keyedProviders: Array<[string, string, string]> = [
    ["OpenAI 新聞解析", "OPENAI_API_KEY", "https://platform.openai.com/docs/api-reference"],
    ["Finnhub 美股/新聞", "FINNHUB_API_KEY", "https://finnhub.io/docs/api"],
    ["Polygon/Massive 美股", "POLYGON_API_KEY", "https://massive.com/docs"],
    ["Alpha Vantage 技術指標", "ALPHA_VANTAGE_API_KEY", "https://www.alphavantage.co/documentation/"],
    ["FRED 美國總經", "FRED_API_KEY", "https://fred.stlouisfed.org/docs/api/fred/"],
    ["TEJ 商業台股資料", "TEJ_API_KEY", "https://api.tej.com.tw/"],
    ["FactSet/LSEG 目標價", "FACTSET_API_KEY", "https://developer.factset.com/api-catalog/factset-estimates-api"],
  ];
  return [
    { name: "TWSE OpenAPI", status: "connected", detail: "上市行情、估值、重大訊息、注意/處置、融資融券、外資持股", url: "https://openapi.twse.com.tw/", requires_key: false },
    { name: "TPEx OpenAPI", status: "connected", detail: "上櫃行情與本益比/殖利率/股價淨值比", url: "https://www.tpex.org.tw/openapi/", requires_key: false },
    { name: "TDCC OpenData", status: "connected", detail: "股權分散與大額持股集中度 reference", url: tdccOwnershipDistributionUrl, requires_key: false },
    { name: "CNA RSS", status: "connected", detail: "財經與科技新聞 RSS，前台新聞時間線已連動", url: cnaFinanceRssUrl, requires_key: false },
    ...keyedProviders.map(([name, envName, url]) => ({
      name,
      status: process.env[envName] ? "configured" as const : "needs_key" as const,
      detail: process.env[envName] ? `${envName} 已設定，可進入正式 provider 串接` : `${envName} 尚未設定，前台先顯示免授權資料與保留欄位`,
      url,
      requires_key: true,
    })),
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
  const quote = quoteMap.get(signalPayload.symbol) ?? tpexQuoteMap.get(signalPayload.symbol) ?? null;
  const valuation = valuationMap.get(signalPayload.symbol) ?? tpexValuationMap.get(signalPayload.symbol) ?? null;
  const market = quote?.source === "TPEx OpenAPI" || valuation?.source === "TPEx OpenAPI" ? "TPEX" : "TW";
  const instrument: StockInstrument = {
    symbol: signalPayload.symbol,
    name: quote?.name || valuation?.name || signalPayload.name,
    sector: signalPayload.sector ?? null,
    market,
    currency: "TWD",
  };
  const news = await getNewsForInstrument(instrument);
  const withMarketData = applyNewsSignal({
    ...signalPayload,
    name: instrument.name,
    quote,
    valuation,
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

async function loadAllFallbackSignals(): Promise<PredictionSignal[]> {
  const stocks = await getFallbackInstruments();
  const selected = stocks.slice(0, Math.min(stocks.length, 120));
  fallbackSignalsCache = await Promise.all(selected.map((item, index) => attachTwseMarketData(signal(item.symbol, item.name, index, item.sector))));
  return fallbackSignalsCache;
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

async function mockResponse(path: string): Promise<unknown> {
  if (path === "/api/market/summary") {
    const stocks = await getFallbackInstruments();
    return {
      session_date: "2026-06-02",
      tw_status: "盤後資料就緒",
      us_premarket_status: "美股開盤前觀察",
      disclaimer,
      instruments: stocks,
      us_linkage: linkage,
      data_source_status: getDataSourceStatus(),
    } satisfies MarketSummary;
  }
  if (path === "/api/stocks") {
    const stocks = await getFallbackInstruments();
    return { disclaimer, stocks } satisfies StockListResponse;
  }
  if (path === "/api/stocks/ranking" || path === "/api/rankings/top-probability") {
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
