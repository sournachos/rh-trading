# Takes ~20sec to spin up (3 API calls - could be improved?)
# When and if conditions to buy are good, it buys a CALL and PUT (2 API calls)
# Monitoring to sell is every 10sec (2 API calls)
# When selling, take-profit or stop-loss, it sell the CALL and PUT (2 API calls)

import time
from decimal import Decimal

import robin_stocks.robinhood as r
from loguru import logger

from models import OptionType
from utils import (
    buy_option_limit_order,
    closest_friday,
    find_best_strikes,
    log_in,
    monitor_trade_and_sell,
    sell_option_limit_order,
)


# Function to buy a strangle (one call, one put)
def buy_strangle(ticker, call_option, put_option) -> tuple[dict, dict]:
    # Place a market order for the call and put options
    bought_call = buy_option_limit_order(
        ticker,
        OptionType.call,
        call_option["strike_price"],
        call_option["expiration_date"],
        1,
        call_option["adjusted_mark_price_round_down"],
    )
    bought_put = buy_option_limit_order(
        ticker,
        OptionType.put,
        put_option["strike_price"],
        put_option["expiration_date"],
        1,
        put_option["adjusted_mark_price_round_down"],
    )
    return bought_call, bought_put


# Function to calculate prob_win using Greeks
def calculate_prob_win(call_option, put_option) -> Decimal:
    # Use delta to calculate prob of winning
    delta_call = Decimal(call_option.get("delta", 0))
    delta_put = Decimal(put_option.get("delta", 0))

    # Estimate probability
    # For calls: prob of stock > strike is roughly delta_call
    # For puts: prob of stock < strike is roughly 1 - delta_put
    prob_call = delta_call
    prob_put = 1 - delta_put

    prob_win = prob_call + prob_put
    return prob_win


# Main trading loop
def trade_strangle_without_kelly(ticker) -> None:
    # Get best option strike prices for the nearest Friday
    exp_date = closest_friday()
    call_option, put_option = find_best_strikes(ticker, exp_date)

    # Fetch implied volatility
    call_iv = Decimal(call_option["implied_volatility"])
    put_iv = Decimal(put_option["implied_volatility"])
    avg_iv = (call_iv + put_iv) / 2
    logger.info(f"Implied Volatility: {avg_iv}")

    high_vol_threshold = 0.5  # Adjust this threshold as needed

    if avg_iv > high_vol_threshold:
        logger.info(
            f"High volatility detected: {avg_iv}. Finding best strangle opportunity..."
        )

        # Calculate prob_win using Greeks
        prob_win = calculate_prob_win(call_option, put_option)
        logger.info(f"Calculated Probability of Winning: {prob_win:.2f}")

        if prob_win > 1.00:
            # Buy the strangle with same-week expiration
            # bought_call, bought_put = buy_strangle(ticker, call_option, put_option)
            logger.info("Simulated buy and started monitoring")
            calls_sold = monitor_trade_and_sell(call_option)
            puts_sold = monitor_trade_and_sell(put_option)
            # Monitor the trade for take-profit and stop-loss
            # calls_bought = monitor_trade_and_sell(bought_call)
            # puts_bought = monitor_trade_and_sell(bought_put)
        else:
            logger.info("LOW probability of winning. Skipping trade.")
    else:
        logger.info(
            f"Volatility {avg_iv} is below the threshold of {high_vol_threshold}. Skipping trade."
        )


if __name__ == "__main__":
    log_in()
    # Execute the strategy
    trade_strangle_without_kelly("AAPL")
