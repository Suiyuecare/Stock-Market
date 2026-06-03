"use client";

import { useEffect, useState } from "react";
import { readWatchlist } from "@/components/WatchlistButton";

type WatchlistStock = ReturnType<typeof readWatchlist>[number];

export function WatchlistClient() {
  const [stocks, setStocks] = useState<WatchlistStock[]>([]);

  useEffect(() => {
    const sync = () => setStocks(readWatchlist());
    sync();
    window.addEventListener("suiyue-watchlist-updated", sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener("suiyue-watchlist-updated", sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  function removeStock(symbol: string) {
    const next = stocks.filter((stock) => stock.symbol !== symbol);
    window.localStorage.setItem("suiyue-stock-watchlist", JSON.stringify(next));
    setStocks(next);
  }

  if (stocks.length === 0) {
    return (
      <div className="empty-state">
        <strong>目前還沒有關注股票</strong>
        <span>到「個股明燈」搜尋股票，按下「加入關注」後會出現在這裡。</span>
        <a href="/stocks/2330">先看台積電</a>
      </div>
    );
  }

  return (
    <div className="watchlist-grid">
      {stocks.map((stock) => (
        <article className="watchlist-card" key={stock.symbol}>
          <div>
            <span>{stock.sector ?? "未分類"}</span>
            <h2>{stock.symbol} {stock.name}</h2>
          </div>
          <div className="watchlist-actions">
            <a href={`/stocks/${stock.symbol}`}>看個股明燈</a>
            <button type="button" onClick={() => removeStock(stock.symbol)}>移除</button>
          </div>
        </article>
      ))}
    </div>
  );
}
