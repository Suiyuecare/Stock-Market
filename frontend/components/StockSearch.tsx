"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import type { StockInstrument } from "@/lib/api";

export function StockSearch({ stocks }: { stocks: StockInstrument[] }) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);

  const results = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    const normalizedStocks = stocks.filter((stock) => /^\d{4}$/.test(stock.symbol));
    if (!keyword) return normalizedStocks.slice(0, 8);
    return normalizedStocks
      .filter((stock) => {
        const haystack = `${stock.symbol} ${stock.name} ${stock.sector ?? ""} ${stock.market}`.toLowerCase();
        return haystack.includes(keyword);
      })
      .slice(0, 8);
  }, [query, stocks]);

  function goToStock(symbol: string): void {
    router.push(`/stocks/${symbol}`);
  }

  function submitSearch(): void {
    const target = results[activeIndex] ?? results[0];
    if (target) goToStock(target.symbol);
  }

  return (
    <div className="stock-search" role="search">
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
              <small>{stock.market === "TPEX" ? "上櫃" : "上市"} · {stock.sector ?? "未分類"}</small>
            </button>
          ))
        ) : (
          <p>找不到符合的公司，請改用股票代號或公司簡稱。</p>
        )}
      </div>
    </div>
  );
}
