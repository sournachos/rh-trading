from utils import get_stock_historical_price_deltas, log_in

log_in()

# Just testing shit
print(get_stock_historical_price_deltas("aapl"))
# apple_call_strike_price = get_closest_strike_price('aapl', 'call')
# apple_put_strike_price = get_closest_strike_price('aapl', 'put')

# print(f"\n\nThe current stock price {current_stock_price('aapl')}")
# print(f"The closest call strike price {apple_call_strike_price}")
# print(f"The closest put strike price {apple_put_strike_price}")
#
#
#
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
