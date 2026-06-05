import type { PredictionSignal, StockInstrument } from "@/lib/api";
import { buildStockMetrics } from "@/lib/view-model";

export type MajorIndustryCategory = {
  id: string;
  name: string;
  shortName: string;
  beginnerSummary: string;
  defaultSubcategories: string[];
};

export type StockIndustryClassification = {
  major: MajorIndustryCategory;
  subcategories: string[];
  themeWeights: Array<{ label: string; percent: number; note: string }>;
  reference: string;
};

export type IndustryStockItem = {
  symbol: string;
  name: string;
  score: number;
  riskScore: number;
  sector: string | null;
};

export type RankedSubIndustry = {
  name: string;
  score: number;
  stockCount: number;
  stocks: IndustryStockItem[];
};

export type RankedMajorIndustry = {
  category: MajorIndustryCategory;
  score: number;
  stockCount: number;
  averageRisk: number;
  trend: string;
  reason: string;
  subcategories: RankedSubIndustry[];
  topStocks: IndustryStockItem[];
};

const majorCategories: MajorIndustryCategory[] = [
  {
    id: "semiconductor-ai",
    name: "半導體與 AI 基建",
    shortName: "半導體",
    beginnerSummary: "晶片、製程、封裝、記憶體與 AI 算力基礎設施。",
    defaultSubcategories: ["晶圓代工", "IC 設計", "封測", "先進封裝", "半導體設備", "半導體材料", "記憶體", "矽智財 IP"],
  },
  {
    id: "ai-server-computing",
    name: "AI 伺服器與電腦週邊",
    shortName: "AI 伺服器",
    beginnerSummary: "伺服器、資料中心、電源、散熱與整機代工。",
    defaultSubcategories: ["AI Server", "伺服器 ODM", "GPU 板卡", "電源", "散熱", "水冷", "工業電腦", "PC 週邊"],
  },
  {
    id: "pcb-components",
    name: "PCB 與電子零組件",
    shortName: "PCB 零組件",
    beginnerSummary: "電路板、載板、材料、連接器與被動元件。",
    defaultSubcategories: ["PCB", "CCL", "ABF 載板", "HDI", "軟板", "連接器", "被動元件", "MLCC"],
  },
  {
    id: "communications-cloud",
    name: "通訊網路與雲端",
    shortName: "網通雲端",
    beginnerSummary: "網通設備、光通訊、資安、雲端與資料中心連線。",
    defaultSubcategories: ["網通", "交換器", "路由器", "低軌衛星", "光通訊", "資安", "雲端服務", "系統整合"],
  },
  {
    id: "optics-display",
    name: "光電與顯示",
    shortName: "光電",
    beginnerSummary: "面板、LED、鏡頭與光學元件。",
    defaultSubcategories: ["面板", "Mini LED", "Micro LED", "LED", "光學鏡頭", "光學元件", "投影", "觸控"],
  },
  {
    id: "machinery-robotics",
    name: "電機機械與機器人",
    shortName: "機器人重電",
    beginnerSummary: "馬達、重電、工具機、自動化與機器人供應鏈。",
    defaultSubcategories: ["馬達", "重電", "變壓器", "工具機", "自動化設備", "機器人", "電動化設備", "線纜"],
  },
  {
    id: "ev-automotive",
    name: "車用與電動車",
    shortName: "車用",
    beginnerSummary: "車用電子、電池、充電、車燈與汽車零組件。",
    defaultSubcategories: ["車用電子", "ADAS", "電池材料", "充電樁", "電動巴士", "車用零組件", "輪胎", "車燈"],
  },
  {
    id: "financial-defensive",
    name: "金融與防禦收益",
    shortName: "金融防禦",
    beginnerSummary: "金控、銀行、保險、證券與較防禦的收益型資產。",
    defaultSubcategories: ["金控", "銀行", "保險", "證券", "租賃", "高股息", "防禦型金融"],
  },
  {
    id: "shipping-logistics",
    name: "航運與物流",
    shortName: "運輸物流",
    beginnerSummary: "貨櫃、散裝、航空、貨運與倉儲物流。",
    defaultSubcategories: ["貨櫃航運", "散裝航運", "航空", "空運貨運", "陸運物流", "倉儲", "港埠服務"],
  },
  {
    id: "materials-cyclical",
    name: "原物料與景氣循環",
    shortName: "原物料",
    beginnerSummary: "鋼鐵、水泥、塑化、橡膠、造紙與基礎化學。",
    defaultSubcategories: ["鋼鐵", "水泥", "塑化", "化纖", "橡膠", "玻璃陶瓷", "造紙", "基礎化學"],
  },
  {
    id: "construction-assets",
    name: "建材營造與資產",
    shortName: "營建資產",
    beginnerSummary: "建設、營造、工程、商辦與土地資產。",
    defaultSubcategories: ["建設", "營造", "建材", "工程", "商辦資產", "土地開發", "租賃收益"],
  },
  {
    id: "consumer-domestic",
    name: "消費與內需",
    shortName: "消費內需",
    beginnerSummary: "食品、零售、百貨、餐飲、觀光與生活消費。",
    defaultSubcategories: ["食品", "飲料", "零售通路", "百貨", "餐飲", "觀光", "飯店", "文創", "遊戲"],
  },
  {
    id: "biotech-medical",
    name: "生技醫療",
    shortName: "生技醫療",
    beginnerSummary: "製藥、醫材、檢測、保健與醫療服務。",
    defaultSubcategories: ["製藥", "醫材", "CDMO", "保健食品", "檢測", "醫療通路", "再生醫療"],
  },
  {
    id: "green-utilities",
    name: "綠能與公用事業",
    shortName: "綠能公用",
    beginnerSummary: "太陽能、風電、儲能、油電燃氣與環保。",
    defaultSubcategories: ["太陽能", "風電", "儲能", "電力設備", "油電燃氣", "環保", "水資源", "廢棄物處理"],
  },
  {
    id: "lifestyle-leisure",
    name: "運動休閒與居家生活",
    shortName: "休閒居家",
    beginnerSummary: "自行車、健身、運動用品、家具、家電與居家用品。",
    defaultSubcategories: ["自行車", "健身器材", "運動用品", "家具", "家電", "居家用品"],
  },
  {
    id: "other-general",
    name: "其他與綜合",
    shortName: "其他",
    beginnerSummary: "跨產業、控股或暫時無法明確歸類的股票。",
    defaultSubcategories: ["控股", "綜合型企業", "題材不明確", "跨產業公司"],
  },
];

