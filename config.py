"""
config.py — All credentials and settings in one place.
"""

import os

# ── Twilio (phone calls) ──────────────────────────────────────────
TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID",  "AC79axxxxxx59228aa9")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN",    "fd943xxxxxxxxadsa0c6c306dc36")
TWILIO_FROM_NUMBER  = os.getenv("TWILIO_FROM_NUMBER",   "+191xxxxxxx")

# ── Gmail SMTP (email) ────────────────────────────────────────────
GMAIL_ADDRESS       = os.getenv("GMAIL_ADDRESS",        "xxxxxx@gmail.com")
GMAIL_APP_PASSWORD  = os.getenv("GMAIL_APP_PASSWORD",   "xxxx xxxx xxxx xxx")

# ── Groq (Whisper transcription + LLM) ───────────────────────────
GROQ_API_KEY        = os.getenv("GROQ_API_KEY")

# ── Business rules ────────────────────────────────────────────────
from datetime import datetime
BIRTH_CUTOFF        = datetime(2000, 1, 1)   # process only born after this date
TERM_DATE_CUTOFF    = datetime(2023, 1, 1)   # DQ if terminated before this date

# ── Files ─────────────────────────────────────────────────────────
INPUT_FILE          = "sample_data.xlsx"
OUTPUT_FILE         = "sample_data.xlsx"     # write results back to same file
