from dataclasses import dataclass


@dataclass(slots=True)
class BotConfig:
    """Runtime configuration for the analysis bot."""

    gamma_base_url: str = "https://gamma-api.polymarket.com"
    markets_endpoint: str = "/markets"
    request_timeout_seconds: int = 15

    fetch_limit: int = 50
    top_n: int = 10
    min_volume: float = 1000.0
    min_liquidity: float = 2000.0

    weight_volume: float = 0.35
    weight_liquidity: float = 0.25
    weight_dislocation: float = 0.30
    weight_spread_penalty: float = 0.10
