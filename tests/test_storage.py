import pandas as pd
import pytest

from src.data import storage


@pytest.fixture(autouse=True)
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "t.db")
    storage.init_db()


def test_roundtrip_preserves_data():
    df = pd.DataFrame({"startTime": ["2026-09-29T00:00Z"], "maxKpIndex": [6.67]})
    storage.save_events(df, "storm")
    out = storage.load_events("storm")  # regression: crashed on pandas 3 (literal JSON string)
    assert out.shape == df.shape and out.loc[0, "maxKpIndex"] == 6.67


def test_load_missing_returns_empty():
    assert storage.load_events("flare").empty


def test_save_replaces_previous_snapshot():
    storage.save_events(pd.DataFrame({"a": [1, 2]}), "cme")
    storage.save_events(pd.DataFrame({"a": [9]}), "cme")
    assert list(storage.load_events("cme")["a"]) == [9]


def test_empty_save_keeps_old_snapshot():
    storage.save_events(pd.DataFrame({"a": [1]}), "cme")
    storage.save_events(pd.DataFrame(), "cme")
    assert len(storage.load_events("cme")) == 1
