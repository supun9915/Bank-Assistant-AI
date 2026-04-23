# Smart Banking Assistant - Project Structure & Technology Reference

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

## 🚀 What This Project Can Do

The **Smart Banking Assistant** is an AI-powered conversational chatbot backend that allows bank customers to interact with their banking data via natural language. Here is a full list of capabilities:

### 💬 Conversational Capabilities

| Feature                       | Description                                                                                        |
| ----------------------------- | -------------------------------------------------------------------------------------------------- |
| **Greeting & Onboarding**     | Recognizes common greetings (Hello, Hi, Hey, Good morning, Namaste, etc.) and responds warmly      |
| **Account Balance Inquiry**   | Fetches and returns the real-time account balance for a user from the database                     |
| **Transaction History**       | Retrieves and formats the last N (default: 5) transactions with date, amount, type and description |
| **Loan & Credit Information** | Provides informational answers about loan products, EMI, mortgage, and financing options           |
| **General Banking Q&A**       | Searches a structured knowledge base to answer common banking questions                            |
| **Unknown Query Handling**    | When a question cannot be answered, it is saved to the database for future improvement             |
| **Self-Learning**             | Unknown questions are stored with deduplication, building a dataset for future model training      |
| **Multi-user Support**        | Each request can carry a `user_id`, enabling per-user data retrieval                               |

### 🧠 NLP Capabilities

- Tokenizes and lemmatizes user input using spaCy
- Removes English stop words to focus on meaningful terms
- Scores each intent via weighted keyword matching (exact phrase vs. lemma match)
- Returns the best-matching intent with a confidence score (0.0 – 1.0)
- Extracts numeric entities and currency values via regex patterns
- Handles edge cases: empty input, no-match scenarios, ambiguous messages

### 🌐 API Capabilities

- RESTful HTTP API built on FastAPI
- Interactive auto-generated documentation at `/docs` (Swagger UI) and `/redoc`
- Health check endpoints (`/` and `/health`) for monitoring
- CORS-enabled for browser-based frontends
- Structured JSON responses with `reply`, `intent`, `confidence`, and optional `data` fields

---

## 🛠️ Technologies Used & Why

### Programming Language

| Technology | Version | Why Used                                                                                                                                             |
| ---------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Python** | 3.10+   | Industry-standard for AI/NLP projects; rich ecosystem of ML, web, and database libraries; clean syntax suitable for rapid prototyping and coursework |

### Runtime & Server

| Technology              | Version  | Why Used                                                                                                                              |
| ----------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **CPython (Python VM)** | 3.10+    | Reference Python interpreter; standard for production Python applications                                                             |
| **Uvicorn**             | ≥ 0.30.0 | Lightning-fast ASGI server required to run FastAPI; supports async I/O, WebSockets, and HTTP/2; ideal for real-time chatbot workloads |

### Web Framework

| Technology  | Version   | Why Used                                                                                                                                                                                             |
| ----------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **FastAPI** | ≥ 0.115.0 | Modern, high-performance Python web framework; auto-generates OpenAPI/Swagger docs; native async support; built-in Pydantic validation; significantly faster than Flask/Django for API-only backends |

### Data Validation

| Technology   | Version  | Why Used                                                                                                                                                              |
| ------------ | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Pydantic** | ≥ 2.10.0 | Enforces data types and constraints on API request/response models at runtime; integrated directly into FastAPI; prevents malformed data from reaching business logic |

### Natural Language Processing

| Technology                | Version | Why Used                                                                                                                                                                                  |
| ------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **spaCy**                 | ≥ 3.7.0 | Industrial-strength NLP library; built-in tokenizer, lemmatizer, stop-word lists, and named entity recognition; no manual corpus downloads required; reliable cross-platform installation |
| **spaCy: en_core_web_sm** | 3.8.x   | Small English pipeline model providing tokenization, POS tagging, dependency parsing, and NER used by `nlp.py`                                                                            |

### Database

| Technology                 | Version | Why Used                                                                                                                                                        |
| -------------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MySQL**                  | 8.x     | Reliable, widely-used relational database; strong support for financial/transactional data; ACID compliance ensures data integrity; familiar to most developers |
| **mysql-connector-python** | 8.3.0   | Official Oracle-maintained MySQL driver for Python; supports parameterized queries (SQL injection prevention); context-manager-compatible connection handling   |

### Utilities

| Technology           | Version | Why Used                                                                                                                                   |
| -------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **python-dotenv**    | 1.0.0   | Loads environment variables from a `.env` file; keeps database credentials and secrets out of source code; standard 12-factor app practice |
| **python-multipart** | ≥ 0.0.6 | Required by FastAPI to support `multipart/form-data` request bodies (file uploads, form submissions)                                       |
| **email-validator**  | 2.1.0   | Validates email address format in Pydantic models; prevents invalid emails from being stored in the database                               |

### Development & Testing Tools

