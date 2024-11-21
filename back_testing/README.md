I intend for this module to basically take a strategy and run it against historical data.
I then intend for it to iterate on that strategy with different parameters to the strategy.
For instance the moving averages strat. We care about a low moving average, a high moving average, and RSI.
If we can provide a range of integers for each parameter, we can brute force this to spit out the optimal parameter values for the given stock and timeframe.