const majorById = new Map(majorCategories.map((category) => [category.id, category]));

const explicitStockMap: Record<string, { majorId: string; subcategories: string[] }> = {
  "2330": { majorId: "semiconductor-ai", subcategories: ["晶圓代工", "先進製程", "AI/HPC"] },
  "2303": { majorId: "semiconductor-ai", subcategories: ["晶圓代工", "成熟製程"] },
  "2454": { majorId: "semiconductor-ai", subcategories: ["IC 設計", "Edge AI"] },
  "3035": { majorId: "semiconductor-ai", subcategories: ["ASIC", "晶片設計服務", "AI/HPC"] },
  "3661": { majorId: "semiconductor-ai", subcategories: ["ASIC", "HPC", "矽智財 IP"] },
  "3711": { majorId: "semiconductor-ai", subcategories: ["封測", "先進封裝"] },
  "6147": { majorId: "semiconductor-ai", subcategories: ["封測", "驅動 IC"] },
  "6223": { majorId: "semiconductor-ai", subcategories: ["測試介面", "探針卡"] },
  "6488": { majorId: "semiconductor-ai", subcategories: ["半導體材料", "矽晶圓"] },
  "2408": { majorId: "semiconductor-ai", subcategories: ["記憶體", "DRAM"] },
  "2379": { majorId: "semiconductor-ai", subcategories: ["IC 設計", "網通 IC"] },
  "2458": { majorId: "semiconductor-ai", subcategories: ["IC 設計", "MCU", "觸控 IC"] },
  "3260": { majorId: "semiconductor-ai", subcategories: ["記憶體模組", "Edge AI", "儲存"] },
  "5274": { majorId: "semiconductor-ai", subcategories: ["BMC", "伺服器管理晶片", "資安晶片"] },
  "6510": { majorId: "semiconductor-ai", subcategories: ["測試介面", "測試板", "TPU 測試"] },
  "2382": { majorId: "ai-server-computing", subcategories: ["AI Server", "伺服器 ODM", "雲端資料中心"] },
  "3231": { majorId: "ai-server-computing", subcategories: ["AI Server", "伺服器 ODM", "雲端資料中心"] },
  "6669": { majorId: "ai-server-computing", subcategories: ["AI Server", "伺服器 ODM", "資料中心"] },
  "2317": { majorId: "ai-server-computing", subcategories: ["EMS", "伺服器", "電動車"] },
  "2324": { majorId: "ai-server-computing", subcategories: ["AI Server", "伺服器 ODM", "液冷模組"] },
  "2356": { majorId: "ai-server-computing", subcategories: ["AI Server", "伺服器 ODM", "液冷"] },
  "4938": { majorId: "ai-server-computing", subcategories: ["EMS", "PC 週邊"] },
  "2357": { majorId: "ai-server-computing", subcategories: ["AI PC", "PC 週邊", "品牌硬體"] },
  "2376": { majorId: "ai-server-computing", subcategories: ["AI PC", "主機板", "GPU 板卡"] },
  "2377": { majorId: "ai-server-computing", subcategories: ["AI PC", "Edge AI", "Server"] },
  "3515": { majorId: "ai-server-computing", subcategories: ["AI PC", "主機板", "Edge AI"] },
  "2395": { majorId: "ai-server-computing", subcategories: ["工業電腦", "邊緣運算"] },
  "2308": { majorId: "ai-server-computing", subcategories: ["電源", "資料中心", "散熱"] },
  "3017": { majorId: "ai-server-computing", subcategories: ["散熱", "水冷", "高功耗平台"] },
  "3324": { majorId: "ai-server-computing", subcategories: ["散熱", "水冷", "高功耗平台"] },
  "2421": { majorId: "ai-server-computing", subcategories: ["散熱", "風扇"] },
  "3653": { majorId: "ai-server-computing", subcategories: ["散熱", "MCL", "均熱片"] },
  "8210": { majorId: "ai-server-computing", subcategories: ["機櫃", "整櫃", "Busbar"] },
  "2059": { majorId: "machinery-robotics", subcategories: ["導軌", "伺服器機構件", "AI Server"] },
  "2345": { majorId: "communications-cloud", subcategories: ["交換器", "高速網通", "資料中心"] },
  "2455": { majorId: "communications-cloud", subcategories: ["光通訊", "CPO", "PA"] },
  "3081": { majorId: "communications-cloud", subcategories: ["光通訊", "雷射元件", "CPO"] },
  "3710": { majorId: "communications-cloud", subcategories: ["光通訊", "光收發模組", "高速互連"] },
  "4971": { majorId: "communications-cloud", subcategories: ["光通訊", "磊晶", "CPO"] },
  "4991": { majorId: "communications-cloud", subcategories: ["光通訊", "砷化鎵", "CPO"] },
  "6197": { majorId: "communications-cloud", subcategories: ["高速連接器", "光互連", "資料中心"] },
  "6442": { majorId: "communications-cloud", subcategories: ["光通訊", "CPO", "資料中心"] },
  "4904": { majorId: "communications-cloud", subcategories: ["電信服務", "通信網路"] },
  "2383": { majorId: "pcb-components", subcategories: ["CCL", "高速材料", "AI 伺服器供應鏈"] },
  "3037": { majorId: "pcb-components", subcategories: ["ABF 載板", "PCB", "HDI"] },
  "3189": { majorId: "pcb-components", subcategories: ["ABF 載板", "PCB", "先進封裝"] },
  "3665": { majorId: "pcb-components", subcategories: ["高速連接器", "HVDC", "CPO"] },
  "6274": { majorId: "pcb-components", subcategories: ["CCL", "高速材料", "Low-Dk"] },
  "8046": { majorId: "pcb-components", subcategories: ["ABF 載板", "PCB"] },
  "2368": { majorId: "pcb-components", subcategories: ["PCB", "伺服器板"] },
  "3008": { majorId: "optics-display", subcategories: ["光學鏡頭", "光學元件"] },
  "8069": { majorId: "optics-display", subcategories: ["電子紙", "顯示"] },
  "1590": { majorId: "machinery-robotics", subcategories: ["機器人", "氣動元件", "自動化設備"] },
  "2049": { majorId: "machinery-robotics", subcategories: ["機器人", "線性傳動", "自動化設備"] },
  "2359": { majorId: "machinery-robotics", subcategories: ["機器人", "AI 視覺", "自動化設備"] },
  "1504": { majorId: "machinery-robotics", subcategories: ["馬達", "電動化設備", "重電"] },
  "1513": { majorId: "machinery-robotics", subcategories: ["重電", "電網升級", "變壓器"] },
  "1519": { majorId: "machinery-robotics", subcategories: ["重電", "變壓器", "電網升級"] },
  "1605": { majorId: "machinery-robotics", subcategories: ["線纜", "電線電纜", "電網"] },
  "2207": { majorId: "ev-automotive", subcategories: ["汽車銷售", "車用"] },
  "2634": { majorId: "ev-automotive", subcategories: ["航太", "國防", "車用零組件"] },
  "2880": { majorId: "financial-defensive", subcategories: ["金控", "銀行"] },
  "2881": { majorId: "financial-defensive", subcategories: ["金控", "保險"] },
  "2882": { majorId: "financial-defensive", subcategories: ["金控", "保險"] },
  "2884": { majorId: "financial-defensive", subcategories: ["金控", "銀行"] },
  "2885": { majorId: "financial-defensive", subcategories: ["金控", "證券"] },
  "2886": { majorId: "financial-defensive", subcategories: ["金控", "銀行"] },
  "2891": { majorId: "financial-defensive", subcategories: ["金控", "銀行"] },
  "5871": { majorId: "financial-defensive", subcategories: ["租賃", "金融服務"] },
  "5876": { majorId: "financial-defensive", subcategories: ["銀行", "防禦型金融"] },
  "5880": { majorId: "financial-defensive", subcategories: ["金控", "銀行"] },
  "2603": { majorId: "shipping-logistics", subcategories: ["貨櫃航運", "景氣循環"] },
  "2609": { majorId: "shipping-logistics", subcategories: ["貨櫃航運", "景氣循環"] },
  "2615": { majorId: "shipping-logistics", subcategories: ["貨櫃航運", "景氣循環"] },
  "2610": { majorId: "shipping-logistics", subcategories: ["航空", "旅運復甦"] },
  "2618": { majorId: "shipping-logistics", subcategories: ["航空", "旅運復甦"] },
  "1101": { majorId: "materials-cyclical", subcategories: ["水泥", "建材"] },
  "1102": { majorId: "materials-cyclical", subcategories: ["水泥", "建材"] },
  "1301": { majorId: "materials-cyclical", subcategories: ["塑化", "景氣循環"] },
  "1303": { majorId: "materials-cyclical", subcategories: ["塑化", "化工材料"] },
  "1326": { majorId: "materials-cyclical", subcategories: ["塑化", "化纖"] },
  "2002": { majorId: "materials-cyclical", subcategories: ["鋼鐵", "景氣循環"] },
  "6505": { majorId: "green-utilities", subcategories: ["油電燃氣", "能源", "油品價差"] },
  "1216": { majorId: "consumer-domestic", subcategories: ["食品", "零售通路", "內需防禦"] },
  "2912": { majorId: "consumer-domestic", subcategories: ["零售通路", "百貨", "內需防禦"] },
  "6446": { majorId: "biotech-medical", subcategories: ["製藥", "新藥"] },
};

