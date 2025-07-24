import yfinance as yf
import pandas as pd

# 1. Define index tickers
indexes = {
    "S&P 500": "^GSPC",
    "Nasdaq Composite": "^IXIC",
    "Dow Jones": "^DJI",
    "Russell 2000": "^RUT"
}

# 2. Sample stock lists
sp500_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "PFE", "XOM", "KO"]
russell_symbols = ["RBLX", "FUBO", "RITM", "MNDY", "IPI"]  # example Russell 2000 names

# 3. Fetch and format index data
idx_data = []
for name, sym in indexes.items():
    info = yf.Ticker(sym).info
    price = info.get("regularMarketPrice")
    pct = info.get("regularMarketChangePercent")
    idx_data.append({
        "Index": name,
        "Price": price,
        "Change (%)": f"{pct:+.2f}%" if pct is not None else "N/A"
    })
df_idx = pd.DataFrame(idx_data)

# 4. Fetch S&P stock changes
def get_changes(symbols):
    stash = []
    for sym in symbols:
        info = yf.Ticker(sym).info
        pct = info.get("regularMarketChangePercent", 0)
        stash.append({"Symbol": sym,
                      "Price": info.get("regularMarketPrice"),
                      "Change (%)": pct})
    return pd.DataFrame(stash)

df_sp = get_changes(sp500_symbols)
df_ru = get_changes(russell_symbols)

df_sp_gainers = df_sp.nlargest(3, "Change (%)")
df_sp_losers = df_sp.nsmallest(3, "Change (%)")
df_ru_gainers = df_ru.nlargest(3, "Change (%)")
df_ru_losers = df_ru.nsmallest(3, "Change (%)")

# 5. Print results
print("📊 Major Indexes:")
print(df_idx.to_string(index=False))

print("\n🟢 Top 3 S&P 500 Gainers:")
for _, r in df_sp_gainers.iterrows():
    print(f"- {r.Symbol}: {r.Price} USD, {r['Change (%)']:+.2f}%")

print("\n🔻 Top 3 S&P 500 Losers:")
for _, r in df_sp_losers.iterrows():
    print(f"- {r.Symbol}: {r.Price} USD, {r['Change (%)']:+.2f}%")

print("\n🟢 Top 3 Russell 2000 Gainers:")
for _, r in df_ru_gainers.iterrows():
    print(f"- {r.Symbol}: {r.Price} USD, {r['Change (%)']:+.2f}%")

print("\n🔻 Top 3 Russell 2000 Losers:")
for _, r in df_ru_losers.iterrows():
    print(f"- {r.Symbol}: {r.Price} USD, {r['Change (%)']:+.2f}%")
