import type { PredictionSignal } from "@/lib/api";

type NewsEvent = PredictionSignal["news"][number];

const positiveWords = [
  "漲價",
  "上漲",
  "成長",
  "創高",
  "創新高",
  "上修",
  "利多",
  "買超",
  "看好",
  "需求",
  "擴產",
  "得標",
  "獲利",
  "量產",
  "年增",
  "大漲",
  "收紅",
  "攀升",
  "打入",
  "合作",
  "續熱",
  "配息",
  "股利",
  "營收增加",
  "positive",
  "growth",
  "strong",
  "resilient",
];

const negativeWords = [
  "下跌",
  "降價",
  "下修",
  "利空",
  "衰退",
  "虧損",
  "賣超",
  "裁罰",
  "訴訟",
  "停工",
  "違約",
  "風險",
  "cautious",
  "negative",
  "weak",
  "risk",
  "loss",
];

export function newsHref(event: NewsEvent): string {
  const directUrl = normalizeUrl(event.url);
  if (directUrl) return directUrl;

  const sourceUrl = normalizeUrl(event.source_url);
  if (sourceUrl) return sourceUrl;

  const query = encodeURIComponent(`${event.title} ${event.source}`.trim());
  return `https://www.google.com/search?q=${query}`;
}

export function newsTone(event: Pick<NewsEvent, "title" | "summary" | "sentiment" | "impact_score">): "positive" | "negative" | "neutral" {
  const content = `${event.sentiment} ${event.title} ${event.summary ?? ""}`.toLowerCase();
  const positiveHits = positiveWords.filter((word) => content.includes(word.toLowerCase())).length;
  const negativeHits = negativeWords.filter((word) => content.includes(word.toLowerCase())).length;

  if (positiveHits > negativeHits || event.impact_score > 0.05) return "positive";
  if (negativeHits > positiveHits || event.impact_score < -0.05) return "negative";
  return "neutral";
}

export function newsToneLabel(tone: ReturnType<typeof newsTone>): string {
  if (tone === "positive") return "偏好 / 可能推升";
  if (tone === "negative") return "偏弱 / 可能壓抑";
  return "中立";
}

function normalizeUrl(value?: string): string | null {
  if (!value) return null;
  const trimmed = value.trim();
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  return null;
}
