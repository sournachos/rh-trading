from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from itertools import product

from trading_strategies import Strategy, StrategyTester


@dataclass
class Trade:
    buy_date: datetime
    sell_date: datetime
    buy_price: Decimal
    sell_price: Decimal


@dataclass
class TestOutput:
    profit: Decimal
    loss: Decimal
    trades: list[Trade]


class BackTester:
    def __init__(
        self,
        strategy_tester: StrategyTester,
        ticker: str,
        start_date: datetime,
        end_date: datetime,
    ):
        self.strategy_tester = strategy_tester
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date

    def fetch_options_pricing_history(self) -> dict:
        # fetch options pricing history
        return {}

    def fetch_stock_price_history(self) -> dict:
        # fetch stock price history
        return {}

    def create_strategy_variations(self) -> list[Strategy]:
        strat_params = self.strategy_tester.strategy_parameters
        param_ranges = {
            key: range(value[0], value[1] + 1) for key, value in strat_params.items()
        }
        param_combinations = list(product(*param_ranges.values()))
        return [
            self.strategy_tester.strategy_type(
                **dict(zip(param_ranges.keys(), combination))
            )
            for combination in param_combinations
        ]

    def run(self):
        options_history = self.fetch_options_pricing_history()
        stock_history = self.fetch_stock_price_history()
        strategy_variations = self.create_strategy_variations()
        test_outputs = []
        for strategy in strategy_variations:
            test_outputs.append(back_test(strategy, options_history, stock_history))
        test_outputs.sort(key=lambda x: x.profit, reverse=True)
        return test_outputs


# I want to make this async so we can run multiple backtests simultaneously.
# There will be thousands of variations to test so we need to run them in parallel
def back_test(
    strategy: Strategy, options_history: dict, stock_history: dict
) -> TestOutput:
    pass
