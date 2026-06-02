import type { PredictionSignal } from "@/lib/api";
import { sanitizeDisplayText } from "@/lib/view-model";

export function NewsTimeline({ news }: { news: PredictionSignal["news"] }) {
  return (
    <div className="timeline">
      {news.map((event) => (
        <div className="timeline-item" key={event.title}>
          <strong>{sanitizeDisplayText(event.title)}</strong>
          <span>{event.source} · {event.sentiment} · impact {event.impact_score}</span>
        </div>
      ))}
    </div>
  );
}
