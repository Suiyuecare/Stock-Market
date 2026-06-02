import { SignalChart } from "@/components/SignalChart";
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
          <a href="#us-linkage">美股連動</a>
          <a href="#detail">個股分析</a>
          <a href="#news">事件時間線</a>
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
          <article className="metric">
            <span>台股盤後狀態</span>
            <strong>{summary.tw_status}</strong>
            <small>{summary.session_date}</small>
          </article>
          <article className="metric">
            <span>美股開盤前連動</span>
            <strong>{summary.us_premarket_status}</strong>
            <small>20:30 Asia/Taipei job</small>
          </article>
          <article className="metric">
            <span>追蹤標的</span>
            <strong>{summary.instruments.length}</strong>
            <small>TW seed universe</small>
          </article>
          <article className="metric">
            <span>最高機率訊號</span>
            <strong>{signals[0].symbol}</strong>
            <small>{Math.round(signals[0].probability_up * 100)}% probability style</small>
          </article>
        </section>

        <section className="grid">
          <article className="panel span-2">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Prediction Score</p>
                <h2>下一交易日訊號趨勢</h2>
              </div>
            </div>
            <SignalChart />
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
            <div className="radar-grid">
              {Object.entries(summary.us_linkage).map(([name, value]) => (
                <div className="radar-item" key={name}>
                  <span>{name}</span>
                  <strong className={value >= 0 ? "positive" : "negative"}>{Math.round(value * 100)}</strong>
                </div>
              ))}
            </div>
          </article>

          <article id="detail" className="panel span-2">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Stock Detail</p>
                <h2>{selected.symbol} {selected.name}</h2>
              </div>
            </div>
            <div className="detail-grid">
              <div className="score-card">
                <span>Probability-style signal</span>
                <strong>{Math.round(selected.probability_up * 100)}%</strong>
                <small>Composite {selected.composite_score}</small>
              </div>
              <div className="score-card risk">
                <span>Risk score</span>
                <strong>{Math.round(selected.risk_score.total * 100)}</strong>
                <small>{selected.risk_score.explanation}</small>
              </div>
            </div>
          </article>

          <article className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Explanation</p>
                <h2>正向/負向因子</h2>
              </div>
            </div>
            <div className="driver-list">
              {selected.positive_drivers.map((driver) => (
                <div className="driver positive-border" key={driver.name}>
                  <strong>{driver.name}</strong>
                  <span>{driver.explanation}</span>
                </div>
              ))}
              {selected.negative_drivers.map((driver) => (
                <div className="driver negative-border" key={driver.name}>
                  <strong>{driver.name}</strong>
                  <span>{driver.explanation}</span>
                </div>
              ))}
            </div>
          </article>

          <article id="news" className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">News Timeline</p>
                <h2>新聞/事件時間線</h2>
              </div>
            </div>
            <div className="timeline">
              {selected.news.map((event) => (
                <div className="timeline-item" key={event.title}>
                  <strong>{event.title}</strong>
                  <span>{event.source} · {event.sentiment} · impact {event.impact_score}</span>
                </div>
              ))}
            </div>
          </article>
        </section>
      </section>
    </main>
  );
}
