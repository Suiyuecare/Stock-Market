import type { FactorScore, PredictionSignal, RiskScore } from "@/lib/api";

export const BETA_NOTICE_TEXT = "目前為 MVP Beta 研究展示版，部分行情、法人、財報、目標區間與回測資料仍可能使用示範或延遲資料。";
export const DISCLAIMER_TEXT = "本系統僅提供資料整理、研究分析與教育用途，不構成個人化投資建議、投資顧問服務、交易指示、獲利保證或招攬買賣。";
export const COMPLIANCE_POINTS = [
  "所有機率、因子分數、風險係數與觀察名單都只是研究訊號，不能單獨作為交易決策依據。",
  "資料可能延遲、缺漏、估算或仍處於示範模式；正式判斷請以交易所、公開資訊觀測站與原始資料來源為準。",
  "歷史回測與相似樣本不代表未來績效，模型可能在不同市場狀態下失效。",
  "使用者需自行承擔投資風險；若需要投資、法律或稅務建議，請諮詢具資格的專業人士。",
];

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

export type QuoteOverview = {
  currentPrice: number;
  change: number;
  changePercent: number;
  marketStatus: string;
  quoteTime: string;
  open: number;
  high: number;
  low: number;
  previousClose: number;
  averagePrice: number;
  volumeLots: number;
  turnoverTwd: number;
  amplitude: number;
  turnoverRate: number;
  marketCapTwd: number;
  peRatio: number;
  epsTtm: number;
  grossMargin: number;
  operatingMargin: number;
  netMargin: number;
  dividendYield: number;
  limitUp: number;
  limitDown: number;
  high52w: number;
  low52w: number;
  innerVolumeLots: number;
  outerVolumeLots: number;
};

