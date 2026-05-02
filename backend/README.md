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
