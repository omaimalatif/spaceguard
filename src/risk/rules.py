"""
Transparent, rule-based risk scoring.

Kept intentionally simple and documented for Step 8 of the roadmap — presented
as a student prototype, not a scientific forecasting model. Tune the thresholds
here as you validate against real historical events in Step 9.
"""

import pandas as pd

# Event-count thresholds per look-back window (tune during testing)
MODERATE_THRESHOLD = 2
HIGH_THRESHOLD = 5


def compute_risk_level(flares: pd.DataFrame, cmes: pd.DataFrame, storms: pd.DataFrame) -> str:
    """
    Very simple v1 rule: total event count across all three categories in the
    selected window drives the risk level. Replace/extend with severity-aware
    logic (e.g. flare class X vs C, storm Kp-index) once you're validating
    against real data in Step 9.
    """
    total_events = len(flares) + len(cmes) + len(storms)

    if total_events >= HIGH_THRESHOLD:
        return "High"
    if total_events >= MODERATE_THRESHOLD:
        return "Moderate"
    return "Low"
