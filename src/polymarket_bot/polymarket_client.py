from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from polymarket_bot.config import BotConfig
from polymarket_bot.models import Market


class PolymarketClient:
    """Client for reading market data from Polymarket Gamma API."""

    def __init__(self, config: BotConfig) -> None:
        self.config = config

    def fetch_active_markets(self, limit: int | None = None) -> list[Market]:
        limit_value = limit if limit is not None else self.config.fetch_limit
        query = urlencode({"active": "true", "closed": "false", "limit": limit_value})
        url = f"{self.config.gamma_base_url}{self.config.markets_endpoint}?{query}"

        request = Request(url, method="GET")
        with urlopen(request, timeout=self.config.request_timeout_seconds) as response:
            payload = response.read().decode("utf-8")
        raw_markets = json.loads(payload)

        markets: list[Market] = []
        for row in raw_markets:
            parsed = self._parse_market(row)
            if parsed is not None:
                markets.append(parsed)

        return markets

    @staticmethod
    def _parse_market(row: dict[str, Any]) -> Market | None:
        try:
            market_id = str(row.get("id") or row.get("conditionId") or "")
            question = str(row.get("question") or row.get("title") or "")

            yes_price = _to_float(row.get("outcomePrices", []), index=0, default=0.5)
            no_price = _to_float(row.get("outcomePrices", []), index=1, default=max(0.0, 1 - yes_price))

            volume = _to_float_value(row.get("volume") or row.get("volumeNum") or row.get("volume24hr"), 0.0)
            liquidity = _to_float_value(row.get("liquidity") or row.get("liquidityNum"), 0.0)
            spread = abs(yes_price + no_price - 1.0)

            if not market_id or not question:
                return None

            return Market(
                id=market_id,
                question=question,
                yes_price=yes_price,
                no_price=no_price,
                volume=volume,
                liquidity=liquidity,
                spread=spread,
            )
        except (TypeError, ValueError):
            return None


class PolymarketClientError(RuntimeError):
    pass


def _to_float(outcome_prices: Any, index: int, default: float) -> float:
    if isinstance(outcome_prices, list) and len(outcome_prices) > index:
        return _to_float_value(outcome_prices[index], default)
    return default


def _to_float_value(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
