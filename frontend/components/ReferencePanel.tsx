import type { PredictionSignal } from "@/lib/api";
import { buildReferences } from "@/lib/view-model";

export function ReferencePanel({ signal }: { signal: PredictionSignal }) {
  const references = buildReferences(signal);

  return (
    <div className="reference-list">
      {references.map((reference) => (
        <div className="reference-item" key={reference}>
          <span>Reference</span>
          <strong>{reference}</strong>
        </div>
      ))}
    </div>
  );
}
