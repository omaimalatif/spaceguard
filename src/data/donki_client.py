"""
Thin wrapper around NASA's DONKI (Database Of Notifications, Knowledge, Information) API.
Docs: https://api.nasa.gov/ (see DONKI section) and https://ccmc.gsfc.nasa.gov/tools/DONKI/
"""

import os

import pandas as pd
import requests

BASE_URL = "https://api.nasa.gov/DONKI"
API_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")  # DEMO_KEY works but has a low rate limit
TIMEOUT_SECONDS = 15


def _get(endpoint: str, start_date: str, end_date: str) -> list:
    """Call a DONKI endpoint and return the raw JSON list. Raises on HTTP/network errors."""
    params = {"startDate": start_date, "endDate": end_date, "api_key": API_KEY}
    response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json() or []


def get_solar_flares(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch solar flare (FLR) events for the given date range."""
    data = _get("FLR", start_date, end_date)
    return pd.DataFrame(data)


def get_cme_events(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch coronal mass ejection (CME) events for the given date range."""
    data = _get("CME", start_date, end_date)
    return pd.DataFrame(data)


def get_geomagnetic_storms(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch geomagnetic storm (GST) events for the given date range."""
    data = _get("GST", start_date, end_date)
    return pd.DataFrame(data)
