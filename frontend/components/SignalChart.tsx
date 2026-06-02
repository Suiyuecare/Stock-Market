"use client";

import { AreaSeries, ColorType, createChart } from "lightweight-charts";
import { useEffect, useRef } from "react";

const data = [
  { time: "2026-05-24", value: 54 },
  { time: "2026-05-25", value: 57 },
  { time: "2026-05-26", value: 55 },
  { time: "2026-05-27", value: 62 },
  { time: "2026-05-28", value: 66 },
  { time: "2026-05-29", value: 64 },
  { time: "2026-06-01", value: 68 },
];

export function SignalChart() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      height: 260,
      layout: {
        background: { type: ColorType.Solid, color: "#ffffff" },
        textColor: "#27343b",
      },
      grid: {
        horzLines: { color: "#e6eef0" },
        vertLines: { color: "#e6eef0" },
      },
      rightPriceScale: {
        borderVisible: false,
      },
      timeScale: {
        borderVisible: false,
      },
    });

    const series = chart.addSeries(AreaSeries, {
      lineColor: "#177e89",
      topColor: "rgba(23, 126, 137, 0.28)",
      bottomColor: "rgba(23, 126, 137, 0.02)",
    });

    series.setData(data);
    chart.timeScale().fitContent();

    const resizeObserver = new ResizeObserver(([entry]) => {
      chart.applyOptions({ width: entry.contentRect.width });
    });
    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
    };
  }, []);

  return <div className="chart" ref={containerRef} />;
}
