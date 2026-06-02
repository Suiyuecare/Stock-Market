import type { USMarketRadarResponse } from "@/lib/api";
import { formatScore, sanitizeDisplayText, signedLabel } from "@/lib/view-model";

export function USMarketRadar({
  linkage,
  stocks = [],
}: {
  linkage: Record<string, number>;
  stocks?: USMarketRadarResponse["stocks"];
}) {
  return (
    <div className="radar-stack">
      <div className="radar-grid">
        {Object.entries(linkage).map(([name, value]) => (
          <div className="radar-item" key={name}>
            <span>{name}</span>
            <strong className={value >= 0 ? "positive" : "negative"}>{signedLabel(value)}</strong>
          </div>
        ))}
      </div>
      {stocks.length > 0 ? (
        <div className="mini-table">
          {stocks.slice(0, 5).map((stock) => (
            <a className="mini-row" href={`/stocks/${stock.stock_id}`} key={stock.stock_id}>
              <span>{stock.stock_id} {stock.stock_name}</span>
              <b>{formatScore(stock.score)}</b>
              <small>{sanitizeDisplayText(stock.positive_factors[0] ?? stock.risk_factors[0] ?? "連動訊號觀察中")}</small>
            </a>
          ))}
        </div>
      ) : null}
    </div>
  );
}
