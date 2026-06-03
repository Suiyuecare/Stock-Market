import type { ReactNode } from "react";
import { ComplianceNotice } from "@/components/ComplianceNotice";
import { MarketAutoRefresh } from "@/components/MarketAutoRefresh";

const navItems = [
  { href: "/stocks/2330", label: "個股明燈", description: "先看一檔股票現在值不值得觀察" },
  { href: "/industries", label: "產業明燈", description: "看族群風向，理解資金在追什麼" },
  { href: "/watchlist", label: "關注名單", description: "把看得懂、想追蹤的股票收起來" },
  { href: "/calculation", label: "計算模組", description: "用白話看機率、權重與風險扣分" },
];

export function AppShell({ active, children }: { active: string; children: ReactNode }) {
  const isStockDetail = active.startsWith("/stocks/");

  return (
    <main className="finance-shell">
      <aside className="finance-sidebar">
        <div className="brand">
          <span>S</span>
          <div>
            <strong>歲悅股票明燈</strong>
            <small>Beginner Signal Desk</small>
          </div>
        </div>
        <div className="finance-sidebar-headline">新手順序：先看結論 → 再看原因 → 最後看風險</div>
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
        <div className="finance-sidebar-foot">本系統把行情、新聞、籌碼與風險翻成研究訊號，幫你先整理，不替你下決定。</div>
        <ComplianceNotice compact />
      </aside>
      <section className="finance-main">
        <div className="finance-content">{children}</div>
      </section>
    </main>
  );
}
