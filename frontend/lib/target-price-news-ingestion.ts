import { createHash } from "node:crypto";

import {
  insertAnalystTargetPriceRun,
  type AnalystTargetPriceNewsRow,
  upsertAnalystTargetPriceRows,
} from "@/lib/supabase-analyst-targets";

type ArticleCandidate = {
  title: string;
  link: string;
  summary: string;
  sourceName: string;
  sourceUrl: string;
  publishedAt: string | null;
};

type TargetPriceMention = {
  targetPrice: number;
  targetPriceLow: number | null;
  targetPriceHigh: number | null;
  broker: string | null;
  rating: string | null;
  confidence: number;
  windowText: string;
};

export type TargetPriceIngestionResult = {
  ok: boolean;
  status: "success" | "partial" | "skipped" | "failed";
  message: string;
  source_count: number;
  scanned_count: number;
  extracted_count: number;
  inserted_count: number;
  started_at: string;
  finished_at: string;
};

const defaultRssSources = [
  { name: "CNA 財經 RSS", url: "https://feeds.feedburner.com/rsscna/finance" },
  { name: "CNA 科技 RSS", url: "https://feeds.feedburner.com/rsscna/technology" },
  { name: "鉅亨台股 RSS", url: "https://m.cnyes.com/news/cat/tw_stock?r=rss" },
];

const stockAliases: Array<[string, string, string]> = [
  ["1101", "台泥", "台泥"],
  ["1102", "亞泥", "亞泥"],
  ["1216", "統一", "統一"],
  ["1301", "台塑", "台塑"],
  ["1303", "南亞", "南亞"],
  ["1326", "台化", "台化"],
  ["1402", "遠東新", "遠東新"],
  ["1504", "東元", "東元"],
  ["1513", "中興電", "中興電"],
  ["1519", "華城", "華城"],
  ["1590", "亞德客-KY", "亞德客"],
  ["1605", "華新", "華新"],
  ["2002", "中鋼", "中鋼"],
  ["2049", "上銀", "上銀"],
  ["2059", "川湖", "川湖"],
  ["2207", "和泰車", "和泰車"],
  ["2301", "光寶科", "光寶科"],
  ["2303", "聯電", "聯電"],
  ["2308", "台達電", "台達電"],
  ["2317", "鴻海", "鴻海"],
  ["2324", "仁寶", "仁寶"],
  ["2330", "台積電", "台積電"],
  ["2345", "智邦", "智邦"],
  ["2356", "英業達", "英業達"],
  ["2357", "華碩", "華碩"],
  ["2359", "所羅門", "所羅門"],
  ["2376", "技嘉", "技嘉"],
  ["2377", "微星", "微星"],
  ["2379", "瑞昱", "瑞昱"],
  ["2382", "廣達", "廣達"],
  ["2383", "台光電", "台光電"],
  ["2395", "研華", "研華"],
  ["2408", "南亞科", "南亞科"],
  ["2454", "聯發科", "聯發科"],
  ["2455", "全新", "全新"],
  ["2458", "義隆", "義隆"],
  ["2603", "長榮", "長榮"],
  ["2609", "陽明", "陽明"],
  ["2610", "華航", "華航"],
  ["2615", "萬海", "萬海"],
  ["2618", "長榮航", "長榮航"],
  ["2634", "漢翔", "漢翔"],
  ["2881", "富邦金", "富邦金"],
  ["2882", "國泰金", "國泰金"],
  ["2884", "玉山金", "玉山金"],
  ["2885", "元大金", "元大金"],
  ["2886", "兆豐金", "兆豐金"],
  ["2891", "中信金", "中信金"],
  ["3008", "大立光", "大立光"],
  ["3017", "奇鋐", "奇鋐"],
  ["3034", "聯詠", "聯詠"],
  ["3035", "智原", "智原"],
  ["3037", "欣興", "欣興"],
  ["3081", "聯亞", "聯亞"],
  ["3189", "景碩", "景碩"],
  ["3231", "緯創", "緯創"],
  ["3260", "威剛", "威剛"],
  ["3324", "雙鴻", "雙鴻"],
  ["3515", "華擎", "華擎"],
  ["3653", "健策", "健策"],
  ["3661", "世芯-KY", "世芯"],
  ["3665", "貿聯-KY", "貿聯"],
  ["3711", "日月光投控", "日月光"],
  ["4904", "遠傳", "遠傳"],
  ["4938", "和碩", "和碩"],
  ["4971", "IET-KY", "IET"],
  ["4991", "環宇-KY", "環宇"],
  ["5274", "信驊", "信驊"],
  ["5876", "上海商銀", "上海商銀"],
  ["5880", "合庫金", "合庫金"],
  ["6197", "佳必琪", "佳必琪"],
  ["6223", "旺矽", "旺矽"],
  ["6274", "台燿", "台燿"],
  ["6442", "光聖", "光聖"],
  ["6446", "藥華藥", "藥華藥"],
  ["6488", "環球晶", "環球晶"],
  ["6510", "精測", "精測"],
  ["6669", "緯穎", "緯穎"],
  ["8046", "南電", "南電"],
  ["8069", "元太", "元太"],
  ["8210", "勤誠", "勤誠"],
];

