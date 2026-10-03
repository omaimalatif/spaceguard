"""
Lightweight SQLite-backed local storage so the dashboard has historical data
to show trends from, and something to fall back on if the live API call fails.
"""

import sqlite3
from io import StringIO
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent.parent / "spaceguard.db"


def init_db() -> None:
    """Create the events table if it doesn't already exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def save_events(df: pd.DataFrame, event_type: str) -> None:
    """Persist the latest fetch for an event type, replacing the previous snapshot."""
    if df.empty:
        return
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM events WHERE event_type = ?", (event_type,))
        conn.execute(
            "INSERT INTO events (event_type, payload) VALUES (?, ?)",
            (event_type, df.to_json(orient="records")),
        )


def load_events(event_type: str) -> pd.DataFrame:
    """Load the last cached snapshot for an event type. Returns an empty DataFrame if none exists."""
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT payload FROM events WHERE event_type = ? ORDER BY fetched_at DESC LIMIT 1",
            (event_type,),
        ).fetchone()
    if row is None:
        return pd.DataFrame()
    return pd.read_json(StringIO(row[0]), orient="records")
