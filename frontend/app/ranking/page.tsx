import { AppShell } from "@/components/AppShell";
import { ScoreCard } from "@/components/ScoreCard";
import { StockRankingTable } from "@/components/StockRankingTable";
import { DISCLAIMER_TEXT } from "@/lib/view-model";
import { fetchRanking } from "@/lib/api";

export default async function RankingPage() {
  const ranking = await fetchRanking();
  const top = ranking.signals[0];

  return (
    <AppShell active="/ranking">
      <header className="topbar">
        <div>
          <p className="eyebrow">Taiwan Ranking</p>
          <h1>台股因子排名</h1>
        </div>
        <div className="status">研究訊號</div>
      </header>
      <div className="disclaimer">{DISCLAIMER_TEXT}</div>
      <section className="metric-grid">
        <ScoreCard label="樣本數" value={`${ranking.signals.length}`} detail="目前 MVP 追蹤標的" />
        <ScoreCard label="最高觀察標的" value={top.symbol} detail={top.name} tone="positive" />
        <ScoreCard label="資料頻率" value="每日" detail="盤後與美股開盤前" />
        <ScoreCard label="輸出類型" value="機率" detail="不提供個人化建議" />
      </section>
      <article className="panel">
        <StockRankingTable signals={ranking.signals} />
      </article>
    </AppShell>
  );
}
