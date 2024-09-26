import math
import os
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

import pyotp
import robin_stocks.robinhood as r
from dotenv import load_dotenv
from loguru import logger

from exceptions import NoStrikePriceError
from models import Bounds, Interval, OptionType, Span


def closest_friday() -> str:
    """Returns the nearest Friday as a string in YYYY-MM-DD format"""
    today = datetime.today()
    return (today + timedelta((4 - today.weekday()) % 7)).strftime("%Y-%m-%d")


# Function to fetch the nearest expiration date and most profitable strike
# ~14sec slower on avg than `get_closest_strike_price()`
def find_best_strikes(ticker, exp_date) -> tuple[dict, dict]:
    stock_price = Decimal(r.stocks.get_latest_price(ticker)[0])

    # Fetch call and put options for the nearest expiration date
    call_options = r.options.find_options_by_expiration(
        ticker, expirationDate=exp_date, optionType=OptionType.call
    )
    put_options = r.options.find_options_by_expiration(
        ticker, expirationDate=exp_date, optionType=OptionType.put
    )

    # Find the strike prices closest to the current stock price
    best_call_option = min(
        call_options, key=lambda x: abs(Decimal(x["strike_price"]) - stock_price)
    )
    best_put_option = min(
        put_options, key=lambda x: abs(Decimal(x["strike_price"]) - stock_price)
    )

    return best_call_option, best_put_option


def ensure_orders_are_filled(func):
    def wrapper(*args, **kwargs):
        all_filled = None
        filled_orders = 0
        while not all_filled:
            time.sleep(2)
            orders = func(*args, **kwargs)
            for order in orders:
                if is_option_position_bought(order["id"]):
                    filled_orders += 1
            if filled_orders == len(orders):
                all_filled = True
                logger.info("Success - Orders filled")
            logger.info("Failure - Orders not filled. Trying again...")
        return orders

    return wrapper


def round_to_nearest_half_dollar(
    price: float | Decimal, option_type: OptionType
) -> Decimal:
    if option_type == OptionType.call:
        return Decimal(math.ceil(price * 2) / 2)
    if option_type == OptionType.put:
        return Decimal(math.floor(price * 2) / 2)


def calculate_mean(list) -> Decimal:
    return Decimal(sum(list) / len(list))


def calculate_std_dev(list, mean: Decimal) -> Decimal:
    variance = sum((x - mean) ** 2 for x in list) / len(list)
    return Decimal(math.sqrt(variance))


def log_in() -> dict | None:
    load_dotenv()
    totp = pyotp.TOTP(os.getenv("MFA_CODE")).now()
    return r.login(os.getenv("EMAIL"), os.getenv("PASSWORD"), mfa_code=totp)


def current_stock_price(ticker: str | list[str]) -> dict | list[dict]:
    price_list = r.stocks.get_latest_price(ticker)
    if len(price_list) == 1:
        return Decimal(price_list[0])
    return [Decimal(price) for price in price_list]


def get_stock_basic_info(ticker: str | list[str]) -> dict | list[dict]:
    """
    - A dict is returned per ticker symbol provided
    - A single ticker symbol i.e. "aapl" returns a dict of basic info
    - A list of ticket symbols i.e ["aapl", "tsla"] returns a list[dict] of basic info
    """
    res = r.stocks.get_fundamentals(ticker)
    curated_info = [
        {
            "open": r["open"],
            "high": r["high"],
            "low": r["low"],
            "high_52_weeks": r["high_52_weeks"],
            "low_52_weeks": r["low_52_weeks"],
        }
        for r in res
    ]
    if len(curated_info) == 1:
        return curated_info[0]
    return curated_info


def at_stop_loss(
    position: dict, current_price: Decimal, stop_loss_percentage: Decimal
) -> bool:
    entry_price = position["entry_price"]  # Get this somehow
    loss = (entry_price - current_price) / entry_price
    logger.info(f"Current loss: {loss}")
    return loss >= stop_loss_percentage


