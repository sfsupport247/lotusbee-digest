from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
from typing import List, Dict, Union, Optional

# Initialize the FastAPI application
app = FastAPI(
    title="Cryptocurrency Price API",
    description="API to fetch current prices and 24-hour percentage changes of selected cryptocurrencies from CoinGecko.",
    version="1.1.0"
)

def fetch_crypto_prices() -> Union[List[Dict[str, Union[str, float, None]]], Dict[str, str]]:
    """
    Fetches the current prices and 24-hour percentage changes of Bitcoin, Ethereum, Solana, and XRP from CoinGecko.

    Returns:
        list: A list of dictionaries containing the cryptocurrency name, symbol, current price in USD,
              and 24-hour percentage change. Includes status for unavailable data.
        dict: An error dictionary if the API request fails.
    """
    try:
        # Define the cryptocurrencies to fetch using their CoinGecko IDs
        # Note: 'ripple' is the CoinGecko ID for XRP
        crypto_ids = ["bitcoin", "ethereum", "solana", "ripple"]
        
        # CoinGecko API endpoint for simple price lookup
        url = "https://api.coingecko.com/api/v3/simple/price"
        
        # Parameters for the API request
        params = {
            "ids": ",".join(crypto_ids),  # Join the crypto IDs with commas
            "vs_currencies": "usd",       # Fetch prices in USD
            "include_24hr_change": "true" # Include 24-hour percentage change
        }

        # Make the API request
        response = requests.get(url, params=params, timeout=10)  # Added a timeout for robustness
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        data = response.json()

        # Process the response to extract prices and 24-hour changes
        results: List[Dict[str, Union[str, float, None]]] = []
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
                    "24hr_change_percent": data[crypto_id].get("usd_24h_change", None)
                })
            else:
                # If data for a specific crypto is not available
                results.append({
                    "name": crypto_name,
                    "symbol": crypto_symbol,
                    "price_usd": None,  # Explicitly None for missing price
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

@app.get('/api/crypto-prices', response_model=List[Dict[str, Union[str, float, None]]])
async def get_crypto_prices_endpoint():
    """
    API endpoint to fetch the current prices and 24-hour percentage changes of Bitcoin, Ethereum, Solana, and XRP.
    """
    data = fetch_crypto_prices()
    
    # If fetch_crypto_prices returns an error dictionary, raise an HTTPException
    if isinstance(data, dict) and "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
    
    return JSONResponse(content=data)

# To run this application:
# 1. Save the code as a Python file (e.g., main.py).
# 2. Make sure you have uvicorn installed: pip install uvicorn
# 3. Run from your terminal: uvicorn main:app --reload --port 5004
# 4. http://127.0.0.1:5004/api/crypto-prices