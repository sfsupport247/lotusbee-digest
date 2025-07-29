from flask import Flask, jsonify
import yfinance as yf
from datetime import date, timedelta

app = Flask(__name__)

def fetch_index_data(ticker, index_name):
    """
    Fetches and returns today's and the most recent previous trading day's data for the given index ticker.
    
    Args:
        ticker (str): The ticker symbol for the index.
        index_name (str): The name of the index (for display purposes).
    
    Returns:
        dict: A dictionary containing the index name, today's close, previous close, percentage change, and status.
    """
    try:
        # Define today's date
        today = date.today()
        start_date = today - timedelta(days=7)  # Fetch data for the last 7 days to ensure we capture recent trading days
        end_date = today + timedelta(days=1)  # End date is exclusive in yfinance

        # Fetch data for the ticker
        data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=False)

        if not data.empty:
            # Sort the data by date to ensure proper ordering
            data = data.sort_index()

            # Get the last two available trading days
            available_dates = data.index[-2:]  # Get the last two dates
            if len(available_dates) < 2:
                return {
                    "index": index_name,
                    "today_close": None,
                    "previous_close": None,
                    "percent_change": None,
                    "status": "Not enough data to calculate change."
                }

            # Extract today's and the previous trading day's Close values
            previous_close = float(data.loc[available_dates[0], 'Close'])
            today_close = float(data.loc[available_dates[1], 'Close'])

            # Calculate percentage change
            change = today_close - previous_close
            percent_change = (change / previous_close) * 100

            return {
                "index": index_name,
                "today_close": round(today_close, 2),
                "previous_close": round(previous_close, 2),
                "percent_change": round(percent_change, 2),
                "status": "success"
            }
        else:
            return {
                "index": index_name,
                "today_close": None,
                "previous_close": None,
                "percent_change": None,
                "status": f"No data available for the last 7 days."
            }
    except Exception as e:
        return {
            "index": index_name,
            "today_close": None,
            "previous_close": None,
            "percent_change": None,
            "status": f"Error: {str(e)}"
        }

@app.route('/api/index-data', methods=['GET'])
def get_index_data():
    """
    API endpoint to fetch today's and the previous trading day's data for major indexes.
    """
    indexes = {
        "^GSPC": "S&P 500",
        "^DJI": "Dow Jones Industrial Average",
        "^RUT": "Russell 2000",
        "^IXIC": "Nasdaq Composite"
    }

    # Fetch data for all indexes
    results = []
    for ticker, index_name in indexes.items():
        results.append(fetch_index_data(ticker, index_name))

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, port=5001)