const fallbackRules: Array<{ pattern: RegExp; majorId: string; subcategories: string[] }> = [
  { pattern: /半導體|IC|晶片|封裝|測試|矽晶圓|記憶體/, majorId: "semiconductor-ai", subcategories: ["半導體", "IC 設計", "封測"] },
  { pattern: /電腦|週邊|伺服器|雲端|資料中心|電子代工|電源|散熱/, majorId: "ai-server-computing", subcategories: ["AI Server", "伺服器 ODM", "PC 週邊"] },
  { pattern: /PCB|CCL|載板|ABF|電子零組件|被動元件|連接器/, majorId: "pcb-components", subcategories: ["PCB", "電子零組件", "連接器"] },
  { pattern: /通信|網路|網通|資訊服務|數位雲端|資安/, majorId: "communications-cloud", subcategories: ["網通", "雲端服務", "系統整合"] },
  { pattern: /光電|面板|LED|鏡頭|光學/, majorId: "optics-display", subcategories: ["光電", "光學元件", "顯示"] },
  { pattern: /電機|機械|自動化|機器人|重電|電線|電纜|變壓器/, majorId: "machinery-robotics", subcategories: ["電機機械", "自動化設備", "重電"] },
  { pattern: /汽車|車用|電動車|輪胎/, majorId: "ev-automotive", subcategories: ["車用", "車用零組件", "電動車"] },
  { pattern: /金融|銀行|金控|保險|證券|租賃/, majorId: "financial-defensive", subcategories: ["金控", "銀行", "防禦型金融"] },
  { pattern: /航運|航空|貨櫃|運輸|物流|倉儲/, majorId: "shipping-logistics", subcategories: ["貨櫃航運", "航空", "物流"] },
  { pattern: /水泥|塑膠|鋼鐵|化學|玻璃|陶瓷|造紙|橡膠|原物料/, majorId: "materials-cyclical", subcategories: ["景氣循環", "基礎材料", "原物料報價"] },
  { pattern: /建材|營造|建設|工程/, majorId: "construction-assets", subcategories: ["建材營造", "工程", "資產"] },
  { pattern: /食品|飲料|百貨|觀光|餐飲|零售|文創|遊戲/, majorId: "consumer-domestic", subcategories: ["內需防禦", "零售通路", "消費"] },
  { pattern: /生技|醫療|製藥|醫材/, majorId: "biotech-medical", subcategories: ["製藥", "醫材", "生技醫療"] },
  { pattern: /綠能|油電|燃氣|能源|環保|太陽能|風電|儲能/, majorId: "green-utilities", subcategories: ["綠能", "油電燃氣", "公用事業"] },
  { pattern: /運動|休閒|居家|生活|自行車|家具|家電/, majorId: "lifestyle-leisure", subcategories: ["運動休閒", "居家用品", "生活消費"] },
];

