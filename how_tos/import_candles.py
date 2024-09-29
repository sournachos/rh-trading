# importing historical candle data for any stock marker ticker
# candle data needs to be 1m candles for jesse's visualization
import json

import jesse.helpers as jh
import requests
from jesse.modes.import_candles_mode import (
    store_candles_list as store_candles_from_list,
)

ticker = "AAPL"  # Ticker u want data for
start_date = "2024-01-02"  # Data is returned starting at 9:30am ET
end_date = "2024-01-03"  # Data is returned ending at 3:59pm ET
# extended_hours = "true"  # If sent as a URL parameter, returns data from 4am ET to 8pm ET

url = f"https://api.marketdata.app/v1/stocks/candles/1/{ticker}?from={start_date}&to={end_date}"

candles = json.loads(requests.request("GET", url).text)

arr = [
    {
        "id": jh.generate_unique_id(),
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

# store_candles_from_list(arr)
