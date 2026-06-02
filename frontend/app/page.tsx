import { SignalChart } from "@/components/SignalChart";
import { fetchMarketSummary, fetchPredictionSignals } from "@/lib/api";

export default async function Home() {
  const [summary, signals] = await Promise.all([fetchMarketSummary(), fetchPredictionSignals()]);

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
          <a href="#signals">預測訊號</a>
          <a href="#watchlist">觀察名單</a>
          <a href="#jobs">排程任務</a>
        </nav>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">每日盤後 + 美股開盤前</p>
            <h1>台美股連動預測工作台</h1>
          </div>
          <div className="status">MVP v0.1</div>
        </header>

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
            <small>TW + US seed list</small>
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

          <article id="signals" className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Signals</p>
                <h2>預測訊號</h2>
              </div>
            </div>
            <div className="signal-list">
              {signals.map((signal) => (
                <div className="signal" key={signal.symbol}>
                  <div>
                    <strong>{signal.symbol}</strong>
                    <span>{signal.horizon}</span>
                  </div>
                  <b>{Math.round(signal.score * 100)}</b>
                  <small>confidence {Math.round(signal.confidence * 100)}%</small>
                </div>
              ))}
            </div>
          </article>

          <article id="watchlist" className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Universe</p>
                <h2>觀察名單</h2>
              </div>
            </div>
            <table>
              <thead>
                <tr>
                  <th>代號</th>
                  <th>市場</th>
                  <th>名稱</th>
                  <th>產業</th>
                </tr>
              </thead>
              <tbody>
                {summary.instruments.map((item) => (
                  <tr key={item.symbol}>
                    <td>{item.symbol}</td>
                    <td>{item.market}</td>
                    <td>{item.name}</td>
                    <td>{item.sector}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>

          <article id="jobs" className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Jobs</p>
                <h2>排程任務</h2>
              </div>
            </div>
            <ul className="job-list">
              <li>
                <strong>15:20</strong>
                <span>台股每日盤後資料整理</span>
              </li>
              <li>
                <strong>20:30</strong>
                <span>美股開盤前連動訊號</span>
              </li>
              <li>
                <strong>Queued</strong>
                <span>LLM 新聞事件解析</span>
              </li>
            </ul>
          </article>
        </section>
      </section>
    </main>
  );
}
