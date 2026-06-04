import { StockSearch } from "@/components/StockSearch";
import type { PredictionSignal, StockInstrument } from "@/lib/api";
import { classifySignal } from "@/lib/industry-classification";
import { buildStockMetrics, DISCLAIMER_TEXT } from "@/lib/view-model";

function buildAiSummary(signal: PredictionSignal): string {
  const classification = classifySignal(signal);
  const metrics = buildStockMetrics(signal);
  const newsHint = signal.news[0]?.event_type || signal.news[0]?.title;
  return `${signal.name} 目前歸在「${classification.major.name}」，主要小分類是「${classification.subcategories.slice(0, 3).join("、")}」。新手可以先把它想成：${classification.major.beginnerSummary} 系統再用法人籌碼 ${metrics.chipScore}、技術量價 ${metrics.technicalScore}、基本面 ${metrics.fundamentalScore}、新聞 ${metrics.newsScore} 與風險 ${metrics.riskScore} 量化進觀察分數。${newsHint ? `近期可留意「${newsHint}」。` : ""}`;
}

export function StockAiSelector({ signal, stocks }: { signal: PredictionSignal; stocks: StockInstrument[] }) {
  const classification = classifySignal(signal);
  const themes = classification.themeWeights;

  return (
    <section className="panel stock-ai-selector">
      <div className="stock-ai-picker">
        <p className="eyebrow">選擇股票</p>
        <h2>想看哪一檔？</h2>
        <p>輸入代號、公司名或產業，切換後會自動整理公司在做什麼、相關題材與觀察比例。</p>
        <StockSearch stocks={stocks} compact />
        <small className="compact-compliance-line">{DISCLAIMER_TEXT}</small>
      </div>

      <div className="stock-ai-brief">
        <div>
          <p className="eyebrow">AI 快速說明</p>
          <h2>{signal.symbol} {signal.name} 在做什麼？</h2>
          <p>{buildAiSummary(signal)}</p>
          <div className="industry-tags compact-tags">
            <b>{classification.major.name}</b>
            {classification.subcategories.slice(0, 4).map((subcategory) => <b key={subcategory}>{subcategory}</b>)}
          </div>
        </div>
        <div className="theme-bars" aria-label="題材比例">
          <p className="eyebrow">題材比例</p>
          {themes.map((theme) => (
            <div className="theme-row" key={theme.label} title={theme.note}>
              <span>{theme.label}</span>
              <div className="theme-track">
                <i style={{ width: `${theme.percent}%` }} />
              </div>
              <b>{theme.percent}%</b>
            </div>
          ))}
        </div>
        <div className="theme-source">
          <span>Reference</span>
          <small>{classification.reference}；比例由大分類、小分類、新聞事件、法人籌碼、技術因子、美股連動與風險分數估算。正式資料以交易所、公開資訊觀測站與已授權 API 為準。</small>
        </div>
      </div>
    </section>
  );
}
