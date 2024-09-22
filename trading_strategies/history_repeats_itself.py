from decimal import Decimal
import sys
sys.path.append("../")
from models import Interval
from utils import get_stock_historical_price_deltas, log_in

log_in()

# Just testing shit
# print(get_stock_historical_price_deltas("aapl"))
# apple_call_strike_price = get_closest_strike_price('aapl', 'call')
# apple_put_strike_price = get_closest_strike_price('aapl', 'put')

# print(f"\n\nThe current stock price {current_stock_price('aapl')}")
# print(f"The closest call strike price {apple_call_strike_price}")
# print(f"The closest put strike price {apple_put_strike_price}")
#
# ----------------------------------------------------------------------------
#
# Alright so I think for a first strat something like comparing the rate of
# price change in the past 60, 30, 15, 10, 5 and 1min to get a general idea
# of direction to buy and sell an option contract as soon as there is profit.

# Potential Basic Flow:
# - Find general direction (Grab historical data on ticker)
# - Buy the closest out-of-the-money contract (Improve performance of that logic)
# - Sell as soon as there is a .05 profit per contract (aka $5)
#   - Once bought, check prices every 5sec to sell (Not sure if Robinhood will throttle)
#   - We'll need to think about stop losses, settling for profits under .05 after x time
#     to reduce risk and prioritize profit, etc.

def identify_general_trend(ticker, chunk_interval_in_min:int) -> list[list]:
    '''Given a ticker and interval, it returns a list[list]
        where the child lists contain the stock price movement
        for the specified interval.
        A positive number is an uptrend
        A negative number is a downtrend
    '''
    chunked_deltas = []
    deltas_ten_min_interval = get_stock_historical_price_deltas(ticker, Interval.five_min)
    for delta in range(0, len(deltas_ten_min_interval), int(chunk_interval_in_min/5)):
        chunked_deltas.append([str(sum([Decimal(delta["open_to_close_price_delta"]) for delta in deltas_ten_min_interval[delta:delta+int(chunk_interval_in_min/5)]]))])
    return chunked_deltas

def history_repeats_itself(ticker, chunk_interval_in_min:int = 15):
    # Use 5, 10, 15, 30, 60min intervals
    chunked_deltas = identify_general_trend(ticker, chunk_interval_in_min)
    print(chunked_deltas)
    

history_repeats_itself('aapl')
