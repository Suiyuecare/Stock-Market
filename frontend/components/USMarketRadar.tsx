import { signedLabel } from "@/lib/view-model";

export function USMarketRadar({ linkage }: { linkage: Record<string, number> }) {
  return (
    <div className="radar-grid">
      {Object.entries(linkage).map(([name, value]) => (
        <div className="radar-item" key={name}>
          <span>{name}</span>
          <strong className={value >= 0 ? "positive" : "negative"}>{signedLabel(value)}</strong>
        </div>
      ))}
    </div>
  );
}
