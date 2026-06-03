"use client";

import { CandlestickSeries, ColorType, createChart, HistogramSeries, LineSeries } from "lightweight-charts";
import { useEffect, useMemo, useRef, useState } from "react";
import type { PredictionSignal, RevenueGrowthPoint } from "@/lib/api";
import { estimateCurrentPrice } from "@/lib/view-model";

type RangeKey = "1M" | "3M" | "6M" | "YTD" | "1Y";

type OhlcPoint = {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

const ranges: Array<{ key: RangeKey; label: string; count: number }> = [
  { key: "1M", label: "近一個月", count: 22 },
  { key: "3M", label: "近三個月", count: 66 },
  { key: "6M", label: "近六個月", count: 132 },
  { key: "YTD", label: "今年", count: 120 },
  { key: "1Y", label: "近一年", count: 252 },
];

const MAIN_CHART_HEIGHT = 420;
const VOLUME_CHART_HEIGHT = 180;
const KD_CHART_HEIGHT = 230;

export function StockGrowthTimeline({
  history,
  signal,
}: {
  history: RevenueGrowthPoint[];
  signal: PredictionSignal;
}) {
  const [active, setActive] = useState<RangeKey>("3M");
  const mainRef = useRef<HTMLDivElement>(null);
  const volumeRef = useRef<HTMLDivElement>(null);
  const kdRef = useRef<HTMLDivElement>(null);
  const allRows = useMemo(() => buildOhlcHistory(signal, history), [signal, history]);
  const activeRange = ranges.find((range) => range.key === active) ?? ranges[1];
  const rows = useMemo(() => allRows.slice(-activeRange.count), [activeRange.count, allRows]);
  const latest = rows.at(-1);
  const previous = rows.at(-2);
  const change = latest && previous ? latest.close - previous.close : signal.quote?.change ?? 0;
  const changePercent = previous ? (change / previous.close) * 100 : 0;
  const isUp = change >= 0;

  useEffect(() => {
    if (!mainRef.current || !volumeRef.current || !kdRef.current || rows.length === 0) return;

    const mainChart = createChart(mainRef.current, baseChartOptions(MAIN_CHART_HEIGHT, false));
    const volumeChart = createChart(volumeRef.current, baseChartOptions(VOLUME_CHART_HEIGHT, false));
    const kdChart = createChart(kdRef.current, baseChartOptions(KD_CHART_HEIGHT, true));

    const candleSeries = mainChart.addSeries(CandlestickSeries, {
      upColor: "#ef3b2d",
      downColor: "#65a844",
      borderUpColor: "#ef3b2d",
      borderDownColor: "#65a844",
      wickUpColor: "#ef3b2d",
      wickDownColor: "#65a844",
    });
    const ma20Series = mainChart.addSeries(LineSeries, { color: "#ffbf2f", lineWidth: 2, priceLineVisible: false });
    const ma60Series = mainChart.addSeries(LineSeries, { color: "#ff1493", lineWidth: 2, priceLineVisible: false });
    const volumeSeries = volumeChart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceLineVisible: false,
    });
    const volumeMa5Series = volumeChart.addSeries(LineSeries, { color: "#ffbf2f", lineWidth: 2, priceLineVisible: false });
    const volumeMa20Series = volumeChart.addSeries(LineSeries, { color: "#ff1493", lineWidth: 2, priceLineVisible: false });
    const kSeries = kdChart.addSeries(LineSeries, { color: "#16d7de", lineWidth: 2, priceLineVisible: false });
    const dSeries = kdChart.addSeries(LineSeries, { color: "#ffbf2f", lineWidth: 2, priceLineVisible: false });
    const jSeries = kdChart.addSeries(LineSeries, { color: "#ff1493", lineWidth: 2, priceLineVisible: false });

    candleSeries.setData(rows.map(({ time, open, high, low, close }) => ({ time, open, high, low, close })));
    ma20Series.setData(movingAverage(rows, 20, "close"));
    ma60Series.setData(movingAverage(rows, 60, "close"));
    volumeSeries.setData(rows.map((row) => ({
      time: row.time,
      value: row.volume,
      color: row.close >= row.open ? "#ef3b2d" : "#65a844",
    })));
    volumeMa5Series.setData(movingAverage(rows, 5, "volume"));
    volumeMa20Series.setData(movingAverage(rows, 20, "volume"));

    const kd = stochasticKd(rows);
    kSeries.setData(kd.map((point) => ({ time: point.time, value: point.k })));
    dSeries.setData(kd.map((point) => ({ time: point.time, value: point.d })));
    jSeries.setData(kd.map((point) => ({ time: point.time, value: point.j })));

    mainChart.timeScale().fitContent();
    volumeChart.timeScale().fitContent();
    kdChart.timeScale().fitContent();

    const resizeObserver = new ResizeObserver(([entry]) => {
      mainChart.applyOptions({ width: entry.contentRect.width });
      volumeChart.applyOptions({ width: entry.contentRect.width });
      kdChart.applyOptions({ width: entry.contentRect.width });
    });
    resizeObserver.observe(mainRef.current);

    return () => {
      resizeObserver.disconnect();
      mainChart.remove();
      volumeChart.remove();
      kdChart.remove();
    };
  }, [rows]);

  return (
    <section className="kline-panel">
      <div className="kline-toolbar">
        <div className="kline-quote-line">
          <strong>{formatDate(latest?.time)}</strong>
          <span>開 <b className={toneClass(latest?.open, previous?.close)}>{formatPrice(latest?.open)}</b></span>
          <span>高 <b className={toneClass(latest?.high, previous?.close)}>{formatPrice(latest?.high)}</b></span>
          <span>低 <b className={toneClass(latest?.low, previous?.close)}>{formatPrice(latest?.low)}</b></span>
          <span>收 <b className={isUp ? "taiwan-up" : "taiwan-down"}>{formatPrice(latest?.close)}</b></span>
          <span>
            <b className={isUp ? "taiwan-up" : "taiwan-down"}>
              {change >= 0 ? "↑" : "↓"}{Math.abs(change).toFixed(1)} ({changePercent.toFixed(2)}%)
            </b>
          </span>
          <span>量 <b className={isUp ? "taiwan-up" : "taiwan-down"}>{formatVolume(latest?.volume)}</b></span>
        </div>
        <div className="kline-actions">
          <button type="button">日線</button>
          <button type="button" aria-label="圖表設定">⚙</button>
          <button type="button" aria-label="標註工具">✎</button>
        </div>
      </div>

      <div className="kline-range-tabs" role="tablist" aria-label="K 線時間區間">
        {ranges.map((range) => (
          <button className={active === range.key ? "on" : ""} key={range.key} type="button" onClick={() => setActive(range.key)}>
            {range.label}
          </button>
        ))}
      </div>

      <div className="kline-chart-frame">
        <div className="kline-main-chart" ref={mainRef} />
      </div>
      <div className="kline-chart-frame compact">
        <div className="kline-volume-chart" ref={volumeRef} />
      </div>
      <div className="kline-chart-frame compact">
        <div className="kline-kd-chart" ref={kdRef} />
      </div>
      <div className="kline-legend">
        <span><i className="legend-red" />紅 K：收盤高於開盤</span>
        <span><i className="legend-green" />綠 K：收盤低於開盤</span>
        <span><i className="legend-yellow" />MA20 / KD-D</span>
        <span><i className="legend-pink" />MA60 / KD-J</span>
        <small>最後一根使用 {signal.quote?.source ?? "MVP"} 報價；完整歷史 K 線待接交易所歷史 API，現階段用穩定序列補齊閱讀體驗。</small>
      </div>
    </section>
  );
}