function envList(name: string): string[] {
  return String(process.env[name] ?? "")
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function normalizeWhitespace(value: string): string {
  return value.replace(/\s+/g, " ").trim();
}

function decodeXml(value: string): string {
  return value
    .replaceAll("&amp;", "&")
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">")
    .replaceAll("&quot;", "\"")
    .replaceAll("&#39;", "'");
}

function stripTags(value: string): string {
  return normalizeWhitespace(value.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<[^>]+>/g, " "));
}

function readRssTag(item: string, tag: string): string {
  const match = item.match(new RegExp(`<${tag}[^>]*>([\\s\\S]*?)<\\/${tag}>`, "i"));
  return match?.[1]?.replace("<![CDATA[", "").replace("]]>", "").trim() ?? "";
}

function parseRssDate(value: string): string | null {
  const parsed = Date.parse(value);
  return Number.isFinite(parsed) ? new Date(parsed).toISOString() : null;
}

function parseRssItems(xml: string, sourceName: string, sourceUrl: string): ArticleCandidate[] {
  const items = xml.match(/<item>[\s\S]*?<\/item>/g) ?? [];
  return items
    .map((item) => {
      const title = decodeXml(readRssTag(item, "title"));
      const summary = stripTags(decodeXml(readRssTag(item, "description")));
      const link = decodeXml(readRssTag(item, "link"));
      if (!title || !/^https?:\/\//i.test(link)) return null;
      return {
        title,
        link,
        summary,
        sourceName,
        sourceUrl,
        publishedAt: parseRssDate(readRssTag(item, "pubDate")),
      } satisfies ArticleCandidate;
    })
    .filter((item): item is ArticleCandidate => item !== null);
}

function sourceNameFromUrl(url: string): string {
  try {
    const host = new URL(url).hostname.replace(/^www\./, "");
    if (host.includes("cnyes")) return "鉅亨網";
    if (host.includes("ctee")) return "工商時報";
    if (host.includes("wantrich")) return "旺得富";
    if (host.includes("cna")) return "中央社";
    if (host.includes("yahoo")) return "Yahoo 股市";
    return host;
  } catch {
    return "公開新聞網站";
  }
}

async function fetchText(url: string, timeoutMs = 8000): Promise<string | null> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      headers: {
        "user-agent": "SuiyuecareStockResearchBot/1.0 (+https://stock.suiyuecare.com)",
        accept: "text/html,application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.8",
      },
      signal: controller.signal,
      next: { revalidate: 60 * 60 * 24 },
    });
    if (!response.ok) return null;
    return await response.text();
  } catch {
    return null;
  } finally {
    clearTimeout(timeout);
  }
}

function extractHtmlMeta(html: string, property: string): string {
  const escaped = property.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const pattern = new RegExp(`<meta[^>]+(?:property|name)=["']${escaped}["'][^>]+content=["']([^"']+)["'][^>]*>`, "i");
  return decodeXml(pattern.exec(html)?.[1] ?? "");
}

function extractHtmlTitle(html: string): string {
  const ogTitle = extractHtmlMeta(html, "og:title");
  if (ogTitle) return ogTitle;
  const title = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i)?.[1] ?? "";
  return stripTags(decodeXml(title));
}

function extractArticleText(html: string): string {
  const description = extractHtmlMeta(html, "description") || extractHtmlMeta(html, "og:description");
  const title = extractHtmlTitle(html);
  const body = stripTags(html);
  return normalizeWhitespace([title, description, body].filter(Boolean).join(" "));
}

function isTargetPriceRelevant(text: string): boolean {
  return /目標價|合理價|上看|喊到|調升至|調高至|上修至|升至|評等|券商|投顧|法人|買進|中立|持有|Overweight|Neutral|Buy|Hold/i.test(text);
}

function parseNumber(value: string): number | null {
  const parsed = Number(value.replaceAll(",", "").trim());
  if (!Number.isFinite(parsed)) return null;
  if (parsed < 5 || parsed > 10000) return null;
  return parsed;
}

function findBroker(text: string): string | null {
  const match = /(摩根士丹利|高盛|花旗|麥格理|里昂|大摩|小摩|美銀|瑞銀|野村|元大|富邦|國泰|群益|凱基|統一|永豐|玉山|中信|合庫|華南永昌|第一金|台新|國票|康和|兆豐|法人|投顧|券商)/i.exec(text);
  return match?.[1] ?? null;
}

