"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const refreshIntervalMs = 60_000;

export function MarketAutoRefresh() {
  const router = useRouter();
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  useEffect(() => {
    let lastRefreshAt = Date.now();

    function refreshNow() {
      if (document.visibilityState !== "visible" || navigator.onLine === false) return;
      lastRefreshAt = Date.now();
      setLastRefresh(new Date(lastRefreshAt));
      router.refresh();
    }

    const interval = window.setInterval(refreshNow, refreshIntervalMs);
    const onVisible = () => {
      if (document.visibilityState === "visible" && Date.now() - lastRefreshAt >= refreshIntervalMs) {
        refreshNow();
      }
    };

    document.addEventListener("visibilitychange", onVisible);
    return () => {
      window.clearInterval(interval);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [router]);

  return (
    <div className="refresh-indicator" aria-live="polite">
      <span>自動更新</span>
      <strong>新聞每 1 分鐘</strong>
      <small>{lastRefresh ? `上次同步 ${lastRefresh.toLocaleTimeString("zh-TW", { hour12: false })}` : "等待首次同步"}</small>
    </div>
  );
}