function baseChartOptions(height: number, showTimeScale: boolean) {
  return {
    height,
    layout: {
      background: { type: ColorType.Solid, color: "#ffffff" },
      textColor: "#1f2937",
    },
    grid: {
      horzLines: { color: "#e6e6e6" },
      vertLines: { color: "#f4f4f4" },
    },
    rightPriceScale: {
      borderColor: "#cdd6e4",
    },
    timeScale: {
      borderColor: "#cdd6e4",
      timeVisible: false,
      visible: showTimeScale,
      fixLeftEdge: true,
      fixRightEdge: true,
    },
    crosshair: {
      mode: 1,
    },
  };
}

function buildOhlcHistory(signal: PredictionSignal, revenueHistory: RevenueGrowthPoint[]): OhlcPoint[] {
  const latestClose = signal.quote?.close ?? estimateCurrentPrice(signal);
  const latestOpen = signal.quote?.open ?? latestClose * 0.992;
  const latestHigh = signal.quote?.high ?? Math.max(latestOpen, latestClose) * 1.018;
  const latestLow = signal.quote?.low ?? Math.min(latestOpen, latestClose) * 0.982;
  const latestVolume = Math.max(50, Math.round((signal.quote?.trade_volume ?? 25000000) / 1000));
  const seed = symbolSeed(signal.symbol);
  const days = businessDaysBefore(signal.quote?.date ?? "2026-06-03", 252);
  const revenueMomentum = revenueHistory.at(-1)?.revenue_yoy ?? 0;
  const trend = Math.max(-0.22, Math.min(0.26, revenueMomentum / 160 + (signal.composite_score - 0.5) * 0.18));
  const startClose = latestClose / (1 + trend || 1);
  const rows: OhlcPoint[] = [];
  let close = startClose;

  days.forEach((day, index) => {
    const progress = index / Math.max(1, days.length - 1);
    const wave = Math.sin(index * 0.17 + seed) * 0.018 + Math.cos(index * 0.071 + seed) * 0.012;
    const drift = trend / days.length;
    const dailyMove = drift + wave * 0.22 + seeded(seed + index * 13) * 0.022 - 0.011;
    const open = close * (1 + (seeded(seed + index * 5) - 0.5) * 0.018);
    close = close * (1 + dailyMove);
    const high = Math.max(open, close) * (1 + seeded(seed + index * 7) * 0.028);
    const low = Math.min(open, close) * (1 - seeded(seed + index * 11) * 0.026);
    const volumePulse = 0.7 + seeded(seed + index * 17) * 0.9 + Math.abs(wave) * 9 + progress * 0.2;
    rows.push({
      time: day,
      open: roundPrice(open),
      high: roundPrice(high),
      low: roundPrice(low),
      close: roundPrice(close),
      volume: Math.round(latestVolume * volumePulse),
    });
  });

  const scale = latestClose / Math.max(rows.at(-1)?.close ?? latestClose, 1);
  const scaled = rows.map((row) => ({
    ...row,
    open: roundPrice(row.open * scale),
    high: roundPrice(row.high * scale),
    low: roundPrice(row.low * scale),
    close: roundPrice(row.close * scale),
  }));

  scaled[scaled.length - 1] = {
    time: signal.quote?.date ?? scaled[scaled.length - 1].time,
    open: roundPrice(latestOpen),
    high: roundPrice(latestHigh),
    low: roundPrice(latestLow),
    close: roundPrice(latestClose),
    volume: latestVolume,
  };

  return scaled;
}

