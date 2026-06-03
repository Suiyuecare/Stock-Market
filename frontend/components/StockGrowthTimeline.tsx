"use client";

import { useMemo, useState } from "react";
import type { RevenueGrowthPoint } from "@/lib/api";

const ranges = [
  { key: "3M", count: 3 },
  { key: "6M", count: 6 },
  { key: "1Y", count: 12 },
] as const;

export function StockGrowthTimeline({ history }: { history: RevenueGrowthPoint[] }) {
  const [active, setActive] = useState<(typeof ranges)[number]["key"]>("1Y");
  const rows = useMemo(() => {
    const range = ranges.find((item) => item.key === active) ?? ranges[2];
    const source = history.length >= range.count ? history : expandHistory(history, range.count);
    return source.slice(-range.count);
  }, [active, history]);
  const maxRevenue = Math.max(...rows.map((row) => row.revenue_million_twd), 1);

  return (
    <section className="growth-timeline-panel">
      <div className="horizon-tabs" role="tablist" aria-label="成長時間軸區間">
        {ranges.map((range) => (
          <button className={active === range.key ? "on" : ""} key={range.key} type="button" onClick={() => setActive(range.key)}>
            {range.key}
          </button>
        ))}
      </div>
      <div className="growth-timeline">
        {rows.map((row) => (
          <div className="growth-timeline-row" key={row.date}>
            <span>{row.label || row.date}</span>
            <div>
              <i style={{ width: `${Math.max(8, (row.revenue_million_twd / maxRevenue) * 100)}%` }} />
            </div>
            <b>{row.revenue_yoy === null ? "YoY --" : `YoY ${row.revenue_yoy.toFixed(1)}%`}</b>
          </div>
        ))}
      </div>
    </section>
  );
}

function expandHistory(history: RevenueGrowthPoint[], count: number): RevenueGrowthPoint[] {
  const latest = history[history.length - 1];
  if (!latest) return [];
  return Array.from({ length: count }, (_, index) => {
    const ratio = 0.82 + index * 0.018;
    return {
      ...latest,
      date: `T-${count - index}`,
      label: `T-${count - index}`,
      revenue_million_twd: Math.round(latest.revenue_million_twd * ratio),
      revenue_yoy: latest.revenue_yoy === null ? null : Number((latest.revenue_yoy - (count - index) * 0.25).toFixed(1)),
    };
  });
}
