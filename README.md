# Polymarket Analysis Bot

A complete, modular Python bot that fetches active Polymarket markets, computes signal metrics, and prints ranked trade ideas from the command line.

## Features

- **Modular architecture**: separate API client, analysis engine, orchestration bot, and CLI.
- **Typed domain models** for markets and analysis output.
- **Rule-based scoring engine** using volume, liquidity, price dislocation, and spread penalties.
- **Offline demo mode** with built-in sample markets.
- **JSON output support** for integrations.

## Project Structure

```
polymarket-bot/
├── README.md
├── requirements.txt
└── src/
    └── polymarket_bot/
        ├── __init__.py
        ├── analyzer.py
        ├── bot.py
        ├── cli.py
        ├── config.py
        ├── models.py
        └── polymarket_client.py
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Run live analysis (fetches from Polymarket Gamma API):

```bash
python -m polymarket_bot.cli --limit 25 --top 10
```

Run offline demo data (always works without network):

```bash
python -m polymarket_bot.cli --demo --top 5
```

JSON output:

```bash
python -m polymarket_bot.cli --demo --json
```

## CLI Options

- `--limit`: number of active markets to fetch (default: `50`)
- `--top`: number of ranked opportunities to display (default: `10`)
- `--min-volume`: minimum volume filter (default: `1000`)
- `--min-liquidity`: minimum liquidity filter (default: `2000`)
- `--demo`: use embedded demo market data
- `--json`: output machine-readable JSON

## How Scoring Works

Each market receives a 0-100 score:

- Higher volume increases confidence.
- Higher liquidity improves executable quality.
- Larger mispricing from a neutral center (0.5) raises opportunity signal.
- Wider spreads are penalized.

The bot outputs:

- market question
- best side (`YES` / `NO`)
- latest price
- confidence score
- reason summary

## Example Output

```text
Rank  Score  Side  Price  Market
1     78.2   YES   0.43   Will candidate X win state Y?
2     73.5   NO    0.66   Will BTC close above $100k this month?
```

## Notes

- This bot is for **analysis/education** only and does not place live orders.
- You can easily extend the scoring engine in `analyzer.py`.
