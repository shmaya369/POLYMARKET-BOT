from __future__ import annotations

import argparse
import json

from polymarket_bot.bot import PolymarketAnalysisBot
from polymarket_bot.config import BotConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Polymarket analysis bot")
    parser.add_argument("--limit", type=int, default=50, help="Number of markets to fetch")
    parser.add_argument("--top", type=int, default=10, help="Number of top opportunities to show")
    parser.add_argument("--min-volume", type=float, default=1000.0, help="Minimum volume filter")
    parser.add_argument("--min-liquidity", type=float, default=2000.0, help="Minimum liquidity filter")
    parser.add_argument("--demo", action="store_true", help="Use built-in demo market data")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    config = BotConfig(
        fetch_limit=args.limit,
        top_n=args.top,
        min_volume=args.min_volume,
        min_liquidity=args.min_liquidity,
    )
    bot = PolymarketAnalysisBot(config=config)
    results = bot.run(demo=args.demo, limit=args.limit, top_n=args.top)

    if args.json:
        print(json.dumps([result.to_dict() for result in results], indent=2))
        return

    if not results:
        print("No markets matched filters.")
        return

    print(f"{'Rank':<5} {'Score':<7} {'Side':<5} {'Price':<7} Market")
    for index, item in enumerate(results, start=1):
        print(f"{index:<5} {item.score:<7} {item.side:<5} {item.price:<7.2f} {item.question}")


if __name__ == "__main__":
    main()
