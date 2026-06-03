import type { PredictionSignal } from "@/lib/api";
import { buildQuoteOverview, buildStockMetrics, scoreTone } from "@/lib/view-model";

export function StockQuoteOverview({ signal }: { signal: PredictionSignal }) {
  const quote = buildQuoteOverview(signal);
  const metrics = buildStockMetrics(signal);
  const changeTone = quote.change >= 0 ? "positive" : "negative";
  const flow = buildOrderFlowBias(quote, metrics);
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
        <QuoteFlowGroup flow={flow} />
        <QuoteMetricGroup title="獲利能力" rows={financeRows} />
      </div>
    </section>
  );
}

function buildOrderFlowBias(
  quote: ReturnType<typeof buildQuoteOverview>,
  metrics: ReturnType<typeof buildStockMetrics>,
) {
  const totalBidAskLots = Math.max(1, quote.innerVolumeLots + quote.outerVolumeLots);
  const buyRatio = quote.outerVolumeLots / totalBidAskLots;
  const sellRatio = quote.innerVolumeLots / totalBidAskLots;
  const orderFlowScore = (buyRatio - sellRatio) * 55;
  const priceScore = quote.changePercent * 4.5;
  const probabilityScore = (metrics.probabilityUp5d - 50) * 0.5;
  const chipScore = (metrics.chipScore - 50) * 0.3;
  const score = orderFlowScore + priceScore + probabilityScore + chipScore;

  if (score >= 18) {
    return {
      label: "買多",
      tone: "buy-strong",
      description: "買方力道明顯較強",
      buyRatio,
      sellRatio,
      confidence: Math.min(90, Math.round(58 + Math.abs(score))),
    };
  }
  if (score >= 4) {
    return {
      label: "買少",
      tone: "buy-light",
      description: "買方略占優勢",
      buyRatio,
      sellRatio,
      confidence: Math.min(82, Math.round(54 + Math.abs(score))),
    };
  }
  if (score <= -18) {
    return {
      label: "賣多",
      tone: "sell-strong",
      description: "賣方力道明顯較強",
      buyRatio,
      sellRatio,
      confidence: Math.min(90, Math.round(58 + Math.abs(score))),
    };
  }
  if (score <= -4) {
    return {
      label: "賣少",
      tone: "sell-light",
      description: "賣方略占優勢",
      buyRatio,
      sellRatio,
      confidence: Math.min(82, Math.round(54 + Math.abs(score))),
    };
  }
  return {
    label: "中性",
    tone: "neutral",
    description: "買賣力道接近",
    buyRatio,
    sellRatio,
    confidence: 52,
  };
}

function QuoteFlowGroup({ flow }: { flow: ReturnType<typeof buildOrderFlowBias> }) {
  return (
    <div className="quote-metric-group quote-flow-group">
      <h3>買賣力道</h3>
      <div className={`flow-badge ${flow.tone}`}>
        <strong>{flow.label}</strong>
        <span>{flow.description}</span>
      </div>
      <dl>
        <div>
          <dt>買方占比</dt>
          <dd>{Math.round(flow.buyRatio * 100)}%</dd>
        </div>
        <div>
          <dt>賣方占比</dt>
          <dd>{Math.round(flow.sellRatio * 100)}%</dd>
        </div>
        <div>
          <dt>量化信心</dt>
          <dd>{flow.confidence}%</dd>
        </div>
        <div>
          <dt>依據</dt>
          <dd>內外盤+漲跌+籌碼</dd>
        </div>
      </dl>
      <small>此欄為盤中/盤後資金傾向估算，不是個人化交易指示。</small>
    </div>
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
