import type { PredictionSignal } from "@/lib/api";
import { buildQuoteOverview, buildStockMetrics, scoreTone } from "@/lib/view-model";

export function StockQuoteOverview({ signal }: { signal: PredictionSignal }) {
  const quote = buildQuoteOverview(signal);
  const metrics = buildStockMetrics(signal);
  const changeTone = quote.change >= 0 ? "positive" : "negative";
  const marketLabel = signal.quote?.source === "TPEx OpenAPI"
    ? "上櫃"
    : signal.quote?.source === "TWSE OpenAPI" || signal.quote?.source === "TWSE Official STOCK_DAY"
      ? "上市"
      : "台股";
  const quoteRows: Array<[string, string | number]> = [
    ["今開", quote.open],
    ["最高", quote.high],
    ["最低", quote.low],
    ["昨收", quote.previousClose],
    ["均價", quote.averagePrice],
    ["成交量", `${quote.volumeLots.toLocaleString()} 張`],
    ["成交額", `${quote.turnoverTwd} 億`],
    ["振幅", `${quote.amplitude.toFixed(2)}%`],
    ["週轉率", `${quote.turnoverRate.toFixed(2)}%`],
    ["本益比", quote.peRatio],
    ["市值", `${quote.marketCapTwd} 億`],
    ["殖利率", `${quote.dividendYield}%`],
  ];
  const rangeRows: Array<[string, string | number]> = [
    ["漲停", quote.limitUp],
    ["跌停", quote.limitDown],
    ["52W 高", quote.high52w],
    ["52W 低", quote.low52w],
    ["內盤量", `${quote.innerVolumeLots.toLocaleString()} 張`],
    ["外盤量", `${quote.outerVolumeLots.toLocaleString()} 張`],
  ];
  const financeRows: Array<[string, string | number]> = [
    ["近四季 EPS", quote.epsTtm],
    ["毛利率", `${quote.grossMargin}%`],
    ["營益率", `${quote.operatingMargin}%`],
    ["淨利率", `${quote.netMargin}%`],
  ];

  return (
    <section className="quote-overview">
      <div className="quote-main">
        <div>
          <span className="market-chip">{marketLabel} · {quote.marketStatus}</span>
          <h2>{signal.name} {signal.symbol}</h2>
          <small>{quote.quoteTime}</small>
        </div>
        <div>
          <strong>{quote.currentPrice.toLocaleString()}</strong>
          <b className={changeTone}>
            {quote.change >= 0 ? "+" : ""}
            {quote.change.toFixed(0)} · {quote.changePercent >= 0 ? "+" : ""}
            {quote.changePercent.toFixed(2)}%
          </b>
        </div>
      </div>

      <div className="quote-signal-strip">
        <div>
          <span>5D 上漲機率</span>
          <b className={scoreTone(metrics.probabilityUp5d)}>{metrics.probabilityUp5d}%</b>
        </div>
        <div>
          <span>風險係數</span>
          <b>{metrics.riskScore}</b>
        </div>
        <div>
          <span>風險調整分數</span>
          <b>{metrics.riskAdjustedScore}</b>
        </div>
        <div>
          <span>資料信心</span>
          <b>{Math.round(signal.confidence * 100)}%</b>
        </div>
      </div>

      <div className="quote-detail-grid">
        <QuoteMetricGroup title="詳細報價" rows={quoteRows} />
        <QuoteMetricGroup title="區間與買賣盤" rows={rangeRows} />
        <QuoteMetricGroup title="獲利能力" rows={financeRows} />
      </div>
    </section>
  );
}

function QuoteMetricGroup({ title, rows }: { title: string; rows: Array<[string, string | number]> }) {
  return (
    <div className="quote-metric-group">
      <h3>{title}</h3>
      <dl>
        {rows.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
