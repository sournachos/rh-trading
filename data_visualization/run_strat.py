import jesse.helpers as jh
from jesse.modes.backtest_mode import _step_simulator
from jesse.research.backtest import _isolated_backtest
from jesse.services.candle import _get_candles_from_db
from strategies.SimpleDonchian import SimpleDonchian

# ticker and dates u wanna backtest
ticker = "AAPL"
start_date = 1704205800000  # "2024-01-02"
end_date = 1728071940000  # "2024-10-04"

db_candles = _get_candles_from_db("NYSE", f"NYSE-{ticker}", start_date, end_date)
config = {
    "starting_balance": 10_000,
    "fee": 0,
    "type": "futures",
    "futures_leverage": 2,
    "futures_leverage_mode": "cross",
    "exchange": "NYSE",
    "warm_up_candles": 0,
}
routes = [
    {
        "exchange": "NYSE",
        "strategy": SimpleDonchian,
        "symbol": f"NYSE-{ticker}",
        "timeframe": "1m",
    },
]
data_routes = []
candles = {
    jh.key("NYSE", f"NYSE-{ticker}"): {
        "exchange": "NYSE",
        "symbol": f"NYSE-{ticker}",
        "candles": db_candles,
    },
}

_isolated_backtest(config, routes, data_routes, candles)

_step_simulator
