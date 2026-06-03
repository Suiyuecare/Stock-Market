"use client";

import { useState } from "react";
import type { PredictionSignal } from "@/lib/api";
import { buildQuoteOverview, buildStockMetrics, formatScore } from "@/lib/view-model";

const tabs = ["行情", "K線", "訊號", "族群", "法人", "大戶"] as const;

type TechnicalTabData = {
  latest_indicators: PredictionSignal["technicals"];
  signals: Record<string, { state?: string; golden_cross?: boolean; death_cross?: boolean }>;
  technical_score: {
    score: number;
    trend_score?: number;
    volume_price_score?: number;
    macd_score?: number;
    rsi_score?: number;
    kd_score?: number;
    breakout_score?: number;
  };
};

type InstitutionalTabData = {
  chip_score: { score: number };
  summary: Record<string, number | boolean | null | undefined>;
};

type RadarTabData = {
  stocks: Array<{
    stock_id: string;
    stock_name: string;
    score: number;
    positive_factors: string[];
  }>;
};

export function StockInsightTabs({
  signal,
  technical,
  institutional,
  radar,
}: {
  signal: PredictionSignal;
  technical: TechnicalTabData;
  institutional: InstitutionalTabData;
  radar: RadarTabData;
}) {
  const [active, setActive] = useState<(typeof tabs)[number]>("行情");
  const quote = buildQuoteOverview(signal);
  const metrics = buildStockMetrics(signal);
  const linkedStocks = radar.stocks.slice(0, 5);

  return (
    <section className="stock-insight-tabs">
      <div className="horizon-tabs" role="tablist" aria-label="個股資訊分類">
        {tabs.map((tab) => (
          <button className={active === tab ? "on" : ""} key={tab} type="button" onClick={() => setActive(tab)}>
            {tab}
          </button>
        ))}
      </div>

      {active === "行情" ? (
        <div className="insight-grid">
          <Metric label="詳細報價" value={`${quote.currentPrice}`} note={`今開 ${quote.open} / 高 ${quote.high} / 低 ${quote.low}`} />
          <Metric label="區間與買賣盤" value={`${quote.limitDown} - ${quote.limitUp}`} note={`內盤 ${quote.innerVolumeLots.toLocaleString()} 張 / 外盤 ${quote.outerVolumeLots.toLocaleString()} 張`} />
          <Metric label="獲利能力" value={`EPS ${quote.epsTtm}`} note={`PE ${quote.peRatio} / 殖利率 ${quote.dividendYield}%`} />
          <Metric label="成交狀態" value={`${quote.volumeLots.toLocaleString()} 張`} note={`成交額 ${quote.turnoverTwd} 億 / 週轉 ${quote.turnoverRate.toFixed(2)}%`} />
        </div>
      ) : null}

      {active === "K線" ? (
        <div className="insight-grid">
          <Metric label="MA5 / MA20 / MA60" value={`${formatScore(signal.technicals.ma_5)} / ${formatScore(signal.technicals.ma_20)} / ${formatScore(signal.technicals.ma_60)}`} note="先用均線結構描述 K 線趨勢，正式版可接完整 OHLC chart。" />
          <Metric label="MACD" value={`${formatScore(signal.technicals.macd_histogram)}`} note={`DIF ${formatScore(signal.technicals.macd)} / DEA ${formatScore(signal.technicals.macd_signal)}`} />
          <Metric label="RSI / KD" value={`${formatScore(signal.technicals.rsi_14)} / ${formatScore(signal.technicals.k_9)}`} note="用於動能與過熱風險量化。" />
          <Metric label="量價背離" value={`${formatScore(signal.technicals.volume_price_divergence)}`} note={String(technical.signals.volume_price_divergence.state ?? "觀察中")} />
        </div>
      ) : null}

      {active === "訊號" ? (
        <div className="insight-grid">
          <Metric label="BullishScore" value={`${metrics.bullishScore}`} note="正向因子加權後分數。" />
          <Metric label="RiskScore" value={`${metrics.riskScore}`} note="波動、流動性、事件風險加總。" />
          <Metric label="RiskAdjustedScore" value={`${metrics.riskAdjustedScore}`} note="扣除風險後的研究分數。" />
          <Metric label="NewsScore" value={`${metrics.newsScore}`} note={`${signal.news.length} 則新聞事件進入量化。`} />
        </div>
      ) : null}

      {active === "族群" ? (
        <div className="mini-table compact">
          {linkedStocks.map((stock) => (
            <a className="mini-row" href={`/stocks/${stock.stock_id}`} key={stock.stock_id}>
              <span>{stock.stock_id} {stock.stock_name}</span>
              <b>{stock.score}</b>
              <small>{stock.positive_factors[0] ?? "同族群連動觀察"}</small>
            </a>
          ))}
        </div>
      ) : null}

      {active === "法人" ? (
        <div className="insight-grid">
          <Metric label="ChipScore" value={`${institutional.chip_score.score}`} note="外資、投信、自營商同步性與量比。" />
          <Metric label="外資買超比" value={`${Number(institutional.summary.foreign_net_ratio ?? 0).toFixed(2)}`} note="以成交量正規化。" />
          <Metric label="投信買超比" value={`${Number(institutional.summary.investment_trust_net_ratio ?? 0).toFixed(2)}`} note="連續買超會加分。" />
          <Metric label="同步買盤" value={institutional.summary.synchronized_institutional_buying ? "是" : "否"} note="三大法人一致性訊號。" />
        </div>
      ) : null}

      {active === "大戶" ? (
        <div className="insight-grid">
          <Metric label="集保/大戶 Reference" value={`${signal.risk_flags?.filter((flag) => flag.source.includes("TDCC")).length ?? 0} 筆`} note="命中 TDCC 股權分散資料時會列入風險分析。" />
          <Metric label="外資持股 Reference" value={`${signal.risk_flags?.filter((flag) => flag.source.includes("外資")).length ?? 0} 筆`} note="TWSE 外資持股 top list reference。" />
          <Metric label="集中度風險" value={`${Math.round(signal.risk_score.concentration * 100)}`} note="集中度越高，訊號防守區要更保守。" />
          <Metric label="流動性風險" value={`${Math.round(signal.risk_score.liquidity * 100)}`} note="低流動性會降低可執行性。" />
        </div>
      ) : null}
    </section>
  );
}

function Metric({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <div className="insight-metric">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </div>
  );
}
