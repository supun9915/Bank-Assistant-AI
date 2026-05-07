# Smart Banking Assistant

An AI-powered banking chatbot that uses a TensorFlow/Keras ANN to classify user intent and respond to banking queries in real time. The system provides account balance lookups, transaction history, loan/FD/pawning information, OTP-based account verification, and general banking support — all through a conversational chat interface.

---

## Features

- **AI Intent Classification** — TensorFlow/Keras ANN trained on 22 banking intents with a Lancaster-stemmed Bag-of-Words feature pipeline
- **Hybrid NLP** — ANN primary path (confidence threshold 0.40) with NLTK keyword fallback
- **OTP Account Verification** — 3-factor identity check (email + National ID + account number) before exposing personal data
- **English-Only Guard** — Non-English input politely declined using Unicode range detection + `langdetect`
- **Context-Aware Follow-ups** — `last_intent` field carries conversation context across turns
- **Self-Learning** — Unrecognised questions saved to `unknown_questions` table for future retraining
- **Chat Log Persistence** — Every request/response logged to MySQL
- **React Frontend** — Responsive SPA with animated chat bubbles and an account verification panel

---

## Tech Stack

| Layer    | Technology                                      |
| -------- | ----------------------------------------------- |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Axios |
| Backend  | FastAPI, Uvicorn, Pydantic                      |
| AI / NLP | TensorFlow/Keras, NLTK, scikit-learn, NumPy     |
| Database | MySQL 8                                         |
| Email    | Gmail SMTP (TLS)                                |

---

## Prerequisites

| Requirement | Version |
| ----------- | ------- |
| Python      | 3.10+   |
| Node.js     | 18+     |
| MySQL       | 8.0+    |
| pip         | latest  |
| npm         | latest  |

---

## Quick Start

### 1. Clone the repository

```bash
git clone <repo-url>
cd Bank-Assistant-AI
```

### 2. Backend setup

**Windows:**

```bat
cd backend
setup.bat
python migrate.py up
copy .env.example .env   # then fill in your credentials
.\venv\Scripts\activate
python train_model.py
uvicorn main:app --reload
```

**Linux / macOS:**

```bash
cd backend
chmod +x setup.sh && ./setup.sh
python migrate.py up
cp .env.example .env     # then fill in your credentials
source venv/bin/activate
python train_model.py
uvicorn main:app --reload
```

Backend runs at **http://localhost:8000** — Swagger UI at **http://localhost:8000/docs**

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:5173**

### 4. Environment variables

Create `backend/.env` from the example and set:

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

---

## Project Structure

```
Bank-Assistant-AI/
├── backend/
│   ├── main.py               # FastAPI app entry point & CORS config
│   ├── db.py                 # Centralised MySQL query executor
│   ├── nlp.py                # ANN inference + keyword fallback
│   ├── train_model.py        # Offline ANN training script
│   ├── migrate.py            # Versioned schema migration runner
│   ├── intents/
│   │   └── intents.json      # Intent patterns and responses (22 intents)
│   ├── migrations/           # Versioned SQL migration scripts
│   ├── models/
│   │   ├── chat_models.py    # Pydantic request/response schemas
│   │   └── chatbot_model.keras  # Trained ANN artefact (generated)
│   ├── routes/
│   │   ├── chat.py           # POST /api/chat
│   │   └── account.py        # POST /api/account/send-otp & verify-otp
│   └── services/
│       ├── chat_service.py   # Intent handlers and response formatters
│       └── email_service.py  # Gmail SMTP OTP delivery
└── frontend/
    ├── src/
    │   ├── App.tsx            # Root component & session state
    │   ├── api.ts             # Axios HTTP client
    │   └── components/
    │       ├── Header.tsx
    │       ├── ChatContainer.tsx
    │       ├── MessageBubble.tsx
    │       ├── ChatInput.tsx
    │       ├── TypingIndicator.tsx
    │       └── AccountPanel.tsx
    └── index.html
```

---

## API Overview

