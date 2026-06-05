import type { AnalystTargetPrice, PredictionSignal, StockInstrument } from "@/lib/api";

type BrokerResearchEvent = PredictionSignal["news"][number] & {
  report_id: string;
  report_title: string;
  broker: string;
  themes: string[];
  related_industry?: string;
};

type BrokerTargetInput = {
  symbol: string;
  target: number;
  high?: number;
  low?: number;
  broker: string;
  reportTitle: string;
  publishedAt: string;
  rating: "正向評等" | "持有評等" | "未評等";
  confidence: number;
};

const reportSourceNote = "本機匯入券商研究報告；正式引用與轉載需依原報告授權與公司內部權限控管。";

export const brokerResearchSymbols = [
  "2059", "2308", "2317", "2324", "2330", "2356", "2357", "2376", "2377", "2379",
  "2382", "2383", "2454", "2455", "2458", "3017", "3037", "3081", "3189", "3324",
  "3515", "3653", "3665", "3710", "4971", "4991", "5274", "6197", "6223", "6274",
  "6442", "6510", "6669", "8069", "8210",
];

const brokerResearchEvents: BrokerResearchEvent[] = [
  {
    report_id: "cathay-ai-factory-20260505",
    report_title: "AI factory 到平台生態系閉環，GPU、ASIC 攜手並進",
    broker: "國泰證期研究部",
    source: "國泰證期研究部研究報告",
    published_at: "2026-05-05T08:00:00+08:00",
    title: "國泰：AI factory 與 GPU/ASIC 並進，台積電、聯發科與 TPU 測試鏈進入重點追蹤",
    summary: "報告把 AI factory 視為長期資本循環，認為 GPU 與 ASIC/TPU 互補，並把台積電、聯發科、旺矽、精測列為台灣供應鏈觀察重點。",
    sentiment: "positive",
    impact_score: 0.28,
    related_symbols: ["2330", "2454", "6223", "6510", "NVDA", "GOOG", "AVGO"],
    event_type: "broker_research",
    related_industry: "AI factory / ASIC / TPU",
    themes: ["AI factory", "ASIC", "TPU", "先進製程", "測試介面"],
    linkage_reason: "券商報告指出 AI 資料中心與 ASIC/TPU 需求會影響先進製程、IC 設計與測試供應鏈。",
  },
  {
    report_id: "yuanta-computex-20260603",
    report_title: "COMPUTEX 2026：AI 代理趨勢成形，規格升級持續",
    broker: "元大投顧",
    source: "元大投顧研究報告",
    published_at: "2026-06-03T08:00:00+08:00",
    title: "元大：Computex 2026 主軸為 AI agent，伺服器、散熱、電源、連接器、PCB/CCL 受規格升級影響",
    summary: "報告整理 AI PC、VR200/Rubin、AMD/ASIC、HVDC、光通訊與 PCB/CCL 規格升級，將多個台灣供應鏈族群納入研究觀察。",
    sentiment: "positive",
    impact_score: 0.24,
    related_symbols: ["2357", "2376", "2377", "3515", "8210", "3653", "3017", "3324", "2317", "2382", "6669", "2356", "2324", "2308", "2059", "3665", "3037", "3189", "2383", "6274", "3081", "2455", "4991", "4971", "8069", "2454", "2379", "2458"],
    event_type: "broker_research",
    related_industry: "COMPUTEX 2026 / AI infrastructure",
    themes: ["AI PC", "AI 伺服器", "散熱", "電源", "連接器", "PCB/CCL", "光通訊"],
    linkage_reason: "Computex 規格升級把 AI 從晶片延伸到整櫃、電力、散熱與互連零組件。",
  },
  {
    report_id: "yuanta-ai-pc-20260603",
    report_title: "COMPUTEX 2026：RTX Spark / AI PC",
    broker: "元大投顧",
    source: "元大投顧研究報告",
    published_at: "2026-06-03T08:15:00+08:00",
    title: "元大：RTX Spark 重新定義 AI PC，PC/NB 品牌與聯發科合作鏈成為觀察題材",
    summary: "報告指出 RTX Spark 搭載 Blackwell RTX GPU 與 Grace CPU，AI PC 可能在 2027 年帶動換機與地端 agent 應用，相關品牌與 IC 設計鏈進入追蹤。",
    sentiment: "positive",
    impact_score: 0.18,
    related_symbols: ["2357", "2376", "2377", "3515", "2454", "2330"],
    event_type: "broker_research",
    related_industry: "AI PC / RTX Spark",
    themes: ["AI PC", "RTX Spark", "Edge AI"],
    linkage_reason: "AI agent 從雲端延伸到本地端裝置，可能改變 NB/PC 規格與單價結構。",
  },
  {
    report_id: "yuanta-server-rubin-20260603",
    report_title: "COMPUTEX 2026：VR200 / Rubin 供應鏈",
    broker: "元大投顧",
    source: "元大投顧研究報告",
    published_at: "2026-06-03T08:20:00+08:00",
    title: "元大：VR200、Rubin 與整櫃架構推升 ODM、散熱、電源與導軌供應鏈重要性",
    summary: "報告提到新一代 AI server 與 rack-scale 系統讓 ODM、散熱、電源、導軌與機殼設計同步升級，受惠不只集中在單一 AI 股。",
    sentiment: "positive",
    impact_score: 0.22,
    related_symbols: ["8210", "3653", "3017", "3324", "2317", "2382", "6669", "2356", "2324", "2308", "2059"],
    event_type: "broker_research",
    related_industry: "AI server / rack-scale",
    themes: ["AI Server", "Rubin", "液冷", "HVDC", "導軌", "整櫃"],
    linkage_reason: "AI 伺服器升級讓機櫃、散熱、電力與 ODM 協同設計成為分數來源。",
  },
  {
    report_id: "yuanta-interconnect-pcb-20260603",
    report_title: "COMPUTEX 2026：高速互連、光通訊、PCB/CCL",
    broker: "元大投顧",
    source: "元大投顧研究報告",
    published_at: "2026-06-03T08:25:00+08:00",
    title: "元大：448G、1.6T、CPO 與高階板材升級，連接器、光通訊、載板與 CCL 進入觀察",
    summary: "報告把傳輸與互連視為 AI 基礎設施的瓶頸之一，並提到高速連接器、光通訊、ABF 載板、PCB 與 CCL 材料等升級方向。",
    sentiment: "positive",
    impact_score: 0.23,
    related_symbols: ["3665", "3037", "3189", "2383", "6274", "3081", "2455", "4991", "4971", "6442", "2454", "6669", "3710", "6197"],
    event_type: "broker_research",
    related_industry: "高速互連 / 光通訊 / PCB/CCL",
    themes: ["448G", "1.6T", "CPO", "ABF", "CCL", "光通訊"],
    linkage_reason: "頻寬與功耗瓶頸讓高速互連、光通訊與高階板材成為 AI 基建分支題材。",
  },
  {
    report_id: "ctbc-computex-20260605",
    report_title: "COMPUTEX Taipei 2026 評析",
    broker: "中信投顧",
    source: "中信投顧研究報告",
    published_at: "2026-06-05T08:00:00+08:00",
    title: "中信：Computex 展示 AI Together，從鴻海、英業達、仁寶到微星皆展出 AI factory / edge AI 解決方案",
    summary: "報告整理 Computex 展出內容，包括 Vera Rubin NVL72、AI factory、Edge AI、BMC、機櫃、液冷與互連，作為公司題材與供應鏈 Reference。",
    sentiment: "positive",
    impact_score: 0.2,
    related_symbols: ["2317", "2324", "2356", "2377", "5274", "8210", "3324", "3653", "3665", "2454", "3260", "8069"],
    event_type: "broker_research",
    related_industry: "COMPUTEX 2026 company showcases",
    themes: ["Vera Rubin", "AI factory", "Edge AI", "BMC", "液冷", "互連"],
    linkage_reason: "公司展出內容可補強個股頁的『這家公司在做什麼』與題材比例。",
  },
  {
    report_id: "hoku-nvidia-gtc-20260603",
    report_title: "NVIDIA GTC Taipei 2026 Keynote",
    broker: "合庫投顧",
    source: "合庫投顧研究報告",
    published_at: "2026-06-03T08:00:00+08:00",
    title: "合庫：NVIDIA GTC Taipei 強調 AI factory、Vera Rubin 與 tokenomics，長期基建趨勢延續",
    summary: "報告把 AI factory 視為未來 10 至 15 年的大型基礎建設，並提到 Vera Rubin 量產、異質運算與 AI PC 進展。",
    sentiment: "positive",
    impact_score: 0.21,
    related_symbols: ["NVDA", "2330", "2454", "2317", "2382", "3231", "6669", "2308", "3017", "3324", "3653", "2357", "2377"],
    event_type: "broker_research",
    related_industry: "NVIDIA GTC / AI factory",
    themes: ["AI factory", "Vera Rubin", "Tokenomics", "AI PC"],
    linkage_reason: "NVIDIA 平台演進會透過伺服器、散熱、電源、先進製程與 AI PC 鏈影響台股。",
  },
  {
    report_id: "fubon-marvell-20260602",
    report_title: "2026 Computex Marvell Keynote",
    broker: "富邦投顧",
    source: "富邦投顧研究報告",
    published_at: "2026-06-02T08:00:00+08:00",
    title: "富邦：Marvell Computex 指出 AI 資料中心瓶頸轉向 Connectivity 與光互連",
    summary: "報告聚焦 Scale-Across、Scale-Out、CPO、100T Ethernet switch 與 NVLink Fusion，將 AI 基建瓶頸從 compute/memory 延伸到 connectivity。",
    sentiment: "positive",
    impact_score: 0.19,
    related_symbols: ["MRVL", "AVGO", "NVDA", "2454", "6669", "3710", "6197", "3081", "2455", "4991", "4971", "6442", "2345"],
    event_type: "broker_research",
    related_industry: "Marvell / optical interconnect",
    themes: ["CPO", "光互連", "Ethernet switch", "NVLink Fusion"],
    linkage_reason: "Marvell 與 NVIDIA 的光互連與客製 ASIC 生態會影響網通、光通訊、CPO 與高速互連鏈。",
  },
];

