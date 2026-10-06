"""Tests for jarvis.alerts. No real HTTP requests are made (all mocked)."""

from unittest import mock

from jarvis.alerts import check_website, alert_if_down


def _response(status):
    resp = mock.Mock()
    resp.status_code = status
    return resp


def test_check_website_true_when_up():
    with mock.patch("jarvis.alerts.requests.get", return_value=_response(200)):
        assert check_website("https://example.com") is True


def test_check_website_false_on_server_error():
    with mock.patch("jarvis.alerts.requests.get", return_value=_response(503)):
        assert check_website("https://example.com") is False


def test_check_website_false_on_connection_error():
    import requests
    with mock.patch("jarvis.alerts.requests.get",
                    side_effect=requests.ConnectionError("down")):
        assert check_website("https://example.com") is False


def test_alert_if_down_calls_when_down():
    client = mock.Mock()
    client.make_call.return_value = "CA123"
    with mock.patch("jarvis.alerts.check_website", return_value=False):
        sid = alert_if_down("https://example.com", client, to="+911234567890")
    assert sid == "CA123"
    client.make_call.assert_called_once()
    assert "down" in client.make_call.call_args.args[0].lower()


def test_alert_if_down_stays_silent_when_up():
    client = mock.Mock()
    with mock.patch("jarvis.alerts.check_website", return_value=True):
        assert alert_if_down("https://example.com", client) is None
    client.make_call.assert_not_called()
