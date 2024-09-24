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
# import sys
import time

# sys.path.append("../")
from decimal import Decimal

from loguru import logger

from models import Interval
from utils import (
    buy_option_limit_order,
    calculate_mean,
    calculate_std_dev,
    get_nearest_out_of_the_money_option_contract_details,
    get_stock_historical_price_deltas,
    is_option_position_bought,
    log_in,
)

log_in()


def identify_price_changes(ticker, chunk_interval_in_min: int) -> list[list]:
    """Given a ticker and interval, it returns a list[list]
    where the child lists contain the stock price movement
    for the specified interval.
     - A positive number is an uptrend
     - A negative number is a downtrend
    """
    chunked_deltas = []
    deltas_ten_min_interval = get_stock_historical_price_deltas(
        ticker, Interval.five_min
    )
    for delta in range(0, len(deltas_ten_min_interval), int(chunk_interval_in_min / 5)):
        chunked_deltas.append(
            sum(
                [
                    Decimal(delta["open_to_close_price_delta"])
                    for delta in deltas_ten_min_interval[
                        delta : delta + int(chunk_interval_in_min / 5)
                    ]
                ]
            )
        )
    return chunked_deltas


def history_repeats_itself(ticker, chunk_interval_in_min: int = 15):
    price_changes = identify_price_changes(ticker, chunk_interval_in_min)
    mean = calculate_mean(price_changes[-3:])
    std_dev = calculate_std_dev(price_changes[-3:], mean)
    ma_of_chunk = price_changes[-1]
    logger.info(f"{chunk_interval_in_min*3}min Mean: {mean}")
    logger.info(f"{chunk_interval_in_min*3}min Standard Deviation: {std_dev}")
    logger.info(f"{chunk_interval_in_min}min Moving Average: {ma_of_chunk}")

    # throwing numbers on these IFs - testing pending for legit logical parameters
    if mean > 0.15 and ma_of_chunk >= 0.15 and std_dev < 0.10:
        bought = False
        while not bought:
            call_details = get_nearest_out_of_the_money_option_contract_details(
                ticker, "call"
            )
            call_option = buy_option_limit_order(
                ticker,
                "call",
                call_details["strike_price"],
                call_details["expiration_date"],
                1,
                call_details["fair_midpoint_price"],
            )
            time.sleep(2)
            # Any option order is set to immediately fill or be cancelled
            bought = is_option_position_bought(call_option["id"])
        logger.info(
            f"Buy order filled - 1 CALL contract - {ticker} for {call_details['fair_midpoint_price']}"
        )
    if mean < -0.15 and ma_of_chunk <= -0.15 and std_dev < 0.10:
        bought = False
        while not bought:
            put_details = get_nearest_out_of_the_money_option_contract_details(
                ticker, "put"
            )
            put_option = buy_option_limit_order(
                ticker,
                "put",
                put_details["strike_price"],
                put_details["expiration_date"],
                1,
                put_details["fair_midpoint_price"],
            )
            # Any option order is set to immediately fill or be cancelled
            time.sleep(2)
            bought = is_option_position_bought(put_option["id"])
        logger.info(
            f"Buy order filled - 1 PUT contract - {ticker} for {call_details['fair_midpoint_price']}"
        )

    # Add option monitoring for take-profit and stop-loss below
    # the calls below are to confirm both sold and bough option contracts
    # is_option_position_bought(call_option)
    # is_option_position_bought(put_option)


# Use 5, 10, 15, 30, 60min intervals
history_repeats_itself("aapl", 5)
