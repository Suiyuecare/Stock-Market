import { runAnalystTargetPriceNewsIngestion } from "@/lib/target-price-news-ingestion";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET(request: Request): Promise<Response> {
  const cronSecret = process.env.CRON_SECRET;
  const authorization = request.headers.get("authorization");
  if (!cronSecret || authorization !== `Bearer ${cronSecret}`) {
    return Response.json({ ok: false, error: "Unauthorized cron request." }, { status: 401 });
  }

  const result = await runAnalystTargetPriceNewsIngestion();
  const status = result.status === "failed" ? 500 : 200;
  return Response.json(result, { status });
}
