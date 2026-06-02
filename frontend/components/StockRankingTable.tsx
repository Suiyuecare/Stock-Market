import type { PredictionSignal } from "@/lib/api";
import { buildStockMetrics, scoreTone } from "@/lib/view-model";

export function StockRankingTable({ signals }: { signals: PredictionSignal[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>股票</th>
            <th>5D 機率</th>
            <th>因子分數</th>
            <th>風險係數</th>
            <th>為什麼入選</th>
          </tr>
        </thead>
        <tbody>
          {signals.map((signal) => {
            const metrics = buildStockMetrics(signal);
            const topDriver = signal.positive_drivers[0]?.name ?? "多因子資料觀察中";
            return (
              <tr key={signal.symbol}>
                <td>
                  <a className="stock-link" href={`/stocks/${signal.symbol}`}>
                    <strong>{signal.symbol}</strong>
                    <span>{signal.name}</span>
                  </a>
                </td>
                <td>
                  <b className={scoreTone(metrics.probabilityUp5d)}>{metrics.probabilityUp5d}%</b>
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
