"""Example alert: call your phone when a website goes down."""

import requests


def check_website(url, timeout=10):
    """Return True if the website answers with HTTP status < 400, else False."""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code < 400
    except requests.RequestException:
        return False


def alert_if_down(url, client, to=None, voice=None, language=None):
    """Ring `to` and speak an alert if `url` is down.

    Returns the Twilio call SID when a call was made, else None.
    """
    if check_website(url):
        print(f"[jarvis] {url} is UP - no call made.")
        return None
    message = f"Alert from Jarvis. The website {url} appears to be down."
    print(f"[jarvis] {url} is DOWN - calling now...")
    return client.make_call(message, to=to, voice=voice, language=language)
