import type { PredictionSignal } from "@/lib/api";

export function MACDPanel({ signal }: { signal: PredictionSignal }) {
  const histogram = signal.technicals.macd_histogram ?? 0;
  const macd = signal.technicals.macd ?? 0;
  const signalLine = signal.technicals.macd_signal ?? 0;
  const status = histogram >= 0 ? "MACD 柱狀體偏正向" : "MACD 柱狀體偏弱";

  return (
    <div className="stack">
      <div className="status-row">
        <span>MACD 狀態</span>
        <strong className={histogram >= 0 ? "positive" : "negative"}>{status}</strong>
      </div>
      <div className="mini-metrics">
        <div>
          <span>DIF</span>
          <b>{macd.toFixed(2)}</b>
        </div>
        <div>
          <span>DEA</span>
          <b>{signalLine.toFixed(2)}</b>
        </div>
        <div>
          <span>Histogram</span>
          <b>{histogram.toFixed(2)}</b>
        </div>
        <div>
          <span>台股柱</span>
          <b>{(histogram * 2).toFixed(2)}</b>
        </div>
      </div>
    </div>
  );
}
