# Smart Banking Assistant - Project Structure

## 📁 Complete Directory Structure

```
backend/
│
├── 📄 main.py                          # FastAPI application entry point
├── 📄 db.py                            # Database connection and queries
├── 📄 nlp.py                           # NLP processing with spaCy
│
├── 📂 models/                          # Pydantic data models
│   ├── __init__.py
│   └── chat_models.py                  # Request/Response models
│
├── 📂 routes/                          # API endpoints
│   ├── __init__.py
│   └── chat.py                         # Chat API routes
│
├── 📂 services/                        # Business logic layer
│   ├── __init__.py
│   └── chat_service.py                 # Chat processing service
│
├── 📄 requirements.txt                 # Python dependencies
├── 📄 schema.sql                       # MySQL database schema
├── 📄 .env.example                     # Environment variables template
├── 📄 .gitignore                       # Git ignore rules
│
├── 📄 README.md                        # Main documentation
├── 📄 QUICKSTART.md                    # Quick setup guide
├── 📄 CONFIGURATION.md                 # Configuration details
├── 📄 API_EXAMPLES.md                  # API usage examples
├── 📄 PROJECT_STRUCTURE.md             # This file
│
├── 📄 test_chatbot.py                  # Test script
├── 📄 setup.bat                        # Windows setup script
├── 📄 setup.sh                         # Linux/Mac setup script
└── 📄 Smart_Banking_Assistant.postman_collection.json
```

---

## 📋 File Descriptions

### Core Application Files

#### `main.py`

- FastAPI application initialization
- CORS middleware configuration
- Route registration
- Logging setup
- Health check endpoints

**Key Components:**

- `app` - FastAPI instance
- `@app.get("/")` - Root health check
- `@app.get("/health")` - Detailed health check

---

#### `db.py`

- Database connection management
- SQL query execution functions
- Context manager for connections
- All database operations

**Key Functions:**

- `get_db_connection()` - Connection context manager
- `execute_query()` - Generic query executor
- `get_account_balance()` - Fetch user balance
- `get_recent_transactions()` - Fetch transaction history
- `get_answer_from_knowledge()` - Search knowledge base
- `save_unknown_question()` - Store unknown queries
- `test_connection()` - Database health check

**Database Tables Used:**

- `users` - User accounts
- `accounts` - Bank accounts
- `transactions` - Transaction history
- `knowledge` - Q&A knowledge base
- `unknown_questions` - Learning data

---

#### `nlp.py`

- Natural Language Processing with spaCy
- Intent detection engine
- Text preprocessing
- Lemmatization and tokenization

**Key Functions:**

- `preprocess_text()` - Clean and normalize text
- `extract_lemmas()` - Extract lemmatized tokens
- `detect_intent()` - Detect user intent
- `extract_entities()` - Extract named entities
- `get_intent_info()` - Get intent metadata

**Supported Intents:**

- `GREETING` - Greetings and salutations
- `BALANCE` - Account balance queries
- `TRANSACTIONS` - Transaction history
- `LOAN` - Loan inquiries
- `UNKNOWN` - Fallback intent

---

### Models Directory (`models/`)

#### `chat_models.py`

Pydantic models for request/response validation

**Classes:**

- `ChatRequest` - Validates incoming chat messages
  - `message: str` - User input (required, 1-500 chars)
  - `user_id: int` - User identifier (optional, default=1)

- `ChatResponse` - Structures bot responses
  - `reply: str` - Bot's response message
  - `intent: str` - Detected intent
  - `confidence: float` - Confidence score
  - `data: dict` - Additional data (optional)

---

### Routes Directory (`routes/`)

#### `chat.py`

Chat API endpoints and request handling

**Endpoints:**

- `POST /api/chat` - Main chat endpoint
- `GET /api/chat/health` - Chat service health check

**Features:**

- Request validation
- Error handling
- Response formatting
- Logging

---

### Services Directory (`services/`)

#### `chat_service.py`

Core business logic for chat processing

**Main Function:**

- `process_chat_message()` - Orchestrates chat flow

**Intent Handlers:**

- `handle_greeting_intent()` - Process greetings
- `handle_balance_intent()` - Fetch and format balance
- `handle_transactions_intent()` - Fetch and format transactions
- `handle_loan_intent()` - Provide loan information
- `handle_unknown_intent()` - Handle unknown queries

**Helper Functions:**

- `format_balance_response()` - Format currency
- `format_transactions_response()` - Format transaction list

---

## 🔄 Request Flow

