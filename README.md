# Employee Agent POC

An AI-powered HR automation agent that reads employee data from Excel, applies business rules via a **LangGraph state machine**, makes outbound phone calls with **Twilio**, transcribes responses using **Groq Whisper**, and sends follow-up emails via **Gmail SMTP** — writing all results back into the same Excel file.

---

## Architecture

```
Excel Input
    │
    ▼
┌─────────────┐     born ≤ 2000
│ filter_node │ ──────────────────────────────► END (skip)
│  rule-based │     not terminated
└──────┬──────┘
       │ eligible
       ▼
┌─────────────┐     term date ≤ 2023
│ router_node │ ──────────────────────► disqualify_node ──► save_node
│  rule-based │                         STATUS = DQ
└──────┬──────┘
       │ term date > 2023
       ▼
┌──────────────┐
│ contact_node │──► make_call_tool  (Twilio call + Groq Whisper STT)
│ LangChain    │──► send_email_tool (Gmail SMTP)
└──────┬───────┘
       │
       ▼
  save_node ──► Write results to Excel ──► END
```

### Tech stack

| Component | Purpose |
|---|---|
| **LangGraph** | State machine — routes each employee through graph nodes |
| **LangChain `@tool`** | Wraps Twilio and Gmail as discoverable, typed tool functions |
| **Twilio** | Places outbound phone calls, records spoken response |
| **Groq Whisper (`whisper-large-v3`)** | Transcribes recorded call audio to text (free) |
| **Gmail SMTP** | Sends personalised follow-up emails |
| **pandas** | Reads Excel data into a DataFrame |
| **openpyxl** | Appends result columns back to Excel without touching original data |

---

## Graph Nodes

| Node | Type | What it does |
|---|---|---|
| `filter_node` | Rule-based | Skips records born before 2000 or not terminated |
| `router_node` | Rule-based | Routes to `contact` if term date > 2023, else `disqualify` |
| `contact_node` | Action | Calls `make_call_tool` then `send_email_tool` exactly once each |
| `disqualify_node` | Action | Sets `STATUS = DisQualified`, no call/email |
| `save_node` | Terminal | Marks record ready, triggers Excel write |

---

## Output Columns Added to Excel

| Column | Value |
|---|---|
| `STATUS` | `DisQualified` or `Contacted` |
| `EMAIL_SENT` | `Yes` / `No` |
| `EMAIL_TEXT` | Full body of email sent |
| `PHONE_CALL_STATUS` | `Completed` / `No Answer` / `Busy` / `Failed` |
| `PHONE_CONVERSATION` | Voice-to-text transcript of call response |

> Original data, formats, and NULL values are never modified — only new columns are appended.

---

## Prerequisites

- Python 3.9+
- A [Twilio](https://twilio.com) account (trial works, $15 free credit)
- A [Groq](https://console.groq.com) account (completely free)
- A Gmail account with an App Password

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install langchain langgraph langchain-core twilio groq pandas openpyxl requests
```

---

## Configuration

Fill in `config.py` with your credentials (never commit this file):

```python
# Twilio
TWILIO_ACCOUNT_SID  = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN   = "your_auth_token"
TWILIO_FROM_NUMBER  = "+1XXXXXXXXXX"

# Gmail
GMAIL_ADDRESS       = "your-email@gmail.com"
GMAIL_APP_PASSWORD  = "xxxx xxxx xxxx xxxx"   # 16-char App Password

# Groq
GROQ_API_KEY        = "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxx"
```

Or set as environment variables:

**Windows (PowerShell):**
```powershell
$env:TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
$env:TWILIO_AUTH_TOKEN="your_auth_token"
$env:TWILIO_FROM_NUMBER="+1XXXXXXXXXX"
$env:GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxx"
$env:GMAIL_ADDRESS="your-email@gmail.com"
$env:GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

**Mac/Linux:**
```bash
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_FROM_NUMBER="+1XXXXXXXXXX"
export GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxxxxxxxxxxxx"
export GMAIL_ADDRESS="your-email@gmail.com"
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

### Getting credentials

**Twilio:**
1. Sign up at https://www.twilio.com/try-twilio
2. Console → Account Info → copy `Account SID` and `Auth Token`
3. Get a phone number → Console → Phone Numbers
4. For trial accounts: verify your test number at Console → Verified Caller IDs

**Groq:**
1. Sign up at https://console.groq.com
2. API Keys → Create API Key → copy key

**Gmail App Password:**
1. https://myaccount.google.com/security → enable 2-Step Verification
2. Search "App Passwords" → Create → copy the 16-character password

---

## Usage

```bash
# Run full flow
python main.py

# Test email only
python main.py --test-email

# Test call only
python main.py --test-call
```

### Expected output

```
Reading Excel file...
  Loaded 20 records

  -- Gunter Erler        | born before 2000, skip
  -- Maria Iacobucci     | born before 2000, skip
  DQ Dale Fowler         | terminated before 2023 → disqualify
  >> Frank Fuhlroth      | terminated after 2023 → calling + emailing

  >> Contacting Frank Fuhlroth
     [make_call_tool] Calling Frank Fuhlroth at +1...
     Call status: ringing
     Call status: completed
     Transcript: I am available next week for a discussion.
     [send_email_tool] Emailing Frank Fuhlroth at FFuhlroth@...
     Email sent via port 587

==================================================
Done! Output: sample_data.xlsx
  DisQualified : 1
  Emails sent  : 2
  Calls done   : 2
  No Answer    : 0
==================================================
```

---

## Project Structure

```
your-folder/
├── main.py              # Agent logic — LangGraph graph + LangChain tools
├── config.py            # Credentials and settings (add to .gitignore)
├── sample_data.xlsx     # Input Excel file
├── architecture.drawio  # Draw.io architecture diagram
└── README.md
```

---

## .gitignore

```
config.py
venv/
*.xlsx
tmp_recording.mp3
__pycache__/
```

---

## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `model_decommissioned` | Groq model removed | Update `LLM_MODEL` in `config.py` to `llama-3.3-70b-versatile` |
| `SMTP error 10060` | Port 587 blocked | Code auto-retries on port 465 |
| `SMTPAuthenticationError` | Wrong App Password | Regenerate at myaccount.google.com/apppasswords |
| `Groq 503` | Temporary overload | Code auto-retries 3 times with backoff |
| `Twilio no-answer` | Call not picked up | `PHONE_CALL_STATUS = No Answer` written to Excel |
| `ModuleNotFoundError: twilio...` | Corrupted install | `pip uninstall twilio -y && pip install twilio>=9.0.0` |
| `Recording too short` | No speech detected | `PHONE_CONVERSATION = No response spoken` |

---

## Notes

**Why LangGraph?**
The flowchart maps directly to a state machine — each decision diamond is a conditional edge, each action is a node. Adding a new step (e.g. SMS notification) is just a new node and edge without touching existing logic.

**Why not LLM for routing?**
Birth date, termination status, and term date are hard deterministic rules — no judgment needed. Using an LLM agent (`create_agent`) here caused a ReAct loop that called tools multiple times per person. Rule-based routing is faster, cheaper, and more reliable.

**Why LangChain `@tool`?**
The `@tool` decorator adds a typed schema and docstring to each function, making it discoverable by any LLM agent. If requirements change and an LLM needs to decide which tools to call, the tools are already properly registered.

**Switching test → production:**
In `contact_node`, replace `state["phone"]` / `state["email"]` — they already use the real Excel data.
