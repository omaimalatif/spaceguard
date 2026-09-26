"""
Cleaning and normalization for raw DONKI event DataFrames.

Each DONKI endpoint returns a different shape, so each event type gets its
own cleaning function that extracts the fields that actually indicate
severity — not just "an event happened," but "how strong was it."

Reference (from NASA DONKI docs):
- FLR (solar flares): `classType` e.g. "M1.2", "X2.5" — letter = class, number = magnitude
- CME: `cmeAnalyses` is a list of analysis dicts, each with a `speed` (km/s)
- GST (geomagnetic storms): `allKpIndex` is a list of dicts, each with a `kpIndex`
"""

import pandas as pd

FLARE_CLASS_ORDER = {"A": 1, "B": 2, "C": 3, "M": 4, "X": 5}


def _flare_class_letter(class_type: str) -> str:
    """'M1.2' -> 'M'. Falls back to '?' if the field is missing/unrecognized."""
    if not class_type or not isinstance(class_type, str):
        return "?"
    return class_type[0].upper() if class_type[0].upper() in FLARE_CLASS_ORDER else "?"


def _flare_class_magnitude(class_type: str) -> float:
    """'M1.2' -> 1.2. Returns 0.0 if it can't be parsed."""
    if not class_type or not isinstance(class_type, str) or len(class_type) < 2:
        return 0.0
    try:
        return float(class_type[1:])
    except ValueError:
        return 0.0


def clean_flares(df: pd.DataFrame) -> pd.DataFrame:
    """Extract class letter/magnitude and a human-readable summary from raw FLR events."""
    if df.empty:
        return df
    out = df.copy()
    if "classType" in out.columns:
        out["flareClassLetter"] = out["classType"].apply(_flare_class_letter)
        out["flareMagnitude"] = out["classType"].apply(_flare_class_magnitude)
    else:
        out["flareClassLetter"] = "?"
        out["flareMagnitude"] = 0.0
    keep = [c for c in ["classType", "flareClassLetter", "flareMagnitude",
                         "beginTime", "peakTime", "endTime", "sourceLocation"] if c in out.columns]
    return out[keep].reset_index(drop=True)


def clean_cmes(df: pd.DataFrame) -> pd.DataFrame:
    """Pull the most-accurate analysis speed out of each CME's `cmeAnalyses` list."""
    if df.empty:
        return df
    out = df.copy()

    def extract_speed(analyses):
        if not isinstance(analyses, list) or not analyses:
            return None
        accurate = [a for a in analyses if a.get("isMostAccurate")]
        chosen = accurate[0] if accurate else analyses[0]
        return chosen.get("speed")

    if "cmeAnalyses" in out.columns:
        out["speedKmS"] = out["cmeAnalyses"].apply(extract_speed)
    else:
        out["speedKmS"] = None

    keep = [c for c in ["startTime", "speedKmS", "sourceLocation", "note"] if c in out.columns]
    return out[keep].reset_index(drop=True)


def clean_storms(df: pd.DataFrame) -> pd.DataFrame:
    """Pull the maximum Kp-index observed during each geomagnetic storm."""
    if df.empty:
        return df
    out = df.copy()

    def extract_max_kp(kp_list):
        if not isinstance(kp_list, list) or not kp_list:
            return None
        values = [k.get("kpIndex") for k in kp_list if k.get("kpIndex") is not None]
        return max(values) if values else None

    if "allKpIndex" in out.columns:
        out["maxKpIndex"] = out["allKpIndex"].apply(extract_max_kp)
    else:
        out["maxKpIndex"] = None

    keep = [c for c in ["startTime", "maxKpIndex"] if c in out.columns]
    return out[keep].reset_index(drop=True)


def clean_events(df: pd.DataFrame) -> pd.DataFrame:
    """Generic fallback cleanup, kept for backward compatibility."""
    if df.empty:
        return df
    return df.dropna(axis=1, how="all").reset_index(drop=True)
