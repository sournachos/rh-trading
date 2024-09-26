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
    ensure_orders_are_filled,
    get_nearest_out_of_the_money_option_contract_details,
    get_stock_historical_price_deltas,
    is_option_position_bought,
    log_in,
    monitor_trade,
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


@ensure_orders_are_filled
def buy_call(ticker, call_details, positions=1):
    call_option = buy_option_limit_order(
        ticker,
        "call",
        call_details["strike_price"],
        call_details["expiration_date"],
        positions,
        call_details["fair_midpoint_price"],
    )
    return [call_option]


@ensure_orders_are_filled
def buy_put(ticker, put_details, positions=1):
    put_option = buy_option_limit_order(
        ticker,
        "put",
        put_details["strike_price"],
        put_details["expiration_date"],
        positions,
        put_details["fair_midpoint_price"],
    )
    return [put_option]


def history_repeats_itself(
    ticker,
    take_profit=0.1,
    stop_loss=0.05,
    chunk_interval_in_min: int = 15,
    positions: int = 1,
):
    price_changes = identify_price_changes(ticker, chunk_interval_in_min)
    mean = calculate_mean(price_changes[-3:])
    std_dev = calculate_std_dev(price_changes[-3:], mean)
    ma_of_chunk = price_changes[-1]
    logger.info(f"{chunk_interval_in_min*3}min Mean: {mean}")
    logger.info(f"{chunk_interval_in_min*3}min Standard Deviation: {std_dev}")
    logger.info(f"{chunk_interval_in_min}min Moving Average: {ma_of_chunk}")

    # throwing numbers on these IFs - testing pending for legit logical parameters
    if mean > 0.15 and ma_of_chunk >= 0.15 and std_dev < 0.10:
        call_details = get_nearest_out_of_the_money_option_contract_details(
            ticker, "call"
        )
        # TODO: figure out what to do with 'filled_call'
        # maybe after 3 tries we bump up the price?
        # a lil more thinking needed
        filled_call = buy_call(ticker, call_details, positions)
        logger.info(
            f"Buy order filled - 1 CALL contract - {ticker} - {call_details["fair_midpoint_price"]}"
        )
    if mean < -0.15 and ma_of_chunk <= -0.15 and std_dev < 0.10:
        put_details = get_nearest_out_of_the_money_option_contract_details(
            ticker, "put"
        )
        # TODO: figure out what to do with 'filled_put'
        # maybe after 3 tries we bump up the price?
        # a lil more thinking needed
        filled_put = buy_put(ticker, put_details, positions)
        logger.info(
            f"Buy order filled - 1 PUT contract - {ticker} - {put_details["fair_midpoint_price"]}"
        )
    monitor_trade(
        option=call_details or put_details,
        take_profit=Decimal(take_profit),
        stop_loss=Decimal(stop_loss),
    )


# Use 5, 10, 15, 30, 60min intervals
history_repeats_itself("aapl", chunk_interval_in_min=10, positions=1)
