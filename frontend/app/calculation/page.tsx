import { AppShell } from "@/components/AppShell";
import { ComplianceNotice } from "@/components/ComplianceNotice";
import { ScoreCard } from "@/components/ScoreCard";

const factorWeights = [
  {
    name: "基本面",
    weight: "20%",
    inputs: "營收 YoY / MoM、EPS、毛利率、現金流、負債比",
    reason: "看公司體質與成長是否同步改善。",
  },
  {
    name: "法人籌碼",
    weight: "18%",
    inputs: "外資、投信、自營商買賣超，占成交量比例與連續天數",
    reason: "判斷資金是否持續流入，並檢查三大法人是否共振。",
  },
  {
    name: "技術面",
    weight: "17%",
    inputs: "MA、MACD、RSI、KD、OBV、量價背離、突破訊號",
    reason: "確認價格趨勢、動能與成交量是否互相支持。",
  },
  {
    name: "美股連動",
    weight: "15%",
    inputs: "Nasdaq、SOX、TSM ADR、NVDA、AMD、AAPL、VIX",
    reason: "電子、AI、半導體供應鏈會受到美股與 ADR 明顯影響。",
  },
  {
    name: "新聞事件",
    weight: "12%",
    inputs: "重大訊息、營收新聞、產業新聞、情緒、事件可信度",
    reason: "把新聞拆成事件類型、影響方向與信心分數。",
  },
  {
    name: "總經",
    weight: "8%",
    inputs: "利率、匯率、資金環境、市場狀態",
    reason: "調整不同市場環境下的風險與因子有效性。",
  },
  {
    name: "目標價",
    weight: "5%",
    inputs: "法人目標價區間、目前股價、上看空間",
    reason: "用區間方式輔助判斷，不把單一目標價當結論。",
  },
  {
    name: "流動性",
    weight: "5%",
    inputs: "成交量、成交值、滑價、流動性分數",
    reason: "排除成交太薄、回測漂亮但實務不易成交的訊號。",
  },
];

const horizonRules = [
  {
    label: "1D",
    title: "隔日觀察",
    rule: "優先使用 API 回傳 probability_up_1d；若資料不足，採用核心機率作為短線基準。",
    target: "目標金額使用目前價到 5D 基準目標的 35% 區間。",
  },
  {
    label: "5D",
    title: "主模型週期",
    rule: "MVP 主目標是 up_5d_relative，也就是 5 日淨報酬要勝過大盤與交易成本。",
    target: "目標金額使用基準目標價，並搭配風險分數決定防守區。",
  },
  {
    label: "20D",
    title: "中期觀察",
    rule: "優先使用 probability_up_20d；若資料不足，用短線機率與 BullishScore 混合估算。",
    target: "目標金額使用目前價到基準目標的 155% 延伸區間，但會受風險扣分約束。",
  },
];

const signalRules = [
  "上漲機率達 60% 以上，才會進入主要觀察邏輯。",
  "RiskScore 必須低於 55，避免高風險訊號直接排到前面。",
  "RiskAdjustedScore 必須大於 50，代表扣掉風險後仍有研究價值。",
  "若出現重大利空、流動性不足或高檔量價背離，會降級為高風險觀察。",
];

const dataStates = [
  { name: "已連動", detail: "TWSE / TPEx / CNA RSS / TDCC 等公開資料入口與 mock fallback。" },
  { name: "MVP 中性占位", detail: "總經、目標價、流動性在缺少授權資料時採中性或保守值。" },
  { name: "仍需授權", detail: "法人目標價、部分即時行情與商用新聞，需正式資料授權後才能完整啟用。" },
];

export default function CalculationPage() {
  return (
    <AppShell active="/calculation">
      <header className="topbar">
        <div>
          <p className="eyebrow">計算模組</p>
          <h1>把機率分析、因子權重與風險扣分講清楚</h1>
        </div>
        <div className="status ok">MVP 權重 v1</div>
      </header>
      <ComplianceNotice />

      <section className="metric-grid">
        <ScoreCard label="主目標" value="5D 相對勝率" detail="勝過大盤、成本與最小超額報酬" />
        <ScoreCard label="輸出週期" value="1D / 5D / 20D" detail="短線、主模型、中期觀察" />
        <ScoreCard label="風險扣分" value="0.35x" detail="RiskScore 越高，分數扣越多" tone="negative" />
        <ScoreCard label="前台結論" value="是否列入觀察" detail="不輸出買賣指令" />
      </section>

      <section className="grid">
        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">核心公式</p>
              <h2>先算多因子分數，再扣風險</h2>
            </div>
          </div>
          <div className="formula-stack">
            <div className="formula-card">
              <span>BullishScore</span>
              <code>
                0.20 基本面 + 0.18 籌碼 + 0.17 技術 + 0.15 美股連動 + 0.12 新聞 + 0.08 總經 + 0.05 目標價 + 0.05 流動性
              </code>
            </div>
            <div className="formula-card">
              <span>RiskAdjustedScore</span>
              <code>BullishScore - 0.35 x RiskScore</code>
            </div>
            <div className="formula-card">
              <span>Probability</span>
              <code>RiskAdjustedScore 經校正規則轉成 1D / 5D / 20D 上漲機率</code>
            </div>
          </div>
          <p className="muted-copy">
            現階段前台使用可解釋的規則式 MVP。等資料量與回測樣本足夠後，會把機率校正、walk-forward 驗證與模型監控接上，讓機率更接近真實歷史勝率。
          </p>
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">因子權重</p>
              <h2>每個數值都會量化加總到機率分析</h2>
            </div>
          </div>
          <div className="weight-grid">
            {factorWeights.map((factor) => (
              <div className="weight-card" key={factor.name}>
                <div>
                  <span>{factor.name}</span>
                  <strong>{factor.weight}</strong>
                </div>
                <p>{factor.inputs}</p>
                <small>{factor.reason}</small>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">週期邏輯</p>
              <h2>1D / 5D / 20D 怎麼拆</h2>
            </div>
          </div>
          <div className="calculation-list">
            {horizonRules.map((item) => (
              <div className="calculation-row" key={item.label}>
                <b>{item.label}</b>
                <div>
                  <strong>{item.title}</strong>
                  <span>{item.rule}</span>
                  <small>{item.target}</small>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">觀察門檻</p>
              <h2>高機率不代表一定進觀察名單</h2>
            </div>
          </div>
          <ul className="rule-list">
            {signalRules.map((rule) => (
              <li key={rule}>{rule}</li>
            ))}
          </ul>
        </article>

        <article className="panel span-2">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">資料狀態</p>
              <h2>已接 API 與仍需授權資料會分開標示</h2>
            </div>
          </div>
          <div className="data-state-grid">
            {dataStates.map((state) => (
              <div key={state.name}>
                <strong>{state.name}</strong>
                <span>{state.detail}</span>
              </div>
            ))}
          </div>
        </article>
      </section>
    </AppShell>
  );
}
