import type { PredictionSignal } from "@/lib/api";
import { buildPortfolioAllocation } from "@/lib/view-model";

export function PortfolioAllocationPanel({ signal }: { signal: PredictionSignal }) {
  const allocation = buildPortfolioAllocation(signal);

  return (
    <div className="allocation-list">
      {allocation.map((item) => (
        <div className="allocation-item" key={item.label}>
          <div className="allocation-title">
            <strong>{item.label}</strong>
            <b>{item.percent}%</b>
          </div>
          <div className="allocation-bar">
            <span style={{ width: `${item.percent}%` }} />
          </div>
          <small>{item.reason}</small>
        </div>
      ))}
    </div>
  );
}
