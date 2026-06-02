import { AppShell } from "@/components/AppShell";
import { ComplianceNotice } from "@/components/ComplianceNotice";
import { NewsTimeline } from "@/components/NewsTimeline";
import { ScoreCard } from "@/components/ScoreCard";
import { fetchStocks, fetchStockNews } from "@/lib/api";

export default async function NewsPage() {
  const stocks = await fetchStocks();
  const stockNews = await Promise.all(stocks.stocks.slice(0, 80).map((stock) => fetchStockNews(stock.symbol)));
  const news = stockNews.flatMap((detail) => detail.news);

  return (
    <AppShell active="/news">
      <header className="topbar">
        <div>
          <p className="eyebrow">新聞時間軸</p>
          <h1>新聞事件時間線</h1>
        </div>
        <div className="status">以事件補充因子說明依據</div>
      </header>
      <ComplianceNotice />
      <section className="metric-grid">
        <ScoreCard label="事件數" value={`${news.length}`} detail="樣本新聞與事件" />
        <ScoreCard label="涵蓋標的" value={`${stocks.stocks.length}`} detail="台股追蹤池，事件頁先列前 80 檔" />
        <ScoreCard label="情緒欄位" value="Sentiment" detail="LLM parser interface" />
        <ScoreCard label="用途" value="研究" detail="事件風險與因子解釋" />
      </section>
      <article className="panel">
        <NewsTimeline news={news} />
      </article>
    </AppShell>
  );
}
