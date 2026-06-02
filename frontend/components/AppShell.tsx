import type { ReactNode } from "react";
import { ComplianceNotice } from "@/components/ComplianceNotice";

const navItems = [
  { href: "/", label: "首頁總覽", description: "新手導覽與首要訊號" },
  { href: "/ranking", label: "台股觀察榜", description: "因子排名與訊號名單" },
  { href: "/us-radar", label: "美股連動", description: "NASDAQ / SOX / NVDA" },
  { href: "/stocks/2330", label: "個股面板", description: "原因、區間、配置建議" },
  { href: "/risk", label: "風險雷達", description: "風險係數與壓力測試" },
  { href: "/news", label: "新聞事件", description: "資料來源與時間軸" },
];

export function AppShell({ active, children }: { active: string; children: ReactNode }) {
  const isStockDetail = active.startsWith("/stocks/");

  return (
    <main className="finance-shell">
      <aside className="finance-sidebar">
        <div className="brand">
          <span>TW</span>
          <div>
            <strong>歲悅 Stock</strong>
            <small>金融因子研究平台</small>
          </div>
        </div>
        <div className="finance-sidebar-headline">信號導向版｜非投資建議</div>
        <nav>
          {navItems.map((item) => {
            const isActive =
              item.href === "/stocks/2330"
                ? isStockDetail
                : item.href === active;

            return (
              <a className={`finance-nav-item ${isActive ? "on" : ""}`} href={item.href} key={item.href}>
                {item.label}
                <small>{item.description}</small>
              </a>
            );
          })}
        </nav>
        <div className="finance-sidebar-foot">研究流程：樣本池 → 因子評分 → 風險篩選 → 信號備註</div>
        <ComplianceNotice compact />
      </aside>
      <section className="finance-main">
        <div className="finance-content">{children}</div>
      </section>
    </main>
  );
}
