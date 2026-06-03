const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
const twseListedCompanyUrl = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L";
const twseMonthlyRevenueUrl = "https://openapi.twse.com.tw/v1/opendata/t187ap05_L";
const twseDailyQuoteUrl = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL";
const twseValuationUrl = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL";

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
  quote?: TwseQuote | null;
  valuation?: TwseValuation | null;
};

export type TwseQuote = {
  source: "TWSE OpenAPI";
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
  source: "TWSE OpenAPI";
  endpoint: string;
  date: string;
  symbol: string;
  name: string;
  pe_ratio: number | null;
  dividend_yield: number | null;
  pb_ratio: number | null;
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
    const response = await fetch(`${apiBaseUrl}${path}`, { cache: "no-store" });
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
  try {
    const response = await fetch(twseListedCompanyUrl, { next: { revalidate: 60 * 60 * 6 } });
    if (response.ok) {
      const rows = (await response.json()) as Array<Record<string, string>>;
      const normalized = rows
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
        .filter((item): item is StockInstrument => item !== null);
      if (normalized.length > 0) {
        twseInstrumentCache = normalized;
        return normalized;
      }
    }
  } catch {
    // Keep the frontend resilient when TWSE is temporarily unavailable.
  }
  twseInstrumentCache = uniqueInstruments(seedInstruments);
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
  const map = new Map<string, TwseQuote>();
  try {
    const response = await fetch(twseDailyQuoteUrl, { next: { revalidate: 60 * 30 } });
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
  const map = new Map<string, TwseValuation>();
  try {
    const response = await fetch(twseValuationUrl, { next: { revalidate: 60 * 30 } });
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

async function attachTwseMarketData(signalPayload: PredictionSignal): Promise<PredictionSignal> {
  const [quoteMap, valuationMap] = await Promise.all([getTwseQuoteMap(), getTwseValuationMap()]);
  const quote = quoteMap.get(signalPayload.symbol) ?? null;
  const valuation = valuationMap.get(signalPayload.symbol) ?? null;
  return {
    ...signalPayload,
    name: quote?.name || valuation?.name || signalPayload.name,
    quote,
    valuation,
  };
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
  const stocks = await getFallbackInstruments();
  return stocks.slice(0, limit ?? stocks.length).map((item, index) => signal(item.symbol, item.name, index, item.sector));
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
  const stocks = await getFallbackInstruments();
  const signals = await getFallbackSignals();
  const compactSignals = signals.slice(0, 80);
  if (path === "/api/market/summary") {
    return {
      session_date: "2026-06-02",
      tw_status: "盤後資料就緒",
      us_premarket_status: "美股開盤前觀察",
      disclaimer,
      instruments: stocks,
      us_linkage: linkage,
    } satisfies MarketSummary;
  }
  if (path === "/api/stocks") {
    return { disclaimer, stocks } satisfies StockListResponse;
  }
  if (path === "/api/stocks/ranking" || path === "/api/rankings/top-probability") {
    return { disclaimer, signals } satisfies RankingResponse;
  }
  if (path === "/api/rankings/institutional-buying") {
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
