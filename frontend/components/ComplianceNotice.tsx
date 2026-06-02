import { BETA_NOTICE_TEXT, COMPLIANCE_POINTS, DISCLAIMER_TEXT } from "@/lib/view-model";

export function ComplianceNotice({ compact = false }: { compact?: boolean }) {
  if (compact) {
    return (
      <div className="compliance-compact">
        <strong>Beta 研究版</strong>
        <span>{DISCLAIMER_TEXT}</span>
      </div>
    );
  }

  return (
    <section className="compliance-notice" aria-label="合規與資料聲明">
      <div>
        <span>重要聲明</span>
        <strong>{BETA_NOTICE_TEXT}</strong>
        <p>{DISCLAIMER_TEXT}</p>
      </div>
      <ul>
        {COMPLIANCE_POINTS.map((point) => (
          <li key={point}>{point}</li>
        ))}
      </ul>
    </section>
  );
}
