"""Make real phone calls that speak a message, using Twilio Programmable Voice.

How it works: we ask Twilio's API to call a phone number and pass the spoken
message as *inline TwiML* (the ``twiml=`` parameter). Twilio reads the
``<Say>`` verb out loud when the call is answered. No webhook server needed.
"""

import os
from xml.sax.saxutils import escape

from twilio.rest import Client


def _attr(name, value):
    """Build an XML attribute like ' voice="..."', safely escaped."""
    if not value:
        return ""
    quote_escaped = escape(value, {'"': "&quot;"})
    return " " + name + '="' + quote_escaped + '"'


class TwilioConfigError(Exception):
    """Raised when required Twilio settings are missing from the environment."""


# Environment variable names. Never hardcode credentials in code.
ENV_ACCOUNT_SID = "TWILIO_ACCOUNT_SID"
ENV_AUTH_TOKEN = "TWILIO_AUTH_TOKEN"
ENV_FROM_NUMBER = "TWILIO_PHONE_NUMBER"     # your Twilio number (caller)
ENV_DEFAULT_TO = "ALERT_PHONE_NUMBER"       # who to call if --to is not given


class TwilioCallClient:
    """Thin wrapper around Twilio's API for 'say this message' phone calls."""

    def __init__(self, dry_run=False):
        """Read config from the environment.

        In dry-run mode no credentials are needed and no API calls are made,
        so you can test the whole flow for free.
        """
        self.dry_run = dry_run
        if dry_run:
            self.account_sid = self.auth_token = None
            self.from_number = self.default_to = None
            self._client = None
            return

        self.account_sid = os.environ.get(ENV_ACCOUNT_SID)
        self.auth_token = os.environ.get(ENV_AUTH_TOKEN)
        self.from_number = os.environ.get(ENV_FROM_NUMBER)
        self.default_to = os.environ.get(ENV_DEFAULT_TO)

        missing = [name for name, value in (
            (ENV_ACCOUNT_SID, self.account_sid),
            (ENV_AUTH_TOKEN, self.auth_token),
            (ENV_FROM_NUMBER, self.from_number),
            (ENV_DEFAULT_TO, self.default_to),
        ) if not value]
        if missing:
            raise TwilioConfigError(
                "Missing required setting(s): " + ", ".join(missing) + ". "
                "Copy .env.example to .env and fill in your Twilio credentials."
            )

        self._client = Client(self.account_sid, self.auth_token)

    def build_twiml(self, message, voice=None, language=None):
        """Build the TwiML document Twilio will speak on the call."""
        if not message or not message.strip():
            raise ValueError("message must not be empty")
        # Escape XML so characters like <, >, & in the message don't break TwiML.
        safe_message = escape(message.strip())
        return (f"<Response><Say{_attr('voice', voice)}{_attr('language', language)}>"
                f"{safe_message}</Say></Response>")

    def make_call(self, message, to=None, voice=None, language=None):
        """Call `to` (or ALERT_PHONE_NUMBER) and speak `message`.

        Returns the Twilio call SID. In dry-run mode nothing is sent;
        it just prints what *would* happen and returns "DRY-RUN".
        """
        to = to or self.default_to
        if not to:
            raise ValueError("no destination number: pass --to or set ALERT_PHONE_NUMBER")
        if not to.startswith("+"):
            raise ValueError(
                f"phone number {to!r} must be in E.164 format, e.g. +918081315140"
            )

        twiml = self.build_twiml(message, voice=voice, language=language)

        if self.dry_run:
            print("[dry-run] Would call:", to)
            print("[dry-run] Would say :", message.strip())
            print("[dry-run] TwiML     :", twiml)
            print("[dry-run] Zero API calls made.")
            return "DRY-RUN"

        call = self._client.calls.create(to=to, from_=self.from_number, twiml=twiml)
        return call.sid
