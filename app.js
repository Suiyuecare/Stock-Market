const initialWatchlist = [
  { symbol: "2330", name: "台積電", price: 1085, change: 1.88, target: 1180 },
  { symbol: "2454", name: "聯發科", price: 1340, change: -0.74, target: 1450 },
  { symbol: "AAPL", name: "Apple", price: 196.6, change: 0.42, target: 215 },
  { symbol: "NVDA", name: "NVIDIA", price: 141.2, change: 2.36, target: 155 },
];

const portfolio = [
  { name: "半導體", weight: 38 },
  { name: "AI / 雲端", weight: 24 },
  { name: "金融", weight: 12 },
  { name: "ETF", weight: 18 },
  { name: "現金", weight: 8 },
];

const formatMoney = new Intl.NumberFormat("zh-TW", {
  style: "currency",
  currency: "TWD",
  maximumFractionDigits: 0,
});

let watchlist = [...initialWatchlist];
let supabaseClient = null;
let currentUser = null;

function setStatus(selector, message, mode = "") {
  const status = document.querySelector(selector);
  status.textContent = message;
  status.className = `status-pill ${mode}`.trim();
}

function setDbStatus(message, mode = "") {
  setStatus("#dbStatus", message, mode);
}

function setUserStatus(message, mode = "") {
  setStatus("#userStatus", message, mode);
}

function userLabel(user) {
  return user?.user_metadata?.full_name || user?.email || "已登入使用者";
}

function toAppStock(row) {
  return {
    id: row.id,
    symbol: row.symbol,
    name: row.name,
    price: Number(row.price),
    change: Number(row.change_percent),
    target: Number(row.target_price),
  };
}

function toDbStock(stock) {
  return {
    user_id: currentUser.id,
    symbol: stock.symbol,
    name: stock.name,
    price: stock.price,
    change_percent: stock.change,
    target_price: stock.target,
  };
}

async function setupSupabase() {
  try {
    const response = await fetch("/api/config");
    if (!response.ok) throw new Error("Config endpoint unavailable");

    const config = await response.json();
    if (!config.supabaseUrl || !config.supabasePublishableKey) {
      throw new Error("Supabase env vars missing");
    }

    const { createClient } = await import("https://esm.sh/@supabase/supabase-js@2");
    supabaseClient = createClient(config.supabaseUrl, config.supabasePublishableKey);
    setDbStatus("Supabase 已連線", "connected");
  } catch (error) {
    supabaseClient = null;
    setDbStatus("使用本機暫存，尚未連線 Supabase", "offline");
  }
}

async function setupAuth() {
  if (!supabaseClient) {
    setUserStatus("尚未登入", "offline");
    updateAuthUi();
    return;
  }

  const { data, error } = await supabaseClient.auth.getUser();
  currentUser = error ? null : data.user;
  updateAuthUi();

  supabaseClient.auth.onAuthStateChange(async (_event, session) => {
    currentUser = session?.user || null;
    updateAuthUi();
    await loadUserData();
  });
}

function updateAuthUi() {
  const loginButton = document.querySelector("#loginButton");
  const logoutButton = document.querySelector("#logoutButton");
  const addSymbolButton = document.querySelector("#addSymbolButton");
  const saveJournalButton = document.querySelector("#saveJournalButton");

  loginButton.hidden = Boolean(currentUser);
  logoutButton.hidden = !currentUser;
  addSymbolButton.disabled = !currentUser;
  saveJournalButton.disabled = !currentUser;

  if (currentUser) {
    setUserStatus(`${userLabel(currentUser)} 的後台`, "connected");
    return;
  }

  setUserStatus("請用 Google 登入啟用個人後台", "offline");
}

async function signInWithGoogle() {
  if (!supabaseClient) {
    setDbStatus("尚未連線 Supabase，無法登入", "offline");
    return;
  }

  const { error } = await supabaseClient.auth.signInWithOAuth({
    provider: "google",
    options: {
      redirectTo: window.location.origin,
    },
  });

  if (error) setUserStatus(`Google 登入失敗：${error.message}`, "offline");
}

async function signOut() {
  if (!supabaseClient) return;
  await supabaseClient.auth.signOut();
  currentUser = null;
  watchlist = [...initialWatchlist];
  document.querySelector("#journalText").value = "";
  document.querySelector("#saveStatus").textContent = "尚未儲存";
  updateAuthUi();
  renderWatchlist();
}

async function loadUserData() {
  await loadWatchlist();
  await loadJournal();
}

async function seedWatchlistIfEmpty() {
  const payload = initialWatchlist.map((stock) => toDbStock(stock));
  const { error } = await supabaseClient.from("watchlist_items").insert(payload);
  if (error) {
    setDbStatus("建立個人清單失敗，請確認 RLS schema", "offline");
    return false;
  }
  return true;
}

async function loadWatchlist() {
  if (!supabaseClient || !currentUser) {
    watchlist = [...initialWatchlist];
    renderWatchlist();
    return;
  }

  const { data, error } = await supabaseClient
    .from("watchlist_items")
    .select("id,symbol,name,price,change_percent,target_price")
    .order("created_at", { ascending: true });

  if (error) {
    setDbStatus("個人資料表尚未完成，使用示範資料", "offline");
    watchlist = [...initialWatchlist];
    renderWatchlist();
    return;
  }

  if (data.length === 0 && (await seedWatchlistIfEmpty())) {
    await loadWatchlist();
    return;
  }

  watchlist = data.map(toAppStock);
  renderWatchlist();
}

