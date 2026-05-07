# Smart Banking Assistant - Backend API

An AI-powered banking chatbot backend built with **FastAPI**, **NLTK**, **TensorFlow/Keras**, and **MySQL**.

## ðŸš€ Quick Start

### Prerequisites

- Python 3.10 or higher
- MySQL 8.0 or higher
- pip package manager

### ðŸƒ Fast Setup (Windows)

```bat
# 1. Run the automated setup script
setup.bat

# 2. Apply database migrations
python migrate.py up

# 3. Configure credentials â€” copy .env.example to .env and fill in your values
copy .env.example .env

# 4. Train the AI model (required once before first run)
.\venv\Scripts\activate
python train_model.py

# 5. Start the server
uvicorn main:app --reload
```

### ðŸƒ Fast Setup (Linux/Mac)

```bash
# 1. Run the automated setup script
chmod +x setup.sh
./setup.sh

# 2. Apply database migrations
python migrate.py up

# 3. Configure credentials
cp .env.example .env

# 4. Train the AI model
source venv/bin/activate
python train_model.py

# 5. Start the server
uvicorn main:app --reload
```

**ðŸŽ‰ Server running at:** http://localhost:8000  
**ðŸ“š API Docs:** http://localhost:8000/docs

---

## ðŸ“‹ Features

- **AI Intent Classification**: TensorFlow/Keras ANN trained on 22 banking intents
- **Hybrid NLP**: ANN primary path (threshold 0.40) + NLTK keyword fallback
- **English-Only Guard**: Non-English messages (Sinhala, Arabic, Chinese, French, etc.) are politely declined using Unicode range detection + `langdetect`
- **OTP Account Verification**: 3-factor identity check (email + National ID + account number) before exposing personal data
- **Smart Routing**: Personal-data intents (balance, transactions, FD, pawning) require verified account; general info queries do not
- **Context-Aware Follow-ups**: Remembers previous intent to answer follow-up questions intelligently
- **Emoji-Rich Responses**: All replies include relevant emojis for a friendly UX
- **Self-Learning**: Unrecognised questions saved to DB for model improvement
- **Chat Log Persistence**: Every request and response logged to MySQL
- **RESTful API**: Clean FastAPI endpoints with auto-generated Swagger/ReDoc docs
- **CORS Support**: Ready for any frontend framework

---

## ðŸ› ï¸ Detailed Installation

### 1. Clone and Navigate to Project

```bash
cd backend
```

