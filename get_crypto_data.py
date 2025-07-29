from flask import Flask, jsonify
import requests

app = Flask(__name__)

def fetch_crypto_data(crypto_ids):
    """
    Fetches the current prices and 24-hour percentage changes of cryptocurrencies from CoinGecko.

    Args:
        crypto_ids (list): A list of cryptocurrency IDs to fetch data for.

    Returns:
        list: A list of dictionaries containing the cryptocurrency name, symbol, current price in USD,
              and 24-hour percentage change. Includes status for unavailable data.
    """
    try:
        # CoinGecko API endpoint for simple price lookup
        url = "https://api.coingecko.com/api/v3/simple/price"
        
        # Parameters for the API request
        params = {
            "ids": ",".join(crypto_ids),  # Join the crypto IDs with commas
            "vs_currencies": "usd",       # Fetch prices in USD
            "include_24hr_change": "true" # Include 24-hour percentage change
        }

        # Make the API request
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        data = response.json()

        # Process the response to extract prices and 24-hour changes
        results = []
        for crypto_id in crypto_ids:
            # Get the display name and symbol based on the crypto_id
            name_map = {
                "bitcoin": "Bitcoin",
                "ethereum": "Ethereum",
                "solana": "Solana",
                "ripple": "XRP"  # Special handling for Ripple/XRP symbol
            }
            symbol_map = {
                "bitcoin": "BTC",
                "ethereum": "ETH",
                "solana": "SOL",
                "ripple": "XRP"
            }

            crypto_name = name_map.get(crypto_id, crypto_id.capitalize())
            crypto_symbol = symbol_map.get(crypto_id, crypto_id[:3].upper())

            if crypto_id in data and "usd" in data[crypto_id]:
                results.append({
                    "name": crypto_name,
                    "symbol": crypto_symbol,
                    "price_usd": data[crypto_id]["usd"],
                    "24hr_change_percent": round(data[crypto_id].get("usd_24h_change", 0), 2)
                })
            else:
                # If data for a specific crypto is not available
                results.append({
                    "name": crypto_name,
                    "symbol": crypto_symbol,
                    "price_usd": None,
                    "24hr_change_percent": None,
                    "status": "Data not available"
                })
        return results

    except requests.exceptions.Timeout:
        # Handle request timeout error
        return {"error": "The request to CoinGecko timed out."}
    except requests.exceptions.RequestException as e:
        # Handle other request-related errors (e.g., connection error, HTTP error)
        return {"error": f"Failed to fetch data from CoinGecko: {e}"}
    except Exception as e:
        # Catch any other unexpected errors
        return {"error": f"An unexpected error occurred: {str(e)}"}

@app.route('/api/crypto-data', methods=['GET'])
def get_crypto_data():
    """
    API endpoint to fetch the current prices and 24-hour percentage changes of cryptocurrencies.
    """
    crypto_ids = ["bitcoin", "ethereum", "solana", "ripple"]  # Define the cryptocurrencies to fetch
    data = fetch_crypto_data(crypto_ids)

    # If there's an error, return it with a 500 status code
    if isinstance(data, dict) and "error" in data:
        return jsonify({"error": data["error"]}), 500

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, port=5006)

    # python .\get_crypto_data.py
    # http://127.0.0.1:5006/api/crypto-data