# Note: Extended and Trading hours FORCE you to use a 'day' time window - whatever
# Note: Default args for the daily pre-market prep - shift args for subsequent calls as needed
def get_stock_historical_price_deltas(
    ticker: str | list[str],
    candle_interval: Optional[Interval] = Interval.ten_min,
    time_window: Optional[Span] = Span.day,
    trading_hours: Optional[Bounds] = Bounds.extended,
) -> list[dict]:
    curated_data = []
    raw_data = r.stocks.get_stock_historicals(
        ticker, candle_interval, time_window, trading_hours
    )
    for entry in raw_data:
        curated_data.append(
            {
                # Time is UTC so market hours are 14:30 to 21:00
                "datetime": entry["begins_at"],
                "open_to_close_price_delta": (
                    str(Decimal(entry["close_price"]) - Decimal(entry["open_price"]))
                ),
            }
        )
    return curated_data


def get_closest_strike_price(ticker: str, option_type: OptionType) -> Decimal:
    # TODO: Performance can be improved by getting a list of all strike prices
    # for that ticker, sort that array and grab the closest one above the current price.
    # It'll be 1 API call + static array sorting and indexing vs a max of 5 API calls
    price = Decimal(r.stocks.get_latest_price(ticker)[0])
    nearest_half_dollar_increment = round_to_nearest_half_dollar(price, option_type)
    logger.info(
        f"Current Stock price: {price} \nFinding closest out-of-the-money strike price..."
    )

    if r.options.find_options_by_strike(
        ticker, nearest_half_dollar_increment, option_type, info="expiration_date"
    ):
        logger.info(f"Closest strike price: {nearest_half_dollar_increment}")
        return nearest_half_dollar_increment

    for i in range(4):
        if option_type == OptionType.call:
            nearest_half_dollar_increment = nearest_half_dollar_increment + Decimal(0.5)
        if option_type == OptionType.put:
            nearest_half_dollar_increment = nearest_half_dollar_increment - Decimal(0.5)

        if r.options.find_options_by_strike(
            ticker, nearest_half_dollar_increment, option_type, info="expiration_date"
        ):
            logger.info(f"Closest strike price: {nearest_half_dollar_increment}")
            return nearest_half_dollar_increment
    raise NoStrikePriceError(
        f"No strike price found for {ticker} within 2.5 dollars of the current stock price"
    )


def get_nearest_out_of_the_money_option_contract_details(
    ticker: str, call_or_put: OptionType, exp_date: Optional[str] = None
) -> dict | None:
    """
    - This will find find the closest out-of-the-money option contract for the ticker and option type requested.
    - The expiration date, unless specified, will default to the closest Friday
    - The strike price is set by looking .5 to 1 dollar above the current stock price
    Arguments:
        ticker: The stock ticker
        call_or_put: The option type -> 'call' or 'put'
        exp_date (optional): Option exp date in YYYY-MM-DD format
            - Default -> Nearest Friday
    """
    if not exp_date:
        next_friday = closest_friday()
    if details := r.options.find_options_by_expiration_and_strike(
        inputSymbols=ticker,
        optionType=call_or_put,
        expirationDate=exp_date if exp_date else next_friday,
        strikePrice=get_closest_strike_price(ticker, call_or_put),
    ):
        details = details[0]
    if details["state"] == "active" and details["tradability"] == "tradable":
        return {
            "symbol": details["chain_symbol"],
            "expiration_date": details["expiration_date"],
            "strike_price": details["strike_price"],
            "last_trade_price": details["last_trade_price"],
            "fair_midpoint_price": details["mark_price"],
            "buying_details": {
                "high_fill_rate_price": details["high_fill_rate_buy_price"],
                "low_fill_rate_price": details["low_fill_rate_buy_price"],
            },
            "selling_details": {
                "high_fill_rate_price": details["high_fill_rate_sell_price"],
                "low_fill_rate_price": details["low_fill_rate_sell_price"],
            },
            "ask_price": details["ask_price"],
            "ask_size": details["ask_size"],
            "bid_price": details["bid_price"],
            "bid_size": details["bid_size"],
            "greeks": {
                "delta": details["delta"],
                "gamma": details["gamma"],
                "rho": details["rho"],
                "theta": details["theta"],
                "vega": details["vega"],
            },
        }
    logger.warning(
        "Requested stock has no active or tradable options contract. Try a different stock, option type, etc"
    )


