import { AppShell } from "@/components/AppShell";
import { ScoreCard } from "@/components/ScoreCard";
import type { PredictionSignal } from "@/lib/api";
import { fetchTopProbabilityRanking } from "@/lib/api";
import { buildStockMetrics, sanitizeDisplayText, scoreTone } from "@/lib/view-model";

type RecommendationRow = {
  signal: PredictionSignal;
  score: number;
  reason: string;
  aiThemes: string[];
  aiRelevance: number;
  metrics: ReturnType<typeof buildStockMetrics>;
};

const aiThemeMap: Record<string, { relevance: number; themes: string[] }> = {
  "2330": { relevance: 100, themes: ["晶圓代工", "CoWoS", "AI 晶片"] },
  "2317": { relevance: 94, themes: ["AI 伺服器", "EMS", "NVDA 供應鏈"] },
  "2382": { relevance: 96, themes: ["AI 伺服器", "雲端資料中心"] },
  "3231": { relevance: 94, themes: ["AI 伺服器", "雲端資料中心"] },
  "6669": { relevance: 98, themes: ["AI 伺服器", "雲端資料中心"] },
  "2308": { relevance: 92, themes: ["電源管理", "散熱電源", "資料中心"] },
  "2345": { relevance: 90, themes: ["高速網通", "資料中心交換器"] },
  "2356": { relevance: 84, themes: ["AI PC", "伺服器"] },
  "2357": { relevance: 82, themes: ["AI PC", "伺服器"] },
  "2376": { relevance: 86, themes: ["AI PC", "主機板", "伺服器"] },
  "2377": { relevance: 82, themes: ["AI PC", "伺服器"] },
  "4938": { relevance: 80, themes: ["EMS", "AI 終端"] },
  "2324": { relevance: 78, themes: ["NB/AI PC", "EMS"] },
  "2454": { relevance: 88, themes: ["IC 設計", "Edge AI"] },
  "2379": { relevance: 82, themes: ["IC 設計", "網通晶片"] },
  "3034": { relevance: 78, themes: ["IC 設計", "顯示晶片"] },
  "3035": { relevance: 86, themes: ["ASIC", "AI 晶片設計服務"] },
  "3443": { relevance: 90, themes: ["ASIC", "AI 晶片設計服務"] },
  "3661": { relevance: 94, themes: ["ASIC", "AI/HPC"] },
  "5274": { relevance: 86, themes: ["伺服器管理晶片", "BMC"] },
  "3017": { relevance: 92, themes: ["散熱", "液冷"] },
  "3324": { relevance: 90, themes: ["散熱", "液冷"] },
  "6230": { relevance: 86, themes: ["散熱", "伺服器風扇"] },
  "2421": { relevance: 82, themes: ["散熱", "風扇"] },
  "3653": { relevance: 84, themes: ["散熱", "均熱片"] },
  "2383": { relevance: 92, themes: ["CCL", "高速材料"] },
  "6274": { relevance: 90, themes: ["CCL", "高速材料"] },
  "6213": { relevance: 84, themes: ["CCL", "PCB 材料"] },
  "2368": { relevance: 90, themes: ["PCB", "AI 伺服器板"] },
  "3037": { relevance: 88, themes: ["ABF", "PCB", "AI 載板"] },
  "8046": { relevance: 86, themes: ["ABF", "載板"] },
  "3189": { relevance: 84, themes: ["載板", "先進封裝"] },
  "4958": { relevance: 82, themes: ["PCB", "供應鏈"] },
  "3711": { relevance: 90, themes: ["封裝測試", "先進封裝"] },
  "2449": { relevance: 86, themes: ["測試", "AI/HPC"] },
  "3264": { relevance: 80, themes: ["測試", "半導體"] },
  "6147": { relevance: 78, themes: ["封測", "驅動 IC"] },
  "6515": { relevance: 82, themes: ["測試介面", "HPC"] },
  "2408": { relevance: 78, themes: ["記憶體", "AI 伺服器"] },
  "2344": { relevance: 76, themes: ["記憶體", "邊緣 AI"] },
  "8299": { relevance: 80, themes: ["NAND 控制晶片", "儲存"] },
  "6412": { relevance: 78, themes: ["電源供應", "伺服器"] },
};

