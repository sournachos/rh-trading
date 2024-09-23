from decimal import Decimal


class Strategy:
    def __init__(
        self,
        ticker: str,
        rsi_period: int,
        stop_loss_percentage: Decimal,
        rsi_threshold_low: int,
        rsi_threshold_high: int,
    ):
        self.ticker = ticker
        self.rsi_period = rsi_period
        self.stop_loss_percentage = stop_loss_percentage
        self.rsi_threshold_low = rsi_threshold_low
        self.rsi_threshold_high = rsi_threshold_high

    def should_buy(self) -> bool:
        raise NotImplementedError

    def should_sell(self) -> bool:
        # implement partial functions so we can check stop loss every time we call should_sell
        raise NotImplementedError

    def should_wait(self) -> bool:
        raise NotImplementedError
