"use client";

import { AreaSeries, ColorType, createChart } from "lightweight-charts";
import { useEffect, useMemo, useRef } from "react";
import type { DataSourceReference, RevenueGrowthPoint } from "@/lib/api";

function formatPercent(value: number | null) {
  if (value === null || !Number.isFinite(value)) return "待補";
  return `${value > 0 ? "+" : ""}${value.toFixed(1)}%`;
}

function formatRevenue(value: number) {
  if (value >= 10000) return `${(value / 10000).toFixed(1)} 億`;
  return `${Math.round(value).toLocaleString("zh-TW")} 百萬`;
}

export function GrowthCurvePanel({
  history,
  source,
}: {
  history: RevenueGrowthPoint[];
  source: DataSourceReference;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const points = useMemo(
    () =>
      history
        .filter((point) => Number.isFinite(point.revenue_million_twd))
        .map((point) => ({
          time: point.date,
          value: point.revenue_million_twd,
        })),
    [history],
  );
  const latest = history.at(-1);

  useEffect(() => {
    if (!containerRef.current || points.length === 0) return;

    const chart = createChart(containerRef.current, {
      height: 280,
      layout: {
        background: { type: ColorType.Solid, color: "#ffffff" },
        textColor: "#314155",
      },
      grid: {
        horzLines: { color: "#edf2f7" },
        vertLines: { color: "#edf2f7" },
      },
      rightPriceScale: {
        borderVisible: false,
      },
      timeScale: {
        borderVisible: false,
        timeVisible: false,
      },
      crosshair: {
        vertLine: { color: "#0f766e" },
        horzLine: { color: "#0f766e" },
      },
    });

    const series = chart.addSeries(AreaSeries, {
      lineColor: "#0f766e",
      lineWidth: 2,
      topColor: "rgba(15, 118, 110, 0.22)",
      bottomColor: "rgba(37, 99, 235, 0.03)",
      priceFormat: {
        type: "price",
        precision: 0,
        minMove: 1,
      },
    });

    series.setData(points);
    chart.timeScale().fitContent();

    const resizeObserver = new ResizeObserver(([entry]) => {
      chart.applyOptions({ width: entry.contentRect.width });
    });
    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
    };
  }, [points]);

  return (
    <div className="growth-panel">
      <div className="growth-summary">
        <div>
          <span>最新月營收</span>
          <strong>{latest ? formatRevenue(latest.revenue_million_twd) : "待補"}</strong>
          <small>{latest?.date ?? "等待資料"} · TWD</small>
        </div>
        <div className="growth-metrics">
          <div>
            <span>YoY</span>
            <b className={(latest?.revenue_yoy ?? 0) >= 0 ? "positive" : "negative"}>{formatPercent(latest?.revenue_yoy ?? null)}</b>
          </div>
          <div>
            <span>MoM</span>
            <b className={(latest?.revenue_mom ?? 0) >= 0 ? "positive" : "negative"}>{formatPercent(latest?.revenue_mom ?? null)}</b>
          </div>
          <div>
            <span>累計 YoY</span>
            <b className={(latest?.accumulated_yoy ?? 0) >= 0 ? "positive" : "negative"}>{formatPercent(latest?.accumulated_yoy ?? null)}</b>
          </div>
        </div>
      </div>
      <div className="growth-chart" ref={containerRef} />
      <div className="growth-source">
        <div>
          <span>Reference API</span>
          <strong>{source.dataset}</strong>
          <small>公布日：{source.published_at}</small>
        </div>
        <a href={source.url} target="_blank" rel="noreferrer">
          TWSE OpenAPI
        </a>
      </div>
      <p className="muted-copy">{source.note}</p>
    </div>
  );
}
