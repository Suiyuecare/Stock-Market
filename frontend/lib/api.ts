const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type MarketSummary = {
  session_date: string;
  tw_status: string;
  us_premarket_status: string;
  instruments: Array<{
    symbol: string;
    market: string;
    name: string;
    sector: string | null;
    currency: string;
  }>;
};

export type PredictionSignal = {
  symbol: string;
  signal_date: string;
  horizon: string;
  score: number;
  confidence: number;
  drivers: Array<{ type: string; label: string; weight: number }>;
};

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`API request failed: ${path}`);
  }
  return response.json() as Promise<T>;
}

export async function fetchMarketSummary(): Promise<MarketSummary> {
  return getJson<MarketSummary>("/api/market/summary");
}

export async function fetchPredictionSignals(): Promise<PredictionSignal[]> {
  return getJson<PredictionSignal[]>("/api/predictions/signals");
}
