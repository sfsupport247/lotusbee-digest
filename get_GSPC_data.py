import yfinance as yf
from datetime import date, timedelta

def get_sp500_index():
    """
    Fetches and prints the S&P 500 index value (via ^GSPC) from Yahoo Finance for today only.
    """
    try:
        # Define today's date
        today = date.today()

        # Define the ticker for the S&P 500 index
        tickerSP500 = "^GSPC"
        tickerDJI40 = "^DJI"
        tickerRUT2000 = "^RUT"
        tickerIXIC = "^IXIC"

        # Fetch data only for today
        start_date = today
        end_date = today + timedelta(days=1)  # End date is exclusive in yfinance

        print(f"Fetching data for S&P 500 index (via ^GSPC) for today ({today})...")
        dataSP500 = yf.download(tickerSP500, start=start_date, end=end_date, progress=False, auto_adjust=False)
        dataDJI40 = yf.download(tickerDJI40, start=start_date, end=end_date, progress=False, auto_adjust=False)
        dataRUT2000 = yf.download(tickerRUT2000, start=start_date, end=end_date, progress=False, auto_adjust=False)
        dataIXIC = yf.download(tickerIXIC, start=start_date, end=end_date, progress=False, auto_adjust=False)

        # Print the raw data
        if not dataSP500.empty:
            print(dataSP500)
            print(dataDJI40)
            print(dataRUT2000)
            print(dataIXIC)
        else:
            print(f"No data available for {today}.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    get_sp500_index()