function movingAverage(rows: OhlcPoint[], period: number, field: "close" | "volume") {
  return rows
    .map((row, index) => {
      const window = rows.slice(Math.max(0, index - period + 1), index + 1);
      if (window.length < Math.min(period, 3)) return null;
      const value = window.reduce((sum, item) => sum + item[field], 0) / window.length;
      return { time: row.time, value: Number(value.toFixed(field === "volume" ? 0 : 2)) };
    })
    .filter((point): point is { time: string; value: number } => point !== null);
}

function stochasticKd(rows: OhlcPoint[]) {
  let k = 50;
  let d = 50;
  return rows.map((row, index) => {
    const window = rows.slice(Math.max(0, index - 8), index + 1);
    const highest = Math.max(...window.map((item) => item.high));
    const lowest = Math.min(...window.map((item) => item.low));
    const rsv = highest === lowest ? 50 : ((row.close - lowest) / (highest - lowest)) * 100;
    k = k * 2 / 3 + rsv / 3;
    d = d * 2 / 3 + k / 3;
    const j = Math.max(0, Math.min(100, 3 * k - 2 * d));
    return { time: row.time, k: Number(k.toFixed(2)), d: Number(d.toFixed(2)), j: Number(j.toFixed(2)) };
  });
}

function businessDaysBefore(latestDate: string, count: number): string[] {
  const end = Number.isFinite(Date.parse(latestDate)) ? new Date(`${latestDate}T00:00:00+08:00`) : new Date("2026-06-03T00:00:00+08:00");
  const days: string[] = [];
  const cursor = new Date(end);
  while (days.length < count) {
    const day = cursor.getDay();
    if (day !== 0 && day !== 6) days.push(formatIsoDate(cursor));
    cursor.setDate(cursor.getDate() - 1);
  }
  return days.reverse();
}

function formatIsoDate(date: Date): string {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

function formatDate(value?: string): string {
  if (!value) return "資料日期待確認";
  return value.replaceAll("-", "/");
}

function formatPrice(value?: number): string {
  if (typeof value !== "number") return "--";
  return value >= 100 ? value.toFixed(0) : value.toFixed(1);
}

function formatVolume(value?: number): string {
  if (typeof value !== "number") return "--";
  return value.toLocaleString("zh-TW");
}

function roundPrice(value: number): number {
  return Number(value.toFixed(value >= 100 ? 0 : 1));
}

function toneClass(value?: number, base?: number): string {
  if (typeof value !== "number" || typeof base !== "number") return "neutral";
  return value >= base ? "taiwan-up" : "taiwan-down";
}

function symbolSeed(symbol: string): number {
  return symbol.split("").reduce((sum, char, index) => sum + char.charCodeAt(0) * (index + 7), 17);
}

function seeded(value: number): number {
  const raw = Math.sin(value * 12.9898) * 43758.5453;
  return raw - Math.floor(raw);
}
