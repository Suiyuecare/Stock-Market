import type { PredictionSignal } from "@/lib/api";
import { buildProfessionalInfoSections } from "@/lib/view-model";

export function ProfessionalInfoDeck({ signal }: { signal: PredictionSignal }) {
  const sections = buildProfessionalInfoSections(signal);

  return (
    <div className="professional-deck">
      <div className="stock-tabs" aria-label="個股資訊分類">
        {sections.map((section) => (
          <a href={`#${section.title}`} key={section.title}>{section.title}</a>
        ))}
      </div>
      <div className="professional-grid">
        {sections.map((section) => (
          <section className="professional-section" id={section.title} key={section.title}>
            <div>
              <p className="eyebrow">Stock Data</p>
              <h3>{section.title}</h3>
              <span>{section.description}</span>
            </div>
            <div className="professional-rows">
              {section.rows.map((row) => (
                <div className="professional-row" key={row.label}>
                  <span>{row.label}</span>
                  <b>{row.value}</b>
                  <small>{row.note}</small>
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
