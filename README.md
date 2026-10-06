# jarvis-call 📞

A tiny "Jarvis" that **calls your own phone and speaks an alert message**
when something goes wrong — built on Twilio Programmable Voice.

No webhook server needed: the spoken message is sent to Twilio as inline
TwiML (`<Say>`), so one Python call = one phone call that talks.

## How it works

1. You run `python main.py --message "..."`.
2. The script asks Twilio's API to call your number.
3. When you pick up, Twilio speaks your message out loud (text-to-speech).
4. `alert_if_down(url)` does the same automatically when a website is down.

## Setup (you do this once)

1. **Create a free Twilio trial account** at https://www.twilio.com/try-twilio
   (no credit card needed — you get ~$15 of free credit).
2. **Verify your mobile number** in the Twilio Console
   (Phone Numbers → Verified Caller IDs). Trial accounts can only call
   numbers you verify — for this project that's perfect, since you only
   ever call yourself.
3. **Get a Twilio phone number** in the Console (paid from your free
   credit, roughly $1–2/month). This is the number that "calls" you.
4. In the Console dashboard, copy your **Account SID** and **Auth Token**.
5. Copy `.env.example` to `.env` and fill it in:

```bash
cp .env.example .env
```

```ini
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx      # your Twilio number (calls come FROM this)
ALERT_PHONE_NUMBER=+91xxxxxxxxxx      # your mobile (calls go TO this)
```

Phone numbers must be in E.164 format: `+` followed by country code and
number, e.g. `+918081315140`.

## Usage

```bash
pip install -r requirements.txt

# 1. Free dry run - prints what WOULD happen, makes zero API calls:
python main.py --message "Server is down!" --test-mode

# 2. Real call (needs .env):
python main.py --message "Server is down!"

# 3. Call only if a website is down:
python main.py --check-url https://example.com

# 4. Speak in Hindi (test first with --test-mode):
python main.py --message "Server down hai!" --voice Polly.Aditi --language hi-IN
```

## Cost notes

- Free trial ≈ **$15 credit**, no credit card required.
- Calls to Indian mobiles cost roughly **$0.0135–$0.091 per minute**
  (billed per minute, so a 30-second alert costs 1 minute).
- A Twilio phone number costs ~$1–2/month, also from the credit.
- Roughly: a few hundred short alert calls fit in the free credit.
- Trial calls can only go to **verified numbers** (your own number —
  exactly what this project needs).

## Project layout

```
jarvis-call/
├── main.py            # CLI: --message / --check-url / --to / --test-mode
├── jarvis/
│   ├── caller.py      # TwilioCallClient - makes the speaking phone call
│   └── alerts.py      # check_website() + alert_if_down() example
└── tests/             # pytest suite (Twilio API is mocked - free to run)
```

## Running the tests

```bash
pytest -v
```

All tests mock the Twilio API, so running them costs nothing.

## Security

- Credentials live **only** in `.env`, which is git-ignored. Never commit it.
- Only `.env.example` (with empty values) is in the repo.