| Method | Endpoint                  | Description                          |
| ------ | ------------------------- | ------------------------------------ |
| POST   | `/api/chat`               | Send a chat message, receive a reply |
| POST   | `/api/account/send-otp`   | Send OTP to registered email         |
| POST   | `/api/account/verify-otp` | Verify OTP and authenticate account  |
| GET    | `/`                       | Health check                         |
| GET    | `/docs`                   | Swagger UI                           |

See [backend/README.md](backend/README.md) for full request/response schemas and all 22 supported intents.

---

## High-Level Architecture

### 1. System Overview

The system is composed of four runtime layers and one offline pipeline:

**1. Client Layer (Browser)**
A React 18 Single-Page Application built with TypeScript and Vite runs entirely in the user's browser. It communicates with the backend exclusively via HTTP/JSON requests using the Axios library.

**2. Application Layer (FastAPI — port 8000)**
The FastAPI server is the central hub of the system. It exposes two route groups:

- `/api/chat` — handled by the Chat Service, which calls the NLP module to classify the user's intent and then queries the database for any required data.
- `/api/account/send-otp` and `/api/account/verify-otp` — handled by the Account routes, which use the Email Service to deliver one-time passwords and the database layer to persist verification state.

All database access is centralised in `db.py`, which acts as a MySQL query executor for all routes and services.

**3. AI / ML Layer**
The NLP module (`nlp.py`) loads the trained Keras ANN model at startup. To classify a message, it preprocesses the input text, converts it to a Bag-of-Words vector using the Lancaster Stemmer (NLTK), and runs it through the ANN. Intent definitions (patterns and responses) are stored in `intents.json`.

**4. Data Layer (MySQL)**
The relational database stores all persistent data across nine tables: `users`, `accounts`, `transactions`, `chat_logs`, `unknown_questions`, `loans`, `fixed_deposits`, `pawning`, and `verified_users`.

**5. Offline Training Pipeline**
The ANN model is trained separately using `train_model.py`. It reads patterns from `intents.json`, tokenises and stems them, builds a Bag-of-Words feature matrix, performs a stratified train/validation split via scikit-learn, and trains the model with TensorFlow/Keras. The resulting artefacts (`chatbot_model.keras`, `words.pkl`, `classes.pkl`) are saved to the `models/` directory and loaded by the NLP module at runtime.

---

### 2. Frontend Architecture

The frontend is structured as a tree of React components rooted at the application entry point:

- **`index.tsx`** — The entry point that mounts the React application into the DOM.
- **`App.tsx`** — The root component and central state manager. It renders the top-level layout, manages the `accountInfo` session state, and syncs that state to and from `localStorage` for session persistence across page reloads.
  - **`Header.tsx`** — Displays the application title and provides the Account verification button to open the account panel.
  - **`ChatContainer.tsx`** — Orchestrates the entire chat experience. It renders the message list, typing indicator, and the chat input field. It calls `api.ts` to send messages to the backend.
    - **`MessageBubble.tsx`** — Renders individual chat messages, styled differently for user and bot bubbles.
    - **`TypingIndicator.tsx`** — Shows an animated three-dot indicator while the bot is processing a response.
    - **`ChatInput.tsx`** — The text input field and send button for composing messages.
  - **`AccountPanel.tsx`** — The OTP verification UI where users enter their email, NIC, and account number. It also calls `api.ts` directly for OTP-related endpoints.
- **`api.ts`** — The centralised Axios HTTP client. All network requests from the frontend go through this module.
- **`localStorage`** — Used by `App.tsx` to persist verified account session data between browser sessions.

#### Frontend Libraries

| Library        | Version | Purpose                     |
| -------------- | ------- | --------------------------- |
| React          | 18.3.1  | UI component framework      |
| React DOM      | 18.3.1  | DOM rendering               |
| TypeScript     | 5.5.4   | Static type safety          |
| Vite           | 5.2.0   | Build tool & dev server     |
| Tailwind CSS   | 3.4.17  | Utility-first CSS styling   |
| Framer Motion  | 11.5.4  | Animations & transitions    |
| Axios          | 1.7.7   | HTTP client for API calls   |
| Lucide React   | 0.522.0 | Icon components             |
| @emotion/react | 11.13.3 | CSS-in-JS support           |
| PostCSS        | latest  | CSS transformation pipeline |
| Autoprefixer   | latest  | Vendor CSS prefixing        |

