import type { AnalystTargetPrice, StockInstrument } from "@/lib/api";

export type AnalystTargetPriceNewsRow = {
  dedupe_key: string;
  symbol: string;
  company_name: string | null;
  broker: string | null;
  rating: string | null;
  target_price_mean: number;
  target_price_low: number | null;
  target_price_high: number | null;
  currency: string;
  source_name: string;
  source_url: string;
  article_title: string;
  summary_excerpt: string | null;
  published_at: string | null;
  captured_at: string;
  confidence: number;
  extraction_method: string;
  raw_text_hash: string | null;
  updated_at?: string;
};

export type AnalystTargetPriceIngestionRun = {
  started_at: string;
  finished_at: string;
  status: "success" | "partial" | "skipped" | "failed";
  source_count: number;
  scanned_count: number;
  extracted_count: number;
  inserted_count: number;
  error_message?: string | null;
};

type SupabaseConfig = {
  url: string;
  key: string;
};

const targetPriceTable = "analyst_target_price_news";
const ingestionRunsTable = "analyst_target_price_ingestion_runs";

function getSupabaseUrl(): string | undefined {
  return process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
}

function getSupabaseReadKey(): string | undefined {
  return (
    process.env.SUPABASE_SERVICE_ROLE_KEY ||
    process.env.SUPABASE_SECRET_KEY ||
    process.env.SUPABASE_PUBLISHABLE_KEY ||
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
  );
}

function getSupabaseWriteKey(): string | undefined {
  return process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SECRET_KEY;
}

function getSupabaseConfig(mode: "read" | "write"): SupabaseConfig | null {
  const url = getSupabaseUrl();
  const key = mode === "write" ? getSupabaseWriteKey() : getSupabaseReadKey();
  if (!url || !key) return null;
  return { url: url.replace(/\/$/, ""), key };
}

function buildHeaders(config: SupabaseConfig): HeadersInit {
  return {
    apikey: config.key,
    authorization: `Bearer ${config.key}`,
    "content-type": "application/json",
  };
}

function asNullableNumber(value: unknown): number | null {
  if (value === null || value === undefined) return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export function isSupabaseAnalystTargetReadConfigured(): boolean {
  return Boolean(getSupabaseConfig("read"));
}

export function isSupabaseAnalystTargetWriteConfigured(): boolean {
  return Boolean(getSupabaseConfig("write"));
}

export async function fetchLatestSupabaseAnalystTargetPrice(
  instrument: Pick<StockInstrument, "symbol">,
): Promise<AnalystTargetPrice | null> {
  const config = getSupabaseConfig("read");
  if (!config) return null;

  const params = new URLSearchParams({
    select: "*",
    symbol: `eq.${instrument.symbol}`,
    order: "published_at.desc.nullslast,captured_at.desc",
    limit: "1",
  });
  const endpoint = `${config.url}/rest/v1/${targetPriceTable}?${params.toString()}`;

  try {
    const response = await fetch(endpoint, {
      headers: buildHeaders(config),
      next: { revalidate: 60 * 60 * 2 },
    });
    if (!response.ok) return null;
    const rows = (await response.json()) as Array<Record<string, unknown>>;
    const row = rows[0];
    if (!row) return null;

    const targetPriceMean = asNullableNumber(row.target_price_mean);
    if (typeof targetPriceMean !== "number") return null;
    const sourceName = String(row.source_name ?? "新聞擷取");
    const broker = typeof row.broker === "string" && row.broker.trim() ? row.broker.trim() : null;
    return {
      symbol: instrument.symbol,
      currency: String(row.currency ?? "TWD"),
      target_price_mean: targetPriceMean,
      target_price_high: asNullableNumber(row.target_price_high),
      target_price_low: asNullableNumber(row.target_price_low),
      analyst_count: 1,
      broker,
      rating: typeof row.rating === "string" ? row.rating : null,
      source: broker ? `新聞擷取：${sourceName} / ${broker}` : `新聞擷取：${sourceName}`,
      source_type: "news_extracted",
      source_url: typeof row.source_url === "string" ? row.source_url : undefined,
      published_at: typeof row.published_at === "string" ? row.published_at : undefined,
      confidence: asNullableNumber(row.confidence) ?? 0.5,
      provider_status: "extracted",
      note: "每兩天由公開新聞/RSS 擷取法人或券商目標價並寫入 Supabase；不是付費法人共識，請點開來源確認報告日期、評等與假設。",
    };
  } catch {
    return null;
  }
}

export async function upsertAnalystTargetPriceRows(rows: AnalystTargetPriceNewsRow[]): Promise<number> {
  if (rows.length === 0) return 0;
  const config = getSupabaseConfig("write");
  if (!config) {
    throw new Error("SUPABASE_SERVICE_ROLE_KEY or SUPABASE_SECRET_KEY is required for target price ingestion.");
  }

  const endpoint = `${config.url}/rest/v1/${targetPriceTable}?on_conflict=dedupe_key`;
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      ...buildHeaders(config),
      prefer: "resolution=merge-duplicates,return=minimal",
    },
    body: JSON.stringify(rows),
  });
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(`Supabase target price upsert failed: ${response.status} ${detail}`);
  }
  return rows.length;
}

export async function insertAnalystTargetPriceRun(run: AnalystTargetPriceIngestionRun): Promise<void> {
  const config = getSupabaseConfig("write");
  if (!config) return;

  const response = await fetch(`${config.url}/rest/v1/${ingestionRunsTable}`, {
    method: "POST",
    headers: {
      ...buildHeaders(config),
      prefer: "return=minimal",
    },
    body: JSON.stringify(run),
  });
  if (!response.ok) {
    // Keep the ingestion result useful even if the optional run log table is not ready.
    console.warn("Supabase target price run log insert failed", response.status, await response.text().catch(() => ""));
  }
}
