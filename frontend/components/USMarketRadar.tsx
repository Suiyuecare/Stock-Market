export function USMarketRadar({ linkage }: { linkage: Record<string, number> }) {
  return (
    <div className="radar-grid">
      {Object.entries(linkage).map(([name, value]) => (
        <div className="radar-item" key={name}>
          <span>{name}</span>
          <strong className={value >= 0 ? "positive" : "negative"}>{Math.round(value * 100)}</strong>
        </div>
      ))}
    </div>
  );
}
