"""Tests for jarvis.caller. The Twilio API is never touched (all mocked)."""

import os
from unittest import mock

import pytest

from jarvis.caller import TwilioCallClient, TwilioConfigError

# Fake (but correctly shaped) credentials - never real secrets in tests.
FAKE_ENV = {
    "TWILIO_ACCOUNT_SID": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "TWILIO_AUTH_TOKEN": "fake_token_for_tests",
    "TWILIO_PHONE_NUMBER": "+15017122661",
    "ALERT_PHONE_NUMBER": "+918081315140",
}

ENV_KEYS = list(FAKE_ENV)


def _patched_env(extra=None):
    """os.environ with only our fake Twilio vars (plus optional extras)."""
    env = {k: v for k, v in os.environ.items() if k not in ENV_KEYS}
    env.update(FAKE_ENV)
    if extra:
        env.update(extra)
    return mock.patch.dict(os.environ, env, clear=True)


def test_make_call_passes_right_to_from_and_twiml():
    with _patched_env(), mock.patch("jarvis.caller.Client") as MockClient:
        client = TwilioCallClient()
        sid = client.make_call("Server is down!", to="+911234567890")

    MockClient.assert_called_once_with(
        FAKE_ENV["TWILIO_ACCOUNT_SID"], FAKE_ENV["TWILIO_AUTH_TOKEN"]
    )
    create = MockClient.return_value.calls.create
    create.assert_called_once()
    kwargs = create.call_args.kwargs
    assert kwargs["to"] == "+911234567890"
    assert kwargs["from_"] == FAKE_ENV["TWILIO_PHONE_NUMBER"]
    assert kwargs["twiml"] == "<Response><Say>Server is down!</Say></Response>"
    assert sid == MockClient.return_value.calls.create.return_value.sid


def test_make_call_uses_default_number_when_to_not_given():
    with _patched_env(), mock.patch("jarvis.caller.Client") as MockClient:
        client = TwilioCallClient()
        client.make_call("hello")

    kwargs = MockClient.return_value.calls.create.call_args.kwargs
    assert kwargs["to"] == FAKE_ENV["ALERT_PHONE_NUMBER"]


def test_missing_env_vars_raise_clear_error():
    with mock.patch.dict(os.environ, {}, clear=True):
        with pytest.raises(TwilioConfigError) as exc_info:
            TwilioCallClient()
    message = str(exc_info.value)
    for key in ENV_KEYS:
        assert key in message  # error names every missing variable


def test_dry_run_makes_zero_api_calls_and_needs_no_credentials():
    with mock.patch.dict(os.environ, {}, clear=True):
        with mock.patch("jarvis.caller.Client") as MockClient:
            client = TwilioCallClient(dry_run=True)
            sid = client.make_call("hello", to="+911234567890")
    MockClient.assert_not_called()  # the real API client is never even built
    assert sid == "DRY-RUN"


def test_build_twiml_escapes_xml_special_chars():
    with _patched_env(), mock.patch("jarvis.caller.Client"):
        client = TwilioCallClient()
    twiml = client.build_twiml('CPU > 90% & disk < 10GB "urgent"')
    assert twiml == ("<Response><Say>CPU &gt; 90% &amp; disk &lt; 10GB "
                     '"urgent"</Say></Response>')


def test_build_twiml_supports_hindi_voice():
    with _patched_env(), mock.patch("jarvis.caller.Client"):
        client = TwilioCallClient()
    twiml = client.build_twiml("Server down hai!", voice="Polly.Aditi",
                               language="hi-IN")
    assert twiml == ('<Response><Say voice="Polly.Aditi" language="hi-IN">'
                     'Server down hai!</Say></Response>')


def test_empty_message_raises():
    with _patched_env(), mock.patch("jarvis.caller.Client"):
        client = TwilioCallClient()
    with pytest.raises(ValueError):
        client.make_call("   ", to="+911234567890")


def test_non_e164_number_raises():
    with _patched_env(), mock.patch("jarvis.caller.Client"):
        client = TwilioCallClient()
    with pytest.raises(ValueError):
        client.make_call("hello", to="8081315140")  # missing leading +