const brokerTargets: BrokerTargetInput[] = [
  { symbol: "2330", target: 2710, broker: "國泰證期研究部", reportTitle: "AI factory 到平台生態系閉環，GPU、ASIC 攜手並進", publishedAt: "2026-05-05", rating: "正向評等", confidence: 0.72 },
  { symbol: "2454", target: 3200, broker: "國泰證期研究部", reportTitle: "AI factory 到平台生態系閉環，GPU、ASIC 攜手並進", publishedAt: "2026-05-05", rating: "正向評等", confidence: 0.72 },
  { symbol: "6223", target: 4785, broker: "國泰證期研究部", reportTitle: "AI factory 到平台生態系閉環，GPU、ASIC 攜手並進", publishedAt: "2026-05-05", rating: "未評等", confidence: 0.58 },
  { symbol: "6510", target: 4461, broker: "國泰證期研究部", reportTitle: "AI factory 到平台生態系閉環，GPU、ASIC 攜手並進", publishedAt: "2026-05-05", rating: "未評等", confidence: 0.58 },
  { symbol: "2357", target: 1200, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "2376", target: 325, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "2377", target: 160, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "3515", target: 280, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "8210", target: 1790, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "3653", target: 4270, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "3017", target: 3610, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "3324", target: 1505, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "2317", target: 282, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "持有評等", confidence: 0.64 },
  { symbol: "2382", target: 385, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "6669", target: 6600, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "2356", target: 48, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "持有評等", confidence: 0.64 },
  { symbol: "2324", target: 35, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "持有評等", confidence: 0.64 },
  { symbol: "2308", target: 2660, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "2059", target: 5700, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "3665", target: 2800, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "3037", target: 965, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "3189", target: 450, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "2383", target: 5100, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "6274", target: 1600, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "3081", target: 3400, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "持有評等", confidence: 0.64 },
  { symbol: "2455", target: 475, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "4991", target: 865, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "4971", target: 855, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "持有評等", confidence: 0.64 },
  { symbol: "8069", target: 305, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "2454", target: 3500, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "2379", target: 620, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "正向評等", confidence: 0.7 },
  { symbol: "2458", target: 135, broker: "元大投顧", reportTitle: "COMPUTEX 2026", publishedAt: "2026-06-03", rating: "持有評等", confidence: 0.64 },
];

