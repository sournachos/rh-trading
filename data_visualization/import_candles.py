# importing historical candle data for any stock marker ticker
# candle data needs to be 1m candles for jesse's visualization
import json
import os
import uuid

import requests
from dotenv import load_dotenv
from jesse.modes.import_candles_mode import (
    store_candles_list as store_candles_from_list,
)
from jesse.services.db import database

load_dotenv()
api_key: str = os.getenv("API_KEY")

"""
Given a ticker and a date range, it will store historical candle data
in the local docker db instance for backtesting strategies on.
"""


def db_import(ticker, start_date, end_date, api_key) -> None:
    headers = {"Accept": "application/json", "Authorization": f"Bearer {api_key}"}
    url = f"https://api.marketdata.app/v1/stocks/candles/1/{ticker}?from={start_date}&to={end_date}"
    candles = json.loads(requests.request("GET", url, headers=headers).text)
    arr = [
        {
            "id": str(uuid.uuid4()),
            "exchange": "NYSE",
            "symbol": f"NYSE-{ticker}",
            "timeframe": "1m",
            "timestamp": candles["t"][i] * 1000,
            "open": candles["o"][i],
            "close": candles["c"][i],
            "high": candles["h"][i],
            "low": candles["l"][i],
            "volume": candles["v"][i],
        }
        for i in range(len(candles["t"]))
    ]
    database.open_connection()
    store_candles_from_list(arr)
    database.close_connection()

    with open(f"./ticker_data/{ticker}/candle_data.json", "w") as f:
        json.dump({"data": arr}, f, indent=4)


# Customize ur dates here (free for the last year of data)
start_date = "2024-01-01"
end_date = "2024-10-05"

# with open("./stock_lists/mag7.json") as f:
#     tickers = json.load(f)["tickers"]
# OR
tickers = ["AAPL"]  # free demo data from the API lol

if tickers:
    for ticker in tickers:
        db_import(ticker, start_date, end_date, api_key)
