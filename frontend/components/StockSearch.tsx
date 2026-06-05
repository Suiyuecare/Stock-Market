"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import type { StockInstrument } from "@/lib/api";
import { classifyInstrument } from "@/lib/industry-classification";

const stockSearchUniverse: StockInstrument[] = [
  { symbol: "1101", market: "TW", name: "台泥", sector: "水泥工業", currency: "TWD" },
  { symbol: "1102", market: "TW", name: "亞泥", sector: "水泥工業", currency: "TWD" },
  { symbol: "1216", market: "TW", name: "統一", sector: "食品工業", currency: "TWD" },
  { symbol: "1301", market: "TW", name: "台塑", sector: "塑膠工業", currency: "TWD" },
  { symbol: "1303", market: "TW", name: "南亞", sector: "塑膠工業", currency: "TWD" },
  { symbol: "1402", market: "TW", name: "遠東新", sector: "紡織纖維", currency: "TWD" },
  { symbol: "1590", market: "TW", name: "亞德客-KY", sector: "電機機械", currency: "TWD" },
  { symbol: "2002", market: "TW", name: "中鋼", sector: "鋼鐵工業", currency: "TWD" },
  { symbol: "2207", market: "TW", name: "和泰車", sector: "汽車工業", currency: "TWD" },
  { symbol: "2301", market: "TW", name: "光寶科", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2303", market: "TW", name: "聯電", sector: "半導體", currency: "TWD" },
  { symbol: "2308", market: "TW", name: "台達電", sector: "電源管理", currency: "TWD" },
  { symbol: "2317", market: "TW", name: "鴻海", sector: "電子代工", currency: "TWD" },
  { symbol: "2324", market: "TW", name: "仁寶", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2330", market: "TW", name: "台積電", sector: "半導體", currency: "TWD" },
  { symbol: "2345", market: "TW", name: "智邦", sector: "通信網路", currency: "TWD" },
  { symbol: "2357", market: "TW", name: "華碩", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2379", market: "TW", name: "瑞昱", sector: "半導體", currency: "TWD" },
  { symbol: "2382", market: "TW", name: "廣達", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2395", market: "TW", name: "研華", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2408", market: "TW", name: "南亞科", sector: "半導體", currency: "TWD" },
  { symbol: "2454", market: "TW", name: "聯發科", sector: "半導體", currency: "TWD" },
  { symbol: "2059", market: "TW", name: "川湖", sector: "伺服器導軌", currency: "TWD" },
  { symbol: "2356", market: "TW", name: "英業達", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2376", market: "TW", name: "技嘉", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2377", market: "TW", name: "微星", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "2383", market: "TW", name: "台光電", sector: "CCL", currency: "TWD" },
  { symbol: "2455", market: "TW", name: "全新", sector: "光通訊", currency: "TWD" },
  { symbol: "2458", market: "TW", name: "義隆", sector: "半導體", currency: "TWD" },
  { symbol: "3017", market: "TW", name: "奇鋐", sector: "散熱", currency: "TWD" },
  { symbol: "3037", market: "TW", name: "欣興", sector: "PCB/載板", currency: "TWD" },
  { symbol: "3081", market: "TPEX", name: "聯亞", sector: "光通訊", currency: "TWD" },
  { symbol: "3189", market: "TW", name: "景碩", sector: "PCB/載板", currency: "TWD" },
  { symbol: "3260", market: "TPEX", name: "威剛", sector: "記憶體模組", currency: "TWD" },
  { symbol: "3324", market: "TPEX", name: "雙鴻", sector: "散熱", currency: "TWD" },
  { symbol: "3515", market: "TPEX", name: "華擎", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "3653", market: "TW", name: "健策", sector: "散熱", currency: "TWD" },
  { symbol: "3665", market: "TW", name: "貿聯-KY", sector: "高速連接器", currency: "TWD" },
  { symbol: "3710", market: "TPEX", name: "連展投控", sector: "光通訊/連接器", currency: "TWD" },
  { symbol: "4971", market: "TPEX", name: "IET-KY", sector: "光通訊", currency: "TWD" },
  { symbol: "4991", market: "TPEX", name: "環宇-KY", sector: "光通訊", currency: "TWD" },
  { symbol: "5274", market: "TPEX", name: "信驊", sector: "半導體", currency: "TWD" },
  { symbol: "6197", market: "TW", name: "佳必琪", sector: "連接器", currency: "TWD" },
  { symbol: "6274", market: "TW", name: "台燿", sector: "CCL", currency: "TWD" },
  { symbol: "6442", market: "TW", name: "光聖", sector: "光通訊", currency: "TWD" },
  { symbol: "6510", market: "TPEX", name: "精測", sector: "半導體", currency: "TWD" },
  { symbol: "8210", market: "TW", name: "勤誠", sector: "伺服器機殼", currency: "TWD" },
  { symbol: "2603", market: "TW", name: "長榮", sector: "航運業", currency: "TWD" },
  { symbol: "2881", market: "TW", name: "富邦金", sector: "金融保險", currency: "TWD" },
  { symbol: "2882", market: "TW", name: "國泰金", sector: "金融保險", currency: "TWD" },
  { symbol: "2884", market: "TW", name: "玉山金", sector: "金融保險", currency: "TWD" },
  { symbol: "2886", market: "TW", name: "兆豐金", sector: "金融保險", currency: "TWD" },
  { symbol: "2891", market: "TW", name: "中信金", sector: "金融保險", currency: "TWD" },
  { symbol: "3008", market: "TW", name: "大立光", sector: "光電業", currency: "TWD" },
  { symbol: "3034", market: "TW", name: "聯詠", sector: "半導體", currency: "TWD" },
  { symbol: "3035", market: "TW", name: "智原", sector: "半導體", currency: "TWD" },
  { symbol: "3231", market: "TW", name: "緯創", sector: "電腦及週邊", currency: "TWD" },
  { symbol: "3661", market: "TW", name: "世芯-KY", sector: "半導體", currency: "TWD" },
  { symbol: "3711", market: "TW", name: "日月光投控", sector: "半導體", currency: "TWD" },
  { symbol: "4938", market: "TW", name: "和碩", sector: "電子代工", currency: "TWD" },
  { symbol: "6147", market: "TPEX", name: "頎邦", sector: "半導體", currency: "TWD" },
  { symbol: "6187", market: "TPEX", name: "萬潤", sector: "半導體設備", currency: "TWD" },
  { symbol: "6223", market: "TPEX", name: "旺矽", sector: "半導體", currency: "TWD" },
  { symbol: "6488", market: "TPEX", name: "環球晶", sector: "半導體", currency: "TWD" },
  { symbol: "8069", market: "TPEX", name: "元太", sector: "光電業", currency: "TWD" },
];

export function StockSearch({ stocks = stockSearchUniverse, compact = false }: { stocks?: StockInstrument[]; compact?: boolean }) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);
  const keyword = query.trim();

  const results = useMemo(() => {
    const normalizedKeyword = query.trim().toLowerCase();
    const normalizedStocks = stocks.filter((stock) => /^\d{4}$/.test(stock.symbol));
    if (!normalizedKeyword) return compact ? [] : normalizedStocks.slice(0, 8);
    return normalizedStocks
      .filter((stock) => {
        const haystack = `${stock.symbol} ${stock.name} ${stock.sector ?? ""} ${stock.market}`.toLowerCase();
        return haystack.includes(normalizedKeyword);
      })
      .slice(0, 8);
  }, [compact, query, stocks]);

  function goToStock(symbol: string): void {
    router.push(`/stocks/${symbol}`);
  }

  function submitSearch(): void {
    const directSymbol = query.trim();
    if (/^\d{4}$/.test(directSymbol)) {
      goToStock(directSymbol);
      return;
    }
    const target = results[activeIndex] ?? results[0];
    if (target) goToStock(target.symbol);
  }

  return (
    <div className={`stock-search ${compact ? "compact" : ""}`} role="search">
      <label htmlFor="stock-search-input">搜尋公司</label>
      <div className="stock-search-box">
        <input
          id="stock-search-input"
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setActiveIndex(0);
          }}
          onKeyDown={(event) => {
            if (event.key === "ArrowDown") {
              event.preventDefault();
              setActiveIndex((index) => Math.min(index + 1, Math.max(0, results.length - 1)));
            }
            if (event.key === "ArrowUp") {
              event.preventDefault();
              setActiveIndex((index) => Math.max(0, index - 1));
            }
            if (event.key === "Enter") {
              event.preventDefault();
              submitSearch();
            }
          }}
          placeholder="輸入代號、公司名、產業"
          type="search"
        />
        <button type="button" onClick={submitSearch} aria-label="前往搜尋結果">
          搜尋
        </button>
      </div>
      <div className="stock-search-results" aria-live="polite">
        {results.length > 0 ? (
          results.map((stock, index) => (
            <button
              className={index === activeIndex ? "on" : ""}
              key={stock.symbol}
              onMouseEnter={() => setActiveIndex(index)}
              onClick={() => goToStock(stock.symbol)}
              type="button"
            >
              <strong>{stock.symbol}</strong>
              <span>{stock.name}</span>
              <small>{stock.market === "TPEX" ? "上櫃" : "上市"} · {formatStockClassification(stock)}</small>
            </button>
          ))
        ) : keyword ? (
          <p>找不到符合的公司，請改用股票代號或公司簡稱。</p>
        ) : compact ? null : (
          <p>輸入代號、公司名或產業，系統會列出可查看的股票。</p>
        )}
      </div>
    </div>
  );
}

function formatStockClassification(stock: StockInstrument): string {
  const classification = classifyInstrument(stock);
  return `${classification.major.shortName} · ${classification.subcategories.slice(0, 2).join(" / ")}`;
}
