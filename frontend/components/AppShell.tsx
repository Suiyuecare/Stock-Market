import type { ReactNode } from "react";
import { ComplianceNotice } from "@/components/ComplianceNotice";
import { MarketAutoRefresh } from "@/components/MarketAutoRefresh";

const navItems = [
  { href: "/stocks/2330", label: "個股明燈", description: "搜尋個股、行情、訊號與新聞" },
  { href: "/industries", label: "產業明燈", description: "產業趨勢、族群與細分題材" },
  { href: "/watchlist", label: "關注名單", description: "自己收藏的觀察標的" },
  { href: "/calculation", label: "計算模組", description: "機率公式、因子權重與風險扣分" },
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
        <div className="finance-sidebar-headline">三步驟：找個股 → 看產業 → 放進關注</div>
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
        <MarketAutoRefresh />
        <div className="finance-sidebar-foot">研究流程：樣本池 → 因子評分 → 風險篩選 → 信號備註</div>
        <ComplianceNotice compact />
      </aside>
      <section className="finance-main">
        <div className="finance-content">{children}</div>
      </section>
    </main>
  );
}