---

### 3. Backend Architecture

The backend is a FastAPI application with a layered module structure:

- **`main.py`** — The application entry point. It creates the FastAPI app instance, configures CORS middleware to allow requests from the frontend, and registers all route modules.

- **`routes/`** — Contains the HTTP route handlers:
  - **`chat.py`** — Handles `POST /api/chat`. Validates the incoming `ChatRequest` using Pydantic and delegates processing to the Chat Service.
  - **`account.py`** — Handles `POST /api/account/send-otp` and `POST /api/account/verify-otp`. Calls both the Email Service (to send the OTP) and the database module (to look up users and save verification state).

- **`services/`** — Contains the core business logic:
  - **`chat_service.py`** — Houses all intent handlers and response formatters. It calls `nlp.py` to classify the intent and then calls `db.py` to fetch any required data from the database before building a response.
  - **`email_service.py`** — Constructs and sends HTML-formatted OTP emails via Gmail SMTP with TLS.

- **`models/`** — Contains Pydantic data models:
  - **`chat_models.py`** — Defines the `ChatRequest` and `ChatResponse` schemas used by the chat route for request validation and response serialisation.

- **`nlp.py`** — Loads the trained Keras model on startup and exposes an intent detection function. It preprocesses input, computes the Bag-of-Words vector, runs ANN inference, and falls back to keyword matching if the model's confidence is below the threshold.

- **`db.py`** — The MySQL query executor. All database interactions (lookups, inserts, updates) across all routes and services are centralised here.

- **`migrate.py`** — A schema migration runner that applies versioned SQL scripts from the `migrations/` directory in order.

#### Backend Libraries

| Library                | Version   | Purpose                                     |
| ---------------------- | --------- | ------------------------------------------- |
| FastAPI                | ≥ 0.115.0 | Async REST API framework                    |
| Uvicorn                | ≥ 0.30.0  | ASGI web server                             |
| Pydantic               | ≥ 2.10.0  | Request/response validation & serialisation |
| TensorFlow / Keras     | ≥ 2.16.0  | ANN model loading & inference               |
| NumPy                  | ≥ 1.26.0  | Bag-of-words vector computation             |
| NLTK                   | ≥ 3.8.1   | Tokenisation + Lancaster stemming           |
| scikit-learn           | ≥ 1.4.0   | LabelEncoder, stratified train/val split    |
| mysql-connector-python | 8.3.0     | MySQL database driver                       |
| python-dotenv          | 1.0.0     | `.env` configuration loading                |
| langdetect             | ≥ 1.0.9   | Input language detection                    |
| python-multipart       | 0.0.6     | Form/multipart request parsing              |
| email-validator        | 2.1.0     | Email address validation                    |
| smtplib (stdlib)       | —         | SMTP email transmission                     |

---

## 4. NLP / AI Pipeline

The NLP pipeline has two distinct phases:

**Offline Training (`train_model.py`)**

1. **Load intents** — Read all training patterns and their associated intent tags from `intents.json`.
2. **Tokenise and stem** — Each pattern is tokenised into individual words, which are then reduced to their root forms using the NLTK Lancaster Stemmer.
3. **Build vocabulary** — All unique stemmed words are collected into a vocabulary and saved as `words.pkl`. All unique intent tags are saved as `classes.pkl`.
4. **Build feature matrix** — Every training pattern is encoded as a Bag-of-Words binary vector over the vocabulary.
5. **Stratified split** — The dataset is split into 85% training and 15% validation sets using scikit-learn's stratified split, preserving class proportions.
6. **Train the ANN** — The model is trained using TensorFlow/Keras with an Adam optimiser and cosine-decay learning rate schedule.
7. **Save artefacts** — The trained model is saved as `chatbot_model.keras` and the vocabulary/label artefacts as `words.pkl` and `classes.pkl` in the `models/` directory.

