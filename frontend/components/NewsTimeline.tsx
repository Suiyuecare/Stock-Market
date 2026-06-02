import type { PredictionSignal } from "@/lib/api";

export function NewsTimeline({ news }: { news: PredictionSignal["news"] }) {
  return (
    <div className="timeline">
      {news.map((event) => (
        <div className="timeline-item" key={event.title}>
          <strong>{event.title}</strong>
          <span>{event.source} · {event.sentiment} · impact {event.impact_score}</span>
        </div>
      ))}
    </div>
  );
}
