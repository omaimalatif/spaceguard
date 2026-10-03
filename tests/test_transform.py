import pandas as pd

from src.processing.transform import clean_cmes, clean_flares, clean_storms


def test_flare_parsing(donki_flares):
    out = clean_flares(donki_flares)
    assert list(out["flareClassLetter"]) == ["M", "C", "?", "X"]  # lowercase 'x1.0' normalised, None -> '?'
    assert out.loc[0, "flareMagnitude"] == 5.4
    assert len(out) == len(donki_flares)  # nothing silently dropped


def test_cme_prefers_most_accurate_analysis(donki_cmes):
    out = clean_cmes(donki_cmes)
    assert out.loc[0, "speedKmS"] == 1250.0  # not the 300 km/s non-accurate one
    assert out["speedKmS"].iloc[1:].isna().all()  # None / [] / null speed -> NaN, no crash


def test_cme_without_accuracy_flag_uses_first_analysis():
    df = pd.DataFrame({"startTime": ["t"], "cmeAnalyses": [[{"speed": 620.0}, {"speed": 900.0}]]})
    assert clean_cmes(df).loc[0, "speedKmS"] == 620.0


def test_storm_max_kp(donki_storms):
    out = clean_storms(donki_storms)
    assert out.loc[0, "maxKpIndex"] == 6.67
    assert out["maxKpIndex"].iloc[1:].isna().all()


def test_empty_frames_pass_through():
    for fn in (clean_flares, clean_cmes, clean_storms):
        assert fn(pd.DataFrame()).empty


def test_missing_columns_do_not_crash():
    assert "flareClassLetter" in clean_flares(pd.DataFrame({"foo": [1]})).columns
