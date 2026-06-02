import type { ReactNode } from "react";
import { ComplianceNotice } from "@/components/ComplianceNotice";

const navItems = [
  { href: "/", label: "入門總覽" },
  { href: "/ranking", label: "選股清單" },
  { href: "/us-radar", label: "美股連動" },
  { href: "/stocks/2330", label: "個股說明書" },
  { href: "/risk", label: "風險提醒" },
  { href: "/news", label: "依據來源" },
];

export function AppShell({ active, children }: { active: string; children: ReactNode }) {
  return (
    <main className="workspace">
      <aside className="sidebar">
        <div className="brand">
          <span>TW</span>
          <div>
            <strong>歲悅 Stock</strong>
            <small>新手選股研究台</small>
          </div>
        </div>
        <nav>
          {navItems.map((item) => (
            <a className={item.href === active ? "active" : ""} href={item.href} key={item.href}>
              {item.label}
            </a>
          ))}
        </nav>
        <ComplianceNotice compact />
      </aside>
      <section className="content">{children}</section>
    </main>
  );
}