| Technology                  | Why Used                                                                                                                      |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Postman**                 | API testing and collection management; pre-configured collection included (`Smart_Banking_Assistant.postman_collection.json`) |
| **Python `logging` module** | Built-in structured logging throughout all layers; aids debugging without external dependencies                               |
| **Python `contextlib`**     | Powers the `@contextmanager` database connection pattern; ensures connections are always closed even on exceptions            |
| **Python `re` (regex)**     | Used in `extract_entities()` to find currency amounts and numeric values in user input                                        |
| **Python `typing`**         | Type hints across all modules for code clarity and IDE auto-complete support                                                  |

---

## ⚙️ Runtime & VM Details

```
┌─────────────────────────────────────────────────────────┐
│                   Host Machine                          │
│                                                         │
│  OS: Windows / Linux / macOS                            │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │           Python Virtual Environment              │  │
│  │           (venv / .venv)                          │  │
│  │                                                   │  │
│  │  Runtime: CPython 3.10+                           │  │
│  │  VM: Python bytecode interpreter (CPython VM)     │  │
│  │                                                   │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │   Uvicorn ASGI Server                       │  │  │
│  │  │   (uvicorn main:app --reload)               │  │  │
│  │  │   Default Port: 8000                        │  │  │
│  │  │                                             │  │  │
│  │  │   ┌───────────────────────────────────┐     │  │  │
│  │  │   │  FastAPI Application (main.py)    │     │  │  │
│  │  │   │  + CORS Middleware                │     │  │  │
│  │  │   │  + Routes (/api/chat)             │     │  │  │
│  │  │   │  + Services (chat_service.py)     │     │  │  │
│  │  │   │  + NLP Engine (nlp.py / NLTK)     │     │  │  │
│  │  │   │  + DB Layer (db.py)               │     │  │  │
│  │  │   └───────────────────────────────────┘     │  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │           MySQL Server 8.x                        │  │
│  │           Port: 3306                              │  │
│  │           Database: banking_chatbot               │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Environment Variables (`.env`)

| Variable      | Default           | Description           |
| ------------- | ----------------- | --------------------- |
| `DB_HOST`     | `localhost`       | MySQL server hostname |
| `DB_USER`     | `root`            | MySQL username        |
| `DB_PASSWORD` | `mysql`           | MySQL password        |
| `DB_NAME`     | `banking_chatbot` | Database name         |
| `DB_PORT`     | `3306`            | MySQL port            |

---

## 📦 Complete Package Reference (`requirements.txt`)

```
# Web Framework & Server
fastapi>=0.115.0          # REST API framework
uvicorn[standard]>=0.30.0 # ASGI server (includes websockets, httptools)
pydantic>=2.10.0          # Data validation and serialization

# Database
mysql-connector-python==8.3.0  # MySQL driver

# NLP
nltk==3.8.1               # Natural Language Toolkit

# Utilities
python-dotenv==1.0.0      # .env file loader
python-multipart==0.0.6   # Form data / file upload support

# Optional (recommended)
email-validator==2.1.0    # Email validation in Pydantic models
```

### NLTK Data Downloads (auto-downloaded at startup)

| Resource    | Path                   | Purpose                          |
| ----------- | ---------------------- | -------------------------------- |
| `punkt_tab` | `tokenizers/punkt_tab` | Word tokenizer (newer format)    |
| `punkt`     | `tokenizers/punkt`     | Word tokenizer (legacy fallback) |
| `stopwords` | `corpora/stopwords`    | English stop-word list           |
| `wordnet`   | `corpora/wordnet`      | Lemmatization lexical database   |

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

- Natural Language Processing with **NLTK** (Natural Language Toolkit)
- Intent detection via weighted keyword + lemma scoring
- Text preprocessing and normalization
- Lemmatization using `WordNetLemmatizer`
- Tokenization using `word_tokenize`
- Stop-word filtering using NLTK English corpus
- Regex-based entity extraction

**Key Functions:**

- `preprocess_text()` - Lowercase, strip, normalize whitespace
- `extract_lemmas()` - Tokenize, remove stop-words, lemmatize
- `detect_intent()` - Score all intents, return best match + confidence
- `extract_entities()` - Extract numbers and currency values via regex
- `get_intent_info()` - Get intent metadata (description, DB requirement)

**Supported Intents:**

- `GREETING` - Greetings and salutations
- `BALANCE` - Account balance queries
- `TRANSACTIONS` - Transaction history and statements
- `LOAN` - Loan, credit, mortgage, EMI inquiries
- `UNKNOWN` - Fallback when no intent matches

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
├── nltk
│   ├── nltk.tokenize (word_tokenize)
│   ├── nltk.corpus (stopwords)
│   └── nltk.stem (WordNetLemmatizer)
├── re (regex)
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
├── fastapi>=0.115.0
├── uvicorn[standard]>=0.30.0
└── pydantic>=2.10.0

Database
└── mysql-connector-python==8.3.0

NLP
└── nltk==3.8.1
    ├── punkt / punkt_tab  (tokenizer data)
    ├── stopwords          (stop-word corpus)
    └── wordnet            (lemmatization lexicon)

Utilities
├── python-dotenv==1.0.0
├── python-multipart==0.0.6
└── email-validator==2.1.0
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
- Downloads NLTK data (punkt, stopwords, wordnet)
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

### NLTK

- Official Docs: https://www.nltk.org/
- Book / Guide: https://www.nltk.org/book/

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
✅ NLTK NLP integration
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
