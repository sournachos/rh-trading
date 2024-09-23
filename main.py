# Orchestrate operations here
import time
from datetime import datetime, timezone

from loguru import logger

from trading_strategies import Strategy
from trading_strategies.moving_averages import MovingAverageStrategy
from utils import at_stop_loss, log_in

# Parameters
TICKER = "AAPL"
STOP_LOSS_PERCENTAGE = 0.15


def main(strat: Strategy) -> None:
    log_in()
    position = None
    while True:
        # Get our data. We need things like historical prices, current price, etc.
        # Anything that our strategy needs to make decisions. OR our strategy could do that on it's own
        # But I'm trying to not have the strategy know about which ticker it's trading or it's current position. That's handled by this loop... I think
        if datetime.now(timezone.utc) >= "20:30":
            logger.info("Selling")
            # sell_option_limit_order
            break
        if position:
            if at_stop_loss(position, current_price, STOP_LOSS_PERCENTAGE):
                logger.info(f"Selling because of stop loss at {STOP_LOSS_PERCENTAGE}")
                # sell_option_limit_order
                break
            if strat.should_sell():
                logger.info("Selling because of strategy signal")
                # sell_option_limit_order
                break
            elif strat.should_wait():
                logger.info("Waiting for a signal to sell")
                continue
        else:
            if strat.should_buy():
                logger.info("Buying because of strategy signal")
                # buy_option_limit_order
                position = {"entry_price": current_price}
                continue
            else:
                logger.info("Waiting for a signal to buy")
        time.sleep(10)


if __name__ == "__main__":
    # We could build a CLI tool for this so we can pass in the strategy and ticker from the command line
    rsi_period = 14
    rsi_threshold_low = 30
    rsi_threshold_high = 70
    main(MovingAverageStrategy(rsi_threshold_low, rsi_threshold_high, rsi_period))
