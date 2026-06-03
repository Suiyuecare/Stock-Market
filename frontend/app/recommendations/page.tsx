import { AppShell } from "@/components/AppShell";
import { ScoreCard } from "@/components/ScoreCard";
import type { PredictionSignal } from "@/lib/api";
import { fetchTopProbabilityRanking } from "@/lib/api";
import { buildStockMetrics, sanitizeDisplayText, scoreTone } from "@/lib/view-model";

type RecommendationRow = {
  signal: PredictionSignal;
  score: number;
  reason: string;
  themes: string[];
  themeFit: number;
  metrics: ReturnType<typeof buildStockMetrics>;
};

const marketThemeProfiles: Record<string, { fit: number; themes: string[] }> = {
  "2330": { fit: 88, themes: ["半導體", "AI/HPC"] },
  "2454": { fit: 82, themes: ["IC 設計", "Edge AI"] },
  "3035": { fit: 80, themes: ["ASIC", "晶片設計服務"] },
  "3661": { fit: 84, themes: ["ASIC", "HPC"] },
  "2382": { fit: 86, themes: ["AI 伺服器", "雲端資料中心"] },
  "3231": { fit: 84, themes: ["AI 伺服器", "雲端資料中心"] },
  "6669": { fit: 86, themes: ["AI 伺服器", "雲端資料中心"] },
  "2317": { fit: 78, themes: ["EMS", "伺服器"] },
  "2308": { fit: 82, themes: ["電源管理", "資料中心"] },
  "2345": { fit: 80, themes: ["高速網通", "資料中心"] },
  "3017": { fit: 82, themes: ["散熱", "液冷"] },
  "3324": { fit: 80, themes: ["散熱", "液冷"] },
  "2383": { fit: 82, themes: ["CCL", "高速材料"] },
  "3037": { fit: 78, themes: ["ABF", "PCB/載板"] },
  "8046": { fit: 76, themes: ["ABF", "載板"] },
  "3711": { fit: 78, themes: ["封裝測試", "先進封裝"] },
  "1590": { fit: 82, themes: ["機器人", "氣動元件"] },
  "2049": { fit: 82, themes: ["機器人", "線性傳動"] },
  "2359": { fit: 78, themes: ["機器人", "AI 視覺"] },
  "1504": { fit: 76, themes: ["電機", "機器人/電動化"] },
  "1513": { fit: 78, themes: ["重電", "電網升級"] },
  "1519": { fit: 80, themes: ["重電", "變壓器"] },
  "1605": { fit: 72, themes: ["電線電纜", "電網"] },
  "2603": { fit: 74, themes: ["貨櫃航運", "景氣循環"] },
  "2609": { fit: 72, themes: ["貨櫃航運", "景氣循環"] },
  "2615": { fit: 70, themes: ["貨櫃航運", "景氣循環"] },
  "2618": { fit: 72, themes: ["航空", "旅運復甦"] },
  "2610": { fit: 70, themes: ["航空", "旅運復甦"] },
  "2634": { fit: 68, themes: ["航太", "國防"] },
  "2881": { fit: 78, themes: ["金融避險", "大型金控"] },
  "2882": { fit: 78, themes: ["金融避險", "大型金控"] },
  "2884": { fit: 76, themes: ["金融避險", "銀行"] },
  "2885": { fit: 74, themes: ["金融避險", "券商"] },
  "2886": { fit: 78, themes: ["金融避險", "銀行"] },
  "2891": { fit: 78, themes: ["金融避險", "大型金控"] },
  "5880": { fit: 76, themes: ["金融避險", "銀行"] },
  "5876": { fit: 74, themes: ["金融避險", "銀行"] },
  "1216": { fit: 70, themes: ["內需防禦", "食品通路"] },
  "2912": { fit: 72, themes: ["內需防禦", "零售通路"] },
  "2207": { fit: 70, themes: ["內需消費", "汽車"] },
  "6505": { fit: 68, themes: ["能源", "油品價差"] },
  "1301": { fit: 66, themes: ["塑化", "景氣循環"] },
  "1303": { fit: 66, themes: ["塑化", "景氣循環"] },
  "2002": { fit: 64, themes: ["鋼鐵", "景氣循環"] },
  "6446": { fit: 72, themes: ["生技醫療", "新藥"] },
};

const recommendationWeights = {
  probability: 18,
  riskAdjusted: 17,
  riskQuality: 14,
  themeFit: 12,
  chip: 11,
  technical: 10,
  fundamental: 8,
  news: 5,
  usMarket: 3,
  confidence: 2,
};

