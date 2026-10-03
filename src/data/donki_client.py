"""
Thin wrapper around NASA's DONKI (Database Of Notifications, Knowledge, Information) API.

NOTE: On 2026-09-30 CCMC moved the public DONKI API. The old
https://api.nasa.gov/DONKI/... gateway now redirects to a CCMC news page (HTML), and the
new base is https://ccmc.gsfc.nasa.gov/DONKI-API/get/... (same parameters and JSON format).
Source: https://ccmc.gsfc.nasa.gov/news/major-updates
Override with the DONKI_BASE_URL env var / Streamlit secret if NASA moves it again.
"""

import os

import pandas as pd
import requests

BASE_URL = os.environ.get("DONKI_BASE_URL", "https://ccmc.gsfc.nasa.gov/DONKI-API/get").rstrip("/")
API_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")  # only sent if BASE_URL is the old api.nasa.gov gateway
TIMEOUT_SECONDS = 15


def _get(endpoint: str, start_date: str, end_date: str) -> list:
    """Call a DONKI endpoint and return the raw JSON list. Raises on HTTP/network errors."""
    params = {"startDate": start_date, "endDate": end_date}
    if "api.nasa.gov" in BASE_URL:
        params["api_key"] = API_KEY
    response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    if not response.text.strip():
        return []  # empty body (HTTP 200) = no events
    try:
        return response.json() or []
    except ValueError as exc:  # HTML page (e.g. a redirect to a news page), proxy message, etc.
        raise RuntimeError(
            f"DONKI/{endpoint} returned non-JSON (HTTP {response.status_code}) from {response.url}: "
            f"{response.text[:80]!r}"
        ) from exc


def get_solar_flares(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch solar flare (FLR) events for the given date range."""
    return pd.DataFrame(_get("FLR", start_date, end_date))


def get_cme_events(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch coronal mass ejection (CME) events for the given date range."""
    return pd.DataFrame(_get("CME", start_date, end_date))


def get_geomagnetic_storms(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch geomagnetic storm (GST) events for the given date range."""
    return pd.DataFrame(_get("GST", start_date, end_date))