function findRating(text: string): string | null {
  const match = /(買進|中立|加碼|減碼|優於大盤|劣於大盤|持有|增加持股|降低持股|Buy|Hold|Neutral|Overweight|Underweight|Outperform|Underperform)/i.exec(text);
  return match?.[1] ?? null;
}

function extractTargetPriceMentions(text: string): TargetPriceMention[] {
  const mentions: TargetPriceMention[] = [];
  const pricePattern = /(?:目標價|合理價|上看|喊到|調升至|調高至|上修至|升至|看至)\s*(?:新台幣|台幣|NT\$|\$)?\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:元)?/gi;
  const rangePattern = /(?:目標價|合理價|目標區間|上看區間|區間)\s*(?:新台幣|台幣|NT\$|\$)?\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:至|-|~|到)\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:元)?/gi;
  let match: RegExpExecArray | null;

  while ((match = pricePattern.exec(text)) !== null) {
    const targetPrice = parseNumber(match[1]);
    if (typeof targetPrice !== "number") continue;
    const windowText = text.slice(Math.max(0, match.index - 80), Math.min(text.length, match.index + match[0].length + 100));
    const broker = findBroker(windowText);
    mentions.push({
      targetPrice,
      targetPriceLow: null,
      targetPriceHigh: null,
      broker,
      rating: findRating(windowText),
      confidence: broker ? 0.74 : 0.56,
      windowText,
    });
  }

  while ((match = rangePattern.exec(text)) !== null) {
    const low = parseNumber(match[1]);
    const high = parseNumber(match[2]);
    if (typeof low !== "number" || typeof high !== "number") continue;
    const windowText = text.slice(Math.max(0, match.index - 80), Math.min(text.length, match.index + match[0].length + 100));
    const broker = findBroker(windowText);
    mentions.push({
      targetPrice: Number(((low + high) / 2).toFixed(2)),
      targetPriceLow: Math.min(low, high),
      targetPriceHigh: Math.max(low, high),
      broker,
      rating: findRating(windowText),
      confidence: broker ? 0.72 : 0.54,
      windowText,
    });
  }

  return mentions;
}

function inferSymbolFromText(text: string): { symbol: string; companyName: string } | null {
  const tickerMatch = /(?:^|[^\d])([1-9]\d{3})(?:-TW|\.TW|\.TWO|[^\d]|$)/i.exec(text);
  if (tickerMatch) {
    const symbol = tickerMatch[1];
    const alias = stockAliases.find(([item]) => item === symbol);
    return { symbol, companyName: alias?.[1] ?? symbol };
  }
  const alias = stockAliases.find(([, name, shortName]) => text.includes(name) || text.includes(shortName));
  return alias ? { symbol: alias[0], companyName: alias[1] } : null;
}

function excerptAroundTarget(text: string, mention: TargetPriceMention): string {
  const targetIndex = text.indexOf(mention.windowText);
  const start = targetIndex >= 0 ? Math.max(0, targetIndex - 40) : 0;
  return normalizeWhitespace(text.slice(start, start + 240));
}

function hashText(value: string): string {
  return createHash("sha256").update(value).digest("hex");
}

function rowDedupeKey(row: Omit<AnalystTargetPriceNewsRow, "dedupe_key">): string {
  return hashText([row.symbol, row.source_url, row.target_price_mean, row.broker ?? ""].join("|"));
}

async function collectArticleCandidates(maxArticles: number): Promise<{ candidates: ArticleCandidate[]; sourceCount: number }> {
  const extraRssSources = envList("TARGET_PRICE_NEWS_RSS_URLS").map((url) => ({ name: sourceNameFromUrl(url), url }));
  const rssSources = [...defaultRssSources, ...extraRssSources];
  const rssResponses = await Promise.allSettled(rssSources.map((source) => fetchText(source.url)));
  const rssCandidates = rssResponses.flatMap((result, index) => {
    if (result.status !== "fulfilled" || !result.value) return [];
    const source = rssSources[index];
    return parseRssItems(result.value, source.name, source.url);
  });
  const manualArticles = envList("TARGET_PRICE_NEWS_ARTICLE_URLS").map((url) => ({
    title: sourceNameFromUrl(url),
    link: url,
    summary: "",
    sourceName: sourceNameFromUrl(url),
    sourceUrl: url,
    publishedAt: null,
  }));

  const deduped = new Map<string, ArticleCandidate>();
  for (const candidate of [...manualArticles, ...rssCandidates]) {
    if (!deduped.has(candidate.link)) deduped.set(candidate.link, candidate);
  }
  return { candidates: Array.from(deduped.values()).slice(0, maxArticles), sourceCount: rssSources.length + manualArticles.length };
}

