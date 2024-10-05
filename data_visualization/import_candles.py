# importing historical candle data for any stock marker ticker
# candle data needs to be 1m candles for jesse's visualization
import json
import os
import uuid

import requests
from dotenv import load_dotenv

# from jesse.modes.import_candles_mode import (
#     store_candles_list as store_candles_from_list,
# )
# from jesse.services.db import database

with open("./stock_lists/mag7.json") as f:
    tickers = json.load(f)["tickers"]
print(tickers)

load_dotenv()
ticker: str = os.getenv("TICKER_TO_GET_HISTORICAL_CANDLES_FOR")
start_date: str = os.getenv("HISTORICAL_CANDLES_START_DATE")
end_date: str = os.getenv("HISTORICAL_CANDLES_END_DATE")
api_key: str = os.getenv("API_KEY")

"""
Given a ticker and a date range, it will store historical candle data
in the local docker db instance for backtesting strategies on.
"""


# extended_hours = "true"  # If sent as a URL parameter, returns data from 4am ET to 8pm ET
def data_dump(ticker, start_date, end_date, api_key) -> None:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&apikey={api_key}&interval=1min&extended_hours=false"
    candles = json.loads(requests.request("GET", url).text)
    print(candles)


#     arr = [
#         {
#             "id": str(uuid.uuid4()),
#             "exchange": "NYSE",
#             "symbol": ticker,
#             "timeframe": "1m",
#             "timestamp": candles["t"][i] * 1000,
#             "open": candles["o"][i],
#             "close": candles["c"][i],
#             "high": candles["h"][i],
#             "low": candles["l"][i],
#             "volume": candles["v"][i],
#         }
#         for i in range(len(candles["t"]))
#     ]
#     database.open_connection()
#     store_candles_from_list(arr)
#     database.close_connection()


if tickers:
    for ticker in tickers:
        data_dump(ticker, start_date, end_date, api_key)
# else:
#     data_dump(ticker, start_date, end_date, api_key)
