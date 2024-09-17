import math
import os
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

import pyotp
import robin_stocks.robinhood as r
from dotenv import load_dotenv
from loguru import logger

from exceptions import NoStrikePriceError


class OptionType(str, Enum):
    call = "call"
    put = "put"


def round_to_nearest_half_dollar(price: float | Decimal) -> Decimal:
    return Decimal(math.ceil(price * 2) / 2)


def log_in() -> dict | None:
    load_dotenv()
    totp = pyotp.TOTP(os.getenv("MFA_CODE")).now()
    r.login(os.getenv("EMAIL"), os.getenv("PASSWORD"), mfa_code=totp)


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


def get_closest_strike_price(ticker: str, option_type: OptionType) -> Decimal:
    # TODO: Performance can be improved by getting a list of all strike prices
    # for that ticker, sort that array and grab the closest one above the current price.
    # It'll be 1 API call + static array sorting and indexing vs a max of 5 API calls
    price = Decimal(r.stocks.get_latest_price(ticker)[0])
    nearest_half_dollar_increment = round_to_nearest_half_dollar(price)
    logger.info(
        f"Current Stock price: {price} \nFinding closest out-of-the-money strike price..."
    )
    
    if r.options.find_options_by_strike(
        ticker, nearest_half_dollar_increment, option_type, info="expiration_date"
    ):
        logger.info(f"Closest strike price: {nearest_half_dollar_increment}")
        return nearest_half_dollar_increment
    
    for i in range(4):
        nearest_half_dollar_increment = nearest_half_dollar_increment + Decimal(0.5)
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
        # Calculate the nearest Friday
        today = datetime.today()
        next_friday = (today + timedelta((4 - today.weekday()) % 7)).strftime(
            "%Y-%m-%d"
        )
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


def buy_option_limit_order(
    ticker: str,
    call_or_put: OptionType,
    strike_price: float | Decimal,
    exp_date: str,
    quantity: int,
    option_price: float | Decimal,
) -> dict | Any:
    return r.orders.order_buy_option_limit(
        positionEffect="open",
        creditOrDebit="debit",
        price=option_price,
        symbol=ticker,
        quantity=quantity,
        expirationDate=exp_date,
        strike=strike_price,
        optionType=call_or_put,
        timeInForce="gfd",  # Defaulting to 'good for the day'
    )