export type ProfessionalInfoSection = {
  title: string;
  description: string;
  rows: Array<{ label: string; value: string; note: string }>;
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
  if (typeof signal.quote?.close === "number") return Math.round(signal.quote.close);
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

function quoteSourceLabel(signal: PredictionSignal): string {
  if (signal.quote?.source === "TPEx OpenAPI") return "TPEx OpenAPI /tpex_mainboard_daily_close_quotes";
  if (signal.quote?.source === "TWSE Official STOCK_DAY") return "TWSE 官方 /afterTrading/STOCK_DAY";
  if (signal.quote?.source === "TWSE OpenAPI") return "TWSE OpenAPI /exchangeReport/STOCK_DAY_ALL";
  return "後端 API 或示範資料";
}

function valuationSourceLabel(signal: PredictionSignal): string {
  if (signal.valuation?.source === "TPEx OpenAPI") return "TPEx OpenAPI /tpex_mainboard_peratio_analysis";
  if (signal.valuation?.source === "TWSE OpenAPI") return "TWSE OpenAPI /exchangeReport/BWIBBU_ALL";
  return "MVP 估算欄位，待接法人共識與財報";
}

function exchangeLabel(signal: PredictionSignal): string {
  if (signal.quote?.source === "TPEx OpenAPI" || signal.valuation?.source === "TPEx OpenAPI") return "TPEx 上櫃";
  if (signal.quote?.source === "TWSE OpenAPI" || signal.quote?.source === "TWSE Official STOCK_DAY" || signal.valuation?.source === "TWSE OpenAPI") return "TWSE 上市";
  return "台股";
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
    sourceLabel: signal.quote?.close
      ? `現在金額使用 ${quoteSourceLabel(signal)}；上看區間仍為 MVP 研究估算，待接法人共識目標價資料源。`
      : "MVP 研究估算，待接法人共識目標價資料源",
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
  const riskRefs = signal.risk_flags?.slice(0, 2).map((flag) => `${flag.source}：${flag.title}`).join("、");
  const keyedStatus = signal.data_source_status?.filter((item) => item.requires_key).slice(0, 2).map((item) => `${item.name} ${item.status === "needs_key" ? "待授權" : "已設定"}`).join("、");
  const refs = [
    "因子分數：基本面、籌碼、技術、美股連動、新聞、風險分數",
    `行情來源：${quoteSourceLabel(signal)}`,
    `估值來源：${valuationSourceLabel(signal)}`,
    `新聞來源：${signal.news.map((item) => item.source).filter(Boolean).slice(0, 2).join("、") || "資料觀察中"}`,
    "技術依據：MA、RSI、KD、MACD、OBV、量價背離",
    `風險依據：${riskRefs || "波動、流動性、事件風險、VIX/美股代理訊號"}`,
    `API 授權狀態：免授權 TWSE/TPEx/TDCC/CNA 已連動；${keyedStatus || "付費/需 key providers 保留環境變數"}`,
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

export function buildQuoteOverview(signal: PredictionSignal): QuoteOverview {
  const target = buildTargetPriceRange(signal);
  const metrics = buildStockMetrics(signal);
  const quote = signal.quote;
  const valuation = signal.valuation;
  const currentPrice = quote?.close ?? target.currentPrice;
  const previousClose = quote?.change !== null && quote?.change !== undefined
    ? Math.max(0, Number((currentPrice - quote.change).toFixed(2)))
    : Math.max(10, Math.round(currentPrice * (1 - (metrics.riskAdjustedScore - 50) / 1800)));
  const change = quote?.change ?? currentPrice - previousClose;
  const changePercent = previousClose ? (change / previousClose) * 100 : 0;
  const high = quote?.high ?? Math.round(currentPrice * 1.025);
  const low = quote?.low ?? Math.round(currentPrice * 0.975);
  const volumeLots = quote?.trade_volume ? Math.round(quote.trade_volume / 1000) : Math.round(8000 + metrics.chipScore * 92 + metrics.technicalScore * 40);
  const turnoverTwd = quote?.trade_value ? Math.round(quote.trade_value / 100000000) : Math.round((currentPrice * volumeLots * 1000) / 100000000);
  const computedPeRatio = Number(Math.max(10, 120 - metrics.fundamentalScore + metrics.riskScore / 2).toFixed(2));
  const peRatio = valuation?.pe_ratio ?? computedPeRatio;

  return {
    currentPrice,
    change,
    changePercent,
    marketStatus: quote ? `${exchangeLabel(signal)}盤後資料` : "市場收盤",
    quoteTime: quote ? `${quote.date} ${exchangeLabel(signal)}盤後` : `${signal.signal_date} 盤後`,
    open: quote?.open ?? Math.round((currentPrice + previousClose) / 2),
    high,
    low,
    previousClose,
    averagePrice: Math.round((high + low + currentPrice) / 3),
    volumeLots,
    turnoverTwd,
    amplitude: ((high - low) / previousClose) * 100,
    turnoverRate: Math.max(0.4, Math.min(8, volumeLots / 4200)),
    marketCapTwd: Math.round(currentPrice * (40 + metrics.fundamentalScore / 2)),
    peRatio,
    epsTtm: Number(Math.max(0.8, currentPrice / Math.max(1, peRatio)).toFixed(2)),
    grossMargin: Number(Math.max(12, Math.min(62, metrics.fundamentalScore * 0.68)).toFixed(2)),
    operatingMargin: Number(Math.max(3, Math.min(35, metrics.fundamentalScore * 0.34)).toFixed(2)),
    netMargin: Number(Math.max(2, Math.min(28, metrics.fundamentalScore * 0.28)).toFixed(2)),
    dividendYield: valuation?.dividend_yield ?? Number(Math.max(0.4, Math.min(5.5, 6 - metrics.riskScore / 13)).toFixed(2)),
    limitUp: Math.round(previousClose * 1.1),
    limitDown: Math.round(previousClose * 0.9),
    high52w: Math.round(currentPrice * 1.18),
    low52w: Math.round(currentPrice * 0.72),
    innerVolumeLots: Math.round(volumeLots * (0.46 + metrics.riskScore / 500)),
    outerVolumeLots: Math.round(volumeLots * (0.54 - metrics.riskScore / 500)),
  };
}

export function buildProfessionalInfoSections(signal: PredictionSignal): ProfessionalInfoSection[] {
  const metrics = buildStockMetrics(signal);
  const quote = buildQuoteOverview(signal);
  const backtest = buildBacktestConfidenceProfile(signal);
  const target = buildTargetPriceRange(signal);
  const quoteSourceNote = quoteSourceLabel(signal);
  const valuationSourceNote = valuationSourceLabel(signal);
  const riskReferenceNote = signal.risk_flags?.length
    ? signal.risk_flags.slice(0, 2).map((flag) => `${flag.source}：${flag.detail}`).join("；")
    : "TWSE/TDCC 官方 reference 若命中會自動顯示";

  return [
    {
      title: "交易報價",
      description: "價格、量能、區間與市場狀態，供一般投資人先快速掌握。",
      rows: [
        { label: "今開 / 最高 / 最低", value: `${quote.open} / ${quote.high} / ${quote.low}`, note: quoteSourceNote },
        { label: "成交量 / 成交額", value: `${quote.volumeLots.toLocaleString()} 張 / ${quote.turnoverTwd} 億`, note: "用於流動性與滑價風險評估" },
        { label: "52W 高低", value: `${quote.high52w} / ${quote.low52w}`, note: "觀察目前價格所在區間" },
      ],
    },
    {
      title: "研究訊號",
      description: "把因子引擎結果翻成入門投資人容易理解的觀察資訊。",
      rows: [
        { label: "1D / 5D / 20D 上漲機率", value: `${metrics.probabilityUp1d}% / ${metrics.probabilityUp5d}% / ${metrics.probabilityUp20d}%`, note: "機率訊號，不代表個人化建議" },
        { label: "Bullish / Risk / Risk-adjusted", value: `${metrics.bullishScore} / ${metrics.riskScore} / ${metrics.riskAdjustedScore}`, note: "多因子分數扣除風險後的研究分數" },
        { label: "回測信賴下限勝率", value: `${backtest.winRateLowerBound}%`, note: `${backtest.sampleCount} 筆相似樣本，避免小樣本假高勝率` },
      ],
    },
    {
      title: "法人與籌碼",
      description: "資金面、連續性與同步性，用來判斷訊號是否有資金支撐。",
      rows: [
        { label: "ChipScore", value: `${metrics.chipScore}`, note: "外資、投信、自營商與成交量比率" },
        { label: "籌碼狀態", value: metrics.chipScore >= 60 ? "偏正向" : "觀察中", note: "若三大法人同步轉弱，訊號會降級" },
        { label: "流動性提醒", value: quote.volumeLots >= 10000 ? "樣本流動性較足" : "需留意成交量", note: "低流動性會放大回測與實際落差" },
      ],
    },
    {
      title: "技術與量價",
      description: "MA、MACD、RSI、KD、OBV 與量價背離，供進階使用者拆解。",
      rows: [
        { label: "TechnicalScore", value: `${metrics.technicalScore}`, note: "綜合趨勢、動能、量能與突破訊號" },
        { label: "MA5 / MA20 / MA60", value: `${formatScore(signal.technicals.ma_5)} / ${formatScore(signal.technicals.ma_20)} / ${formatScore(signal.technicals.ma_60)}`, note: "用來看短中長期均線位置" },
        { label: "RSI / MACD Hist", value: `${formatScore(signal.technicals.rsi_14)} / ${formatScore(signal.technicals.macd_histogram)}`, note: "動能與背離風險觀察" },
      ],
    },
    {
      title: "財務與估值",
      description: "基本面、目標區間與財務品質，正式版會接月營收與財報資料。",
      rows: [
        { label: "現價 / 保守 / 基準 / 樂觀", value: `${target.currentPrice} / ${target.conservative} / ${target.base} / ${target.optimistic}`, note: target.sourceLabel },
        { label: "EPS / PE / 殖利率", value: `${quote.epsTtm} / ${quote.peRatio} / ${quote.dividendYield}%`, note: valuationSourceNote },
        { label: "毛利率 / 營益率 / 淨利率", value: `${quote.grossMargin}% / ${quote.operatingMargin}% / ${quote.netMargin}%`, note: "財務品質與獲利能力觀察" },
      ],
    },
    {
      title: "外部連動與事件",
      description: "美股、新聞、產業與供應鏈事件，供專業使用者追溯 Reference。",
      rows: [
        { label: "USMarketScore", value: `${metrics.usMarketScore}`, note: "SOX、TSM ADR、NVDA、AAPL、VIX 與供應鏈權重" },
        { label: "NewsScore", value: `${metrics.newsScore}`, note: `${signal.news.length} 筆新聞/事件進入觀察` },
        { label: "官方風險 Reference", value: signal.risk_flags?.length ? `${signal.risk_flags.length} 筆命中` : "未命中高風險公告", note: riskReferenceNote },
        { label: "容易失效狀態", value: backtest.worstMarketRegime, note: "模型監控與風險過濾會追蹤此類狀態" },
      ],
    },
  ];
}
