from datetime import datetime, timedelta
import math
from typing import Optional
import pyotp
import robin_stocks.robinhood as r

def round_to_nearest_half_dollar(price: float):
    return math.ceil(price * 2) / 2

def log_in():
    totp  = pyotp.TOTP("urMFACode").now()
    login = r.login(
        'email@email.com',
        'password',
        mfa_code=totp
        )
    
def get_stock_basic_info(ticker):
    '''
    - A dict is returned per ticker symbol provided
    - A single ticker symbol i.e. "aapl" returns a dict of basic info
    - A list of ticket symbols i.e ["aapl", "tsla"] returns a list[dict] of basic info
    '''
    try:
        res = r.stocks.get_fundamentals(ticker)
    except Exception as e:
        print(f"Something went wrong retrieving basic info for {ticker}: {e}")
    if type(ticker) is str:
        return {
            "open" : res[0]["open"], 
            "high" : res[0]["high"],
            "low" : res[0]["low"],
            "high_52_weeks" : res[0]["high_52_weeks"],
            "low_52_weeks" : res[0]["low_52_weeks"],
            }
    if type(ticker) is list:
        curated_info = []
        for info in res:
            curated_info.append(
            {
                "ticker": info["symbol"],
                "open" : info["open"], 
                "high" : info["high"],
                "low" : info["low"],
                "high_52_weeks" : info["high_52_weeks"],
                "low_52_weeks" : info["low_52_weeks"],
            }
            )
        return curated_info
    
def get_closest_strike_price(ticker, call_or_put):
    price = float(r.stocks.get_latest_price(ticker)[0])
    half_dollar_increment =  round_to_nearest_half_dollar(price)
    print(f"Current Stock price: {price} \nFinding closest out-of-the-money strike price...")
    if r.options.find_options_by_strike(ticker, half_dollar_increment, call_or_put, info='expiration_date'):
        print(f"Closest strike price: {half_dollar_increment}")
        return half_dollar_increment
    if r.options.find_options_by_strike(ticker, (half_dollar_increment + .5), call_or_put, info='expiration_date'):
        print(f"Closest strike price: {half_dollar_increment + .5}")
        return half_dollar_increment + .5
      
def get_nearest_out_of_the_money_option_contract_details(ticker, call_or_put, exp_date: Optional[str] = None):
    '''
    - This will find find the closest out-of-the-money option contract for the ticker and option type requested.
    - The expiration date, unless specified, will default to the closest Friday
    - The strike price is set by looking .5 to 1 dollar above the current stock price
    Arguments:
        ticker: The stock ticker
        call_or_put: The option type -> 'call' or 'put'
        exp_date (optional): Option exp date in YYYY-MM-DD format
            - Default -> Nearest Friday
    '''
    try:
        if not exp_date:
            today = datetime.today()
            next_friday = (today + timedelta((4-today.weekday()) % 7)).strftime('%Y-%m-%d')
        details = r.options.find_options_by_expiration_and_strike(
            inputSymbols=ticker,
            optionType=call_or_put,
            expirationDate=exp_date if exp_date else next_friday,
            strikePrice=get_closest_strike_price(ticker, call_or_put)
            )[0]
        if details["state"] == 'active' and details["tradability"] == 'tradable':
            return {
                "symbol": details["chain_symbol"],
                "expiration_date": details["expiration_date"],
                "strike_price": details["strike_price"],
                "last_trade_price": details["last_trade_price"],
                "fair_midpoint_price": details["mark_price"],
                "buying_details": {
                    "high_fill_rate_price": details["high_fill_rate_buy_price"],
                    "low_fill_rate_price": details["low_fill_rate_buy_price"]
                },
                "selling_details": {
                    "high_fill_rate_price": details["high_fill_rate_sell_price"],
                    "low_fill_rate_price": details["low_fill_rate_sell_price"]
                },
                "ask_price": details["ask_price"],
                "ask_size": details["ask_size"],
                "bid_price": details["bid_price"],
                "bid_size": details["bid_size"],
                "greeks": {
                    "delta":details["delta"], 
                    "gamma": details["gamma"], 
                    "rho": details["rho"], 
                    "theta": details["theta"], 
                    "vega": details["vega"]
                    }
            }
        print('Requested stock has no active or tradable options contract. Try a different stock, option type, etc')
    except Exception as e:
        print(f"Something went wrong retrieving option contract details for {ticker}: {e}")
        
def buy_option_limit_order(ticker, call_or_put, strike_price, exp_date, quantity, option_price):
    try:
        return r.orders.order_buy_option_limit(
            positionEffect ='open',
            creditOrDebit  = 'debit',
            price = option_price,
            symbol = ticker,
            quantity = quantity,
            expirationDate = exp_date,
            strike = strike_price,
            optionType = call_or_put,
            timeInForce = 'gfd' # Defaulting to 'good for the day'
        )
    except Exception as e:
        print(f"Something went wrong placing {call_or_put} order for {ticker}: {e}")
