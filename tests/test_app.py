"""End-to-end: run the real Streamlit script headlessly with the NASA API mocked."""
from pathlib import Path
from unittest import mock

import pandas as pd
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from src.data import storage

APP = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture(autouse=True)
def isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "t.db")
    st.cache_data.clear()


def run(payloads=None, fail=False):
    with mock.patch("src.data.donki_client._get") as g:
        if fail:
            g.side_effect = RuntimeError("429 Too Many Requests")
        else:
            g.side_effect = lambda ep, s, e: (payloads or {}).get(ep, [])
        at = AppTest.from_file(APP, default_timeout=30).run()
        return at, g


def risk_text(at):
    return " ".join(m.value for m in at.markdown if "Current Risk" in m.value)


def test_live_data_renders(donki_flares, donki_cmes, donki_storms):
    at, _ = run({"FLR": donki_flares.to_dict("records"), "CME": donki_cmes.to_dict("records"), "GST": donki_storms.to_dict("records")})
    assert not at.exception
    assert [m.value for m in at.metric] == ["4", "4", "3"]
    assert "High" in risk_text(at)  # X flare + 1250 km/s CME


def test_empty_window_is_low_not_crash():
    at, _ = run({})
    assert not at.exception and "Low" in risk_text(at)


def test_api_failure_with_cache_shows_warning_not_traceback(donki_flares):
    run({"FLR": donki_flares.to_dict("records")})          # populate cache
    st.cache_data.clear()
    at, _ = run(fail=True)
    assert not at.exception                                 # regression: crashed on pandas 3
    assert at.warning and "cached" in " ".join(m.value for m in at.markdown)


def test_api_failure_with_no_cache_is_unknown_not_low():
    at, _ = run(fail=True)
    assert not at.exception and "Unknown" in risk_text(at)


def test_repeat_run_is_served_from_cache_not_api():
    with mock.patch("src.data.donki_client._get", return_value=[]) as g:
        at = AppTest.from_file(APP, default_timeout=30).run()
        first = g.call_count
        assert first == 3                      # FLR + CME + GST once each
        at.run()                               # rerun, same window
        assert g.call_count == first           # no extra API calls
        at.slider[0].set_value(30).run()       # new window -> must refetch
        assert g.call_count == first + 3