export async function runAnalystTargetPriceNewsIngestion(): Promise<TargetPriceIngestionResult> {
  const startedAt = new Date().toISOString();
  const maxArticles = Number(process.env.TARGET_PRICE_NEWS_MAX_ARTICLES ?? 40);

  if (!process.env.SUPABASE_SERVICE_ROLE_KEY && !process.env.SUPABASE_SECRET_KEY) {
    const finishedAt = new Date().toISOString();
    const result = {
      ok: false,
      status: "skipped" as const,
      message: "Missing SUPABASE_SERVICE_ROLE_KEY or SUPABASE_SECRET_KEY. Cron route is installed but cannot write analyst target prices yet.",
      source_count: 0,
      scanned_count: 0,
      extracted_count: 0,
      inserted_count: 0,
      started_at: startedAt,
      finished_at: finishedAt,
    };
    await insertAnalystTargetPriceRun({
      started_at: startedAt,
      finished_at: finishedAt,
      status: "skipped",
      source_count: 0,
      scanned_count: 0,
      extracted_count: 0,
      inserted_count: 0,
      error_message: result.message,
    });
    return result;
  }

  try {
    const { candidates, sourceCount } = await collectArticleCandidates(Number.isFinite(maxArticles) ? maxArticles : 40);
    const rows: AnalystTargetPriceNewsRow[] = [];

    for (const candidate of candidates) {
      const seedText = normalizeWhitespace(`${candidate.title} ${candidate.summary}`);
      const shouldFetchArticle = isTargetPriceRelevant(seedText) || process.env.TARGET_PRICE_FETCH_ALL_ARTICLES === "true";
      const html = shouldFetchArticle ? await fetchText(candidate.link) : null;
      const bodyText = html ? extractArticleText(html) : "";
      const fullText = normalizeWhitespace(`${candidate.title} ${candidate.summary} ${bodyText}`);
      if (!isTargetPriceRelevant(fullText)) continue;

      for (const mention of extractTargetPriceMentions(fullText)) {
        const symbolHit = inferSymbolFromText(mention.windowText) ?? inferSymbolFromText(candidate.title) ?? inferSymbolFromText(fullText);
        if (!symbolHit) continue;
        const capturedAt = new Date().toISOString();
        const rowWithoutKey: Omit<AnalystTargetPriceNewsRow, "dedupe_key"> = {
          symbol: symbolHit.symbol,
          company_name: symbolHit.companyName,
          broker: mention.broker,
          rating: mention.rating,
          target_price_mean: mention.targetPrice,
          target_price_low: mention.targetPriceLow,
          target_price_high: mention.targetPriceHigh,
          currency: "TWD",
          source_name: candidate.sourceName,
          source_url: candidate.link,
          article_title: candidate.title.slice(0, 260),
          summary_excerpt: excerptAroundTarget(fullText, mention),
          published_at: candidate.publishedAt,
          captured_at: capturedAt,
          confidence: mention.confidence,
          extraction_method: "public_news_regex_v1",
          raw_text_hash: hashText(fullText),
          updated_at: capturedAt,
        };
        rows.push({ ...rowWithoutKey, dedupe_key: rowDedupeKey(rowWithoutKey) });
      }
    }

    const uniqueRows = Array.from(new Map(rows.map((row) => [row.dedupe_key, row])).values());
    const inserted = await upsertAnalystTargetPriceRows(uniqueRows);
    const finishedAt = new Date().toISOString();
    const status = uniqueRows.length > 0 ? "success" : "partial";
    await insertAnalystTargetPriceRun({
      started_at: startedAt,
      finished_at: finishedAt,
      status,
      source_count: sourceCount,
      scanned_count: candidates.length,
      extracted_count: uniqueRows.length,
      inserted_count: inserted,
      error_message: null,
    });
    return {
      ok: true,
      status,
      message: uniqueRows.length > 0 ? "Analyst target prices extracted and written to Supabase." : "No target price mentions found in the scanned public news set.",
      source_count: sourceCount,
      scanned_count: candidates.length,
      extracted_count: uniqueRows.length,
      inserted_count: inserted,
      started_at: startedAt,
      finished_at: finishedAt,
    };
  } catch (error) {
    const finishedAt = new Date().toISOString();
    const message = error instanceof Error ? error.message : "Unknown analyst target price ingestion error.";
    await insertAnalystTargetPriceRun({
      started_at: startedAt,
      finished_at: finishedAt,
      status: "failed",
      source_count: 0,
      scanned_count: 0,
      extracted_count: 0,
      inserted_count: 0,
      error_message: message,
    });
    return {
      ok: false,
      status: "failed",
      message,
      source_count: 0,
      scanned_count: 0,
      extracted_count: 0,
      inserted_count: 0,
      started_at: startedAt,
      finished_at: finishedAt,
    };
  }
}
