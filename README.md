# Stock Market

股票投資管理軟體起始專案。第一版先提供可直接開啟的前端儀表板，用來整理關注清單、持倉概況、交易計畫與風險提醒。

## 功能雛形

- 市場總覽與投資組合摘要
- 股票關注清單
- 持倉配置與損益檢視
- 交易計畫與風險規則
- 每日投資筆記

## 開始使用

直接用瀏覽器開啟 `index.html` 即可。

也可以用本機伺服器預覽：

```bash
python3 -m http.server 8000
```

然後打開 `http://localhost:8000`。

## 下一步

- 串接股票即時/延遲行情 API
- 加入登入與使用者資料庫
- 建立交易紀錄、回測、報表匯出
- 增加風險控管與停損提醒

## Supabase 設定

Vercel 需要設定：

- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY`

資料表 schema 放在 `supabase/schema.sql`。目前是 prototype 公開資料模式，RLS 已開啟，但允許 `anon` 讀取/新增 watchlist 與讀寫共用筆記；正式版應加入 Supabase Auth 後改成每位使用者只存取自己的資料。
