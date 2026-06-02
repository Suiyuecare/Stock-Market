import { AppShell } from "@/components/AppShell";
import { NewsTimeline } from "@/components/NewsTimeline";
import { ScoreCard } from "@/components/ScoreCard";
import { DISCLAIMER_TEXT } from "@/lib/view-model";
import { fetchRanking, fetchStockDetail } from "@/lib/api";

export default async function NewsPage() {
  const ranking = await fetchRanking();
  const details = await Promise.all(ranking.signals.map((signal) => fetchStockDetail(signal.symbol)));
  const news = details.flatMap((detail) => detail.signal.news);

  return (
    <AppShell active="/news">
      <header className="topbar">
        <div>
          <p className="eyebrow">News Timeline</p>
          <h1>新聞事件時間線</h1>
        </div>
        <div className="status">事件解析</div>
      </header>
      <div className="disclaimer">{DISCLAIMER_TEXT}</div>
      <section className="metric-grid">
        <ScoreCard label="事件數" value={`${news.length}`} detail="樣本新聞與事件" />
        <ScoreCard label="涵蓋標的" value={`${ranking.signals.length}`} detail="台股追蹤池" />
        <ScoreCard label="情緒欄位" value="Sentiment" detail="LLM parser interface" />
        <ScoreCard label="用途" value="研究" detail="事件風險與因子解釋" />
      </section>
      <article className="panel">
        <NewsTimeline news={news} />
      </article>
    </AppShell>
  );
}
