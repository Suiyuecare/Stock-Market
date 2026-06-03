"use client";

import { useEffect, useState } from "react";

type WatchlistStock = {
  symbol: string;
  name: string;
  sector: string | null;
};

const storageKey = "suiyue-stock-watchlist";

export function WatchlistButton({ stock }: { stock: WatchlistStock }) {
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setSaved(readWatchlist().some((item) => item.symbol === stock.symbol));
  }, [stock.symbol]);

  function toggleWatchlist() {
    const current = readWatchlist();
    const exists = current.some((item) => item.symbol === stock.symbol);
    const next = exists ? current.filter((item) => item.symbol !== stock.symbol) : [stock, ...current];
    window.localStorage.setItem(storageKey, JSON.stringify(next.slice(0, 80)));
    setSaved(!exists);
    window.dispatchEvent(new CustomEvent("suiyue-watchlist-updated"));
  }

  return (
    <button className={`watchlist-button ${saved ? "saved" : ""}`} type="button" onClick={toggleWatchlist}>
      {saved ? "已加入關注" : "加入關注"}
    </button>
  );
}

export function readWatchlist(): WatchlistStock[] {
  if (typeof window === "undefined") return [];
  try {
    const parsed = JSON.parse(window.localStorage.getItem(storageKey) ?? "[]");
    return Array.isArray(parsed) ? parsed.filter(isWatchlistStock) : [];
  } catch {
    return [];
  }
}

function isWatchlistStock(value: unknown): value is WatchlistStock {
  if (!value || typeof value !== "object") return false;
  const stock = value as Partial<WatchlistStock>;
  return typeof stock.symbol === "string" && typeof stock.name === "string";
}