export function getBrokerResearchEventsForInstrument(instrument: Pick<StockInstrument, "symbol" | "name" | "sector">): PredictionSignal["news"] {
  const symbol = instrument.symbol.toUpperCase();
  const sector = instrument.sector ?? "";
  const matches = brokerResearchEvents.filter((event) => {
    if (event.related_symbols.includes(symbol)) return true;
    if (/半導體|電子|電腦|週邊|通信|光電|資訊服務|數位雲端/.test(sector)) {
      return event.themes.some((theme) => /AI|COMPUTEX|CPO|光通訊|互連|Rubin|RTX/.test(theme));
    }
    return false;
  });

  return matches
    .map((event) => ({
      ...event,
      related_symbols: Array.from(new Set([...event.related_symbols, symbol])),
      summary: `${event.summary} Reference：${event.broker}《${event.report_title}》。${reportSourceNote}`,
    }))
    .sort((left, right) => Date.parse(right.published_at) - Date.parse(left.published_at))
    .slice(0, 6);
}

export function getBrokerAnalystTargetPrice(instrument: Pick<StockInstrument, "symbol">): AnalystTargetPrice | null {
  const candidates = brokerTargets
    .filter((target) => target.symbol === instrument.symbol)
    .sort((left, right) => Date.parse(right.publishedAt) - Date.parse(left.publishedAt) || right.confidence - left.confidence);
  const selected = candidates[0];
  if (!selected) return null;
  return {
    symbol: selected.symbol,
    currency: "TWD",
    target_price_mean: selected.target,
    target_price_high: selected.high ?? null,
    target_price_low: selected.low ?? null,
    analyst_count: 1,
    broker: selected.broker,
    rating: selected.rating,
    source: `${selected.broker}《${selected.reportTitle}》（本機匯入）`,
    source_type: "news_extracted",
    published_at: selected.publishedAt,
    confidence: selected.confidence,
    provider_status: "extracted",
    note: "外部法人目標價來自使用者提供並本機匯入的券商研究報告；不是即時共識，也不構成個人化投資建議。正式商用需確認報告授權、redisplay 權利與更新頻率。",
  };
}

export function getBrokerResearchScore(symbol: string): number | null {
  const directEvents = brokerResearchEvents.filter((event) => event.related_symbols.includes(symbol));
  const directTarget = brokerTargets.find((target) => target.symbol === symbol);
  if (!directEvents.length && !directTarget) return null;
  const eventScore = directEvents.reduce((max, event) => Math.max(max, 58 + event.impact_score * 100), 0);
  const targetScore = directTarget ? (directTarget.rating === "正向評等" ? 78 : 66) : 0;
  return Math.round(Math.min(92, Math.max(eventScore, targetScore)));
}
