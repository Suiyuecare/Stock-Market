import type { PredictionSignal } from "@/lib/api";
import { buildStockMetrics, scoreTone } from "@/lib/view-model";

export function StockRankingTable({ signals }: { signals: PredictionSignal[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>股票</th>
            <th>上漲機率 1D</th>
            <th>因子分數</th>
            <th>風險係數</th>
            <th>觀察訊號</th>
          </tr>
        </thead>
        <tbody>
          {signals.map((signal) => {
            const metrics = buildStockMetrics(signal);
            const topDriver = signal.positive_drivers[0]?.name ?? "資料觀察中";
            return (
              <tr key={signal.symbol}>
                <td>
                  <a className="stock-link" href={`/stocks/${signal.symbol}`}>
                    <strong>{signal.symbol}</strong>
                    <span>{signal.name}</span>
                  </a>
                </td>
                <td>
                  <b className={scoreTone(metrics.probabilityUp1d)}>{metrics.probabilityUp1d}%</b>
                </td>
                <td>{metrics.bullishScore}</td>
                <td>{metrics.riskScore}</td>
                <td>{topDriver}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
