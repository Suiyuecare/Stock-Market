import type { FactorScore } from "@/lib/api";

export function FactorBreakdown({
  positiveDrivers,
  negativeDrivers,
}: {
  positiveDrivers: FactorScore[];
  negativeDrivers: FactorScore[];
}) {
  return (
    <div className="driver-list">
      {positiveDrivers.map((driver) => (
        <div className="driver positive-border" key={driver.name}>
          <strong>{driver.name}</strong>
          <span>{driver.explanation}</span>
        </div>
      ))}
      {negativeDrivers.map((driver) => (
        <div className="driver negative-border" key={driver.name}>
          <strong>{driver.name}</strong>
          <span>{driver.explanation}</span>
        </div>
      ))}
    </div>
  );
}
