from unittest import mock

import pytest

from src.data import donki_client


def fake(text, status=200):
    r = mock.Mock(status_code=status, text=text, url="https://example/test")
    r.raise_for_status.return_value = None
    r.json.side_effect = lambda: __import__("json").loads(text)
    return r


def test_empty_body_means_no_events():
    with mock.patch("requests.get", return_value=fake("")):
        assert donki_client.get_geomagnetic_storms("2026-09-26", "2026-10-03").empty


def test_empty_list_means_no_events():
    with mock.patch("requests.get", return_value=fake("[]")):
        assert donki_client.get_solar_flares("a", "b").empty


def test_valid_json_parses():
    with mock.patch("requests.get", return_value=fake('[{"classType": "M1.0"}]')):
        assert len(donki_client.get_solar_flares("a", "b")) == 1


def test_html_error_page_raises_clear_error():
    with mock.patch("requests.get", return_value=fake("<html>Rate limited</html>")):
        with pytest.raises(RuntimeError, match="non-JSON"):
            donki_client.get_cme_events("a", "b")


def test_uses_new_ccmc_base_url_without_api_key():
    with mock.patch("requests.get", return_value=fake("[]")) as g:
        donki_client.get_solar_flares("2026-09-26", "2026-10-03")
    url = g.call_args.args[0]
    assert url == "https://ccmc.gsfc.nasa.gov/DONKI-API/get/FLR"
    assert "api_key" not in g.call_args.kwargs["params"]