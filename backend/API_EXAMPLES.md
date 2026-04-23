# API Examples and Sample Responses

## Chat API Endpoint

**Endpoint:** `POST /api/chat`

**Base URL:** `http://localhost:8000`

---

## 1. Greeting Intent

### Request

```json
{
  "message": "Hello",
  "user_id": 1
}
```

### Response

```json
{
  "reply": "Hello! Welcome to Smart Banking Assistant. How can I help you today?",
  "intent": "GREETING",
  "confidence": 1.0,
  "data": null
}
```

### Alternative Queries

- "Hi"
- "Good morning"
- "Hey there"
- "Hello, how are you?"

---

## 2. Balance Query

### Request

```json
{
  "message": "What is my account balance?",
  "user_id": 1
}
```

### Response

```json
{
  "reply": "Your current account balance is $5,250.00.",
  "intent": "BALANCE",
  "confidence": 0.9,
  "data": {
    "balance": 5250.0
  }
}
```

### Alternative Queries

- "How much money do I have?"
- "Check my balance"
- "Show my account balance"
- "What's my current balance?"
- "Balance inquiry"

---

## 3. Transaction History

### Request

```json
{
  "message": "Show my recent transactions",
  "user_id": 1
}
```

### Response

```json
{
  "reply": "Here are your recent transactions:\n\n1. +$500.00 (CREDIT) - 2026-04-20\n   Salary Deposit\n\n2. -$150.00 (DEBIT) - 2026-04-19\n   Grocery Shopping at Walmart\n\n3. -$75.50 (DEBIT) - 2026-04-18\n   Restaurant - Pizza Hut\n\n4. +$1,000.00 (CREDIT) - 2026-04-17\n   Freelance Payment\n\n5. -$200.00 (DEBIT) - 2026-04-16\n   Electric Bill Payment",
  "intent": "TRANSACTIONS",
  "confidence": 0.9,
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
      // ... more transactions
    ]
  }
}
```

### Alternative Queries

- "Show transaction history"
- "Recent purchases"
- "What did I spend money on?"
- "Transaction statement"
- "Show my last transactions"

---

## 4. Loan Inquiry

### Request

```json
{
  "message": "I need a loan",
  "user_id": 1
}
```

### Response

```json
{
  "reply": "We offer various loan options:\n\n• Personal Loans: 8-12% interest rate\n• Home Loans: 6-9% interest rate\n• Car Loans: 7-11% interest rate\n\nWould you like to apply for a loan or speak with a loan officer? Please call us at 1-800-BANKING or visit your nearest branch.",
  "intent": "LOAN",
  "confidence": 0.9,
  "data": null
}
```

### Alternative Queries

- "Tell me about loans"
- "Apply for credit"
- "I want to borrow money"
- "Loan options"
- "Home mortgage"

---

## 5. Knowledge Base Query

### Request

```json
{
  "message": "What are your business hours?",
  "user_id": 1
}
```

### Response

```json
{
  "reply": "Our bank is open Monday to Friday from 9:00 AM to 5:00 PM, and Saturday from 9:00 AM to 1:00 PM. We are closed on Sundays and public holidays.",
  "intent": "KNOWLEDGE",
  "confidence": 0.8,
  "data": null
}
```

### Available Knowledge Base Questions

1. "What are your business hours?"
2. "How do I reset my password?"
3. "What is the minimum balance required?"
4. "How can I contact customer support?"
5. "What are the ATM withdrawal limits?"
6. "How do I apply for a credit card?"
7. "What interest rates do you offer?"
8. "How do I transfer money?"

---

## 6. Unknown Intent

### Request

```json
{
  "message": "What is the weather today?",
  "user_id": 1
}
```

### Response

```json
{
  "reply": "I'm sorry, I didn't understand that. Could you please rephrase your question? You can ask me about your account balance, recent transactions, or loan options.",
  "intent": "UNKNOWN",
  "confidence": 0.0,
  "data": null
}
```

**Note:** This question will be saved to the `unknown_questions` table for future learning.

---

## Error Responses

### 400 Bad Request - Empty Message

#### Request

```json
{
  "message": "",
  "user_id": 1
}
```

#### Response

```json
{
  "detail": "Message cannot be empty"
}
```

### 422 Validation Error - Invalid Request

#### Request

```json
{
  "msg": "hello"
}
```

#### Response

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "message"],
      "msg": "Field required",
      "input": { "msg": "hello" }
    }
  ]
}
```

### 500 Internal Server Error

#### Response

```json
{
  "detail": "Internal server error processing your request"
}
```

---

## cURL Examples

### Greeting

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_id": 1}'
```

### Balance

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is my balance?", "user_id": 1}'
```

### Transactions

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show transactions", "user_id": 1}'
```

### Loan

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a loan", "user_id": 1}'
```

---

## Python Examples

### Using `requests` library

```python
import requests
import json

def chat(message, user_id=1):
    url = "http://localhost:8000/api/chat"
    payload = {
        "message": message,
        "user_id": user_id
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        print(f"Bot: {data['reply']}")
        print(f"Intent: {data['intent']}")
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

# Test different queries
chat("Hello")
chat("What is my balance?")
chat("Show my transactions")
```

### Async with `httpx`

```python
import httpx
import asyncio

async def chat_async(message, user_id=1):
    url = "http://localhost:8000/api/chat"
    payload = {
        "message": message,
        "user_id": user_id
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        return response.json()

# Run async
asyncio.run(chat_async("Hello"))
```

---

## JavaScript/Node.js Examples

### Using `fetch` (Browser/Node.js 18+)

```javascript
async function chat(message, userId = 1) {
  const response = await fetch("http://localhost:8000/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message,
      user_id: userId,
    }),
  });

  const data = await response.json();
  console.log("Bot:", data.reply);
  console.log("Intent:", data.intent);
  return data;
}

// Test
chat("What is my balance?");
```

### Using `axios`

```javascript
const axios = require("axios");

async function chat(message, userId = 1) {
  try {
    const response = await axios.post("http://localhost:8000/api/chat", {
      message: message,
      user_id: userId,
    });

    console.log("Bot:", response.data.reply);
    console.log("Intent:", response.data.intent);
    return response.data;
  } catch (error) {
    console.error("Error:", error.message);
  }
}

// Test
chat("Show my transactions");
```

---

## Response Schema

```typescript
interface ChatResponse {
  reply: string; // Bot's response message
  intent: string | null; // Detected intent (GREETING, BALANCE, etc.)
  confidence: number | null; // Confidence score (0.0 to 1.0)
  data: object | null; // Additional data (balance, transactions, etc.)
}
```

---

## Testing with Postman

1. Import the collection: `Smart_Banking_Assistant.postman_collection.json`
2. Set the `base_url` variable to `http://localhost:8000`
3. Run individual requests or the entire collection
4. View formatted responses in the Postman UI

---

## Testing with Swagger UI

1. Start the server: `uvicorn main:app --reload`
2. Open: http://localhost:8000/docs
3. Click on `/api/chat` endpoint
4. Click "Try it out"
5. Enter your message in the request body
6. Click "Execute"
7. View the response below

---

## Performance Metrics

Typical response times (local development):

- Greeting: ~50-100ms
- Balance query: ~100-200ms (with DB query)
- Transactions: ~150-300ms (with DB query)
- Loan inquiry: ~50-100ms
- Unknown intent: ~100-250ms (with DB save)

**Note:** Response times may vary based on system resources and database performance.