**Online Inference (`nlp.py`)**

The saved artefacts are loaded into memory once when the FastAPI server starts. For each incoming user message:

1. **Preprocess** — The message is lowercased and normalised.
2. **Tokenise and stem** — The message is split into tokens and each token is stemmed with the Lancaster Stemmer.
3. **Bag-of-Words encoding** — A NumPy binary vector is built from the stemmed tokens against the loaded vocabulary.
4. **ANN prediction** — The vector is passed to the Keras model, which outputs a probability distribution over all intent classes.
5. **Confidence check** — If the top predicted class meets or exceeds the confidence threshold, that intent is returned along with its score. If not, a keyword-matching fallback is applied to determine the intent.

### ANN Model Architecture

```
Input Layer  : Bag-of-Words vector  (vocab_size features)
Hidden 1     : Dense(256, ReLU) + BatchNormalization + Dropout(0.4)  + L2(5e-4)
Hidden 2     : Dense(128, ReLU) + BatchNormalization + Dropout(0.4)  + L2(5e-4)
Hidden 3     : Dense(64,  ReLU)                      + Dropout(0.2)
Output Layer : Dense(num_classes, Softmax)
Optimiser    : Adam + Cosine-Decay LR Schedule
Loss         : Categorical Cross-Entropy
```

---

## 5. Request / Response Workflow

The following steps describe the end-to-end lifecycle of a single chat message:

1. **User submits a message** — The user types a message and clicks Send in the React frontend.
2. **Optimistic UI update** — The frontend immediately appends the user's message as a chat bubble and shows the animated `TypingIndicator` to signal that a response is being prepared.
3. **HTTP request to backend** — The frontend sends a `POST /api/chat` request containing the message text, user ID, last detected intent (for context), and the verified account number (if the user is authenticated).
4. **Request validation** — FastAPI validates the incoming JSON body against the `ChatRequest` Pydantic schema, rejecting malformed requests early.
5. **Chat service invocation** — The route handler calls `process_chat_message()` in `chat_service.py`, passing the validated request data.
6. **Intent detection** — The Chat Service calls `detect_intent()` in `nlp.py`. The NLP module preprocesses the message, encodes it as a Bag-of-Words vector, and runs it through the Keras ANN. It returns the detected intent tag and its confidence score.
7. **Database query (conditional)** — If the detected intent requires live data (e.g., balance, transactions, loans, fixed deposits, or pawning), the Chat Service queries MySQL via `db.py` and retrieves the relevant rows.
8. **Response construction** — The Chat Service formats a reply string, combining any database results with intent-specific response templates.
9. **HTTP response to frontend** — The FastAPI route returns a `ChatResponse` JSON object containing the reply text, intent tag, confidence score, and any structured data payload.
10. **UI update** — The frontend hides the `TypingIndicator` and appends the bot's reply as a new chat bubble, which is displayed to the user.

---

## 6. Identity Verification (OTP) Workflow

The OTP-based identity verification flow consists of two phases:

**Phase 1 — Request OTP**

1. **User submits credentials** — The user opens the Account Panel and enters their email address, NIC (National Identity Card number), and account number.
2. **Send-OTP request** — The frontend sends a `POST /api/account/send-otp` request with these three fields.
3. **User lookup** — The backend queries MySQL via `get_user_by_email_and_account()` to verify that a matching user and account exist. If no match is found, a 404 error is returned.
4. **OTP generation** — A cryptographically random 6-digit OTP is generated and stored server-side in an in-memory `_otp_store` dictionary with a 5-minute time-to-live (TTL).
5. **Email delivery** — The backend calls `send_otp_email()`, which uses `email_service.py` to send an HTML-formatted email containing the OTP code to the user's address via Gmail SMTP with TLS on port 587.
6. **Acknowledgement** — The backend responds with a success message; the frontend prompts the user to check their email.

**Phase 2 — Verify OTP**