export function getMajorIndustryCategories(): MajorIndustryCategory[] {
  return majorCategories;
}

export function classifyInstrument(input: Pick<StockInstrument, "symbol" | "name" | "sector">): StockIndustryClassification {
  const explicit = explicitStockMap[input.symbol];
  if (explicit) {
    return buildClassification(input, explicit.majorId, explicit.subcategories, "代號對應供應鏈分類");
  }

  const text = `${input.symbol} ${input.name} ${input.sector ?? ""}`;
  const rule = fallbackRules.find((item) => item.pattern.test(text));
  if (rule) return buildClassification(input, rule.majorId, rule.subcategories, "官方產業與關鍵字分類");
  return buildClassification(input, "other-general", ["跨產業公司", input.sector ?? "題材不明確"], "暫以官方產業歸入其他");
}

export function classifySignal(signal: PredictionSignal): StockIndustryClassification {
  return classifyInstrument({
    symbol: signal.symbol,
    name: signal.name,
    sector: signal.sector ?? null,
  });
}

export function buildIndustryRankings(signals: PredictionSignal[]): RankedMajorIndustry[] {
  const majorBuckets = new Map<string, Array<{ signal: PredictionSignal; classification: StockIndustryClassification; score: number; risk: number }>>();

  signals.forEach((signal) => {
    const classification = classifySignal(signal);
    const score = buildSignalIndustryScore(signal);
    const metrics = buildStockMetrics(signal);
    const bucket = majorBuckets.get(classification.major.id) ?? [];
    bucket.push({ signal, classification, score, risk: metrics.riskScore });
    majorBuckets.set(classification.major.id, bucket);
  });

  return Array.from(majorBuckets.entries())
    .map(([majorId, rows]) => {
      const category = majorById.get(majorId) ?? majorCategories.at(-1)!;
      const topRows = [...rows].sort((left, right) => right.score - left.score);
      const topStocks = topRows.slice(0, 8).map(toIndustryStockItem);
      const score = calculateBucketScore(rows.map((row) => row.score));
      const averageRisk = Math.round(rows.reduce((sum, row) => sum + row.risk, 0) / Math.max(1, rows.length));
      const subcategories = buildSubIndustryRankings(rows);
      return {
        category,
        score,
        stockCount: rows.length,
        averageRisk,
        trend: buildTrendLabel(score, averageRisk),
        reason: buildIndustryReason(category, score, averageRisk, subcategories[0]?.name),
        subcategories,
        topStocks,
      } satisfies RankedMajorIndustry;
    })
    .sort((left, right) => {
      const scoreDelta = right.score - left.score;
      if (scoreDelta !== 0) return scoreDelta;
      return left.averageRisk - right.averageRisk;
    });
}