```
┌─────────────┐
│   Client    │
│  (Browser,  │
│   Postman,  │
│   cURL)     │
└──────┬──────┘
       │
       │ POST /api/chat
       │ {"message": "What is my balance?"}
       ▼
┌─────────────────────────────────────────────┐
│           main.py (FastAPI App)             │
│  ┌───────────────────────────────────────┐  │
│  │     CORS Middleware                   │  │
│  └───────────────────────────────────────┘  │
└──────┬──────────────────────────────────────┘
       │
       │ Route to /api/chat
       ▼
┌─────────────────────────────────────────────┐
│         routes/chat.py                      │
│  ┌───────────────────────────────────────┐  │
│  │  Validate Request (Pydantic)          │  │
│  │  - Check message format               │  │
│  │  - Validate user_id                   │  │
│  └───────────────────────────────────────┘  │
└──────┬──────────────────────────────────────┘
       │
       │ Call process_chat_message()
       ▼
┌─────────────────────────────────────────────┐
│      services/chat_service.py               │
│  ┌───────────────────────────────────────┐  │
│  │  1. Detect Intent (nlp.py)            │  │
│  │  2. Route to Handler                  │  │
│  │  3. Process Request                   │  │
│  └───────────────────────────────────────┘  │
└──────┬──────────────────────────────────────┘
       │
       ├─────► nlp.py (Intent Detection)
       │       - Preprocess text
       │       - Extract lemmas
       │       - Match keywords
       │       - Return intent + confidence
       │
       └─────► db.py (Database Queries)
               - Get balance
               - Get transactions
               - Search knowledge base
               - Save unknown questions
               │
               ▼
┌─────────────────────────────────────────────┐
│           MySQL Database                    │
│  ┌───────────────────────────────────────┐  │
│  │  Tables:                              │  │
│  │  - users                              │  │
│  │  - accounts                           │  │
│  │  - transactions                       │  │
│  │  - knowledge                          │  │
│  │  - unknown_questions                  │  │
│  └───────────────────────────────────────┘  │
└──────┬──────────────────────────────────────┘
       │
       │ Return data
       ▼
┌─────────────────────────────────────────────┐
│      services/chat_service.py               │
│  ┌───────────────────────────────────────┐  │
│  │  Format Response                      │  │
│  │  - Create reply message               │  │
│  │  - Add metadata                       │  │
│  └───────────────────────────────────────┘  │
└──────┬──────────────────────────────────────┘
       │
       │ Return response dict
       ▼
┌─────────────────────────────────────────────┐
│         routes/chat.py                      │
│  ┌───────────────────────────────────────┐  │
│  │  Create ChatResponse Model            │  │
│  └───────────────────────────────────────┘  │
└──────┬──────────────────────────────────────┘
       │
       │ JSON Response
       ▼
┌─────────────┐
│   Client    │
│  Receives:  │
│  {          │
│    "reply": "Your balance is $5,250.00",
│    "intent": "BALANCE",
│    "confidence": 0.9,
│    "data": {"balance": 5250.00}
│  }          │
└─────────────┘
```

---

## 🗄️ Database Schema

### Entity Relationship Diagram

```
┌─────────────┐
│   users     │
├─────────────┤
│ id (PK)     │
│ name        │
│ email       │
│ created_at  │
└──────┬──────┘
       │
       │ 1:N
       ▼
┌─────────────────┐
│   accounts      │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ account_number  │
│ balance         │
│ account_type    │
└──────┬──────────┘
       │
       │ 1:N
       ▼
┌─────────────────────┐
│  transactions       │
├─────────────────────┤
│ id (PK)             │
│ account_id (FK)     │
│ amount              │
│ type                │
│ description         │
│ date                │
└─────────────────────┘

┌─────────────────────┐
│   knowledge         │
├─────────────────────┤
│ id (PK)             │
│ question            │
│ answer              │
│ category            │
└─────────────────────┘

┌─────────────────────────┐
│  unknown_questions      │
├─────────────────────────┤
│ id (PK)                 │
│ question                │
│ count                   │
│ created_at              │
│ status                  │
└─────────────────────────┘
```

---

## 🧩 Module Dependencies

```
main.py
├── fastapi
├── fastapi.middleware.cors
├── routes.chat
└── logging

routes/chat.py
├── fastapi
├── models.chat_models
├── services.chat_service
└── logging

services/chat_service.py
├── nlp
├── db
├── logging
└── typing

nlp.py
├── spacy
├── logging
└── typing

db.py
├── mysql.connector
├── contextlib
├── os
├── logging
└── typing

models/chat_models.py
└── pydantic
```

---

## 📦 External Dependencies

```
FastAPI Framework
├── fastapi==0.109.0
├── uvicorn[standard]==0.27.0
└── pydantic==2.5.3

Database
└── mysql-connector-python==8.3.0

NLP
└── spacy==3.7.2
    └── en_core_web_sm (model)

Utilities
├── python-dotenv==1.0.0
└── python-multipart==0.0.6
```

---

## 🔧 Configuration Files

### `.env` (Not in repo)

Runtime environment variables

- Database credentials
- Application settings

### `.env.example`

Template for environment variables

- Shows required variables
- Provides example values

### `requirements.txt`

Python package dependencies

- All required packages
- Specific versions

