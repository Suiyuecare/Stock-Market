import { AppShell } from "@/components/AppShell";
import { RiskPanel } from "@/components/RiskPanel";
import { ScoreCard } from "@/components/ScoreCard";
import { buildStockMetrics, DISCLAIMER_TEXT, sanitizeDisplayText, sanitizeRiskScore } from "@/lib/view-model";
import { fetchRanking, fetchStockDetail } from "@/lib/api";

export default async function RiskPage() {
  const ranking = await fetchRanking();
  const detail = await fetchStockDetail("2330");
  const metrics = buildStockMetrics(detail.signal);

  return (
    <AppShell active="/risk">
      <header className="topbar">
        <div>
          <p className="eyebrow">Risk Monitoring</p>
          <h1>風險監控</h1>
        </div>
        <div className="status">{detail.signal.symbol}</div>
      </header>
      <div className="disclaimer">{DISCLAIMER_TEXT}</div>
      <section className="metric-grid">
        <ScoreCard label="2330 風險係數" value={`${metrics.riskScore}`} detail={sanitizeDisplayText(detail.signal.risk_score.explanation)} tone="risk" />
        <ScoreCard label="風險調整分數" value={`${metrics.riskAdjustedScore}`} detail="BullishScore 扣除風險係數" />
        <ScoreCard label="監控標的" value={`${ranking.signals.length}`} detail="目前樣本池" />
        <ScoreCard label="事件風險" value={`${Math.round(detail.signal.risk_score.event * 100)}`} detail="新聞與 VIX 代理訊號" />
      </section>
      <section className="grid">
        <article className="panel span-2">
          <RiskPanel risk={sanitizeRiskScore(detail.signal.risk_score)} />
        </article>
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Watchlist</p>
              <h2>風險觀察列表</h2>
            </div>
          </div>
          <div className="signal-list">
            {ranking.signals.map((signal) => {
              const signalMetrics = buildStockMetrics(signal);
              return (
                <a className="signal" href={`/stocks/${signal.symbol}`} key={signal.symbol}>
                  <div>
                    <strong>{signal.symbol} {signal.name}</strong>
                    <span>上漲機率 {signalMetrics.probabilityUp1d}%</span>
                  </div>
                  <b>{signalMetrics.riskScore}</b>
                  <small>風險係數</small>
                </a>
              );
            })}
          </div>
        </article>
      </section>
    </AppShell>
  );
}