### 2. Create Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python migrate.py up
```

This auto-creates the `banking_chatbot` database and applies all 4 versioned migrations.

### 5. Configure Environment

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` with your credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=banking_chatbot
DB_PORT=3306
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_APP_PASSWORD=your_app_password
```

### 6. Train the AI Model

```bash
python train_model.py
```

Generates `models/chatbot_model.keras`, `models/words.pkl`, and `models/classes.pkl`.  
Re-run whenever `intents/intents.json` is updated.

---

## ðŸš€ Starting the Application

```bash
uvicorn main:app --reload
```

| URL                         | Purpose      |
| --------------------------- | ------------ |
| http://localhost:8000/      | Health check |
| http://localhost:8000/docs  | Swagger UI   |
| http://localhost:8000/redoc | ReDoc        |

---

## ðŸ§ª Testing the API

### Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Click **POST /api/chat** â†’ Try it out â†’ Execute

### Test Script

```bash
python test_chatbot.py
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello"}'
```

---

## ðŸ“¡ API Endpoints

### Chat

```http
POST /api/chat
```

Request:

```json
{
  "message": "What is my account balance?",
  "user_id": 1,
  "account_number": "ACC001",
  "last_intent": "BALANCE"
}
```

Response:

```json
{
  "reply": "ðŸ’° Your current account balance is **$5,250.00**. Is there anything else I can help you with?",
  "intent": "BALANCE",
  "confidence": 0.97,
  "data": { "balance": 5250.0 }
}
```

### Account Verification

```http
POST /api/account/send-otp
POST /api/account/verify-otp
```

Sends a 6-digit OTP to the user's registered email. On success, returns `user_id` and `account_number` for use in subsequent chat requests.

### Health Check

```http
GET /
GET /health
```

---

## ðŸ§  Supported Intents (22)

| Intent               | Description                         | Example Queries                       |
| -------------------- | ----------------------------------- | ------------------------------------- |
| `GREETING`           | Conversational greeting             | "Hello", "Good morning"               |
| `GOODBYE`            | Farewell / thank-you                | "Bye", "Thank you for your support"   |
| `BALANCE`            | Account balance (requires auth)     | "What is my balance?"                 |
| `TRANSACTIONS`       | Recent transactions (requires auth) | "Show my transactions"                |
| `LOAN`               | Loan types, rates, requirements     | "I need a loan", "Loan interest rate" |
| `ACCOUNT_SERVICES`   | Account opening/closing/updating    | "How do I open an account?"           |
| `SECURITY`           | Passwords, lost cards, fraud        | "I forgot my password"                |
| `TRANSFERS`          | Transfers and bill payments         | "How do I transfer money?"            |
| `FEES`               | Fees, limits, ATM info              | "What are the ATM limits?"            |
| `DIGITAL_BANKING`    | Mobile app, online banking          | "How do I download the app?"          |
| `GENERAL`            | Hours, branches, contact info       | "What are your working hours?"        |
| `FIXED_DEPOSIT`      | FD rates and personal FDs           | "What are your FD rates?"             |
| `PAWNING`            | Pawning service and tickets         | "Tell me about pawning"               |
| `FOREIGN_EXCHANGE`   | Currency rates and exchange         | "What is the USD rate?"               |
| `CARDS`              | Credit/debit card queries           | "How do I block my card?"             |
| `INVESTMENTS`        | Investment products                 | "Tell me about unit trusts"           |
| `CREDIT_SCORE`       | Credit score guidance               | "How can I improve my credit score?"  |
| `COMPLAINTS`         | Complaint submission                | "I want to file a complaint"          |
| `FORGOT_EMAIL`       | Forgotten or change email           | "I cannot remember my email"          |
| `PROFANITY_RESPONSE` | Angry/rude messages                 | De-escalation with empathy            |
| `CAPABILITIES`       | What can the chatbot do             | "What can you help me with?"          |
| `UNKNOWN`            | Unrecognised queries (saved to DB)  | Anything else                         |

---

## ðŸ” How It Works

1. **Language Guard** â€” Non-English input is detected (Unicode ranges + `langdetect`) and politely declined
2. **Action Detection** â€” Explicit action requests ("I want to open an account") are routed before NLP
3. **Intent Detection** â€” Lancaster-stemmed bag-of-words fed into TensorFlow ANN; keyword fallback if confidence < 0.40
4. **Auth Guard** â€” Personal data intents require verified `account_number`
5. **Handler** â€” Appropriate handler called; sub-topic routing for detailed responses
6. **DB Query** â€” Real data fetched from MySQL where needed
7. **Logging** â€” Every interaction saved to `chat_logs`

---

## 🤖 PEAS Model

The Smart Banking Assistant is designed as a **goal-based intelligent agent**. The PEAS framework describes its structure:

| Component | Element             | Description                                                    |
| --------- | ------------------- | -------------------------------------------------------------- |
| **P**     | Performance Measure | Intent accuracy, resolved queries, low UNKNOWN rate            |
| **E**     | Environment         | User messages, MySQL database, email service, REST API         |
| **A**     | Actuators           | Text replies, DB queries, OTP emails, chat log writes          |
| **S**     | Sensors             | User message, user ID, account number, last intent, DB results |

---

### P — Performance Measure

The agent's success is measured by:

| Metric                | How it is captured                                                  |
| --------------------- | ------------------------------------------------------------------- |
| **Intent confidence** | ANN returns a float (0–1); threshold is `0.40`                      |
| **Unknown rate**      | Every unrecognised query is saved to `unknown_questions` table      |
| **Query resolution**  | Responses return `"intent"` + `"confidence"` for logging/monitoring |
| **Auth success**      | OTP 3-factor verification pass/fail is logged                       |

```python
# nlp.py — ANN confidence threshold
CONFIDENCE_THRESHOLD = 0.40
if confidence < CONFIDENCE_THRESHOLD:
    return "UNKNOWN", confidence   # low-confidence → saved to DB for retraining