export default async function RecommendationsPage() {
  const ranking = await fetchTopProbabilityRanking();
  const recommendations = ranking.signals
    .map(buildRecommendation)
    .sort((left, right) => right.score - left.score)
    .slice(0, 20);
  const top = recommendations[0];
  const averageProbability = Math.round(recommendations.reduce((sum, row) => sum + row.metrics.probabilityUp5d, 0) / Math.max(1, recommendations.length));
  const averageRisk = Math.round(recommendations.reduce((sum, row) => sum + row.metrics.riskScore, 0) / Math.max(1, recommendations.length));
  const averageScore = Math.round(recommendations.reduce((sum, row) => sum + row.score, 0) / Math.max(1, recommendations.length));

  return (
    <AppShell active="/recommendations">
      <header className="topbar">
        <div>
          <p className="eyebrow">明燈推薦</p>
          <h1>今日前 20 檔研究觀察名單</h1>
        </div>
        <div className="status ok">高機率 + 低風險 + 多因子共振</div>
      </header>

      <section className="metric-grid">
        <ScoreCard label="推薦數" value={`${recommendations.length}`} detail="跨產業輪動" />
        <ScoreCard label="第一名" value={top?.signal.symbol ?? "-"} detail={top ? top.signal.name : "資料整理中"} tone="positive" />
        <ScoreCard label="平均推薦分數" value={`${averageScore}`} detail="滿分 100" tone={scoreTone(averageScore)} />
        <ScoreCard label="平均 5D 機率" value={`${averageProbability}%`} detail="前 20 檔平均" tone={scoreTone(averageProbability)} />
        <ScoreCard label="平均風險" value={`${averageRisk}`} detail="越低越保守" tone={averageRisk >= 55 ? "risk" : "neutral"} />
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Top 20</p>
            <h2>明燈推薦清單</h2>
          </div>
          <span className="panel-tag">產業輪動模型，非買賣建議</span>
        </div>
        <div className="recommendation-list">
          {recommendations.map((row, index) => (
            <a className="recommendation-row" href={`/stocks/${row.signal.symbol}`} key={row.signal.symbol}>
              <b>{index + 1}</b>
              <div>
                <strong>{row.signal.symbol} {row.signal.name}</strong>
                <span>{row.reason}</span>
              </div>
              <em>{row.score}</em>
              <small>5D {row.metrics.probabilityUp5d}% · 題材 {row.themeFit} · {row.themes.slice(0, 2).join(" / ")} · 風險 {row.metrics.riskScore}</small>
            </a>
          ))}
        </div>
        <p className="panel-note">權重：5D 機率 18%、風險調整 17%、低風險品質 14%、產業/市場適配 12%、籌碼 11%、技術 10%、基本面 8%、新聞 5%、美股連動 3%、信心 2%。</p>
      </section>
    </AppShell>
  );
}

function buildRecommendation(signal: PredictionSignal): RecommendationRow {
  const metrics = buildStockMetrics(signal);
  const confidence = Math.round(signal.confidence * 100);
  const marketProfile = getMarketProfile(signal);
  const score = Math.round(
    metrics.probabilityUp5d * (recommendationWeights.probability / 100)
    + metrics.riskAdjustedScore * (recommendationWeights.riskAdjusted / 100)
    + (100 - metrics.riskScore) * (recommendationWeights.riskQuality / 100)
    + marketProfile.fit * (recommendationWeights.themeFit / 100)
    + metrics.chipScore * (recommendationWeights.chip / 100)
    + metrics.technicalScore * (recommendationWeights.technical / 100)
    + metrics.fundamentalScore * (recommendationWeights.fundamental / 100)
    + metrics.newsScore * (recommendationWeights.news / 100)
    + metrics.usMarketScore * (recommendationWeights.usMarket / 100)
    + confidence * (recommendationWeights.confidence / 100)
    - Math.max(0, metrics.riskScore - 62) * 0.32,
  );

  return {
    signal,
    score,
    reason: buildReason(signal, metrics, marketProfile),
    themes: marketProfile.themes,
    themeFit: marketProfile.fit,
    metrics,
  };
}

function buildReason(signal: PredictionSignal, metrics: ReturnType<typeof buildStockMetrics>, marketProfile: { fit: number; themes: string[] }): string {
  const drivers = [
    marketProfile.themes.length ? `輪動：${marketProfile.themes.slice(0, 2).join(" / ")}` : "",
    metrics.riskScore <= 45 ? "風險較低" : "",
    metrics.chipScore >= 65 ? "籌碼偏強" : "",
    metrics.technicalScore >= 65 ? "技術面偏強" : "",
    metrics.fundamentalScore >= 62 ? "基本面加分" : "",
    metrics.usMarketScore >= 60 ? "外部市場加分" : "",
    metrics.newsScore >= 58 ? "新聞題材加分" : "",
  ].filter(Boolean);
  const fallback = signal.explanation?.top_positive_factors?.[0] ?? "多因子條件相對完整";
  return sanitizeDisplayText(drivers.slice(0, 3).join(" · ") || fallback);
}

function getMarketProfile(signal: PredictionSignal): { fit: number; themes: string[] } {
  const direct = marketThemeProfiles[signal.symbol];
  if (direct) return direct;
  const haystack = `${signal.name} ${signal.sector ?? ""}`;
  const themes: string[] = [];
  if (/半導體|IC|晶片|封裝|測試/.test(haystack)) themes.push("半導體");
  if (/電腦|週邊|伺服器|雲端|資料中心/.test(haystack)) themes.push("AI/雲端");
  if (/電機|機械|自動化|氣動|機器人/.test(haystack)) themes.push("機器人/自動化");
  if (/航運|航空|運輸|物流/.test(haystack)) themes.push("運輸");
  if (/金融|銀行|金控|保險|證券/.test(haystack)) themes.push("金融避險");
  if (/電線|電纜|重電|電力|能源|油電/.test(haystack)) themes.push("電力能源");
  if (/水泥|塑膠|鋼鐵|化學|原物料/.test(haystack)) themes.push("原物料循環");
  if (/食品|百貨|觀光|汽車|零售/.test(haystack)) themes.push("內需防禦");
  if (/生技|醫療|製藥/.test(haystack)) themes.push("生技醫療");
  const fit = themes.length ? 58 + Math.min(18, themes.length * 6) : 52;
  return { fit, themes: themes.length ? themes : ["一般產業"] };
}