1. **User submits OTP** — The user enters the 6-digit code received in their email.
2. **Verify-OTP request** — The frontend sends a `POST /api/account/verify-otp` request with the code.
3. **OTP validation** — The backend looks up the code in `_otp_store`, checks it matches, and confirms it has not expired.
4. **Persist verification** — The backend records the verified user in the `verified_users` table via `save_verified_user()` in `db.py`.
5. **Session returned** — The backend responds with the account holder's name, account type, and user ID.
6. **Session stored** — The frontend stores this session data in `localStorage` so the user remains verified across page reloads, and the chat interface unlocks personal financial data.

---

## 7. Database Schema

The database consists of nine tables. The table structures and their fields are described below:

| Table               | Column           | Type      | Notes                                      |
| ------------------- | ---------------- | --------- | ------------------------------------------ |
| `users`             | id               | INT (PK)  | Auto-increment primary key                 |
|                     | name             | VARCHAR   | Full name of the account holder            |
|                     | email            | VARCHAR   | Unique email address                       |
|                     | id_number        | VARCHAR   | National Identity Card number              |
|                     | created_at       | TIMESTAMP | Record creation timestamp                  |
| `accounts`          | id               | INT (PK)  |                                            |
|                     | user_id          | INT (FK)  | References `users.id`                      |
|                     | account_number   | VARCHAR   | Unique bank account number                 |
|                     | account_type     | ENUM      | e.g., savings, current                     |
|                     | balance          | DECIMAL   | Current account balance                    |
|                     | status           | ENUM      | e.g., active, frozen                       |
| `transactions`      | id               | INT (PK)  |                                            |
|                     | account_id       | INT (FK)  | References `accounts.id`                   |
|                     | amount           | DECIMAL   | Transaction amount                         |
|                     | type             | ENUM      | credit or debit                            |
|                     | description      | VARCHAR   | Human-readable transaction description     |
|                     | date             | TIMESTAMP | Date and time of the transaction           |
|                     | balance_after    | DECIMAL   | Account balance after the transaction      |
| `chat_logs`         | id               | INT (PK)  |                                            |
|                     | user_id          | INT (FK)  | References `users.id`; nullable for guests |
|                     | request_message  | TEXT      | The user's original message                |
|                     | response         | TEXT      | The bot's reply                            |
|                     | intent           | VARCHAR   | Detected intent tag                        |
|                     | confidence       | DECIMAL   | Model confidence score                     |
| `unknown_questions` | id               | INT (PK)  |                                            |
|                     | question         | TEXT      | Message that could not be classified       |
|                     | created_at       | TIMESTAMP |                                            |
| `loans`             | id               | INT (PK)  |                                            |
|                     | user_id          | INT (FK)  | References `users.id`                      |
|                     | amount           | DECIMAL   | Loan principal amount                      |
|                     | interest_rate    | DECIMAL   | Annual interest rate                       |
|                     | status           | VARCHAR   | e.g., active, settled                      |
|                     | start_date       | DATE      |                                            |
|                     | end_date         | DATE      |                                            |
| `fixed_deposits`    | id               | INT (PK)  |                                            |
|                     | user_id          | INT (FK)  | References `users.id`                      |
|                     | amount           | DECIMAL   | Deposited principal                        |
|                     | interest_rate    | DECIMAL   | Annual interest rate                       |
|                     | maturity_date    | DATE      |                                            |
| `pawning`           | id               | INT (PK)  |                                            |
|                     | user_id          | INT (FK)  | References `users.id`                      |
|                     | item_description | VARCHAR   | Description of the pawned item             |
|                     | loan_amount      | DECIMAL   | Amount lent against the item               |
|                     | due_date         | DATE      |                                            |
| `verified_users`    | id               | INT (PK)  |                                            |
|                     | email            | VARCHAR   |                                            |
|                     | id_number        | VARCHAR   |                                            |
|                     | updated_at       | TIMESTAMP | Last OTP verification timestamp            |

**Relationships:**

- A `user` can have one or many `accounts` (one-to-many).
- Each `account` can have many `transactions` (one-to-many).
- A `user` generates many `chat_logs` (one-to-many).
- A `user` can hold many `loans`, `fixed_deposits`, and `pawning` records (one-to-many each).
- Each `user` has exactly one `verified_users` record once OTP verification is completed (one-to-one).

