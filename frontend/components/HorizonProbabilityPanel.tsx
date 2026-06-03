"use client";

import { useMemo, useState } from "react";
import type { PredictionSignal } from "@/lib/api";
import { buildStockMetrics, buildTargetPriceRange, scoreTone } from "@/lib/view-model";

const horizons = [
  { key: "1D", label: "1D", targetKey: "probabilityUp1d", lift: 0.35, suitability: "短期觀察" },
  { key: "5D", label: "5D", targetKey: "probabilityUp5d", lift: 1, suitability: "短線到波段" },
  { key: "20D", label: "20D", targetKey: "probabilityUp20d", lift: 1.55, suitability: "中期觀察" },
] as const;

export function HorizonProbabilityPanel({ signal }: { signal: PredictionSignal }) {
  const [active, setActive] = useState<(typeof horizons)[number]["key"]>("5D");
  const metrics = buildStockMetrics(signal);
  const range = buildTargetPriceRange(signal);
  const current = horizons.find((item) => item.key === active) ?? horizons[1];
  const probability = metrics[current.targetKey];
  const targetAmount = Math.round(range.currentPrice + (range.base - range.currentPrice) * current.lift);
  const defensePrice = Math.max(1, Math.round(range.currentPrice * (metrics.riskScore > 55 ? 0.94 : 0.96)));
  const observation = useMemo(() => {
    const pass = probability >= 60 && metrics.riskScore <= 55 && metrics.riskAdjustedScore >= 50;
    if (!pass) return { label: "否", tone: "negative" as const, reason: "機率、風險或風險調整分數尚未同時通過門檻。" };
    return { label: "是", tone: "positive" as const, reason: `${current.suitability}，但仍需搭配停損、防守區與資料來源交叉確認。` };
  }, [current.suitability, metrics.riskAdjustedScore, metrics.riskScore, probability]);

  return (
    <section className="horizon-panel">
      <div className="horizon-tabs" role="tablist" aria-label="選擇預測週期">
        {horizons.map((item) => (
          <button className={item.key === active ? "on" : ""} key={item.key} type="button" onClick={() => setActive(item.key)}>
            {item.label}
          </button>
        ))}
      </div>
      <div className="horizon-main">
        <div>
          <span>{active} 上漲機率</span>
          <strong className={scoreTone(probability)}>{probability}%</strong>
          <small>所有數值會回寫到機率分析：基本面、籌碼、技術、新聞、美股連動、風險。</small>
        </div>
        <div>
          <span>{active} 目標金額</span>
          <strong>{targetAmount}</strong>
          <small>上升區段 {range.currentPrice} → {targetAmount}，防守區段約 {defensePrice}。</small>
        </div>
        <div>
          <span>是否列入觀察</span>
          <strong className={observation.tone}>{observation.label}</strong>
          <small>{observation.reason}</small>
        </div>
      </div>
    </section>
  );
}