export function buildSignalIndustryScore(signal: PredictionSignal): number {
  const metrics = buildStockMetrics(signal);
  const classification = classifySignal(signal);
  const categoryBreadthBoost = Math.min(4, classification.subcategories.length);
  return Math.round(Math.max(0, Math.min(100,
    metrics.technicalScore * 0.2
    + metrics.chipScore * 0.2
    + metrics.fundamentalScore * 0.18
    + metrics.usMarketScore * 0.1
    + metrics.newsScore * 0.07
    + metrics.riskAdjustedScore * 0.15
    + Math.round(signal.confidence * 100) * 0.06
    + (100 - metrics.riskScore) * 0.04
    + categoryBreadthBoost,
  )));
}

function buildClassification(
  input: Pick<StockInstrument, "symbol" | "name" | "sector">,
  majorId: string,
  subcategories: string[],
  reference: string,
): StockIndustryClassification {
  const major = majorById.get(majorId) ?? majorCategories.at(-1)!;
  const uniqueSubcategories = Array.from(new Set(subcategories.filter(Boolean))).slice(0, 5);
  return {
    major,
    subcategories: uniqueSubcategories.length ? uniqueSubcategories : major.defaultSubcategories.slice(0, 3),
    themeWeights: buildThemeWeights(major, uniqueSubcategories.length ? uniqueSubcategories : major.defaultSubcategories.slice(0, 3), input.sector),
    reference,
  };
}

