from __future__ import annotations

from polymarket_bot.config import BotConfig
from polymarket_bot.models import AnalysisResult, Market


class MarketAnalyzer:
    """Scores and ranks market opportunities."""

    def __init__(self, config: BotConfig) -> None:
        self.config = config

    def analyze(self, markets: list[Market], top_n: int | None = None) -> list[AnalysisResult]:
        filtered = [
            market
            for market in markets
            if market.volume >= self.config.min_volume and market.liquidity >= self.config.min_liquidity
        ]

        results = [self._score_market(market) for market in filtered]
        ranked = sorted(results, key=lambda item: item.score, reverse=True)
        return ranked[: (top_n if top_n is not None else self.config.top_n)]

    def _score_market(self, market: Market) -> AnalysisResult:
        volume_component = min(market.volume / 100000, 1.0)
        liquidity_component = min(market.liquidity / 200000, 1.0)
        dislocation_component = abs(market.best_price - 0.5) * 2
        spread_penalty = min(market.spread, 1.0)

        score = (
            volume_component * self.config.weight_volume
            + liquidity_component * self.config.weight_liquidity
            + dislocation_component * self.config.weight_dislocation
            - spread_penalty * self.config.weight_spread_penalty
        ) * 100

        reason = (
            f"vol={market.volume:.0f}, liq={market.liquidity:.0f}, "
            f"dislocation={dislocation_component:.2f}, spread={market.spread:.4f}"
        )

        return AnalysisResult(
            market_id=market.id,
            question=market.question,
            side=market.best_side,
            price=market.best_price,
            score=round(max(score, 0.0), 2),
            reason=reason,
        )
