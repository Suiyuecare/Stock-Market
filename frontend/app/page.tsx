import { FactorBreakdown } from "@/components/FactorBreakdown";
import { NewsTimeline } from "@/components/NewsTimeline";
import { RiskPanel } from "@/components/RiskPanel";
import { ScoreCard } from "@/components/ScoreCard";
import { TechnicalChart } from "@/components/TechnicalChart";
import { USMarketRadar } from "@/components/USMarketRadar";
import { fetchMarketSummary, fetchRanking, fetchStockDetail } from "@/lib/api";

export default async function Home() {
  const [summary, ranking, detail] = await Promise.all([
    fetchMarketSummary(),
    fetchRanking(),
    fetchStockDetail("2330"),
  ]);
  const signals = ranking.signals;
  const selected = detail.signal;

  return (
    <main className="workspace">
      <aside className="sidebar">
        <div className="brand">
          <span>TW</span>
          <div>
            <strong>Stock Prediction</strong>
            <small>TW-US linkage desk</small>
          </div>
        </div>
        <nav>
          <a className="active" href="#overview">總覽</a>
          <a href="#ranking">台股排名</a>
          <a href="/us-radar">美股連動</a>
          <a href="/stocks/2330">個股分析</a>
          <a href="/risk">風險</a>
        </nav>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">每日盤後 + 美股開盤前</p>
            <h1>台美股因子分析與機率訊號</h1>
          </div>
          <div className="status">Research MVP</div>
        </header>

        <div className="disclaimer">{summary.disclaimer}</div>

        <section id="overview" className="metric-grid">
          <ScoreCard label="台股盤後狀態" value={summary.tw_status} detail={summary.session_date} />
          <ScoreCard label="美股開盤前連動" value={summary.us_premarket_status} detail="20:30 Asia/Taipei job" />
          <ScoreCard label="追蹤標的" value={`${summary.instruments.length}`} detail="TW seed universe" />
          <ScoreCard label="最高機率訊號" value={signals[0].symbol} detail={`${Math.round(signals[0].probability_up * 100)}% probability style`} />
        </section>

        <section className="grid">
          <article className="panel span-2">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Prediction Score</p>
                <h2>下一交易日訊號趨勢</h2>
              </div>
            </div>
            <TechnicalChart />
          </article>

          <article id="ranking" className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Ranking</p>
                <h2>台股因子排名</h2>
              </div>
            </div>
            <div className="signal-list">
              {signals.map((signal) => (
                <div className="signal" key={signal.symbol}>
                  <div>
                    <strong>{signal.symbol}</strong>
                    <span>{signal.name}</span>
                  </div>
                  <b>{Math.round(signal.probability_up * 100)}</b>
                  <small>confidence {Math.round(signal.confidence * 100)}%</small>
                </div>
              ))}
            </div>
          </article>

          <article id="us-linkage" className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">US Linkage Radar</p>
                <h2>美股連動雷達</h2>
              </div>
            </div>
            <USMarketRadar linkage={summary.us_linkage} />
          </article>

          <article id="detail" className="panel span-2">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Stock Detail</p>
                <h2>{selected.symbol} {selected.name}</h2>
              </div>
            </div>
            <RiskPanel risk={selected.risk_score} />
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Explanation</p>
                <h2>正向/負向因子</h2>
              </div>
            </div>
            <FactorBreakdown positiveDrivers={selected.positive_drivers} negativeDrivers={selected.negative_drivers} />
          </article>

          <article id="news" className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">News Timeline</p>
                <h2>新聞/事件時間線</h2>
              </div>
            </div>
            <NewsTimeline news={selected.news} />
          </article>
        </section>
      </section>
    </main>
  );
}
