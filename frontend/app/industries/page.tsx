import { AppShell } from "@/components/AppShell";
import { ComplianceNotice } from "@/components/ComplianceNotice";
import { ScoreCard } from "@/components/ScoreCard";
import { fetchTopProbabilityRanking } from "@/lib/api";
import { buildIndustryRankings } from "@/lib/industry-classification";

export default async function IndustriesPage() {
  const ranking = await fetchTopProbabilityRanking();
  const rankedIndustries = buildIndustryRankings(ranking.signals);
  const top = rankedIndustries[0];
  const weakest = rankedIndustries.at(-1);
  const topSubcategory = top?.subcategories[0];

  return (
    <AppShell active="/industries">
      <header className="topbar">
        <div>
          <p className="eyebrow">產業明燈 · {ranking.data_date?.replaceAll("-", "/") ?? "最新官方資料"}</p>
          <h1>先選大分類，再看小分類熱度</h1>
        </div>
        <div className="status ok">目前最強：{top?.category.name ?? "資料整理中"} {top?.score ?? "-"}</div>
      </header>
      <ComplianceNotice />

      <section className="metric-grid">
        <ScoreCard label="大分類數" value={`${rankedIndustries.length}`} detail="依分數由好到不好排序" />
        <ScoreCard label="最強大分類" value={`${top?.score ?? "-"}`} detail={top?.category.name ?? "資料整理中"} tone="positive" />
        <ScoreCard label="最強小分類" value={topSubcategory?.name ?? "-"} detail={topSubcategory ? `${topSubcategory.score} 分 · ${topSubcategory.stockCount} 檔` : "資料整理中"} />
        <ScoreCard label="相對落後" value={weakest?.category.shortName ?? "-"} detail={weakest ? `${weakest.score} 分，先觀察即可` : "資料整理中"} tone="neutral" />
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Beginner Flow</p>
            <h2>新手先看大分類，點開後再選小分類</h2>
          </div>
          <span className="panel-tag">每日隨明燈候選池重排</span>
        </div>
        <p className="panel-note">排序方式：把同一分類底下股票的 5D 研究分數、最高分股票、平均風險與候選數量合併。分數越高代表目前研究條件越完整，不代表保證上漲。</p>
        <div className="industry-rank-list">
          {rankedIndustries.map((industry, index) => (
            <details className="industry-rank-card" key={industry.category.id} open={index < 3}>
              <summary>
                <b>{index + 1}</b>
                <div>
                  <span>{industry.trend} · {industry.stockCount} 檔候選 · 平均風險 {industry.averageRisk}</span>
                  <strong>{industry.category.name}</strong>
                  <small>{industry.reason}</small>
                </div>
                <em>{industry.score}</em>
              </summary>

              <div className="subindustry-grid">
                {industry.subcategories.map((subcategory, subIndex) => (
                  <article className="subindustry-card" key={subcategory.name}>
                    <div className="subindustry-head">
                      <span>#{subIndex + 1} 小分類</span>
                      <strong>{subcategory.score}</strong>
                    </div>
                    <h3>{subcategory.name}</h3>
                    <small>{subcategory.stockCount} 檔候選，依好壞排序</small>
                    <div className="industry-stock-list">
                      {subcategory.stocks.map((stock) => (
                        <a href={`/stocks/${stock.symbol}`} key={`${subcategory.name}-${stock.symbol}`}>
                          {stock.symbol} {stock.name} · {stock.score}
                        </a>
                      ))}
                    </div>
                  </article>
                ))}
              </div>
            </details>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
