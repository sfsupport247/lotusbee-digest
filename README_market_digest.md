# Market Digest Script

## Overview
The `get_market_digest.py` script fetches and displays daily stock market data using yfinance and Wikipedia.

## Features

### Major Indexes
- S&P 500 (^GSPC)
- Nasdaq Composite (^IXIC)
- Dow Jones Industrial Average (^DJI)
- Russell 2000 (^RUT)

Shows current level and daily percentage change.

### S&P 500 Analysis
- Scrapes current S&P 500 constituents from Wikipedia
- Finds top 3 gainers and losers based on daily percentage change
- Displays company name, ticker, current price, and percentage change

## Dependencies
- yfinance: For stock and index data
- requests: For HTTP requests
- beautifulsoup4: For HTML parsing
- pandas: For data manipulation (available through yfinance)

## Error Handling
- Falls back to mock data if yfinance is not available
- Falls back to curated S&P 500 list if Wikipedia is not accessible
- Gracefully handles individual ticker failures

## Output Format
```
Major Indexes
S&P 500: 6,358.91, +0.78%
Nasdaq Composite: 20,394.13, +1.24%
Dow Jones Industrial Average: 44,296.51, -0.29%
Russell 2000: 2,348.05, -0.45%

🟢 Top 3 S&P 500 Gainers
NVIDIA Corporation (NVDA): $170.78, +2.25%
Meta Platforms Inc. (META): $614.28, +1.89%
Tesla Inc. (TSLA): $488.54, +1.67%

🔻 Top 3 S&P 500 Losers
Coca‑Cola Company (KO): $69.16, -0.72%
Pfizer Inc. (PFE): $25.43, -1.12%
Exxon Mobil Corporation (XOM): $118.92, -1.45%
```

## Usage
```bash
python get_market_digest.py
```

The script is designed to run in GitHub Actions workflows and output the market digest to stdout.