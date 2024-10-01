# importing historical candle data for any stock marker ticker
# candle data needs to be 1m candles for jesse's visualization
import json
import uuid

import requests
from jesse.modes.import_candles_mode import (
    store_candles_list as store_candles_from_list,
)
from jesse.services.db import database
from loguru import logger


def import_candles(
    ticker: str = "AAPL", start_date: str = "2024-01-02", end_date: str = "2024-01-03"
):
    """
    Given a ticker and a date range, it will store historical candle data
    in the local docker db instance for backtesting strategies on.

    ex.
      - ticker = "AAPL"
      - start_date = "2024-01-02"
      - end_date = "2024-01-03"
    """
    # extended_hours = "true"  # If sent as a URL parameter, returns data from 4am ET to 8pm ET

    url = f"https://api.marketdata.app/v1/stocks/candles/1/{ticker}?from={start_date}&to={end_date}"

    candles = json.loads(requests.request("GET", url).text)

    arr = [
        {
            "id": str(uuid.uuid4()),
            "exchange": "NYSE",
            "symbol": ticker,
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

    # database.open_connection()
    # store_candles_from_list(arr)
    # database.close_connection()
    # logger.info(f"Succesfully added candle data for {ticker}")
