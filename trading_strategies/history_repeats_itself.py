from decimal import Decimal
import sys

from loguru import logger
sys.path.append("../")
from models import Interval
from utils import get_stock_historical_price_deltas, log_in, calculate_mean, calculate_std_dev

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

def identify_price_changes(ticker, chunk_interval_in_min:int) -> list[list]:
    '''Given a ticker and interval, it returns a list[list]
        where the child lists contain the stock price movement
        for the specified interval.
        A positive number is an uptrend
        A negative number is a downtrend
    '''
    chunked_deltas = []
    deltas_ten_min_interval = get_stock_historical_price_deltas(ticker, Interval.five_min)
    for delta in range(0, len(deltas_ten_min_interval), int(chunk_interval_in_min/5)):
        chunked_deltas.append(
                sum(
                    [
                        Decimal(delta["open_to_close_price_delta"]) 
                        for delta in deltas_ten_min_interval[delta:delta+int(chunk_interval_in_min/5)]
                    ]
                )
            )
    return chunked_deltas

def history_repeats_itself(ticker, chunk_interval_in_min:int = 15):
    price_changes = identify_price_changes(ticker, chunk_interval_in_min)
    mean = calculate_mean(price_changes[-3:])
    std_dev = calculate_std_dev(price_changes[-3:], mean)
    ma_of_chunk = price_changes[-1]
    logger.info(f"{chunk_interval_in_min*3}min Mean: {mean}")
    logger.info(f"{chunk_interval_in_min*3}min Standard Deviation: {std_dev}")
    logger.info(f"{chunk_interval_in_min}min Moving Average: {ma_of_chunk}")
    
    # throwing numbers on these IFs - testing pending for legit logical parameters
    if mean > 0.15 and ma_of_chunk >= 0.15 and std_dev < 0.10:
        logger.info('Simulated buy CALL')
    if mean < -0.15 and ma_of_chunk <= -0.15 and std_dev < 0.10:
        logger.info('Simulated buy PUT')
        
    # Add option monitoring for take-profit and stop-loss below
    
    
# Use 5, 10, 15, 30, 60min intervals
history_repeats_itself('aapl', 5)
