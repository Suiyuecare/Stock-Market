import { AppShell } from "@/components/AppShell";
import { ComplianceNotice } from "@/components/ComplianceNotice";
import { RiskPanel } from "@/components/RiskPanel";
import { ScoreCard } from "@/components/ScoreCard";
import { sanitizeDisplayText, sanitizeRiskScore, toPercent } from "@/lib/view-model";
import { fetchHighRisk } from "@/lib/api";

export default async function RiskPage() {
  const highRisk = await fetchHighRisk();
  const primary = highRisk.signals[0];
  const risk = primary?.risk_score;

  return (
    <AppShell active="/risk">
      <header className="topbar">
        <div>
          <p className="eyebrow">風險監控</p>
          <h1>風險監控</h1>
        </div>
        <div className="status risk">{primary ? `${primary.stock_id} ${primary.stock_name}` : "Risk Monitor"}</div>
      </header>
      <ComplianceNotice />
      <section className="metric-grid">
        <ScoreCard label="最高風險標的" value={primary?.stock_id ?? "觀察中"} detail={primary?.stock_name ?? "目前無高風險樣本"} tone="risk" />
        <ScoreCard label="風險係數" value={risk ? `${Math.round(risk.total * 100)}` : "0"} detail={risk ? sanitizeDisplayText(risk.explanation) : "資料觀察中"} tone="risk" />
        <ScoreCard label="監控標的" value={`${highRisk.signals.length}`} detail="高風險 API 回傳樣本" />
        <ScoreCard label="事件風險" value={risk ? `${Math.round(risk.event * 100)}` : "0"} detail="新聞與 VIX 代理訊號" />
      </section>
      <section className="grid">
        <article className="panel span-2">
          {risk ? <RiskPanel risk={sanitizeRiskScore(risk)} /> : <p className="muted-copy">目前沒有高風險觀察項目。</p>}
        </article>
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Watchlist</p>
              <h2>風險觀察列表</h2>
            </div>
          </div>
          <div className="signal-list">
            {highRisk.signals.map((signal) => {
              return (
                <a className="signal" href={`/stocks/${signal.stock_id}`} key={signal.stock_id}>
                  <div>
                    <strong>{signal.stock_id} {signal.stock_name}</strong>
                    <span>上漲機率 {toPercent(signal.probability_up_1d ?? 0)}%</span>
                  </div>
                  <b>{Math.round(signal.risk_score.total * 100)}</b>
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
