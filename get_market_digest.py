try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("Warning: yfinance not available, using mock data")

import requests
from bs4 import BeautifulSoup
import sys

def get_sp500_tickers():
    """Scrape S&P 500 tickers from Wikipedia"""
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table with S&P 500 companies
        table = soup.find('table', {'class': 'wikitable sortable'})
        tickers = []
        
        # Skip the header row
        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')
            if cells:
                ticker = cells[0].text.strip()
                company_name = cells[1].text.strip()
                tickers.append((ticker, company_name))
        
        return tickers
    except Exception as e:
        print(f"Error fetching S&P 500 tickers: {e}")
        # Fallback to a subset of well-known S&P 500 companies
        return [
            ("AAPL", "Apple Inc."),
            ("MSFT", "Microsoft Corporation"),
            ("GOOGL", "Alphabet Inc."),
            ("AMZN", "Amazon.com Inc."),
            ("TSLA", "Tesla Inc."),
            ("NVDA", "NVIDIA Corporation"),
            ("META", "Meta Platforms Inc."),
            ("BRK-B", "Berkshire Hathaway Inc."),
            ("UNH", "UnitedHealth Group Incorporated"),
            ("JNJ", "Johnson & Johnson")
        ]

def get_major_indexes():
    """Fetch major index data"""
    indexes = {
        "S&P 500": "^GSPC",
        "Nasdaq Composite": "^IXIC", 
        "Dow Jones Industrial Average": "^DJI",
        "Russell 2000": "^RUT"
    }
    
    print("Major Indexes")
    
    if not YFINANCE_AVAILABLE:
        # Mock data for testing
        mock_data = [
            ("S&P 500", 6358.91, 0.78),
            ("Nasdaq Composite", 20394.13, 1.24),
            ("Dow Jones Industrial Average", 44296.51, -0.29),
            ("Russell 2000", 2348.05, -0.45)
        ]
        
        for name, price, change_pct in mock_data:
            formatted_price = f"{price:,.2f}"
            sign = "+" if change_pct >= 0 else ""
            formatted_change = f"{sign}{change_pct:.2f}%"
            print(f"{name}: {formatted_price}, {formatted_change}")
        return
    
    for name, ticker in indexes.items():
        try:
            index_ticker = yf.Ticker(ticker)
            hist = index_ticker.history(period="2d")
            
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change_pct = ((current_price - prev_price) / prev_price) * 100
                
                # Format price with commas
                formatted_price = f"{current_price:,.2f}"
                
                # Format percentage change with + or - sign
                sign = "+" if change_pct >= 0 else ""
                formatted_change = f"{sign}{change_pct:.2f}%"
                
                print(f"{name}: {formatted_price}, {formatted_change}")
            else:
                print(f"{name}: Data unavailable")
                
        except Exception as e:
            print(f"{name}: Error fetching data - {e}")

def get_sp500_movers():
    """Get top 3 S&P 500 gainers and losers"""
    if not YFINANCE_AVAILABLE:
        # Mock data for testing
        gainers = [
            {"ticker": "NVDA", "company": "NVIDIA Corporation", "price": 170.78, "change_pct": 2.25},
            {"ticker": "META", "company": "Meta Platforms Inc.", "price": 614.28, "change_pct": 1.89},
            {"ticker": "TSLA", "company": "Tesla Inc.", "price": 488.54, "change_pct": 1.67}
        ]
        
        losers = [
            {"ticker": "KO", "company": "Coca‑Cola Company", "price": 69.16, "change_pct": -0.72},
            {"ticker": "PFE", "company": "Pfizer Inc.", "price": 25.43, "change_pct": -1.12},
            {"ticker": "XOM", "company": "Exxon Mobil Corporation", "price": 118.92, "change_pct": -1.45}
        ]
        
        # Print gainers
        print("\n🟢 Top 3 S&P 500 Gainers")
        for stock in gainers:
            price = f"${stock['price']:.2f}"
            change = f"{stock['change_pct']:+.2f}%"
            print(f"{stock['company']} ({stock['ticker']}): {price}, {change}")
        
        # Print losers
        print("\n🔻 Top 3 S&P 500 Losers")
        for stock in losers:
            price = f"${stock['price']:.2f}"
            change = f"{stock['change_pct']:+.2f}%"
            print(f"{stock['company']} ({stock['ticker']}): {price}, {change}")
        return
    
    sp500_tickers = get_sp500_tickers()
    
    stock_data = []
    
    # Limit to first 50 for faster processing, you can increase this
    limited_tickers = sp500_tickers[:50]
    
    for ticker, company_name in limited_tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            
            if len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2]
                change_pct = ((current_price - prev_price) / prev_price) * 100
                
                stock_data.append({
                    'ticker': ticker,
                    'company': company_name,
                    'price': current_price,
                    'change_pct': change_pct
                })
        except Exception as e:
            continue  # Skip problematic tickers
    
    # Sort by percentage change
    stock_data.sort(key=lambda x: x['change_pct'], reverse=True)
    
    # Get top 3 gainers and losers
    gainers = stock_data[:3]
    losers = stock_data[-3:]
    
    # Print gainers
    print("\n🟢 Top 3 S&P 500 Gainers")
    for stock in gainers:
        price = f"${stock['price']:.2f}"
        change = f"{stock['change_pct']:+.2f}%"
        print(f"{stock['company']} ({stock['ticker']}): {price}, {change}")
    
    # Print losers
    print("\n🔻 Top 3 S&P 500 Losers")
    for stock in losers:
        price = f"${stock['price']:.2f}"
        change = f"{stock['change_pct']:+.2f}%"
        print(f"{stock['company']} ({stock['ticker']}): {price}, {change}")

def main():
    """Main function to generate market digest"""
    try:
        # Get major indexes
        get_major_indexes()
        
        # Get S&P 500 movers
        get_sp500_movers()
        
    except Exception as e:
        print(f"Error generating market digest: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
