# API Examples and Sample Responses

## Chat API Endpoint

**Endpoint:** `POST /api/chat`  
**Base URL:** `http://localhost:8000`

### Request Schema

```json
{
  "message": "string (required)",
  "user_id": "integer (optional — set after OTP verification)",
  "account_number": "string (optional — set after OTP verification)",
  "last_intent": "string (optional — used for follow-up context)"
}
```

### Response Schema

```json
{
  "reply": "string — emoji-rich response message",
  "intent": "string | null — detected intent tag",
  "confidence": "float | null — ANN confidence (0.0–1.0)",
  "data": "object | null — additional structured data"
}
```

---

## Supported Intents (22)

| Intent | Requires Auth | Example Message |
|---|---|---|
| `GREETING` | No | "Hello" |
| `GOODBYE` | No | "Bye", "Thank you for your support" |
| `BALANCE` | Yes | "What is my balance?" |
| `TRANSACTIONS` | Yes | "Show my transactions" |
| `LOAN` | No | "I need a loan" |
| `ACCOUNT_SERVICES` | No | "How do I open an account?" |
| `SECURITY` | No | "I lost my card" |
| `TRANSFERS` | No | "How do I transfer money?" |
| `FEES` | No | "What are the ATM limits?" |
| `DIGITAL_BANKING` | No | "How do I use the mobile app?" |
| `GENERAL` | No | "What are your working hours?" |
| `FIXED_DEPOSIT` | No/Yes | "What are your FD rates?" |
| `PAWNING` | No/Yes | "Tell me about pawning" |
| `FOREIGN_EXCHANGE` | No | "What is the USD rate?" |
| `CARDS` | No | "How do I block my card?" |
| `INVESTMENTS` | No | "Tell me about unit trusts" |
| `CREDIT_SCORE` | No | "How to improve my credit score?" |
| `COMPLAINTS` | No | "I want to file a complaint" |
| `FORGOT_EMAIL` | No | "I cannot remember my email" |
| `CAPABILITIES` | No | "What can you do?" |
| `PROFANITY_RESPONSE` | No | (angry/rude messages) |
| `UNKNOWN` | No | (unrecognised queries — saved to DB) |

---

## 1. Greeting

### Request

```json
{
  "message": "Hello"
}
```

### Response

```json
{
  "reply": "👋 Hello! Welcome to Smart Banking Assistant! 😊 I'm here to help you with your banking needs. How can I assist you today?",
  "intent": "GREETING",
  "confidence": 0.99,
  "data": null
}
```

### Alternative Queries

- "Hi", "Good morning", "Hey there", "Hello, how are you?"

---

## 2. Goodbye / Thank You

### Request

```json
{
  "message": "Thank you for your support"
}
```

### Response

```json
{
  "reply": "🙏 Thank you for banking with us! It was a pleasure assisting you today. Have a wonderful day! 😊",
  "intent": "GOODBYE",
  "confidence": 0.95,
  "data": null
}
```

### Alternative Queries

- "Bye", "Goodbye", "See you later", "Okay bye", "That's all", "I'm done", "Bye bye"

---

## 3. What Can You Do (Capabilities)

### Request

```json
{
  "message": "What can you help me with?"
}
```

### Response

```json
{
  "reply": "🌟 I'm your Smart Banking Assistant! Here's what I can help you with:\n\n💰 **Account & Balance** — Check your balance, view transactions\n🏦 **Loans** — Personal, home, vehicle, and business loans\n📊 **Fixed Deposits** — FD rates and your personal FDs\n💳 **Cards** — Block/unblock, card features, apply for new card\n🔐 **Security** — Reset passwords, report lost cards, fraud alerts\n📱 **Digital Banking** — Mobile app and online banking help\n💱 **Foreign Exchange** — Currency rates and exchange services\n🗺️ **General Info** — Branch hours, contact details, locations\n\nJust type your question and I'll do my best to help! 😊",
  "intent": "CAPABILITIES",
  "confidence": 0.97,
  "data": null
}
```

### Alternative Queries

- "What can you do?", "How can you help me?", "What services do you offer?", "Tell me about your features"

---

## 4. Balance Query (requires account verification)

### Request

```json
{
  "message": "What is my account balance?",
  "user_id": 1,
  "account_number": "ACC001"
}
```

### Response (authenticated)

```json
{
  "reply": "💰 Your current account balance is **$5,250.00**. 📊 Your account is in good standing. Is there anything else I can help you with? 😊",
  "intent": "BALANCE",
  "confidence": 0.97,
  "data": {
    "balance": 5250.0
  }
}
```

### Response (not verified)