---

## 8. Supported Intents

| Intent Tag         | DB Required | Description                        |
| ------------------ | :---------: | ---------------------------------- |
| `GREETING`         |     No      | Salutation handling                |
| `GOODBYE`          |     No      | Farewell & thank-you               |
| `BALANCE`          |     ✅      | Account balance inquiry            |
| `TRANSACTIONS`     |     ✅      | Recent transaction history         |
| `LOAN`             |     ✅      | Loan products & eligibility info   |
| `FIXED_DEPOSIT`    |     ✅      | Fixed deposit rates & account info |
| `PAWNING`          |     ✅      | Pawning loan details               |
| `ACCOUNT_SERVICES` |     No      | Opening accounts, card services    |
| `TRANSFER`         |     No      | Fund transfer guidance             |
| `GENERAL`          |     No      | Hours, branches, ATMs, contacts    |
| `UNKNOWN`          |     No      | Unrecognised input fallback        |

---

## 9. Technology Stack Summary

The application is built on four technology groups that interact through well-defined interfaces:

**Frontend** — communicates with the backend via REST/JSON over HTTP:

- **React 18** + **TypeScript 5** — component-based UI with static type safety
- **Vite 5** — fast development server and production build tool
- **Tailwind CSS** — utility-first CSS framework for styling
- **Framer Motion** — animation library for transitions and the typing indicator
- **Axios** — HTTP client for all API calls

**Backend** — serves the frontend and orchestrates all business logic:

- **FastAPI** — async REST API framework
- **Uvicorn** — ASGI web server that runs the FastAPI application
- **Pydantic v2** — request/response data validation and serialisation
- **python-dotenv** — loads environment variables from `.env` files
- **langdetect** — detects the language of incoming messages

**AI / ML** — used by the backend to classify user intents:

- **TensorFlow 2.16+** / **Keras 3** — ANN model training and inference
- **NLTK 3.8+** — tokenisation and Lancaster stemming
- **NumPy 1.26+** — Bag-of-Words vector computation
- **scikit-learn 1.4+** — stratified train/validation splitting and label encoding

**Infrastructure** — data persistence and external communication:

- **MySQL 8** — relational database for all application data
- **mysql-connector-python** — Python driver for MySQL connectivity
- **Gmail SMTP with TLS** (port 587) via the standard **smtplib** library — used to deliver OTP emails

---

## 10. Deployment Layout

```
Bank-Assistant-AI/
├── frontend/                  # React SPA (served by Vite / build → dist/)
│   ├── src/
│   │   ├── App.tsx            # Root component + session state
│   │   ├── api.ts             # Axios API client
│   │   └── components/        # UI components
│   ├── tailwind.config.js
│   └── vite.config.ts
│
└── backend/                   # FastAPI application
    ├── main.py                # App bootstrap + CORS + router registration
    ├── nlp.py                 # Intent detection (ANN + keyword fallback)
    ├── db.py                  # MySQL connection pool + query functions
    ├── train_model.py         # Offline ANN training script
    ├── migrate.py             # Database migration runner
    ├── routes/
    │   ├── chat.py            # POST /api/chat
    │   └── account.py         # POST /api/account/{send,verify}-otp
    ├── services/
    │   ├── chat_service.py    # Intent handlers + response builders
    │   └── email_service.py   # HTML OTP email via SMTP
    ├── models/
    │   ├── chat_models.py     # Pydantic request/response models
    │   ├── chatbot_model.keras # Trained ANN (generated by train_model.py)
    │   ├── words.pkl          # Stemmed vocabulary artefact
    │   └── classes.pkl        # Intent label artefact
    ├── intents/
    │   └── intents.json       # Training patterns, keywords, tags
    └── migrations/            # Versioned SQL migration files
        ├── V001__initial_schema.sql
        ├── V002__add_loans_fd_pawning_tables_and_seed_data.sql
        ├── V003__add_verified_users.sql
        └── V004__add_id_number_to_users.sql
```