export default async function RecommendationsPage() {
  const ranking = await fetchTopProbabilityRanking();
  const recommendations = ranking.signals
    .map(buildRecommendation)
    .filter((row) => row.aiRelevance >= 55)
    .sort((left, right) => right.score - left.score)
    .slice(0, 20);
  const top = recommendations[0];
  const averageProbability = Math.round(recommendations.reduce((sum, row) => sum + row.metrics.probabilityUp5d, 0) / Math.max(1, recommendations.length));
  const averageRisk = Math.round(recommendations.reduce((sum, row) => sum + row.metrics.riskScore, 0) / Math.max(1, recommendations.length));

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
        <ScoreCard label="推薦數" value={`${recommendations.length}`} detail="AI 供應鏈優先" />
        <ScoreCard label="第一名" value={top?.signal.symbol ?? "-"} detail={top ? top.signal.name : "資料整理中"} tone="positive" />
        <ScoreCard label="平均 5D 機率" value={`${averageProbability}%`} detail="前 20 檔平均" tone={scoreTone(averageProbability)} />
        <ScoreCard label="平均風險" value={`${averageRisk}`} detail="越低越保守" tone={averageRisk >= 55 ? "risk" : "neutral"} />
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Top 20</p>
            <h2>明燈推薦清單</h2>
          </div>
          <span className="panel-tag">AI 題材優先，非買賣建議</span>
        </div>
        <div className="recommendation-list">
          {recommendations.map((row, index) => (
            <a className="recommendation-row" href={`/stocks/${row.signal.symbol}`} key={row.signal.symbol}>
              <b>{index + 1}</b>
              <div>
                <strong>{row.signal.symbol} {row.signal.name}</strong>
                <span>{row.reason}</span>
              </div>
              <em>{row.metrics.probabilityUp5d}%</em>
              <small>AI {row.aiRelevance} · {row.aiThemes.slice(0, 2).join(" / ")} · 風險 {row.metrics.riskScore}</small>
            </a>
          ))}
        </div>
      </section>
    </AppShell>
  );
}

function buildRecommendation(signal: PredictionSignal): RecommendationRow {
  const metrics = buildStockMetrics(signal);
  const confidence = Math.round(signal.confidence * 100);
  const aiProfile = getAiProfile(signal);
  const score = Math.round(
    aiProfile.relevance * 0.34
    + metrics.probabilityUp5d * 0.2
    + metrics.riskAdjustedScore * 0.16
    + metrics.chipScore * 0.1
    + metrics.technicalScore * 0.08
    + metrics.usMarketScore * 0.08
    + metrics.newsScore * 0.02
    + confidence * 0.02
    - Math.max(0, metrics.riskScore - 50) * 0.28,
  );

  return {
    signal,
    score,
    reason: buildReason(signal, metrics, aiProfile),
    aiThemes: aiProfile.themes,
    aiRelevance: aiProfile.relevance,
    metrics,
  };
}

function buildReason(signal: PredictionSignal, metrics: ReturnType<typeof buildStockMetrics>, aiProfile: { relevance: number; themes: string[] }): string {
  const drivers = [
    aiProfile.themes.length ? `AI 關聯：${aiProfile.themes.slice(0, 2).join(" / ")}` : "",
    metrics.chipScore >= 65 ? "籌碼偏強" : "",
    metrics.technicalScore >= 65 ? "技術面偏強" : "",
    metrics.usMarketScore >= 60 ? "美股連動加分" : "",
    metrics.newsScore >= 58 ? "新聞題材加分" : "",
    metrics.riskScore <= 50 ? "風險較低" : "",
  ].filter(Boolean);
  const fallback = signal.explanation?.top_positive_factors?.[0] ?? "多因子條件相對完整";
  return sanitizeDisplayText(drivers.slice(0, 3).join(" · ") || fallback);
}

function getAiProfile(signal: PredictionSignal): { relevance: number; themes: string[] } {
  const direct = aiThemeMap[signal.symbol];
  if (direct) return direct;
  const haystack = `${signal.name} ${signal.sector ?? ""} ${signal.explanation?.top_positive_factors?.join(" ") ?? ""}`;
  const themes: string[] = [];
  if (/半導體|IC|晶片|封裝|測試/.test(haystack)) themes.push("半導體");
  if (/電腦|週邊|伺服器|雲端|資料中心/.test(haystack)) themes.push("AI 伺服器");
  if (/電子零組件|PCB|CCL|載板/.test(haystack)) themes.push("PCB/載板");
  if (/通信|網通|交換器/.test(haystack)) themes.push("高速網通");
  const relevance = themes.length ? 58 + Math.min(18, themes.length * 8) : 20;
  return { relevance, themes };
}
