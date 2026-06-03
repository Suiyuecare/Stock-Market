export default function Loading() {
  return (
    <main className="loading-shell" aria-busy="true" aria-live="polite">
      <section className="loading-card">
        <img src="/suiyue-loading-icon.png" alt="歲悅載入圖示" />
        <div>
          <p className="eyebrow">Loading Market Signals</p>
          <h1>正在同步台美股研究資料</h1>
          <span>官方行情、新聞事件、風險 reference 與相關股票連動正在整理中。</span>
        </div>
        <div className="loading-progress" aria-label="資料載入進度">
          <i />
        </div>
        <ul>
          <li>TWSE / TPEx 行情與估值</li>
          <li>CNA / TWSE 新聞事件</li>
          <li>相關股票與供應鏈 reference</li>
        </ul>
      </section>
    </main>
  );
}
