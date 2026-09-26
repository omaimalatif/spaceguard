import pandas as pd

from src.risk.rules import compute_risk_level


def test_low_risk_when_no_events():
    empty = pd.DataFrame()
    assert compute_risk_level(empty, empty, empty) == "Low"


def test_high_risk_when_many_events():
    busy = pd.DataFrame({"x": range(3)})
    assert compute_risk_level(busy, busy, busy) == "High"
