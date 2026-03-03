from __future__ import annotations

from urllib.error import HTTPError, URLError

from polymarket_bot.analyzer import MarketAnalyzer
from polymarket_bot.config import BotConfig
from polymarket_bot.models import AnalysisResult, Market
from polymarket_bot.polymarket_client import PolymarketClient


class PolymarketAnalysisBot:
    """Coordinates data retrieval and market scoring."""

    def __init__(self, config: BotConfig | None = None) -> None:
        self.config = config or BotConfig()
        self.client = PolymarketClient(self.config)
        self.analyzer = MarketAnalyzer(self.config)

    def run(self, demo: bool = False, limit: int | None = None, top_n: int | None = None) -> list[AnalysisResult]:
        markets = self.get_markets(demo=demo, limit=limit)
        return self.analyzer.analyze(markets, top_n=top_n)

    def get_markets(self, demo: bool = False, limit: int | None = None) -> list[Market]:
        return self._demo_markets() if demo else self._fetch_markets_with_fallback(limit)

    def get_demo_markets(self) -> list[Market]:
        return self._demo_markets()

    def _fetch_markets_with_fallback(self, limit: int | None) -> list[Market]:
        try:
            return self.client.fetch_active_markets(limit=limit)
        except (URLError, HTTPError, TimeoutError, ValueError):
            return self._demo_markets()

    @staticmethod
    def _demo_markets() -> list[Market]:
        return [
            Market(
                id="demo-1",
                question="Will BTC close above $100k this month?",
                yes_price=0.41,
                no_price=0.59,
                volume=250000,
                liquidity=180000,
                spread=0.02,
            ),
            Market(
                id="demo-2",
                question="Will the Fed cut rates by next meeting?",
                yes_price=0.63,
                no_price=0.37,
                volume=160000,
                liquidity=120000,
                spread=0.03,
            ),
            Market(
                id="demo-3",
                question="Will ETH outperform BTC this quarter?",
                yes_price=0.48,
                no_price=0.52,
                volume=75000,
                liquidity=90000,
                spread=0.01,
            ),
            Market(
                id="demo-4",
                question="Will inflation print below 3.0% this quarter?",
                yes_price=0.33,
                no_price=0.67,
                volume=310000,
                liquidity=220000,
                spread=0.04,
            ),
            Market(
                id="demo-5",
                question="Will SOL exceed $250 before year-end?",
                yes_price=0.55,
                no_price=0.45,
                volume=98000,
                liquidity=65000,
                spread=0.02,
            ),
        ]