### `schema.sql`

MySQL database schema

- Table definitions
- Sample data
- Verification queries

### `.gitignore`

Git ignore patterns

- Virtual environments
- Environment files
- Cache files

---

## 📚 Documentation Files

### `README.md`

Main project documentation

- Features overview
- Installation guide
- Usage examples
- API documentation

### `QUICKSTART.md`

Quick setup guide

- 5-minute setup
- Essential steps only
- Common issues

### `CONFIGURATION.md`

Configuration reference

- Environment variables
- Database settings
- Performance tuning
- Security recommendations

### `API_EXAMPLES.md`

API usage examples

- Sample requests/responses
- Code examples (Python, JS)
- cURL commands
- Testing instructions

### `PROJECT_STRUCTURE.md`

This file - Architecture documentation

---

## 🧪 Testing & Setup Files

### `test_chatbot.py`

Automated test script

- Tests all intents
- Validates responses
- Provides summary

### `setup.bat` (Windows)

Automated setup script

- Creates virtual environment
- Installs dependencies
- Downloads spaCy model
- Creates .env file

### `setup.sh` (Linux/Mac)

Automated setup script

- Same as setup.bat
- Unix/Linux compatible

### `Smart_Banking_Assistant.postman_collection.json`

Postman API collection

- Pre-configured requests
- All endpoints
- Variable configuration

---

## 🎯 Design Patterns Used

### 1. **Layered Architecture**

```
Presentation Layer (routes/)
    ↓
Business Logic Layer (services/)
    ↓
Data Access Layer (db.py)
    ↓
Database (MySQL)
```

### 2. **Dependency Injection**

- Services injected into routes
- Database functions injected into services

### 3. **Context Manager Pattern**

- Database connections use context managers
- Automatic resource cleanup

### 4. **Strategy Pattern**

- Different intent handlers
- Pluggable intent processing

### 5. **Service Layer Pattern**

- Business logic separated from API layer
- Reusable service functions

---

## 🔐 Security Features

1. **Input Validation**
   - Pydantic models validate all inputs
   - Type checking
   - Length constraints

2. **SQL Injection Prevention**
   - Parameterized queries
   - No string concatenation

3. **Error Handling**
   - Try-catch blocks
   - Proper error messages
   - No sensitive data in errors

4. **Connection Management**
   - Automatic connection cleanup
   - Connection pooling ready

---

## 📈 Scalability Considerations

### Current Implementation

- Single-threaded
- Connection per request
- No caching
- Local database

### Future Improvements

1. **Connection Pooling**
   - Reuse database connections
   - Better performance

2. **Caching**
   - Cache knowledge base
   - Cache user data
   - Redis integration

3. **Load Balancing**
   - Multiple workers
   - Horizontal scaling

4. **Message Queue**
   - Async processing
   - Background tasks

5. **Microservices**
   - Separate NLP service
   - Separate DB service

---

## 🎓 Learning Resources

### FastAPI

- Official Docs: https://fastapi.tiangolo.com/
- Tutorial: https://fastapi.tiangolo.com/tutorial/

### spaCy

- Official Docs: https://spacy.io/
- 101 Guide: https://spacy.io/usage/spacy-101

### MySQL

- MySQL Docs: https://dev.mysql.com/doc/
- MySQL Python: https://dev.mysql.com/doc/connector-python/en/

### Pydantic

- Official Docs: https://docs.pydantic.dev/

---

## 🚀 Development Workflow

1. **Setup**

   ```bash
   ./setup.bat  # or ./setup.sh
   ```

2. **Configure**

   ```bash
   # Edit .env with credentials
   ```

3. **Database**

   ```sql
   SOURCE schema.sql;
   ```

4. **Run**

   ```bash
   uvicorn main:app --reload
   ```

5. **Test**

   ```bash
   python test_chatbot.py
   # or use Postman
   # or use /docs endpoint
   ```

6. **Develop**
   - Add new intents in `nlp.py`
   - Add handlers in `chat_service.py`
   - Add routes in `routes/`
   - Add database functions in `db.py`

---

## 📊 Code Statistics

```
Total Files: 17
Python Files: 8
Documentation: 5
Config Files: 4

Lines of Code (approx):
- main.py: 50
- db.py: 200
- nlp.py: 180
- routes/chat.py: 60
- services/chat_service.py: 220
- models/chat_models.py: 50
- Total Python: ~760 lines
- Total SQL: ~200 lines
```

---

## 🎯 Project Goals Achieved

✅ FastAPI backend
✅ spaCy NLP integration
✅ MySQL database
✅ Intent detection
✅ Multiple intents (5+)
✅ Database queries
✅ Learning feature
✅ Modular structure
✅ Pydantic validation
✅ Error handling
✅ CORS support
✅ Logging
✅ Clean code
✅ Documentation
✅ Test script
✅ Setup automation

---

**End of Project Structure Documentation**