function buildThemeWeights(major: MajorIndustryCategory, subcategories: string[], sector: string | null): StockIndustryClassification["themeWeights"] {
  const primary = subcategories[0] ?? major.shortName;
  const secondary = subcategories[1] ?? major.defaultSubcategories[1] ?? "供應鏈位置";
  const tertiary = subcategories[2] ?? sector ?? "官方產業";
  const rows = [
    { label: primary, raw: 38, note: `主要小分類：${primary}` },
    { label: secondary, raw: 26, note: `第二層題材：${secondary}` },
    { label: tertiary, raw: 20, note: `由官方產業、名稱或供應鏈關鍵字推估：${tertiary}` },
    { label: "多因子分數", raw: 16, note: "籌碼、技術、營收、新聞、風險與市場狀態會再決定排序" },
  ];
  const total = rows.reduce((sum, row) => sum + row.raw, 0);
  return rows.map((row) => ({
    label: row.label,
    note: row.note,
    percent: Math.round((row.raw / total) * 100),
  }));
}

function buildSubIndustryRankings(
  rows: Array<{ signal: PredictionSignal; classification: StockIndustryClassification; score: number; risk: number }>,
): RankedSubIndustry[] {
  const buckets = new Map<string, Array<{ signal: PredictionSignal; score: number; risk: number }>>();
  rows.forEach((row) => {
    row.classification.subcategories.forEach((subcategory) => {
      const bucket = buckets.get(subcategory) ?? [];
      bucket.push({ signal: row.signal, score: row.score, risk: row.risk });
      buckets.set(subcategory, bucket);
    });
  });

  return Array.from(buckets.entries())
    .map(([name, bucketRows]) => ({
      name,
      score: calculateBucketScore(bucketRows.map((row) => row.score)),
      stockCount: bucketRows.length,
      stocks: [...bucketRows].sort((left, right) => right.score - left.score).slice(0, 6).map(toIndustryStockItem),
    }))
    .sort((left, right) => right.score - left.score || right.stockCount - left.stockCount);
}

function calculateBucketScore(scores: number[]): number {
  const sorted = [...scores].sort((left, right) => right - left);
  const topAverage = average(sorted.slice(0, 5));
  const allAverage = average(sorted);
  const best = sorted[0] ?? 50;
  return Math.round(Math.max(0, Math.min(100, topAverage * 0.55 + allAverage * 0.3 + best * 0.15)));
}

function average(values: number[]): number {
  if (values.length === 0) return 50;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function toIndustryStockItem(row: { signal: PredictionSignal; score: number; risk: number }): IndustryStockItem {
  return {
    symbol: row.signal.symbol,
    name: row.signal.name,
    score: Math.round(row.score),
    riskScore: Math.round(row.risk),
    sector: row.signal.sector ?? null,
  };
}

function buildTrendLabel(score: number, risk: number): string {
  if (score >= 70 && risk <= 50) return "強勢且風險可控";
  if (score >= 66) return "熱度偏強";
  if (score >= 60) return "中性偏強";
  if (score >= 54) return "觀察中";
  return "暫時偏弱";
}

function buildIndustryReason(category: MajorIndustryCategory, score: number, risk: number, topSubcategory?: string): string {
  const heat = score >= 70 ? "目前分數排在前段" : score >= 60 ? "目前分數在中上區間" : "目前分數仍需等待更多共振";
  const riskText = risk >= 55 ? "但風險係數偏高，適合降低部位假設。" : "且平均風險尚可控。";
  const subText = topSubcategory ? `最強小分類是 ${topSubcategory}。` : "";
  return `${category.beginnerSummary}${heat}，${riskText}${subText}`;
}