```json
{
  "reply": "🔐 To protect your privacy, I need to verify your identity before showing account details. Please use the **Verify Account** option to complete OTP verification. 😊",
  "intent": "BALANCE",
  "confidence": 0.97,
  "data": null
}
```

### Alternative Queries

- "How much money do I have?", "Check my balance", "Show account balance", "What's my current balance?"

---

## 5. Transaction History (requires account verification)

### Request

```json
{
  "message": "Show my recent transactions",
  "user_id": 1,
  "account_number": "ACC001"
}
```

### Response

```json
{
  "reply": "📋 Here are your recent transactions:\n\n1. 🟢 +$500.00 (CREDIT) — 2026-04-20\n   💼 Salary Deposit\n\n2. 🔴 -$150.00 (DEBIT) — 2026-04-19\n   🛒 Grocery Shopping at Walmart\n\n3. 🔴 -$75.50 (DEBIT) — 2026-04-18\n   🍕 Restaurant — Pizza Hut\n\n4. 🟢 +$1,000.00 (CREDIT) — 2026-04-17\n   💰 Freelance Payment\n\n5. 🔴 -$200.00 (DEBIT) — 2026-04-16\n   ⚡ Electric Bill Payment\n\nIs there anything else I can help you with? 😊",
  "intent": "TRANSACTIONS",
  "confidence": 0.95,
  "data": {
    "transactions": [
      {
        "id": 1,
        "amount": 500.0,
        "type": "credit",
        "date": "2026-04-20T09:00:00",
        "description": "Salary Deposit"
      },
      {
        "id": 2,
        "amount": 150.0,
        "type": "debit",
        "date": "2026-04-19T14:30:00",
        "description": "Grocery Shopping at Walmart"
      }
    ]
  }
}
```

---

## 6. Loan Inquiry

### Request

```json
{
  "message": "I need a loan"
}
```

### Response

```json
{
  "reply": "🏦 We offer a range of loan products to suit your needs:\n\n🏠 **Home Loans** — from 7.5% p.a.\n🚗 **Vehicle Loans** — from 8.0% p.a.\n💳 **Personal Loans** — from 9.5% p.a.\n🏢 **Business Loans** — competitive rates\n\nWould you like details on a specific loan type? You can also ask about eligibility requirements or the application process. 😊",
  "intent": "LOAN",
  "confidence": 0.96,
  "data": null
}
```

### Alternative Queries

- "Tell me about loans", "Apply for credit", "Home mortgage", "Vehicle loan", "Business loan rate"

---

## 7. Fixed Deposit — General Rates

### Request

```json
{
  "message": "What are your FD rates?"
}
```

### Response

```json
{
  "reply": "📅 Our Fixed Deposit interest rates:\n\n• 3 months — 8.00% p.a.\n• 6 months — 9.50% p.a.\n• 12 months — 11.00% p.a.\n• 24 months — 11.50% p.a.\n• 36 months — 12.00% p.a.\n\n💡 *Rates are subject to change. Contact us or visit a branch for the latest rates.* 😊",
  "intent": "FIXED_DEPOSIT",
  "confidence": 0.94,
  "data": null
}
```

---

## 8. Foreign Exchange

### Request

```json
{
  "message": "What is the USD exchange rate?"
}
```

### Response

```json
{
  "reply": "💱 For current USD exchange rates and all foreign currency services, please:\n\n🌍 Visit our website's **Foreign Exchange** section\n📞 Call our hotline: **+94 11 234 5678**\n🏦 Visit any Smart Bank branch\n\nWe offer buying and selling rates for USD, EUR, GBP, AUD, JPY, and many more currencies. 😊",
  "intent": "FOREIGN_EXCHANGE",
  "confidence": 0.92,
  "data": null
}
```

### Alternative Queries

- "Currency exchange rate", "How much is 100 dollars?", "EUR to LKR", "I want to exchange currency"

---

## 9. Forgot Email

### Request

```json
{
  "message": "I cannot remember my email address"
}
```

### Response

```json
{
  "reply": "📧 No worries! If you've forgotten your registered email address, here's how we can help:\n\n1. 🏦 **Visit a Branch** — Bring your NIC/Passport and we'll update your email on the spot\n2. 📞 **Call Us** — +94 11 234 5678 (identity verification required)\n3. 📝 **Submit a Request** — Via our website's contact form\n\nFor security, email changes can only be done with in-person identity verification. 🔐 Is there anything else I can help you with? 😊",
  "intent": "FORGOT_EMAIL",
  "confidence": 0.93,
  "data": null
}
```

### Alternative Queries

- "I forgot my email", "Update my email address", "Change email", "I don't know my email"

