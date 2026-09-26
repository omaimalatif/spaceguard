"""Cleaning and normalization for raw DONKI event DataFrames."""

import pandas as pd


def clean_events(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic cleanup applied to any DONKI event DataFrame:
    - drop fully-empty columns
    - reset index
    (Extend this per event type as you start Step 5 of the roadmap.)
    """
    if df.empty:
        return df
    df = df.dropna(axis=1, how="all").reset_index(drop=True)
    return df
