import type { FactorScore } from "@/lib/api";
import { sanitizeDisplayText, toFactorScore } from "@/lib/view-model";

export function FactorBreakdown({
  positiveDrivers,
  negativeDrivers,
  riskFactors = [],
}: {
  positiveDrivers: FactorScore[];
  negativeDrivers: FactorScore[];
  riskFactors?: string[];
}) {
  return (
    <div className="driver-list">
      {positiveDrivers.map((driver) => (
        <div className="driver positive-border" key={driver.name}>
          <div className="driver-title">
            <strong>{driver.name}</strong>
            <b>{toFactorScore(driver.score)}</b>
          </div>
          <span>{sanitizeDisplayText(driver.explanation)}</span>
        </div>
      ))}
      {negativeDrivers.map((driver) => (
        <div className="driver negative-border" key={driver.name}>
          <div className="driver-title">
            <strong>{driver.name}</strong>
            <b>{toFactorScore(driver.score)}</b>
          </div>
          <span>{sanitizeDisplayText(driver.explanation)}</span>
        </div>
      ))}
      {riskFactors.map((factor) => (
        <div className="driver risk-border" key={factor}>
          <strong>{factor}</strong>
          <span>風險係數觀察項目</span>
        </div>
      ))}
    </div>
  );
}
