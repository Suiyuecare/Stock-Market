import type { PredictionSignal } from "@/lib/api";
import { sanitizeDisplayText } from "@/lib/view-model";

const stockNameMap: Record<string, string> = {
  "2303": "聯電",
  "2308": "台達電",
  "2317": "鴻海",
  "2330": "台積電",
  "2345": "智邦",
  "2357": "華碩",
  "2382": "廣達",
  "2408": "南亞科",
  "2454": "聯發科",
  "2603": "長榮",
  "2609": "陽明",
  "2615": "萬海",
  "2881": "富邦金",
  "2882": "國泰金",
  "2884": "玉山金",
  "2885": "元大金",
  "2886": "兆豐金",
  "2891": "中信金",
  "3008": "大立光",
  "3034": "聯詠",
  "3035": "智原",
  "3231": "緯創",
  "3661": "世芯-KY",
  "3711": "日月光投控",
  "4938": "和碩",
  "6147": "頎邦",
  "6187": "萬潤",
  "6223": "旺矽",
  "6488": "環球晶",
  "6669": "緯穎",
  "8069": "元太",
  AAPL: "Apple",
  AMD: "AMD",
  AVGO: "Broadcom",
  MU: "Micron",
  NVDA: "NVIDIA",
};

export function RelatedStockNewsPanel({ signal }: { signal: PredictionSignal }) {
  const rows = buildRelatedNewsRows(signal);

  if (rows.length === 0) {
    return (
      <div className="related-news-empty">
        <strong>目前沒有明確命中的相關股票新聞</strong>
        <span>若新聞只命中產業背景，系統會先放在下方時間線，等 OpenAI/新聞 provider 授權後再做更細的公司對應。</span>
      </div>
    );
  }

  return (
    <div className="related-news-grid">
      {rows.map((row) => {
        const isTaiwanStock = /^\d{4}$/.test(row.symbol);
        const content = (
          <>
            <div className="related-news-title">
              <strong>{row.symbol}</strong>
              <span>{row.name}</span>
              <b>{row.sentiment}</b>
            </div>
            <p>{sanitizeDisplayText(row.title)}</p>
            <small>{row.source} · {row.reason}</small>
          </>
        );
        return isTaiwanStock ? (
          <a className="related-news-card" href={`/stocks/${row.symbol}`} key={`${row.symbol}-${row.title}`}>
            {content}
          </a>
        ) : (
          <div className="related-news-card" key={`${row.symbol}-${row.title}`}>
            {content}
          </div>
        );
      })}
    </div>
  );
}

function buildRelatedNewsRows(signal: PredictionSignal): Array<{
  symbol: string;
  name: string;
  title: string;
  source: string;
  sentiment: string;
  reason: string;
}> {
  const rows = signal.news.flatMap((event) => {
    const symbols = event.related_symbols
      .filter((symbol) => symbol !== signal.symbol)
      .filter((symbol, index, all) => all.indexOf(symbol) === index)
      .slice(0, 5);
    return symbols.map((symbol) => ({
      symbol,
      name: stockNameMap[symbol] ?? "關聯標的",
      title: event.title,
      source: event.source,
      sentiment: event.sentiment,
      reason: event.linkage_reason ?? "依公司名稱、產業或供應鏈關鍵字連動",
    }));
  });

  const seen = new Set<string>();
  return rows.filter((row) => {
    const key = `${row.symbol}-${row.title}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  }).slice(0, 12);
}