async function saveStock(stock) {
  if (!supabaseClient || !currentUser) return;

  const { error } = await supabaseClient.from("watchlist_items").insert(toDbStock(stock));
  if (error) setDbStatus("新增股票未同步，請確認個人資料權限", "offline");
}

async function loadJournal() {
  const journalText = document.querySelector("#journalText");
  const saveStatus = document.querySelector("#saveStatus");

  if (!supabaseClient || !currentUser) {
    const savedJournal = window.localStorage.getItem("stock-market-journal");
    journalText.value = savedJournal || "";
    saveStatus.textContent = savedJournal ? "已載入本機筆記" : "登入後可儲存個人雲端筆記";
    return;
  }

  const { data, error } = await supabaseClient
    .from("journal_entries")
    .select("content,updated_at")
    .eq("entry_key", "daily")
    .maybeSingle();

  if (error) {
    setDbStatus("個人筆記資料表尚未完成", "offline");
    return;
  }

  journalText.value = data?.content || "";
  saveStatus.textContent = data
    ? `已載入個人筆記 ${new Date(data.updated_at).toLocaleTimeString("zh-TW")}`
    : "尚未儲存個人筆記";
}

function renderWatchlist() {
  const tbody = document.querySelector("#watchlistTable");
  tbody.innerHTML = watchlist
    .map((stock) => {
      const trendClass = stock.change >= 0 ? "gain" : "loss";
      const changeText = `${stock.change >= 0 ? "+" : ""}${stock.change.toFixed(2)}%`;

      return `
        <tr>
          <td><strong>${stock.symbol}</strong></td>
          <td>${stock.name}</td>
          <td>${formatMoney.format(stock.price)}</td>
          <td class="${trendClass}">${changeText}</td>
          <td>${formatMoney.format(stock.target)}</td>
        </tr>
      `;
    })
    .join("");
}

function renderPortfolio() {
  const bars = document.querySelector("#portfolioBars");
  bars.innerHTML = portfolio
    .map(
      (item) => `
        <div class="bar-row">
          <div class="bar-label">
            <strong>${item.name}</strong>
            <span>${item.weight}%</span>
          </div>
          <div class="bar-track" aria-hidden="true">
            <div class="bar-fill" style="width: ${item.weight}%"></div>
          </div>
        </div>
      `
    )
    .join("");
}

function refreshDemoData() {
  watchlist.forEach((stock) => {
    const delta = Number((Math.random() * 4 - 2).toFixed(2));
    stock.change = delta;
    stock.price = Number((stock.price * (1 + delta / 100)).toFixed(2));
  });

  const totalAssets = 1268400 + Math.round(Math.random() * 70000 - 25000);
  const pnl = Math.round(Math.random() * 90000 - 12000);

  document.querySelector("#totalAssets").textContent = formatMoney.format(totalAssets);
  document.querySelector("#unrealizedPnl").textContent = `${pnl >= 0 ? "+" : ""}${formatMoney.format(pnl)}`;
  document.querySelector("#unrealizedPnl").className = pnl >= 0 ? "gain" : "loss";
  document.querySelector("#cashLevel").textContent = `${(12 + Math.random() * 12).toFixed(1)}%`;
  document.querySelector("#riskScore").textContent = pnl < -5000 ? "中" : "低";

  renderWatchlist();
}

async function addSymbol() {
  if (!currentUser) {
    setUserStatus("請先用 Google 登入", "offline");
    return;
  }

  const symbol = window.prompt("請輸入股票代號");
  if (!symbol) return;

  const name = window.prompt("請輸入股票名稱") || "自訂股票";
  const price = Number(window.prompt("請輸入目前價格") || 0);
  const target = Number(window.prompt("請輸入目標價格") || price);
  const stock = {
    symbol: symbol.trim().toUpperCase(),
    name: name.trim(),
    price,
    change: 0,
    target,
  };

  watchlist.push(stock);
  renderWatchlist();
  await saveStock(stock);
}

function setupJournalSave() {
  const journalText = document.querySelector("#journalText");
  const saveStatus = document.querySelector("#saveStatus");

  document.querySelector("#saveJournalButton").addEventListener("click", async () => {
    if (!currentUser) {
      window.localStorage.setItem("stock-market-journal", journalText.value);
      saveStatus.textContent = "請登入後儲存個人雲端筆記";
      return;
    }

    const { error } = await supabaseClient.from("journal_entries").upsert(
      {
        user_id: currentUser.id,
        entry_key: "daily",
        content: journalText.value,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "user_id,entry_key" }
    );

    if (error) {
      saveStatus.textContent = "雲端儲存失敗，請確認個人資料權限";
      return;
    }

    saveStatus.textContent = `已儲存個人雲端筆記 ${new Date().toLocaleTimeString("zh-TW")}`;
  });
}

document.querySelector("#refreshButton").addEventListener("click", refreshDemoData);
document.querySelector("#addSymbolButton").addEventListener("click", addSymbol);
document.querySelector("#loginButton").addEventListener("click", signInWithGoogle);
document.querySelector("#logoutButton").addEventListener("click", signOut);

renderPortfolio();
setupJournalSave();
await setupSupabase();
await setupAuth();
await loadUserData();
