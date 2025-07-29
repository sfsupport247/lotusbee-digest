import yfinance as yf
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed # Import for threading

def fetch_sp500_tickers_from_wikipedia():
    """
    Reads the list of S&P 500 company tickers from Wikipedia.

    Returns:
        list: A list of S&P 500 ticker symbols.
    """
    try:
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        sp500_tables = pd.read_html(url, attrs={'id': 'constituents'}, index_col='Symbol')
        sp500_df = sp500_tables[0]
        tickers = sp500_df.index.tolist()
        print(f"Fetched {len(tickers)} tickers from Wikipedia.")
        return tickers
    except Exception as e:
        print(f"Error reading S&P 500 tickers from Wikipedia: {e}")
        print("Please check the URL and your internet connection.")
        return []

# Helper function to fetch data for a single ticker
def fetch_ticker_data(ticker, period_to_fetch="5d"):
    """
    Fetches historical data for a single ticker and calculates percentage change.
    Returns a dictionary of results or None if an error occurs.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period_to_fetch)

        if len(hist) < 2:
            # print(f"Skipping {ticker}: Not enough historical data for percentage change.")
            return None # Return None to indicate failure for this ticker

        today_close = hist['Close'].iloc[-1]
        previous_close = hist['Close'].iloc[-2]

        if previous_close == 0:
            percent_change = 0
        else:
            percent_change = ((today_close - previous_close) / previous_close) * 100

        return {
            "symbol": ticker,
            "price": round(today_close, 2),
            "percent_change": round(percent_change, 2)
        }
    except Exception as e:
        # print(f"Error fetching data for {ticker}: {e}")
        return None # Return None if any error occurs during fetch

def get_top_movers_threaded(tickers, top_n=3, max_workers=10): # Renamed and added max_workers
    """
    Fetches the top N gainers and losers based on percentage change for the given tickers,
    using threads for speed.

    Args:
        tickers (list): List of stock tickers.
        top_n (int): Number of top gainers and losers to return.
        max_workers (int): Maximum number of threads to use.

    Returns:
        tuple: DataFrames for top N gainers and top N losers.
    """
    all_data = []
    period_to_fetch = "5d"

    # Using ThreadPoolExecutor for parallel execution
    # max_workers specifies the number of threads that will run concurrently.
    # Be careful not to set this too high as it can overwhelm the target server
    # or your own network bandwidth. 10-20 is often a good starting point for web requests.
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks to the executor
        # The map method is simpler if you just want to apply a function to each item
        # and collect results in order. For collecting results as they complete,
        # and handling individual task failures, as_completed is better.
        future_to_ticker = {executor.submit(fetch_ticker_data, ticker, period_to_fetch): ticker for ticker in tickers}

        processed_count = 0
        total_tickers = len(tickers)
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                result = future.result() # Get the result of the completed task
                if result: # If data was successfully fetched and processed
                    all_data.append(result)
            except Exception as exc:
                # This catches exceptions that happened within the fetch_ticker_data function
                # if they weren't caught there and returned None.
                print(f'{ticker} generated an exception: {exc}')
            finally:
                processed_count += 1
                # Optional: print progress
                if processed_count % 50 == 0 or processed_count == total_tickers:
                    print(f"Processed {processed_count}/{total_tickers} tickers...")

    df = pd.DataFrame(all_data)
    if df.empty:
        print("No data collected for any tickers. Returning empty DataFrames.")
        return pd.DataFrame(), pd.DataFrame()

    top_gainers = df.sort_values(by="percent_change", ascending=False).head(top_n)
    top_losers = df.sort_values(by="percent_change").head(top_n)
    return top_gainers, top_losers

# --- Main execution ---
if __name__ == "__main__":
    start_time = time.time() # Start timer

    sp500_tickers = fetch_sp500_tickers_from_wikipedia()

    if sp500_tickers:
        print(f"\nFetching top movers for {len(sp500_tickers)} S&P 500 tickers using threads...")
        # You can adjust max_workers. For I/O bound tasks like network requests,
        # you can often go higher than the number of CPU cores.
        gainers, losers = get_top_movers_threaded(sp500_tickers, max_workers=20) # Increased workers

        print("\n--- Top 3 S&P 500 Gainers (based on last two trading days) ---")
        if not gainers.empty:
            print(gainers.to_string(index=False))
        else:
            print("No gainers found.")

        print("\n--- Top 3 S&P 500 Losers (based on last two trading days) ---")
        if not losers.empty:
            print(losers.to_string(index=False))
        else:
            print("No losers found.")
    else:
        print("Cannot fetch top movers without S&P 500 tickers.")

    end_time = time.time() # End timer
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds.")