import { StockSearch } from "@/components/StockSearch";
import type { PredictionSignal, StockInstrument } from "@/lib/api";
import { buildStockMetrics, DISCLAIMER_TEXT } from "@/lib/view-model";

type ThemeWeight = {
  label: string;
  percent: number;
  note: string;
};

function normalizeThemeWeights(items: Array<Omit<ThemeWeight, "percent"> & { raw: number }>): ThemeWeight[] {
  const total = items.reduce((sum, item) => sum + item.raw, 0) || 1;
  const normalized = items.map((item) => ({
    label: item.label,
    note: item.note,
    percent: Math.max(5, Math.round((item.raw / total) * 100)),
  }));
  const diff = 100 - normalized.reduce((sum, item) => sum + item.percent, 0);
  if (normalized[0]) normalized[0].percent += diff;
  return normalized;
}

function buildThemeWeights(signal: PredictionSignal): ThemeWeight[] {
  const metrics = buildStockMetrics(signal);
  const sector = signal.sector ?? "未分類";
  const sectorText = `${sector} ${signal.news.map((item) => `${item.title} ${item.summary ?? ""} ${item.event_type ?? ""}`).join(" ")}`;

  if (/半導體|電子|電腦|週邊|通信|光電|IC|封測|PCB|CCL|散熱|伺服器/i.test(sectorText)) {
    return normalizeThemeWeights([
      { label: "AI / 美股科技", raw: metrics.usMarketScore + metrics.newsScore * 0.45 + 24, note: "看 SOX、NVDA、TSM ADR、雲端與 AI 需求連動" },
      { label: "供應鏈位置", raw: metrics.fundamentalScore * 0.55 + metrics.usMarketScore * 0.35 + 18, note: "由產業分類、相關新聞與美股連動推估" },
      { label: "法人籌碼", raw: metrics.chipScore + 8, note: "外資、投信、自營商與成交量比重" },
      { label: "技術與量價", raw: metrics.technicalScore + 6, note: "K 線、均線、MACD、KD、量價確認" },
    ]);
  }

  if (/金融|保險|銀行|金控/i.test(sectorText)) {
    return normalizeThemeWeights([
      { label: "利率與金融環境", raw: metrics.fundamentalScore + 18, note: "金融股較受利率、景氣與信用循環影響" },
      { label: "法人籌碼", raw: metrics.chipScore + 12, note: "觀察法人是否同步加碼或轉弱" },
      { label: "風險控管", raw: metrics.riskScore + 10, note: "波動、金融事件與大盤風險" },
      { label: "新聞事件", raw: metrics.newsScore + 6, note: "法說、獲利、政策與配息消息" },
    ]);
  }

  if (/航運|貨櫃|航空|運輸/i.test(sectorText)) {
    return normalizeThemeWeights([
      { label: "景氣循環", raw: metrics.fundamentalScore + metrics.newsScore * 0.4 + 16, note: "運價、需求與供給循環" },
      { label: "油價成本", raw: metrics.riskScore + 12, note: "能源成本與匯率波動會影響利潤" },
      { label: "法人籌碼", raw: metrics.chipScore + 8, note: "觀察短線資金流向" },
      { label: "技術與量價", raw: metrics.technicalScore + 6, note: "適合搭配均線與成交量確認" },
    ]);
  }

  if (/水泥|塑膠|鋼鐵|化學|油電|建材/i.test(sectorText)) {
    return normalizeThemeWeights([
      { label: "原物料報價", raw: metrics.newsScore + metrics.riskScore * 0.35 + 18, note: "原料、能源與報價變化會影響毛利" },
      { label: "景氣循環", raw: metrics.fundamentalScore + 12, note: "營收、庫存與需求回溫是重點" },
      { label: "法人籌碼", raw: metrics.chipScore + 8, note: "觀察法人是否提前布局景氣循環" },
      { label: "技術與量價", raw: metrics.technicalScore + 6, note: "確認突破是否有成交量支持" },
    ]);
  }

  return normalizeThemeWeights([
    { label: "產業基本面", raw: metrics.fundamentalScore + 12, note: "營收、獲利能力與產業分類" },
    { label: "市場資金", raw: metrics.chipScore + metrics.technicalScore * 0.4 + 8, note: "法人籌碼與量價是否同步" },
    { label: "新聞題材", raw: metrics.newsScore + 8, note: "近期事件、產業新聞與公司消息" },
    { label: "風險變數", raw: metrics.riskScore + 6, note: "波動、流動性與重大事件風險" },
  ]);
}

function buildAiSummary(signal: PredictionSignal): string {
  const sector = signal.sector ?? "未分類產業";
  const metrics = buildStockMetrics(signal);
  const newsHint = signal.news[0]?.event_type || signal.news[0]?.title;

  if (/半導體|電子|電腦|週邊|通信|光電|IC|封測|PCB|CCL|散熱|伺服器/i.test(sector)) {
    return `${signal.name} 屬於 ${sector}，可以先用「供應鏈題材、法人籌碼、技術量價、美股科技連動」四個角度看懂。系統目前給它的美股連動分數是 ${metrics.usMarketScore}，代表 SOX、TSM ADR、AI 相關美股與新聞事件會明顯影響短線觀察。`;
  }

  if (/金融|保險|銀行|金控/i.test(sector)) {
    return `${signal.name} 屬於 ${sector}，重點通常在利率環境、金融景氣、資產品質與配息預期。系統目前會把法人籌碼、風險分數與新聞事件一起納入機率分析。`;
  }

  if (/航運|貨櫃|航空|運輸/i.test(sector)) {
    return `${signal.name} 屬於 ${sector}，較容易受到運價、油價、景氣循環與法人短線資金影響。若新聞出現運價或需求變化，系統會把它量化到新聞與風險分數。`;
  }

  return `${signal.name} 目前歸類在 ${sector}。系統會從營收獲利、法人籌碼、技術量價、新聞事件與風險係數交叉檢查，協助新手先理解它跟哪些題材有關。${newsHint ? `近期可留意「${newsHint}」。` : ""}`;
}

export function StockAiSelector({ signal, stocks }: { signal: PredictionSignal; stocks: StockInstrument[] }) {
  const themes = buildThemeWeights(signal);

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
        </div>
        <div className="theme-bars" aria-label="題材比例">
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
          <small>比例由產業分類、新聞事件、法人籌碼、技術因子、美股連動與風險分數估算；正式資料以交易所、公開資訊觀測站與已授權 API 為準。</small>
        </div>
      </div>
    </section>
  );
}
