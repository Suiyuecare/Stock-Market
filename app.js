const watchlist = [
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

function addSymbol() {
  const symbol = window.prompt("請輸入股票代號");
  if (!symbol) return;

  const name = window.prompt("請輸入股票名稱") || "自訂股票";
  const price = Number(window.prompt("請輸入目前價格") || 0);
  const target = Number(window.prompt("請輸入目標價格") || price);

  watchlist.push({
    symbol: symbol.trim().toUpperCase(),
    name: name.trim(),
    price,
    change: 0,
    target,
  });

  renderWatchlist();
}

function setupJournal() {
  const journalText = document.querySelector("#journalText");
  const saveStatus = document.querySelector("#saveStatus");
  const savedJournal = window.localStorage.getItem("stock-market-journal");

  if (savedJournal) {
    journalText.value = savedJournal;
    saveStatus.textContent = "已載入上次筆記";
  }

  document.querySelector("#saveJournalButton").addEventListener("click", () => {
    window.localStorage.setItem("stock-market-journal", journalText.value);
    saveStatus.textContent = `已儲存 ${new Date().toLocaleTimeString("zh-TW")}`;
  });
}

document.querySelector("#refreshButton").addEventListener("click", refreshDemoData);
document.querySelector("#addSymbolButton").addEventListener("click", addSymbol);

renderWatchlist();
renderPortfolio();
setupJournal();
