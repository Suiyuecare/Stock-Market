import { AppShell } from "@/components/AppShell";
import { BacktestConfidencePanel } from "@/components/BacktestConfidencePanel";
import { ComplianceNotice } from "@/components/ComplianceNotice";
import { ScoreCard } from "@/components/ScoreCard";
import { StockRankingTable } from "@/components/StockRankingTable";
import { formatRatio, formatScore, sanitizeDisplayText } from "@/lib/view-model";
import { fetchInstitutionalBuyingRanking, fetchMacdGoldenCrossRanking, fetchTopProbabilityRanking, fetchVolumePriceDivergenceRanking } from "@/lib/api";

export default async function RankingPage() {
  const [ranking, institutional, macd, divergence] = await Promise.all([
    fetchTopProbabilityRanking(),
    fetchInstitutionalBuyingRanking(),
    fetchMacdGoldenCrossRanking(),
    fetchVolumePriceDivergenceRanking(),
  ]);
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
      <ComplianceNotice />
      <section className="metric-grid">
        <ScoreCard label="樣本數" value={`${ranking.signals.length}`} detail="目前 MVP 追蹤標的" />
        <ScoreCard label="最高觀察標的" value={top.symbol} detail={top.name} tone="positive" />
        <ScoreCard label="資料頻率" value="每日" detail="盤後與美股開盤前" />
        <ScoreCard label="輸出類型" value="機率" detail="不提供個人化建議" />
      </section>
      <section className="grid">
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Strategy Evidence</p>
              <h2>本排名採用的勝率篩選邏輯</h2>
            </div>
          </div>
          <BacktestConfidencePanel signal={top} />
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Top Probability</p>
              <h2>上漲機率排名</h2>
            </div>
          </div>
          <StockRankingTable signals={ranking.signals} />
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Institutional</p>
              <h2>法人籌碼排名</h2>
            </div>
          </div>
          <div className="mini-table">
            {institutional.ranking.map((row) => (
              <a className="mini-row" href={`/stocks/${row.stock_id}`} key={row.stock_id}>
                <span>{row.stock_id} {row.stock_name}</span>
                <b>{formatRatio(row.institutional_net_ratio)}</b>
                <small>{sanitizeDisplayText(row.positive_factors[0] ?? "法人籌碼觀察中")}</small>
              </a>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">MACD</p>
              <h2>MACD 黃金交叉觀察</h2>
            </div>
          </div>
          <div className="mini-table">
            {macd.ranking.map((row) => (
              <a className="mini-row" href={`/stocks/${row.stock_id}`} key={row.stock_id}>
                <span>{row.stock_id} {row.stock_name}</span>
                <b>{row.macd_golden_cross ? "已觸發" : "觀察中"}</b>
                <small>技術分數 {formatScore(row.technical_score)} · Hist {row.macd_hist?.toFixed(2) ?? "n/a"}</small>
              </a>
            ))}
          </div>
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Volume Price</p>
              <h2>量價背離排名</h2>
            </div>
          </div>
          <div className="mini-table">
            {divergence.ranking.map((row) => (
              <a className="mini-row" href={`/stocks/${row.stock_id}`} key={row.stock_id}>
                <span>{row.stock_id} {row.stock_name}</span>
                <b>{row.bullish_divergence ? "正向背離" : row.bearish_divergence ? "風險背離" : "一般狀態"}</b>
                <small>{row.states.join(" · ")}</small>
              </a>
            ))}
          </div>
        </article>
      </section>
    </AppShell>
  );
}
