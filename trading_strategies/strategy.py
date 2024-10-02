from decimal import Decimal


class Strategy:
    def __init__(self, ticker: str, stop_loss_percentage: Decimal):
        self.ticker = ticker
        self.stop_loss_percentage = stop_loss_percentage

    def should_buy(self) -> bool:
        raise NotImplementedError

    def should_sell(self) -> bool:
        # implement partial functions so we can check stop loss every time we call should_sell
        raise NotImplementedError
