import { AppShell } from "@/components/AppShell";
import { ComplianceNotice } from "@/components/ComplianceNotice";
import { ScoreCard } from "@/components/ScoreCard";
import { WatchlistClient } from "@/components/WatchlistClient";

export default function WatchlistPage() {
  return (
    <AppShell active="/watchlist">
      <header className="topbar">
        <div>
          <p className="eyebrow">關注名單</p>
          <h1>把想追蹤的股票集中管理</h1>
        </div>
        <div className="status">本機瀏覽器保存</div>
      </header>
      <ComplianceNotice />

      <section className="metric-grid">
        <ScoreCard label="使用方式" value="加入關注" detail="每個個股頁都能加入" />
        <ScoreCard label="資料保存" value="Local" detail="先存在目前瀏覽器" />
        <ScoreCard label="下一版" value="Google 登入" detail="同步個人後台與雲端名單" />
        <ScoreCard label="用途" value="觀察" detail="不是個人化投資建議" />
      </section>

      <article className="panel">
        <WatchlistClient />
      </article>
    </AppShell>
  );
}
