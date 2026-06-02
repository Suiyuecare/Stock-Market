import type { PredictionSignal } from "@/lib/api";
import { buildBacktestConfidenceProfile } from "@/lib/view-model";

export function BacktestConfidencePanel({ signal }: { signal: PredictionSignal }) {
  const profile = buildBacktestConfidenceProfile(signal);

  return (
    <div className="backtest-panel">
      <div className="backtest-summary">
        <div>
          <span>策略版本</span>
          <strong>{profile.strategyVersion}</strong>
          <small>{profile.mainTarget} · {profile.entryRule}</small>
        </div>
        <div className="confidence-badge">
          <span>{profile.confidenceLabel}</span>
          <b>{profile.signalDecision}</b>
        </div>
      </div>

      <div className="backtest-metrics">
        <div>
          <span>相似樣本</span>
          <b>{profile.sampleCount}</b>
        </div>
        <div>
          <span>歷史勝率</span>
          <b>{profile.winRate}%</b>
        </div>
        <div>
          <span>信賴下限勝率</span>
          <b>{profile.winRateLowerBound}%</b>
        </div>
        <div>
          <span>平均淨報酬</span>
          <b>{profile.averageNetReturn}%</b>
        </div>
        <div>
          <span>Profit Factor</span>
          <b>{profile.profitFactor}</b>
        </div>
        <div>
          <span>最大回撤</span>
          <b>{profile.maxDrawdown}%</b>
        </div>
        <div>
          <span>Sharpe</span>
          <b>{profile.sharpeRatio}</b>
        </div>
        <div>
          <span>校正誤差</span>
          <b>{profile.calibrationError}%</b>
        </div>
      </div>

      <div className="backtest-sections">
        <div>
          <span>有效市場狀態</span>
          <b>{profile.bestMarketRegime}</b>
        </div>
        <div>
          <span>容易失效狀態</span>
          <b>{profile.worstMarketRegime}</b>
        </div>
      </div>

      <div className="backtest-columns">
        <div>
          <h3>通過條件</h3>
          <ul>
            {profile.rejectionChecks.map((check) => (
              <li key={check}>{check}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3>高勝率共振</h3>
          <ul>
            {profile.topPositiveCombinations.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <h3>常見失敗型態</h3>
          <ul>
            {profile.topFailurePatterns.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
