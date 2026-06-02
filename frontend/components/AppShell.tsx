import type { ReactNode } from "react";

const navItems = [
  { href: "/", label: "總覽" },
  { href: "/ranking", label: "台股排名" },
  { href: "/us-radar", label: "美股連動" },
  { href: "/stocks/2330", label: "個股分析" },
  { href: "/risk", label: "風險監控" },
  { href: "/news", label: "新聞事件" },
];

export function AppShell({ active, children }: { active: string; children: ReactNode }) {
  return (
    <main className="workspace">
      <aside className="sidebar">
        <div className="brand">
          <span>TW</span>
          <div>
            <strong>Stock Factors</strong>
            <small>台美連動研究台</small>
          </div>
        </div>
        <nav>
          {navItems.map((item) => (
            <a className={item.href === active ? "active" : ""} href={item.href} key={item.href}>
              {item.label}
            </a>
          ))}
        </nav>
      </aside>
      <section className="content">{children}</section>
    </main>
  );
}
