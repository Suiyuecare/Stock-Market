# TW-US Stock Prediction App

台股與美股連動預測系統。第一版先做 Web App + API + 資料庫 + 排程任務，不先做手機 App。

## MVP 範圍

- 每日盤後台股資料整理
- 美股開盤前連動訊號
- 股票 watchlist 與預測摘要
- 新聞/事件 LLM parser 介面
- 基本面、籌碼、技術面、新聞、風險、美股連動因子評分
- MA、RSI、KD、MACD、OBV、量價背離技術指標
- 背景排程任務骨架
- 可用 Docker Compose 一鍵啟動

所有輸出都是研究與教育用途的 probability-style signals，不提供個人化投資建議，也不輸出 buy/sell 指令。

## 技術架構

- Frontend: Next.js / React
- Backend API: Python FastAPI
- Database: PostgreSQL
- Cache / Queue: Redis
- Background Jobs: Celery-ready worker + APScheduler
- AI News Parser: provider interface, default OpenAI-compatible
- Charts: lightweight-charts
- Testing: pytest

## Repo 文件

- `AGENTS.md`: Codex repo-specific guidance
- `docs/PRD.md`: product requirements
- `docs/ARCHITECTURE.md`: system architecture
- `docs/FACTOR_ENGINE.md`: factor and prediction scoring design
- `docs/DATABASE_SCHEMA.md`: database schema notes
- `docs/DATA_SOURCES.md`: data-source policy and candidates
- `docs/CODEX_TASKS.md`: implementation task backlog
- `sample_data/`: mock CSV data for MVP development

## 本機啟動

```bash
cp .env.example .env
docker compose up --build
```

服務：

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Production site: https://stock.suiyuecare.com

## 部署設定

正式站網域：

```text
stock.suiyuecare.com
```

Vercel production environment 建議設定：

```text
NEXT_PUBLIC_SITE_URL=https://stock.suiyuecare.com
NEXT_PUBLIC_API_BASE_URL=<production API base URL>
```

如果前後端分開部署，`NEXT_PUBLIC_API_BASE_URL` 要指向 FastAPI production API。不要把 OpenAI API key 或任何 secrets commit 到 repo，請放在 Vercel Environment Variables 或本機 `.env.local`。

## 第一階段資料流

1. 盤後任務拉取/匯入台股 OHLCV 與基本指標
2. 美股開盤前任務整理美股期貨、ADR、科技股與匯率訊號
3. 新聞 parser 將重大事件轉成結構化 impact signals
4. API 輸出 watchlist、signal summary、prediction score
5. Frontend 顯示市場概況、預測分數與圖表

## MVP API

- `GET /api/health`
- `GET /api/market/summary`
- `GET /api/predictions/signals`
- `GET /api/stocks/ranking`
- `GET /api/stocks/{symbol}`
- `POST /api/news/parse`

## 測試

```bash
PYTHONPATH=backend pytest backend/app/tests
```

## 後續里程碑

- 接入合法行情資料源
- 加入模型訓練與回測 pipeline
- 加入登入與多使用者 watchlist
- 加入部署環境與 CI
- 評估手機 App 或 PWA
