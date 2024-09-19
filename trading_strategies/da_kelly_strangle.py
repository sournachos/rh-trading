import sys
sys.path.append("../")
from loguru import logger
from utils import closest_friday, log_in
import robin_stocks.robinhood as r
from decimal import Decimal
import time

log_in()

# Kelly Criterion function
def kelly_criterion(prob_win, payout_ratio):
    prob_loss = 1 - prob_win
    return (payout_ratio * prob_win - prob_loss) / payout_ratio

# Function to monitor volatility (using implied volatility as a proxy)
def get_implied_volatility(ticker, exp_date, option):
    options = r.options.get_option_market_data(ticker, exp_date, option['strike_price'], option['type'])
    iv_values = [Decimal(option['implied_volatility']) for option in options if 'implied_volatility' in option]
    return sum(iv_values) / len(iv_values) if iv_values else 0

# Function to fetch the nearest expiration date and most profitable strike
def find_best_strikes(ticker, exp_date):
    stock_price = Decimal(r.stocks.get_latest_price(ticker)[0])
    
    # Fetch call and put options for the nearest expiration date
    call_options = r.options.find_options_by_expiration(ticker, expirationDate=exp_date, optionType='call')
    put_options = r.options.find_options_by_expiration(ticker, expirationDate=exp_date, optionType='put')

    # Find the strike prices closest to the current stock price
    best_call_option = min(call_options, key=lambda x: abs(Decimal(x['strike_price']) - stock_price))
    best_put_option = min(put_options, key=lambda x: abs(Decimal(x['strike_price']) - stock_price))
    
    return best_call_option, best_put_option

# Function to estimate the probability of winning using Delta
def get_probability_of_winning(option):
    # Delta is the probability that the option will expire ITM
    return Decimal(option['delta'])

# Function to buy a strangle (one call, one put)
def buy_strangle(ticker, call_option, put_option):
    # Place a market order for the call and put options
    bought_call = r.options.order_buy_option_limit('open', 'debit', call_option['adjusted_mark_price_round_down'], ticker, 1, call_option['expiration_date'], call_option['strike_price'], 'call')
    bought_put = r.options.order_buy_option_limit('open', 'debit', call_option['adjusted_mark_price_round_down'], ticker, 1, put_option['expiration_date'], put_option['strike_price'], 'put')

    return bought_call, bought_put
    
# Position Sizing using Kelly Criterion
def calculate_position_size(prob_win, payout_ratio, capital):
    fraction_to_risk = kelly_criterion(prob_win, payout_ratio)
    # Ensure the fraction is between 0 and 1
    fraction_to_risk = max(min(fraction_to_risk, 1), 0)
    return capital * fraction_to_risk

# Monitor the trade for take-profit or stop-loss
def monitor_trade(call_option, put_option, take_profit=0.05, stop_loss=0.02):
    initial_call_price = Decimal(call_option['adjusted_mark_price'])
    initial_put_price = Decimal(put_option['adjusted_mark_price'])
    
    initial_total_value = initial_call_price + initial_put_price
    
    while True:
        # Refresh option data
        # TODO(experimental): Instead of just the mark price (for take-profits),
        # calculate midpoint price between ask and mark price. Keep mark price for stop-losses.
        call_price = Decimal(r.options.get_option_market_data_by_id(call_option['id'])[0]['adjusted_mark_price'])
        put_price = Decimal(r.options.get_option_market_data_by_id(put_option['id'])[0]['adjusted_mark_price'])
        
        current_total_value = call_price + put_price
        profit_pct = (current_total_value - initial_total_value) / initial_total_value

        logger.info(f"Current Profit: {profit_pct*100:.2f}%")

        if profit_pct >= take_profit:
            logger.info("Take-profit triggered, closing positions.")
            r.options.order_sell_option_limit(
                symbol=call_option['chain_symbol'],
                option_type='call',
                strike_price=call_option['strike_price'],
                expirationDate=call_option['expiration_date'],
                price=call_price,
                quantity=1,
                time_in_force='gtc'
            )
            r.options.order_sell_option_limit(
                symbol=put_option['chain_symbol'],
                option_type='put',
                strike_price=put_option['strike_price'],
                expirationDate=put_option['expiration_date'],
                price=put_price,
                quantity=1,
                time_in_force='gtc'
            )
            break
        elif profit_pct <= -stop_loss:
            logger.info("Stop-loss triggered, closing positions.")
            r.options.order_sell_option_limit(
                symbol=call_option['chain_symbol'],
                option_type='call',
                strike_price=call_option['strike_price'],
                expirationDate=call_option['expiration_date'],
                price=call_price,
                quantity=1,
                time_in_force='gtc'
            )
            r.options.order_sell_option_limit(
                symbol=put_option['chain_symbol'],
                option_type='put',
                strike_price=put_option['strike_price'],
                expirationDate=put_option['expiration_date'],
                price=put_price,
                quantity=1,
                time_in_force='gtc'
            )
            break

        # Sleep for a bit before checking again
        time.sleep(10)

# Function to calculate prob_win using Greeks
def calculate_prob_win(ticker, exp_date, call_option, put_option):
    # Fetch detailed option data
    detailed_call = r.options.find_options_by_expiration_and_strike(ticker, exp_date, call_option['strike_price'])[0]
    detailed_put = r.options.find_options_by_expiration_and_strike(ticker, exp_date, put_option['strike_price'])[0]
    
    delta_call = Decimal(detailed_call.get('delta', 0))
    delta_put = Decimal(detailed_put.get('delta', 0))
    
    # Estimate probability
    # For calls: prob of stock > strike is roughly delta_call
    # For puts: prob of stock < strike is roughly 1 - delta_put
    prob_call = delta_call
    prob_put = 1 - delta_put
    
    prob_win = prob_call + prob_put
    return prob_win

# Main trading loop
def trade_strangle_with_kelly(ticker , capital):
    # Get best option strike prices for the nearest Friday
    exp_date = closest_friday()
    call_option, put_option = find_best_strikes(ticker, exp_date)

    # Fetch implied volatility
    call_iv = get_implied_volatility(ticker, exp_date, call_option)
    put_iv = get_implied_volatility(ticker, exp_date, put_option)
    avg_iv = (call_iv + put_iv) / 2
    logger.info(f"Implied Volatility: {avg_iv}")
    
    high_vol_threshold = 0.5  # Adjust this threshold as needed
    
    if avg_iv > high_vol_threshold:
        logger.info(f"High volatility detected: {avg_iv}. Finding best strangle opportunity...")
        
        # Calculate prob_win using Greeks
        prob_win = calculate_prob_win(ticker, exp_date, call_option, put_option)
        logger.info(f"Calculated Probability of Winning: {prob_win:.2f}")
        
        # Assume a payout ratio; this should be based on your specific strategy
        # NOTE: zero fucking clue - just gotta play around with it
        # payout_ratio = 2.0  # Example value
        
        # Calculate position size based on the Kelly Criterion
        # position_size = calculate_position_size(prob_win, payout_ratio, capital)
        # logger.info(f"Position Size: ${position_size:.2f}")
        
        if prob_win > 999999.00:
            # Buy the strangle with same-week expiration
            # bought_call, bought_put = buy_strangle(ticker, call_option, put_option)
            logger.info('boughtttt')
            # Monitor the trade for take-profit and stop-loss
            # monitor_trade(bought_call, bought_put)
        else:
            logger.info("LOW probability of winning. Skipping trade.")
    else:
        logger.info(f"Volatility {avg_iv} is below the threshold of {high_vol_threshold}. Skipping trade.")

# Execute the strategy
trade_strangle_with_kelly('AAPL', 2000)
