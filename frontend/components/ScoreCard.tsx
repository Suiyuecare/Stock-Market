import { sanitizeDisplayText } from "@/lib/view-model";

export function ScoreCard({
  label,
  value,
  detail,
  tone = "default",
}: {
  label: string;
  value: string;
  detail: string;
  tone?: "default" | "risk" | "positive" | "negative" | "neutral";
}) {
  return (
    <div className={`score-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{sanitizeDisplayText(detail)}</small>
    </div>
  );
}
