"""Risk rules are severity-based (strongest event wins), matching the in-app methodology text."""
import pandas as pd
import pytest

from src.risk.rules import compute_risk_level

E = pd.DataFrame()


def flares(*letters):
    return pd.DataFrame({"flareClassLetter": list(letters)})


def cmes(*speeds):
    return pd.DataFrame({"speedKmS": list(speeds)})


def storms(*kps):
    return pd.DataFrame({"maxKpIndex": list(kps)})


def test_low_when_no_events():
    assert compute_risk_level(E, E, E) == "Low"


def test_many_weak_events_stay_low():
    # Regression: old rules were count-based; new rules must ignore volume.
    assert compute_risk_level(flares(*["C"] * 50), cmes(*[200] * 50), E) == "Low"


@pytest.mark.parametrize("letters,expected", [(["A", "B", "C"], "Low"), (["C", "M"], "Moderate"), (["M", "X"], "High"), (["?"], "Low")])
def test_flare_thresholds(letters, expected):
    assert compute_risk_level(flares(*letters), E, E) == expected


@pytest.mark.parametrize("speed,expected", [(499.9, "Low"), (500, "Moderate"), (999.9, "Moderate"), (1000, "High")])
def test_cme_speed_boundaries(speed, expected):
    assert compute_risk_level(E, cmes(speed), E) == expected


@pytest.mark.parametrize("kp,expected", [(4.67, "Low"), (5, "Moderate"), (6.67, "Moderate"), (7, "High"), (9, "High")])
def test_kp_boundaries(kp, expected):
    assert compute_risk_level(E, E, storms(kp)) == expected


def test_overall_is_highest_of_the_three():
    assert compute_risk_level(flares("C"), cmes(600), storms(7)) == "High"
    assert compute_risk_level(flares("M"), cmes(100), storms(2)) == "Moderate"


def test_missing_values_do_not_crash():
    assert compute_risk_level(E, cmes(None, float("nan")), storms(None)) == "Low"