---

## 10. General Info

### Request

```json
{
  "message": "What are your working hours?"
}
```

### Response

```json
{
  "reply": "🕐 Our branch hours are:\n\n• **Monday–Friday:** 9:00 AM – 5:00 PM\n• **Saturday:** 9:00 AM – 1:00 PM\n• **Sunday & Public Holidays:** Closed\n\n📱 However, our **online banking** and **mobile app** are available 24/7! 🌐 Is there anything else I can help you with? 😊",
  "intent": "GENERAL",
  "confidence": 0.91,
  "data": null
}
```

---

## 11. Unknown Intent

### Request

```json
{
  "message": "What is the weather today?"
}
```

### Response

```json
{
  "reply": "🤔 I'm not sure I understand that question. I'm specialised in banking services — I can help with account balance, transactions, loans, fixed deposits, and more! Could you rephrase, or type **'What can you do?'** to see everything I can help with. 😊",
  "intent": "UNKNOWN",
  "confidence": 0.0,
  "data": null
}
```

> **Note:** Unrecognised questions are automatically saved to the `unknown_questions` table for model improvement.

---

## 12. Non-English Message (Language Guard)

### Request

```json
{
  "message": "ඔබේ ඉතිරිකිරීමේ ශේෂය කීයද?"
}
```

### Response

```json
{
  "reply": "🌐 I'm sorry, I can only understand **English** at the moment. Please rephrase your question in English and I'll be happy to help! 😊",
  "intent": "UNSUPPORTED_LANGUAGE",
  "confidence": null,
  "data": null
}
```

> This guard applies to Sinhala, Arabic, Chinese, Japanese, Hindi, Cyrillic, and other non-Latin scripts, as well as Latin-script non-English languages (French, Spanish, etc.).

---

## Account Verification (OTP) Endpoints

### Send OTP

**Endpoint:** `POST /api/account/send-otp`

#### Request

```json
{
  "account_number": "ACC001",
  "id_number": "200012345678",
  "email": "john@example.com"
}
```

#### Response (success)

```json
{
  "message": "OTP sent to your registered email address."
}
```

---

### Verify OTP

**Endpoint:** `POST /api/account/verify-otp`

#### Request

```json
{
  "account_number": "ACC001",
  "otp": "482931"
}
```

#### Response (success)

```json
{
  "message": "Verification successful.",
  "user_id": 1,
  "account_number": "ACC001"
}
```

Use the returned `user_id` and `account_number` in all subsequent chat requests that require personal data.

---

## Error Responses

### 400 Bad Request — Empty Message

```json
{ "detail": "Message cannot be empty" }
```

### 422 Validation Error — Missing Field

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "message"],
      "msg": "Field required"
    }
  ]
}
```

### 500 Internal Server Error

```json
{ "detail": "Internal server error processing your request" }
```

---

## cURL Examples

```bash
# Greeting
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Balance (authenticated)
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my balance?", "user_id": 1, "account_number": "ACC001"}'

# Capabilities
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What can you do?"}'

# Goodbye
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Thank you for your support"}'

# Send OTP
curl -X POST "http://localhost:8000/api/account/send-otp" \
  -H "Content-Type: application/json" \
  -d '{"account_number": "ACC001", "id_number": "200012345678", "email": "john@example.com"}'
```

---

## Python Example

```python
import requests

BASE = "http://localhost:8000"

def chat(message, user_id=None, account_number=None, last_intent=None):
    payload = {"message": message}
    if user_id:
        payload["user_id"] = user_id
    if account_number:
        payload["account_number"] = account_number
    if last_intent:
        payload["last_intent"] = last_intent
    r = requests.post(f"{BASE}/api/chat", json=payload)
    data = r.json()
    print(f"Bot [{data['intent']}]: {data['reply']}")
    return data

# Unauthenticated queries
chat("Hello")
chat("What can you do?")
chat("What are your FD rates?")
chat("Thank you for your support")

# Authenticated queries (after OTP)
chat("What is my balance?", user_id=1, account_number="ACC001")
chat("Show my transactions", user_id=1, account_number="ACC001")
```

---

## Testing with Postman

1. Import `Smart_Banking_Assistant.postman_collection.json`
2. Set environment variable `base_url` = `http://localhost:8000`
3. Run the **OTP Send** and **OTP Verify** requests first to obtain `user_id` / `account_number`
4. Use those values in the authenticated chat requests

---

## Testing with Swagger UI

1. Start server: `uvicorn main:app --reload`
2. Open: http://localhost:8000/docs
3. Expand **POST /api/chat** → Try it out → paste JSON body → Execute
