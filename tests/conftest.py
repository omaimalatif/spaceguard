import pandas as pd
import pytest


@pytest.fixture
def donki_flares():
    """Raw FLR-shaped payload incl. messy real-world cases (null/lowercase/letter-only class)."""
    return pd.DataFrame([
        {"beginTime": "2026-09-28T01:00Z", "peakTime": "2026-09-28T01:10Z", "endTime": None, "classType": "M5.4", "sourceLocation": "N12W30"},
        {"beginTime": "2026-09-29T05:00Z", "peakTime": "2026-09-29T05:12Z", "endTime": "2026-09-29T05:30Z", "classType": "C2.1", "sourceLocation": ""},
        {"beginTime": "2026-09-30T05:00Z", "peakTime": None, "endTime": None, "classType": None, "sourceLocation": None},
        {"beginTime": "2026-09-30T08:00Z", "peakTime": None, "endTime": None, "classType": "x1.0", "sourceLocation": None},
    ])


@pytest.fixture
def donki_cmes():
    return pd.DataFrame([
        {"startTime": "2026-09-28T02:00Z", "sourceLocation": "N10W20", "note": "", "cmeAnalyses": [{"speed": 1250.0, "isMostAccurate": True}, {"speed": 300.0, "isMostAccurate": False}]},
        {"startTime": "2026-09-29T02:00Z", "sourceLocation": "", "note": "", "cmeAnalyses": None},
        {"startTime": "2026-09-29T12:00Z", "sourceLocation": "", "note": "", "cmeAnalyses": []},
        {"startTime": "2026-09-30T12:00Z", "sourceLocation": "", "note": "", "cmeAnalyses": [{"speed": None, "isMostAccurate": True}]},
    ])


@pytest.fixture
def donki_storms():
    return pd.DataFrame([
        {"startTime": "2026-09-29T00:00Z", "allKpIndex": [{"kpIndex": 4.33}, {"kpIndex": 6.67}, {"kpIndex": 5.0}]},
        {"startTime": "2026-09-30T00:00Z", "allKpIndex": [{"observedTime": "x"}]},
        {"startTime": "2026-09-30T06:00Z", "allKpIndex": None},
    ])
