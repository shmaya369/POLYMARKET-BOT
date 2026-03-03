from __future__ import annotations

from urllib.error import HTTPError, URLError

import pandas as pd
import streamlit as st

from polymarket_bot.bot import PolymarketAnalysisBot
from polymarket_bot.config import BotConfig


def _parse_slugs(raw_slugs: str) -> list[str]:
    return [line.strip() for line in raw_slugs.splitlines() if line.strip()]


def _build_table(results: list[dict[str, float | str]]) -> pd.DataFrame:
    return pd.DataFrame(results)


def _style_table(frame: pd.DataFrame):
    return frame.style.highlight_max(subset=["edge"], color="#ffe0b2")


def main() -> None:
    st.set_page_config(page_title="Polymarket Bot", layout="wide")
    st.title("בוט ניתוח שווקים לפולימרקט")

    raw_slugs = st.text_area("רשימת slugs (אחד בכל שורה)", height=140)

    col1, col2 = st.columns(2)
    with col1:
        limit = st.number_input("limit", min_value=1, max_value=500, value=25, step=1)
    with col2:
        min_edge = st.number_input("min_edge", min_value=0.0, max_value=1.0, value=0.03, step=0.01)

    demo_mode = st.checkbox("מצב דמו", value=False)

    if st.button("נתח שווקים", type="primary"):
        selected_slugs = _parse_slugs(raw_slugs)

        config = BotConfig(fetch_limit=int(limit), top_n=int(limit))
        bot = PolymarketAnalysisBot(config=config)

        try:
            markets = bot._demo_markets() if demo_mode else bot.client.fetch_active_markets(limit=int(limit))
        except (URLError, HTTPError, TimeoutError, ValueError) as exc:
            st.error(f"שגיאה בעת טעינת שווקים מה-API: {exc}")
            return

        if selected_slugs:
            slug_set = {slug.lower() for slug in selected_slugs}
            markets = [
                market
                for market in markets
                if market.id.lower() in slug_set
                or any(slug in market.question.lower() for slug in slug_set)
            ]

        if not markets:
            st.info("לא נמצאו שווקים תואמים ל-slugs שהוזנו.")
            return

        analysis = bot.analyzer.analyze(markets, top_n=int(limit))

        rows: list[dict[str, float | str]] = []
        for result in analysis:
            edge = abs(0.5 - result.price)
            if edge < min_edge:
                continue

            volume = 0.0
            liquidity = 0.0
            for part in result.reason.split(","):
                key, _, value = part.strip().partition("=")
                if key == "vol":
                    volume = float(value)
                elif key == "liq":
                    liquidity = float(value)

            rows.append(
                {
                    "slug": result.market_id,
                    "probability": round(result.price, 4),
                    "edge": round(edge, 4),
                    "EV": round(edge * 100, 2),
                    "volume": round(volume, 2),
                    "liquidity": round(liquidity, 2),
                    "side": result.side,
                    "score": result.score,
                    "question": result.question,
                }
            )

        if not rows:
            st.warning("אין תוצאות שעומדות בערך min_edge שבחרת.")
            return

        table = _build_table(rows)
        st.dataframe(_style_table(table), width="stretch", hide_index=True)

        st.markdown(
            """
            **פירוש קצר לתוצאות:**
            ערך **probability** מציג את המחיר/הסתברות הנוכחית בשוק. **edge** גבוה יותר מצביע על
            סטייה גדולה יותר מנקודת איזון (0.5), ו-**EV** נותן אינדיקציה פשוטה לגודל ההזדמנות.
            בנוסף, **volume** ו-**liquidity** עוזרים להעריך עד כמה השוק סחיר ועמוק בפועל.
            """
        )


if __name__ == "__main__":
    main()