# services/chat_service.py — response always includes performance metadata
return {
    "reply": "...",
    "intent": "BALANCE",
    "confidence": 0.97,   # Performance metric
}
```

---

### E — Environment

The agent operates in a **partially observable, sequential, static, discrete, single-agent** environment:

| Property      | Value      | Reason                                                                         |
| ------------- | ---------- | ------------------------------------------------------------------------------ |
| Observable    | Partial    | Agent sees only the current message and last intent; not the user's full state |
| Deterministic | Stochastic | Any free-text input is possible                                                |
| Episodic      | Sequential | `last_intent` carries context from the previous turn                           |
| Dynamic       | Static     | Banking data in MySQL changes only by external transactions                    |
| Continuous    | Discrete   | Messages are discrete text inputs                                              |

```
User Browser / Postman
        │  HTTP POST /api/chat
        ▼
   FastAPI (main.py)
        │
        ├── routes/chat.py           ← request parsing & routing
        ├── services/chat_service.py ← agent brain
        │       ├── Language Guard   ← environment filter
        │       ├── NLP (nlp.py)     ← perception
        │       └── Intent Handlers  ← action
        ├── db.py                    ← environment state (MySQL)
        └── services/email_service.py← environment effector (SMTP)
```

---

### A — Actuators

The agent influences the environment through these actuators:

| Actuator           | Code Location                                                                                                     | What it Does                                             |
| ------------------ | ----------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Text reply**     | All `handle_*_intent()` in `chat_service.py`                                                                      | Returns natural-language response to the user            |
| **Database read**  | `db.py` → `get_account_balance()`, `get_recent_transactions()`, `get_user_fixed_deposits()`, `get_user_pawning()` | Retrieves personal account data                          |
| **Database write** | `db.py` → `save_chat_log()`, `save_unknown_question()`                                                            | Persists chat history and unknown queries for retraining |
| **OTP email send** | `services/email_service.py`                                                                                       | Sends 6-digit OTP for 3-factor identity verification     |
| **Intent router**  | `process_chat_message()` in `chat_service.py`                                                                     | Dispatches to the correct intent handler                 |

```python
# Actuator 1 — text reply (every intent handler)
return {
    "reply": "💰 Your current account balance is **$5,250.00**.",
    "intent": "BALANCE",
    "confidence": 0.97,
    "data": {"balance": 5250.0}
}

# Actuator 2 — database write (chat_service.py)
save_chat_log(user_id, message, response["reply"], response["intent"])
save_unknown_question(user_message)   # feeds back into retraining loop

# Actuator 3 — OTP email (email_service.py via account route)
send_otp_email(user_email, otp_code)
```

---

### S — Sensors

The agent perceives its environment through these inputs:

| Sensor                | Source                                                  | Used For                                           |
| --------------------- | ------------------------------------------------------- | -------------------------------------------------- |
| **`message`**         | HTTP request body                                       | Primary NLP input — tokenised, stemmed, vectorised |
| **`user_id`**         | Resolved from verified `account_number`                 | Fetching personal DB records                       |
| **`account_number`**  | HTTP request body (set after OTP verification)          | Auth guard for personal-data intents               |
| **`last_intent`**     | HTTP request body (sent by frontend from previous turn) | Context-aware follow-up handling                   |
| **Language detector** | Unicode range check + `langdetect` confidence > 0.90    | Reject non-English input before NLP                |
| **DB query results**  | MySQL via `db.py`                                       | Balance, transactions, FD, pawn ticket data        |

```python
# services/chat_service.py — all sensors arrive as function parameters
def process_chat_message(
    message: str,            # Sensor: raw user text
    user_id: int = 1,        # Sensor: resolved identity
    last_intent: str = None, # Sensor: conversational context (previous turn)
    account_number: str = None,  # Sensor: verified account (auth gate)
) -> Dict[str, Any]:

    # Sensor: language detection (Unicode + langdetect)
    if _has_non_latin(message):
        return UNSUPPORTED_LANGUAGE_RESPONSE

    # Sensor: NLP intent perception (ANN bag-of-words)
    intent, confidence = detect_intent(message)

    # Sensor: database state read
    balance = get_account_balance(user_id)
