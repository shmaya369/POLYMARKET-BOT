from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class Market:
    id: str
    question: str
    yes_price: float
    no_price: float
    volume: float
    liquidity: float
    spread: float

    @property
    def best_side(self) -> str:
        return "YES" if self.yes_price < self.no_price else "NO"

    @property
    def best_price(self) -> float:
        return self.yes_price if self.best_side == "YES" else self.no_price


@dataclass(slots=True)
class AnalysisResult:
    market_id: str
    question: str
    side: str
    price: float
    score: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