def is_option_position_bought(option_id) -> bool:
    open_positions = r.options.get_open_option_positions()
    for position in open_positions:
        if option_id == position["id"]:
            return True  # position is open/bought
    return False  # order is not open/not bought


@ensure_orders_are_filled
def monitor_trade(
    call_option, put_option, take_profit: Decimal = 0.05, stop_loss: Decimal = 0.02
) -> None:
    initial_call_price = Decimal(call_option["fair_midpoint_price"])
    initial_put_price = Decimal(put_option["fair_midpoint_price"])

    initial_total_value = initial_call_price + initial_put_price

    # Refresh option data
    refreshed_call = r.options.get_option_market_data_by_id(call_option["id"])[0]
    refreshed_put = r.options.get_option_market_data_by_id(put_option["id"])[0]
    ideal_call_price = (
        Decimal(refreshed_call["adjusted_mark_price"])
        + Decimal(refreshed_call["ask_price"])
    ) / 2
    ideal_put_price = (
        Decimal(refreshed_put["adjusted_mark_price"])
        + Decimal(refreshed_put["ask_price"])
    ) / 2

    current_total_value = ideal_call_price + ideal_put_price
    profit_pct = (current_total_value - initial_total_value) / initial_total_value

    logger.info(f"Current Profit: {profit_pct*100:.2f}%")

    if profit_pct >= take_profit:
        logger.info("Take-profit triggered, closing positions.")
        sold_call = sell_option_limit_order(
            call_option["chain_symbol"],
            OptionType.call,
            call_option["strike_price"],
            call_option["expiration_date"],
            1,
            ideal_call_price,
        )
        sold_put = sell_option_limit_order(
            put_option["chain_symbol"],
            OptionType.put,
            put_option["strike_price"],
            put_option["expiration_date"],
            1,
            ideal_put_price,
        )
        return [sold_call, sold_put]
    elif profit_pct <= -stop_loss:
        logger.info("Stop-loss triggered, closing positions.")
        sold_call = sell_option_limit_order(
            call_option["chain_symbol"],
            OptionType.call,
            call_option["strike_price"],
            call_option["expiration_date"],
            1,
            ideal_call_price,
        )
        sold_put = sell_option_limit_order(
            put_option["chain_symbol"],
            OptionType.put,
            put_option["strike_price"],
            put_option["expiration_date"],
            1,
            ideal_put_price,
        )
        return [sold_call, sold_put]


def buy_option_limit_order(
    ticker: str,
    call_or_put: OptionType,
    strike_price: float | Decimal,
    exp_date: str,
    quantity: int,
    option_price: float | Decimal,
    time_in_force: str = "ioc",
) -> dict | Any:
    raise Exception("Don't want to buy options right now")
    return r.orders.order_buy_option_limit(
        positionEffect="open",
        creditOrDebit="debit",
        price=option_price,
        symbol=ticker,
        quantity=quantity,
        expirationDate=exp_date,
        strike=strike_price,
        optionType=call_or_put,
        timeInForce=time_in_force,  # Defaulting to 'immediate or cancel'
    )


def sell_option_limit_order(
    ticker: str,
    call_or_put: OptionType,
    strike_price: float | Decimal,
    exp_date: str,
    quantity: int,
    option_price: float | Decimal,
    time_in_force: str = "ioc",
) -> dict | Any:
    raise Exception("Don't want to sell options right now")
    # TODO: We need to monitor if we've actually sold the contracts. Putting them up for sale doesn't mean they've been sold.
    return r.orders.order_sell_option_limit(
        positionEffect="close",
        creditOrDebit="credit",
        price=option_price,
        symbol=ticker,
        quantity=quantity,
        expirationDate=exp_date,
        strike=strike_price,
        optionType=call_or_put,
        timeInForce=time_in_force,  # Defaulting to 'immediate or cancel'
    )
