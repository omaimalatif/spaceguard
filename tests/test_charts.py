import pandas as pd

from src.processing.transform import clean_cmes, clean_flares, clean_storms
from src.viz import charts


def test_all_charts_build_with_messy_data(donki_flares, donki_cmes, donki_storms):
    f, c, s = clean_flares(donki_flares), clean_cmes(donki_cmes), clean_storms(donki_storms)
    for fig in (charts.build_event_count_chart(f, c, s), charts.build_flare_class_chart(f),
                charts.build_cme_speed_chart(c), charts.build_kp_index_chart(s)):
        assert fig.to_json()  # serialises = Streamlit can render it


def test_charts_handle_empty():
    e = pd.DataFrame()
    for fig in (charts.build_flare_class_chart(e), charts.build_cme_speed_chart(e), charts.build_kp_index_chart(e)):
        assert "no data" in fig.layout.title.text


def test_flare_chart_total_matches_metric(donki_flares):
    f = clean_flares(donki_flares)
    fig = charts.build_flare_class_chart(f)
    assert sum(sum(t.y) for t in fig.data) == len(f)  # regression: '?' flares were dropped


def test_event_count_chart_values(donki_flares, donki_cmes, donki_storms):
    fig = charts.build_event_count_chart(donki_flares, donki_cmes, donki_storms)
    assert list(fig.data[0].y) == [4, 4, 3]


def test_chart_threshold_lines_match_risk_rules():
    from src.risk import rules
    cme = charts.build_cme_speed_chart(pd.DataFrame({"startTime": ["2026-09-28"], "speedKmS": [700.0]}))
    kp = charts.build_kp_index_chart(pd.DataFrame({"startTime": ["2026-09-28"], "maxKpIndex": [6.0]}))
    assert {s.y0 for s in cme.layout.shapes} == {rules.CME_HIGH_SPEED, rules.CME_MODERATE_SPEED}
    assert {s.y0 for s in kp.layout.shapes} == {rules.KP_HIGH, rules.KP_MODERATE}
