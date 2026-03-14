# Employee Agent POC - Setup Guide

## What this does

Reads employee Excel data → applies the business logic → AI phone call + voice transcription + email → writes results back into the same Excel file.

```
Read Excel → Born after 01-01-2000?
                ├─ No  → Skip (Read Next Rec)
                └─ Yes → Terminated?
                            ├─ No  → Skip (Read Next Rec)
                            └─ Yes → Term Date > 01-01-2023?
                                        ├─ No  → STATUS = DisQualified (no call, no email)
                                        └─ Yes → AI Call (record + transcribe)
                                                 + AI Email "Hi"
                                                 → Save to same Excel
```

**New columns added to input Excel:**
| Column | Description |
|---|---|
| `STATUS` | `DisQualified` if terminated before 2023 |
| `EMAIL_SENT` | `Yes` / `No` |
| `EMAIL_TEXT` | Full body of email sent |
| `PHONE_CALL_STATUS` | `Completed` / `No Answer` |
| `PHONE_CONVERSATION` | Voice-to-text transcript of call |

---

## Step 1 — Install Python dependencies

```bash
pip install twilio groq pandas openpyxl requests
```

> `smtplib` is built into Python — no install needed for email.

---

## Step 2 — Twilio (Phone Calls)

**Sign up:**
1. Go to https://www.twilio.com/try-twilio → sign up free
2. Trial account gives **$15 free credit** (enough for many test calls)

**Get your credentials:**
1. After login → https://console.twilio.com
2. On the dashboard copy:
   - `Account SID` (starts with `AC...`)
   - `Auth Token`
3. Click **"Get a phone number"** → copy your Twilio number (e.g. `+1XXXXXXXXXX`)

**Verify your Indian test number (required for trial accounts):**
1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/verified
2. Click **"Add a new Caller ID"**
3. Enter `+919176960154` → verify via OTP call or SMS

> ⚠️ Twilio trial plays *"This call is from a Twilio trial account, press any key to continue"* before your prompt. This is expected — just wait and press any key when you pick up.

---

## Step 3 — Groq (Voice Transcription)

Groq runs OpenAI's Whisper model — **completely free**, no billing needed, highly accurate for Indian English.

**Sign up:**
1. Go to https://console.groq.com → sign up free
2. Click **"API Keys"** → **"Create API Key"**
3. Copy the key (starts with `gsk_...`)

---

## Step 4 — Gmail App Password (Email)

No new account needed — uses your existing Gmail.

1. Go to https://myaccount.google.com/security
2. Make sure **2-Step Verification is ON**
3. Search **"App Passwords"** at the top → click it
4. Click **"Create"** → name it `POC` → copy the 16-character password
   - Looks like: `abcd efgh ijkl mnop` (spaces are fine, they're ignored)

> ⚠️ Use this App Password — NOT your regular Gmail login password.
> The code auto-tries port 587 first, then falls back to port 465 if your network blocks 587.

---

## Step 5 — Set environment variables

**Mac/Linux:**
```bash
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="your_auth_token_here"
export TWILIO_FROM_NUMBER="+1XXXXXXXXXX"

export GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxx"

export GMAIL_ADDRESS="lakshmideepakb@gmail.com"
export GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"
```

**Windows (PowerShell):**
```powershell
$env:TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
$env:TWILIO_AUTH_TOKEN="your_auth_token_here"
$env:TWILIO_FROM_NUMBER="+1XXXXXXXXXX"

$env:GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxx"

$env:GMAIL_ADDRESS="lakshmideepakb@gmail.com"
$env:GMAIL_APP_PASSWORD="abcd efgh ijkl mnop"
```

---

## Step 6 — Place files in the same folder

```
your-folder/
├── poc_agent.py
└── sample_data.xlsx
```

---

## Step 7 — Test each piece individually first

```bash
# Test email only
python poc_agent.py --test-email

# Test call only
python poc_agent.py --test-call
```

**What to expect on --test-call:**
1. Your phone (`+919176960154`) will ring
2. Pick up → hear Twilio trial disclaimer → press any key
3. Wait 2 seconds → hear the HR prompt
4. Hear a beep → speak your response
5. 5 seconds of silence ends the recording
6. Transcript appears in terminal

---

## Step 8 — Run the full flow

```bash
python poc_agent.py
```

**Expected terminal output:**
```
Reading Excel file...
  Loaded 20 records

  ✅ Dale Fowler → DisQualified (terminated before 2023)

  ✅ Frank Fuhlroth → Terminated after 2023, initiating call + email
     Trying port 587 STARTTLS...
     ✅ Email sent successfully
     📞 Calling Frank Fuhlroth at +919176960154...
     Call status: completed
     Recording downloaded (49 KB)
     Sending to Groq Whisper for transcription...
     ✅ Groq Whisper transcript: I am available next week...

  ✅ Ken Chambers → Terminated after 2023, initiating call + email
     ...

==================================================
✅ Done! Results written to: sample_data.xlsx
   DisQualified : 1
   Emails sent  : 2
   Calls done   : 2
   No Answer    : 0
==================================================
```

---

## Switching test → production

In `poc_agent.py`, swap these 2 lines inside `process_records()`:

```python
# Currently (test mode)
call_result  = make_call_and_transcribe(TEST_PHONE, name)
email_result = send_email(TEST_EMAIL, name)

# Production mode — use actual data from Excel
call_result  = make_call_and_transcribe(row["WORK_PHONE"], name)
email_result = send_email(row["EMAIL"], name)
```

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `SMTP error 10060` | Port 587 blocked by network | Code auto-retries on port 465 |
| `SMTPAuthenticationError` | Wrong app password | Regenerate at myaccount.google.com/apppasswords |
| `Groq 503` | Groq temporarily overloaded | Code auto-retries 3 times with 10s/20s wait |
| `Twilio no-answer` | Call not picked up | `PHONE_CALL_STATUS` = No Answer in Excel |
| `Recording not found` | Spoke too quietly / too short | Speak clearly for at least 3 seconds after beep |
| `Twilio auth error` | Wrong SID or token | Double check console.twilio.com credentials |

---

## Interview talking points

- **Twilio TwiML**: XML instruction set telling Twilio what to do during the call — `<Say>`, `<Record>`, `<Pause>`
- **finishOnKey=""**: Prevents any keypress from ending the recording (fixes free trial disclaimer issue)
- **Groq Whisper**: Runs `whisper-large-v3` — same model as OpenAI but free; downloads Twilio MP3 and transcribes it
- **Gmail SMTP**: Python built-in `smtplib`, auto-fallback from port 587 → 465 if network blocks it
- **openpyxl append-only**: Opens original file and only writes new columns — zero impact on existing data, formats, or NULLs
- **Retry logic**: Both Groq (503) and SMTP (port fallback) handle transient failures gracefully
- **Test mode**: Single variable swap `TEST_PHONE` / `TEST_EMAIL` → `row["WORK_PHONE"]` / `row["EMAIL"]` to go live