import yfinance as yf
from datetime import date, timedelta
import pandas as pd

def get_major_indexes_data():
    """
    Fetches data for major indexes from Yahoo Finance based on today's date.
    Returns a formatted string with the latest close and percentage change.
    """
    try:
        # Define today's date
        today = date.today()

        # Define the major indexes and their corresponding ETF tickers
        indexes = {
            "S&P 500 (via SPY)": "SPY",
            "Nasdaq Composite (via QQQ)": "QQQ",
            "Dow Jones Industrial Average (via DIA)": "DIA",
            "Russell 2000 (via IWM)": "IWM"
        }

        # Fetch data for the last 7 days to ensure we capture the previous trading day
        start_date = today - timedelta(days=7)
        end_date = today + timedelta(days=1)  # End date is exclusive in yfinance

        output = []
        for name, ticker in indexes.items():
            print(f"Fetching data for {name} ({ticker})...")
            data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)

            if not data.empty:
                # Find the last available date before or equal to today
                last_available_date = data.index[data.index <= pd.Timestamp(today)].max()

                if pd.notna(last_available_date):  # Ensure a valid date is found
                    latest_close = data.loc[last_available_date, 'Close']

                    # Check if there's a previous day for change calculation
                    previous_date = data.index[data.index < last_available_date].max()
                    if pd.notna(previous_date):  # Ensure a valid previous date is found
                        previous_close = data.loc[previous_date, 'Close']
                        change = latest_close - previous_close
                        percent_change = (change / previous_close) * 100
                        arrow = "▲" if change >= 0 else "▼"
                        output.append(
                            f"{name}: {latest_close:,.2f} {arrow} {percent_change:+.2f}%"
                        )
                    else:
                        output.append(
                            f"{name}: {latest_close:,.2f} (No previous day data for change calculation)"
                        )
                else:
                    output.append(f"{name}: No data available for today.")
            else:
                output.append(f"{name}: No data downloaded for {ticker}.")

        return "\n".join(output)

    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Fetch and print the major indexes data
    result = get_major_indexes_data()
    print(result)