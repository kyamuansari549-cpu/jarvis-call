#!/usr/bin/env python3
"""Jarvis-call: ring your own phone and speak an alert message (via Twilio).

Examples:
    # Free dry run - prints what would happen, makes zero API calls:
    python main.py --message "Server is down!" --test-mode

    # Real call (needs .env with Twilio credentials):
    python main.py --message "Server is down!"

    # Call only if a website is down:
    python main.py --check-url https://example.com

    # Speak in Hindi:
    python main.py --message "Server down hai!" --voice Polly.Aditi --language hi-IN --test-mode
"""

import argparse
import os
import sys


def _load_dotenv(path=".env"):
    """Tiny .env loader (no extra dependency). Real env vars always win."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def main():
    parser = argparse.ArgumentParser(
        description="Jarvis-call: phone-call alerts that speak via Twilio."
    )
    parser.add_argument("--message", help="Message to speak on the call.")
    parser.add_argument("--to", help="Number to call in E.164 format "
                                     "(e.g. +918081315140). Defaults to ALERT_PHONE_NUMBER.")
    parser.add_argument("--check-url", help="Only call if this URL is down "
                                            "(speaks an automatic 'website is down' alert).")
    parser.add_argument("--voice", help='TwiML <Say> voice, e.g. "Polly.Aditi" for Hindi.')
    parser.add_argument("--language", help='TwiML <Say> language, e.g. "hi-IN".')
    parser.add_argument("--test-mode", action="store_true",
                        help="Dry run: print what would happen, make zero API calls.")
    args = parser.parse_args()

    _load_dotenv()  # lets you keep credentials in a .env file

    from jarvis import TwilioCallClient, alert_if_down

    client = TwilioCallClient(dry_run=args.test_mode)

    if args.check_url:
        sid = alert_if_down(args.check_url, client,
                            to=args.to, voice=args.voice, language=args.language)
    else:
        if not args.message:
            parser.error("--message is required (or use --check-url)")
        sid = client.make_call(args.message, to=args.to,
                               voice=args.voice, language=args.language)

    if sid:
        print(f"Call SID: {sid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
