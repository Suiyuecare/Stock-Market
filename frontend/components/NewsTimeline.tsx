import type { PredictionSignal } from "@/lib/api";
import { sanitizeDisplayText } from "@/lib/view-model";

export function NewsTimeline({ news }: { news: PredictionSignal["news"] }) {
  return (
    <div className="timeline">
      {news.map((event) => (
        <div className="timeline-item" key={`${event.source}-${event.title}`}>
          <div className="timeline-title">
            {event.url ? (
              <a href={event.url} target="_blank" rel="noreferrer">
                {sanitizeDisplayText(event.title)}
              </a>
            ) : (
              <strong>{sanitizeDisplayText(event.title)}</strong>
            )}
            <b>{event.sentiment}</b>
          </div>
          {event.summary ? <p>{sanitizeDisplayText(event.summary)}</p> : null}
          <span>
            {event.source} · {formatNewsTime(event.published_at)} · impact {event.impact_score.toFixed(2)}
          </span>
          {event.linkage_reason ? <small>{event.linkage_reason}</small> : null}
        </div>
      ))}
    </div>
  );
}

function formatNewsTime(value: string): string {
  const parsed = Date.parse(value);
  if (!Number.isFinite(parsed)) return value;
  return new Intl.DateTimeFormat("zh-TW", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(parsed));
}