```

---

### Full PEAS Agent Loop

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENVIRONMENT                              │
│                                                                 │
│  User ──► HTTP POST /api/chat ──► FastAPI ──► chat_service.py  │
│                                                       │         │
│  SENSORS ◄──────────────────────────────────────────  │         │
│  • message (text)                                     │         │
│  • user_id / account_number                          │         │
│  • last_intent (context)                             │         │
│  • DB state (MySQL balance, FD, pawn tickets)        │         │
│                                                       ▼         │
│                    AGENT BRAIN                                  │
│  Step 1 — Language Guard   (filter non-English)                │
│  Step 2 — Action Detector  (explicit action requests)          │
│  Step 3 — NLP / ANN        (intent + confidence score)         │
│  Step 4 — Auth Guard       (account_number required?)          │
│  Step 5 — Intent Handler   (sub-topic routing)                 │
│  Step 6 — DB Query         (live banking data if needed)       │
│                                                       │         │
│  ACTUATORS ───────────────────────────────────────── ▼         │
│  • JSON reply       ──► User                                   │
│  • save_chat_log()  ──► MySQL  (audit trail)                   │
│  • save_unknown_question() ──► MySQL  (retraining data)        │
│  • send_otp_email() ──► SMTP                                   │
│                                                                 │
│  PERFORMANCE: intent confidence · UNKNOWN rate · auth success  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ðŸ—ƒï¸ Database Tables

| Table               | Description                                |
| ------------------- | ------------------------------------------ |
| `users`             | User accounts (includes `id_number`)       |
| `accounts`          | Bank accounts and balances                 |
| `transactions`      | Transaction history                        |
| `chat_logs`         | Every chatbot interaction (audit log)      |
| `unknown_questions` | Unrecognised queries for model improvement |
| `verified_users`    | OTP verification records                   |
| `loans`             | Customer loan records                      |
| `loan_repayments`   | Loan repayment schedules                   |
| `fixed_deposits`    | Fixed deposit records                      |
| `pawning`           | Pawning ticket records                     |

---

## ðŸ”§ Troubleshooting

### Virtual environment not activating (Windows)

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### MySQL connection errors

- Verify MySQL is running: `mysql -u root -p`
- Check credentials in `.env`
- Ensure the database exists: run `python migrate.py up`

### Model files not found / wrong responses

```bash
python train_model.py
```

### Port already in use

```bash
uvicorn main:app --reload --port 8001
```

### Module not found

```bash
pip install -r requirements.txt
```

---

## ðŸ“š Additional Documentation

| File                                         | Contents                                     |
| -------------------------------------------- | -------------------------------------------- |
| [QUICKSTART.md](QUICKSTART.md)               | 5-minute setup guide                         |
| [API_EXAMPLES.md](API_EXAMPLES.md)           | API usage examples and sample responses      |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Architecture, module descriptions, DB schema |

---

## ðŸ”’ Security Notes

1. All SQL queries use parameterised statements (injection-safe)
2. OTP is 6-digit, 5-minute TTL, stored server-side only
3. Personal data gated behind 3-factor OTP verification
4. Secrets loaded from `.env` only â€” never hardcoded
5. Pydantic validates all incoming request data
6. For production: enable HTTPS, rate limiting, and restrict CORS origins
