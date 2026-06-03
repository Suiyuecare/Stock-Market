import { AppShell } from "@/components/AppShell";
import { ScoreCard } from "@/components/ScoreCard";
import type { PredictionSignal } from "@/lib/api";
import { fetchTopProbabilityRanking } from "@/lib/api";
import { buildStockMetrics, sanitizeDisplayText, scoreTone } from "@/lib/view-model";

type RecommendationRow = {
  signal: PredictionSignal;
  score: number;
  reason: string;
  metrics: ReturnType<typeof buildStockMetrics>;
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
        <ScoreCard label="推薦數" value={`${recommendations.length}`} detail="最多取前 20 檔" />
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
          <span className="panel-tag">研究訊號，非買賣建議</span>
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
              <small>風險 {row.metrics.riskScore} · 調整 {row.metrics.riskAdjustedScore} · 信心 {Math.round(row.signal.confidence * 100)}%</small>
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
  const score = Math.round(
    metrics.probabilityUp5d * 0.34
    + metrics.riskAdjustedScore * 0.24
    + metrics.chipScore * 0.14
    + metrics.technicalScore * 0.1
    + metrics.usMarketScore * 0.08
    + metrics.newsScore * 0.05
    + confidence * 0.05
    - Math.max(0, metrics.riskScore - 50) * 0.28,
  );

  return {
    signal,
    score,
    reason: buildReason(signal, metrics),
    metrics,
  };
}

function buildReason(signal: PredictionSignal, metrics: ReturnType<typeof buildStockMetrics>): string {
  const drivers = [
    metrics.chipScore >= 65 ? "籌碼偏強" : "",
    metrics.technicalScore >= 65 ? "技術面偏強" : "",
    metrics.usMarketScore >= 60 ? "美股連動加分" : "",
    metrics.newsScore >= 58 ? "新聞題材加分" : "",
    metrics.riskScore <= 50 ? "風險較低" : "",
  ].filter(Boolean);
  const fallback = signal.explanation?.top_positive_factors?.[0] ?? "多因子條件相對完整";
  return sanitizeDisplayText(drivers.slice(0, 3).join(" · ") || fallback);
}
