# Taiwan Market Research: 2026-03-01 to 2026-06-03

This document records the research baseline used by the Taiwan prediction tool.

## Data Sources

- TWSE TAIEX historical index: `https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST`
- TWSE daily market quotes: `https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY_ALL`
- TWSE daily index tables: `https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX`
- MOPS monthly revenue: `https://mopsfin.twse.com.tw/opendata/t187ap05_L.csv`
- DGBAS 2026Q1 GDP advance estimate: `https://eng.dgbas.gov.tw/News_Content.aspx?n=4438&s=236205`

## Market Findings

- First trading day in the study window: 2026-03-02.
- Final day in the study window: 2026-06-03.
- Trading days: 65.
- TAIEX close moved from 35,095.09 to 46,459.16, a 32.38% gain.
- 2026-06-03 was the study-window high with an intraday high of 46,552.16.
- The study-window low was 31,529.36 on 2026-03-09.
- Maximum drawdown during the window was about -9.61%, with the drawdown low on 2026-03-31.
- 20-day TAIEX return into 2026-06-03 was 12.93%.
- 60-day TAIEX return into 2026-06-03 was 38.27%.
- TAIEX was above MA20 and MA60 on 2026-06-03.
- On 2026-06-03, 763 listed stocks advanced, 289 declined, and 38 were flat out of 1,090 common-stock rows.
- The last-10-session listed-stock advance ratio was about 70% in the sampled TWSE data.

## Sector Rotation

Leading themes from 2026-03-02 to 2026-06-03:

- Electronic components index: about +75.98%.
- Taiwan AI supply chain alliance index: about +72.76%.
- IC design representative index: about +71.81%.
- Taiwan wafer manufacturing index: about +69.84%.
- Taiwan all-market semiconductor index: about +60.59%.

Lagging themes:

- Food index: about -2.77%.
- Construction index: about -6.23%.
- Automobile index: about -7.05%.
- Biotechnology and medical care index: about -10.62%.

## Tool Design Implications

The regime is classified as **strong bull but concentrated**:

- The market trend is strong enough to allow active stock selection.
- Concentration risk remains high because TAIEX is market-cap weighted.
- A strong broad-market index does not mean every stock should be upgraded.
- Liquidity is a hard filter, not a weighted score.
- Overheated stocks are penalized instead of blindly rewarded.
- AI is an important theme, but it is not the only theme. Financials, shipping, robotics, electric power, domestic demand, and other groups can compete through relative strength, institutional flow, fundamentals, and risk control.

## Horizon Weights

1D:

- Technical / relative strength: 25%
- Chip / institutional flow: 22%
- US market / ADR / SOX linkage: 18%
- Market regime / breadth: 12%
- News events: 10%
- Monthly revenue / industry cycle: 5%
- Fundamentals / profit quality: 5%
- Valuation / upside room: 3%

5D:

- Technical / relative strength: 22%
- Chip / institutional flow: 22%
- US market / ADR / SOX linkage: 13%
- Market regime / breadth: 8%
- News events: 5%
- Monthly revenue / industry cycle: 15%
- Fundamentals / profit quality: 12%
- Valuation / upside room: 3%

20D:

- Technical / relative strength: 15%
- Chip / institutional flow: 18%
- US market / ADR / SOX linkage: 8%
- Market regime / breadth: 8%
- News events: 2%
- Monthly revenue / industry cycle: 22%
- Fundamentals / profit quality: 22%
- Valuation / upside room: 5%

## Important Product Note

Scores are not probabilities. A score of 70 is not a 70% up probability.

True `probability_up_1d`, `probability_up_5d`, and `probability_up_20d` must be calibrated with historical buckets, Brier Score, and walk-forward out-of-sample testing.
