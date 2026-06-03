import type { PredictionSignal } from "@/lib/api";
import { newsHref, newsTone, newsToneLabel } from "@/lib/news";
import { sanitizeDisplayText } from "@/lib/view-model";

export function NewsTimeline({ news }: { news: PredictionSignal["news"] }) {
  return (
    <div className="timeline">
      {news.map((event) => {
        const tone = newsTone(event);
        const href = newsHref(event);

        return (
          <a className={`timeline-item news-${tone}`} href={href} target="_blank" rel="noreferrer" key={`${event.source}-${event.title}`}>
            <div className="timeline-title">
              <strong>
                {sanitizeDisplayText(event.title)}
              </strong>
              <b>{newsToneLabel(tone)}</b>
            </div>
            {event.summary ? <p>{sanitizeDisplayText(event.summary)}</p> : null}
            <span>
              {event.source} · {formatNewsTime(event.published_at)} · impact {event.impact_score.toFixed(2)} · 點擊看來源
            </span>
            {event.linkage_reason ? <small>{event.linkage_reason}</small> : null}
          </a>
        );
      })}
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
