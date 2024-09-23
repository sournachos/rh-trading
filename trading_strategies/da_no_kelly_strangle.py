# Takes ~20sec to spin up (3 API calls - could be improved?)
# When and if conditions to buy are good, it buys a CALL and PUT (2 API calls)
# Monitoring to sell is every 10sec (2 API calls)
# When selling, take-profit or stop-loss, it sell the CALL and PUT (2 API calls)

# import sys
# sys.path.append("../")
from loguru import logger
from utils import closest_friday, log_in
import robin_stocks.robinhood as r
from decimal import Decimal
import time
from models import OptionType



# Function to fetch the nearest expiration date and most profitable strike
def find_best_strikes(ticker, exp_date)-> tuple[dict, dict]:
    stock_price = Decimal(r.stocks.get_latest_price(ticker)[0])
    
    # Fetch call and put options for the nearest expiration date
    call_options = r.options.find_options_by_expiration(ticker, expirationDate=exp_date, optionType=OptionType.call)
    put_options = r.options.find_options_by_expiration(ticker, expirationDate=exp_date, optionType=OptionType.put)

    # Find the strike prices closest to the current stock price
    best_call_option = min(call_options, key=lambda x: abs(Decimal(x['strike_price']) - stock_price))
    best_put_option = min(put_options, key=lambda x: abs(Decimal(x['strike_price']) - stock_price))
    
    return best_call_option, best_put_option

# Function to buy a strangle (one call, one put)
def buy_strangle(ticker, call_option, put_option) -> tuple[dict, dict]:
    # Place a market order for the call and put options
    # TODO: This should use the utils function to place a limit order
    bought_call = r.options.order_buy_option_limit('open', 'debit', call_option['adjusted_mark_price_round_down'], ticker, 1, call_option['expiration_date'], call_option['strike_price'], OptionType.call)
    bought_put = r.options.order_buy_option_limit('open', 'debit', put_option['adjusted_mark_price_round_down'], ticker, 1, put_option['expiration_date'], put_option['strike_price'], OptionType.put))
    return bought_call, bought_put
    
# Monitor the trade for take-profit or stop-loss
def monitor_trade(call_option, put_option, take_profit=0.05, stop_loss=0.02) -> None:
    initial_call_price = Decimal(call_option['adjusted_mark_price_round_down'])
    initial_put_price = Decimal(put_option['adjusted_mark_price_round_down'])
    
    initial_total_value = initial_call_price + initial_put_price
    
    while True:
        # Refresh option data
        refreshed_call = r.options.get_option_market_data_by_id(call_option['id'])[0]
        refreshed_put = r.options.get_option_market_data_by_id(put_option['id'])[0]
        ideal_call_price = (Decimal(refreshed_call['adjusted_mark_price']) + Decimal(refreshed_call['ask_price'])) / 2
        ideal_put_price = (Decimal(refreshed_put['adjusted_mark_price']) + Decimal(refreshed_put['ask_price'])) / 2
        
        current_total_value = ideal_call_price + ideal_put_price
        profit_pct = (current_total_value - initial_total_value) / initial_total_value

        logger.info(f"Current Profit: {profit_pct*100:.2f}%")

        if profit_pct >= take_profit:
            logger.info("Take-profit triggered, closing positions.")
            # TODO: All these sell orders should use a utils function, AND most importantly, we need to monitor if we've actually sold the contracts. Putting them up for sale doesn't mean they've been sold.
            r.options.order_sell_option_limit(
                symbol=call_option['chain_symbol'],
                option_type=OptionType.call,
                strike_price=call_option['strike_price'],
                expirationDate=call_option['expiration_date'],
                price=ideal_call_price,
                quantity=1,
                time_in_force='gtc'
            )
            r.options.order_sell_option_limit(
                symbol=put_option['chain_symbol'],
                option_type=OptionType.put),
                strike_price=put_option['strike_price'],
                expirationDate=put_option['expiration_date'],
                price=ideal_put_price,
                quantity=1,
                time_in_force='gtc'
            )
            break
        elif profit_pct <= -stop_loss:
            logger.info("Stop-loss triggered, closing positions.")
            r.options.order_sell_option_limit(
                symbol=call_option['chain_symbol'],
                option_type=OptionType.call,
                strike_price=call_option['strike_price'],
                expirationDate=call_option['expiration_date'],
                price=call_option['adjusted_mark_price'],
                quantity=1,
                time_in_force='gtc'
            )
            r.options.order_sell_option_limit(
                symbol=put_option['chain_symbol'],
                option_type=OptionType.put),
                strike_price=put_option['strike_price'],
                expirationDate=put_option['expiration_date'],
                price=put_option['adjusted_mark_price'],
                quantity=1,
                time_in_force='gtc'
            )
            break

        # Sleep for a bit before checking again
        time.sleep(10)

# Function to calculate prob_win using Greeks
def calculate_prob_win(call_option, put_option) -> Decimal:
    # Use delta to calculate prob of winning
    delta_call = Decimal(call_option.get('delta', 0))
    delta_put = Decimal(put_option.get('delta', 0))

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
    call_iv = Decimal(call_option['implied_volatility'])
    put_iv = Decimal(put_option['implied_volatility'])
    avg_iv = (call_iv + put_iv) / 2
    logger.info(f"Implied Volatility: {avg_iv}")
    
    high_vol_threshold = 0.5  # Adjust this threshold as needed
    
    if avg_iv > high_vol_threshold:
        logger.info(f"High volatility detected: {avg_iv}. Finding best strangle opportunity...")
        
        # Calculate prob_win using Greeks
        prob_win = calculate_prob_win(call_option, put_option)
        logger.info(f"Calculated Probability of Winning: {prob_win:.2f}")
        
        if prob_win > 1.00:
            # Buy the strangle with same-week expiration
            # bought_call, bought_put = buy_strangle(ticker, call_option, put_option)
            logger.info('Simulated buy and started monitoring')
            monitor_trade(call_option, put_option)
            # Monitor the trade for take-profit and stop-loss
            # monitor_trade(bought_call, bought_put)
        else:
            logger.info("LOW probability of winning. Skipping trade.")
    else:
        logger.info(f"Volatility {avg_iv} is below the threshold of {high_vol_threshold}. Skipping trade.")


if __name__ == '__main__':
    log_in()
    # Execute the strategy
    trade_strangle_without_kelly('AAPL')
