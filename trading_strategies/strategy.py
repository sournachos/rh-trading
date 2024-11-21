class Strategy:
    def __init__(self, data: list[dict]):
        # This data will be the historical and live prices of the stock
        self.data = data

    def should_buy(self) -> bool:
        raise NotImplementedError

    def should_sell(self) -> bool:
        # implement partial functions so we can check stop loss every time we call should_sell
        raise NotImplementedError


class StrategyTester:
    def __init__(self):
        pass

    @property
    def strategy_parameters(self) -> dict:
        return {}

    @property
    def strategy_type(self):
        return Strategy
