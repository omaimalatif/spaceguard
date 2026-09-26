"""
Transparent, severity-based risk scoring — Step 8 of the roadmap, done properly.

Instead of counting raw events, this looks at how *strong* each event was,
using real DONKI fields:
- Solar flares: class letter (X is strongest, then M, C, B, A)
- CMEs: speed in km/s (faster = more likely to be geoeffective)
- Geomagnetic storms: max Kp-index (0-9 scale; 5+ is officially a storm)

Thresholds below are simplified for a student/internship prototype and are
documented here so they can be explained and tuned during Step 9 validation.
"""

import pandas as pd

# Solar flare thresholds (by class letter)
HIGH_FLARE_CLASSES = {"X"}
MODERATE_FLARE_CLASSES = {"M"}

# CME speed thresholds, km/s (NOAA generally treats 500+ km/s CMEs as notable,
# 1000+ km/s as fast/potentially geoeffective)
CME_HIGH_SPEED = 1000
CME_MODERATE_SPEED = 500

# Geomagnetic Kp-index thresholds (NOAA G-scale: Kp 5 = G1 minor storm, Kp 7+ = G3 strong)
KP_HIGH = 7
KP_MODERATE = 5


def _flare_risk(flares: pd.DataFrame) -> str:
    if flares.empty or "flareClassLetter" not in flares.columns:
        return "Low"
    if flares["flareClassLetter"].isin(HIGH_FLARE_CLASSES).any():
        return "High"
    if flares["flareClassLetter"].isin(MODERATE_FLARE_CLASSES).any():
        return "Moderate"
    return "Low"


def _cme_risk(cmes: pd.DataFrame) -> str:
    if cmes.empty or "speedKmS" not in cmes.columns:
        return "Low"
    max_speed = cmes["speedKmS"].dropna().max()
    if pd.isna(max_speed):
        return "Low"
    if max_speed >= CME_HIGH_SPEED:
        return "High"
    if max_speed >= CME_MODERATE_SPEED:
        return "Moderate"
    return "Low"


def _storm_risk(storms: pd.DataFrame) -> str:
    if storms.empty or "maxKpIndex" not in storms.columns:
        return "Low"
    max_kp = storms["maxKpIndex"].dropna().max()
    if pd.isna(max_kp):
        return "Low"
    if max_kp >= KP_HIGH:
        return "High"
    if max_kp >= KP_MODERATE:
        return "Moderate"
    return "Low"


_LEVEL_RANK = {"Low": 0, "Moderate": 1, "High": 2}


def compute_risk_level(flares: pd.DataFrame, cmes: pd.DataFrame, storms: pd.DataFrame) -> str:
    """Overall risk = the highest individual risk among flares, CMEs, and storms."""
    levels = [_flare_risk(flares), _cme_risk(cmes), _storm_risk(storms)]
    return max(levels, key=lambda lvl: _LEVEL_RANK[lvl])
