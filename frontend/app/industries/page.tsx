import { AppShell } from "@/components/AppShell";
import { ComplianceNotice } from "@/components/ComplianceNotice";
import { ScoreCard } from "@/components/ScoreCard";

const industries = [
  {
    name: "AI 伺服器",
    score: 78,
    trend: "需求延續",
    segments: ["散熱", "電源", "組裝", "高速傳輸"],
    stocks: ["2382 廣達", "3231 緯創", "6669 緯穎", "2308 台達電", "2345 智邦"],
    reason: "NVDA / 雲端資本支出 / 伺服器供應鏈新聞會共同影響。",
  },
  {
    name: "半導體",
    score: 74,
    trend: "先進製程與 AI ASIC 支撐",
    segments: ["IC 設計", "晶圓代工", "封裝", "測試", "矽晶圓"],
    stocks: ["2330 台積電", "2454 聯發科", "3035 智原", "3711 日月光投控", "6488 環球晶"],
    reason: "SOX、TSM ADR、NVDA、AMD、AVGO 與台股法人籌碼共同加權。",
  },
  {
    name: "CCL / PCB",
    score: 69,
    trend: "高速材料升級",
    segments: ["CCL", "載板", "高階 PCB", "HDI"],
    stocks: ["8046 南電", "3037 欣興", "2368 金像電", "2383 台光電"],
    reason: "AI 伺服器與高速網通升級會推升材料與板材需求。",
  },
  {
    name: "散熱",
    score: 72,
    trend: "高功耗平台帶動",
    segments: ["液冷", "均熱片", "風扇", "機殼熱流"],
    stocks: ["3017 奇鋐", "3324 雙鴻", "3653 健策", "2421 建準"],
    reason: "GPU/ASIC 功耗提升，使散熱從零組件變成平台級瓶頸。",
  },
  {
    name: "封裝 / 測試",
    score: 73,
    trend: "CoWoS 與先進封裝吃緊",
    segments: ["先進封裝", "測試介面", "探針卡", "封測"],
    stocks: ["3711 日月光投控", "6223 旺矽", "6147 頎邦", "3264 欣銓"],
    reason: "先進封裝產能、測試時間與 AI 晶片需求形成連動。",
  },
  {
    name: "記憶體",
    score: 63,
    trend: "報價復甦觀察",
    segments: ["DRAM", "NAND", "模組", "HBM"],
    stocks: ["2408 南亞科", "8299 群聯", "2337 旺宏", "2344 華邦電"],
    reason: "MU、HBM 需求、報價週期與庫存變化會進入分數。",
  },
];

export default function IndustriesPage() {
  const rankedIndustries = [...industries].sort((left, right) => right.score - left.score);
  const top = rankedIndustries[0];

  return (
    <AppShell active="/industries">
      <header className="topbar">
        <div>
          <p className="eyebrow">產業明燈</p>
          <h1>最夯族群排在最上面，一路看到冷門觀察</h1>
        </div>
        <div className="status ok">最高族群：{top.name} {top.score}</div>
      </header>
      <ComplianceNotice />

      <section className="metric-grid">
        <ScoreCard label="追蹤族群" value={`${rankedIndustries.length}`} detail="依熱度分數由高到低排序" />
        <ScoreCard label="最高趨勢分" value={`${top.score}`} detail={top.name} tone="positive" />
        <ScoreCard label="細分類別" value="CCL / 散熱 / 封裝" detail="可繼續擴充族群樹" />
        <ScoreCard label="輸出方式" value="研究訊號" detail="不構成個人化建議" />
      </section>

      <section className="industry-grid">
        {rankedIndustries.map((industry, index) => (
          <article className="industry-card" key={industry.name}>
            <div className="industry-card-head">
              <div>
                <span>#{index + 1} 熱度排序 · {industry.trend}</span>
                <h2>{industry.name}</h2>
              </div>
              <strong>{industry.score}</strong>
            </div>
            <div className="industry-tags">
              {industry.segments.map((segment) => <b key={segment}>{segment}</b>)}
            </div>
            <p>{industry.reason}</p>
            <div className="industry-stock-list">
              {industry.stocks.map((stock) => {
                const [symbol, ...name] = stock.split(" ");
                return /^\d{4}$/.test(symbol) ? (
                  <a href={`/stocks/${symbol}`} key={stock}>{stock}</a>
                ) : (
                  <span key={stock}>{stock}</span>
                );
              })}
            </div>
          </article>
        ))}
      </section>
    </AppShell>
  );
}
