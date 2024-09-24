"""I want an algorithm for trading stock options profitably. Lets just assume we're doing Call options.

We firstly need to identify IF we should buy a Call option by looking at the moving average and if it has an upward trajectory (or if you have a better idea let me know).

We then need to look at the bid and ask price. I think we should have some logic that cares about the difference between them.

Then we buy the option at some price, and we store that price obviously.
Then what we basically want to do is wait. We want to continue to monitor the price of the option.

The logic:
If at any point we've lost 20% of what we paid for the option, sell the contract and cut our losses.

If the price continues to rise to be profitable, but then dips again, we want to limit how much it dips before we sell our contract. Basically I want there to be some leeway to absorb normal fluctuations in the stock price. I was thinking something like 5%. So if for instance we've gotten to a maximum and it starts dipping, sell the contract if it drops 5% from the maximum

Otherwise just keep riding the wave till we get close to the end of the trading day. Lets say we sell our contract no matter what at 3:30pm eastern

------------------------------------------------------------------------------------------------------------------------
1. Determine When to Buy a Call Option
We'll base this decision on the stock's moving average to identify an upward trend. A simple yet effective method is to use two moving averages:

Short-term moving average (e.g., 10-period MA)
Long-term moving average (e.g., 50-period MA)
The algorithm would buy a call option when the short-term moving average crosses above the long-term moving average, signaling an upward trend (often called a "golden cross"). This approach can help filter out noise and ensure you're entering the trade when the stock is on a bullish trajectory.

Alternative suggestion: Instead of only looking at moving averages, we could add an RSI (Relative Strength Index) filter to avoid buying calls when the stock is overbought (RSI > 70).

2. Check Bid-Ask Spread
The bid-ask spread is crucial when trading options, as a wide spread can eat into your profits. You might want to skip trades where the spread is larger than a certain percentage (e.g., 2%). The logic would be:

3. Buying the Call Option
Once the conditions (moving averages, RSI, and bid-ask spread) are met, the algorithm buys the option at the ask price, storing that price for further tracking.

4. Set a Stop-Loss for 20% Drawdown
After buying, the algorithm should monitor the price of the option. If the price of the option drops 20% from the purchase price, the stop-loss is triggered, and the contract is sold:

5. Trail a Stop-Loss for Profitable Options
When the price of the option moves up, the algorithm should track the highest price it reaches. If the price drops 5% from that high, it will sell the contract to lock in profits. This creates a trailing stop mechanism:

6. Exit by 3:30 PM
Regardless of the current option price, the algorithm will exit the position by 3:30 PM Eastern. This prevents holding options too close to expiration or into uncertain after-hours price movements:


Key Concepts:
Golden Cross: Buy when the short-term moving average crosses above the long-term one.
Bid-Ask Spread: Avoid large spreads to maximize profits.
Stop-Loss: Cut losses at 20%.
Trailing Stop: Sell when the price drops 5% from the highest point to secure profits.
Time-Based Exit: Sell all positions at 3:30 PM to avoid end-of-day volatility.
This strategy uses a combination of trend indicators, risk management, and time-based exits to systematically trade options. Keep in mind that this is a basic framework and should be tested and refined using historical data before live trading.
"""

from loguru import logger
from strategy import Strategy


def calculate_moving_average(data, period):
    if len(data) < period:
        return sum(data) / len(data)
    return sum(data[-period:]) / period


def calculate_rsi(data, period=14):
    gains, losses = 0, 0
    for i in range(1, len(data)):
        delta = data[i] - data[i - 1]
        if delta > 0:
            gains += delta
        else:
            losses -= delta

    if len(data) < period:
        avg_gain = gains / len(data)
        avg_loss = losses / len(data)
    else:
        avg_gain = gains / period
        avg_loss = losses / period

    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


class MovingAverageStrategy(Strategy):
    def __init__(
        self, rsi_threshold_low: int, rsi_threshold_high: int, rsi_period: int
    ):
        self.rsi_threshold_low = rsi_threshold_low
        self.rsi_threshold_high = rsi_threshold_high
        self.rsi_period = rsi_period

    def should_buy(self) -> bool:
        ma_5 = calculate_moving_average(data, 5)
        ma_30 = calculate_moving_average(data, 30)
        rsi = calculate_rsi(data, rsi_period)
        logger.info(f"MA5: {ma_5}, MA30: {ma_30}, RSI: {rsi}")

        if ma_5 > ma_30 and rsi < self.rsi_threshold_low:
            return True
        return False

    def should_sell(self) -> bool:
        ma_5 = calculate_moving_average(data, 5)
        ma_30 = calculate_moving_average(data, 30)
        rsi = calculate_rsi(data, rsi_period)
        logger.info(f"MA5: {ma_5}, MA30: {ma_30}, RSI: {rsi}")

        if ma_5 < ma_30 or rsi > self.rsi_threshold_high:
            return True
        return False
