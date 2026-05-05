# Architecture Diagram — Smart Banking Assistant

## System Overview

The Smart Banking Assistant follows a **Layered Architecture** pattern with four distinct layers: Presentation, Business Logic, Data Access, and Data Storage. All communication is RESTful JSON over HTTP.

---

## High-Level Architecture

```mermaid
graph TD
    subgraph CLIENT["🖥️ Client Layer"]
        B["Browser / Web App"]
        P["Postman / API Client"]
        C["cURL / Other HTTP Clients"]
    end

    subgraph SERVER["🐍 Python Backend  ─  Port 8000"]
        subgraph ASGI["Uvicorn ASGI Server"]
            subgraph FASTAPI["FastAPI Application  (main.py)"]
                MW["CORS Middleware\n(all origins in dev)"]

                subgraph ROUTES["📡 Routes Layer"]
                    RC["routes/chat.py\nPOST /api/chat\nGET /api/chat/health"]
                    RA["routes/account.py\nPOST /api/account/send-otp\nPOST /api/account/verify-otp"]
                end

                subgraph SERVICES["⚙️ Services Layer"]
                    CS["chat_service.py\nprocess_chat_message()\n19 intent handlers"]
                    ES["email_service.py\nsend_otp_email()"]
                end

                subgraph NLP["🧠 NLP Engine  (nlp.py)"]
                    LG["Language Guard\nUnicode ranges + langdetect"]
                    PP["Preprocessor\nLancaster stemmer + BoW encoder"]
                    ANN["TensorFlow / Keras ANN\n22-class softmax\nthreshold = 0.40"]
                    KF["NLTK Keyword Fallback\nWeighted keyword matching"]
                end

                DB_LAYER["🗄️ Data Access Layer  (db.py)\nParameterised SQL queries\nContext-manager connections"]
            end
        end
    end

    subgraph STORAGE["💾 Data Storage"]
        MYSQL[("MySQL 8.x\ndatabase: banking_chatbot\nPort 3306")]
        MODEL["Model Artefacts\nmodels/chatbot_model.keras\nmodels/words.pkl\nmodels/classes.pkl"]
        INTENTS["intents/intents.json\n22 intents · 1142 samples"]
        OTP_MEM["In-Memory OTP Store\n_otp_store dict\n5-minute TTL"]
    end

    subgraph EXTERNAL["🌐 External Services"]
        SMTP["SMTP Server\nsmtp.gmail.com:587\n(OTP email delivery)"]
    end

    %% Client → Server
    B & P & C -->|"HTTP JSON"| MW
    MW --> RC & RA

    %% Routes → Services
    RC --> CS
    RA --> ES
    RA --> DB_LAYER
    RA <--> OTP_MEM

    %% Services → NLP + DB
    CS --> LG
    LG --> PP
    PP --> ANN
    ANN -->|"confidence < 0.40"| KF
    CS --> DB_LAYER

    %% DB Layer → MySQL
    DB_LAYER <-->|"SQL"| MYSQL

    %% Email Service → SMTP
    ES -->|"SMTP TLS"| SMTP

    %% Model loading
    ANN <-->|"load on startup"| MODEL
    LG & PP <-->|"read"| INTENTS
```

---

## Request Processing Pipeline

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI as FastAPI (routes/chat.py)
    participant Service as chat_service.py
    participant NLP as nlp.py
    participant DB as db.py
    participant MySQL

    Client->>FastAPI: POST /api/chat {"message": "...", "account_number": "..."}
    FastAPI->>FastAPI: Pydantic validation (ChatRequest)
    FastAPI->>Service: process_chat_message(request)

    Service->>NLP: Language guard check
    alt Non-English detected
        NLP-->>Service: UNSUPPORTED_LANGUAGE
        Service-->>FastAPI: "English-only" reply
        FastAPI-->>Client: 200 JSON
    end

    Service->>Service: _is_action_request(message)?
    alt Action request detected
        Service-->>FastAPI: Action redirect reply
        FastAPI-->>Client: 200 JSON
    end

    Service->>NLP: detect_intent(message)
    NLP->>NLP: preprocess + bag-of-words encode
    NLP->>NLP: ANN inference (softmax)
    alt confidence >= 0.40
        NLP-->>Service: (intent, confidence)
    else confidence < 0.40
        NLP->>NLP: keyword fallback
        NLP-->>Service: (intent, confidence)
    end

    Service->>Service: Requires account_number?
    alt account_number missing
        Service-->>FastAPI: OTP verification prompt
        FastAPI-->>Client: 200 JSON
    end

    Service->>DB: Query (balance / transactions / FDs / pawning)
    DB->>MySQL: SELECT (parameterised)
    MySQL-->>DB: Result rows
    DB-->>Service: Formatted data

    Service->>DB: save_chat_log(...)
    DB->>MySQL: INSERT chat_logs

    Service-->>FastAPI: ChatResponse {reply, intent, confidence, data}
    FastAPI-->>Client: 200 JSON
```

---

## OTP Verification Flow

```mermaid
sequenceDiagram
    participant Client
    participant Account as routes/account.py
    participant DB as db.py
    participant OTPStore as In-Memory OTP Store
    participant Email as email_service.py
    participant SMTP as Gmail SMTP

    Client->>Account: POST /api/account/send-otp\n{email, id_number, account_number}
    Account->>DB: get_user_by_email_and_account(...)
    DB-->>Account: user record (or None)
    alt credentials invalid
        Account-->>Client: 400 "Credentials not found"
    end
    Account->>Account: Generate 6-digit OTP
    Account->>OTPStore: Store {account_number → {otp, expiry: now+5min}}
    Account->>Email: send_otp_email(email, otp, name)
    Email->>SMTP: SMTP TLS connection + send HTML email
    SMTP-->>Email: Sent
    Account-->>Client: 200 "OTP sent"

    Client->>Account: POST /api/account/verify-otp\n{account_number, otp}
    Account->>OTPStore: Lookup OTP by account_number
    alt OTP expired or not found
        Account-->>Client: 400 "OTP expired"
    end
    alt OTP mismatch
        Account-->>Client: 400 "Invalid OTP"
    end
    Account->>OTPStore: Delete OTP entry
    Account->>DB: save_verified_user(email, id_number)
    Account-->>Client: 200 {user_id, account_number, account_holder, account_type}
```

---

## NLP Engine — Intent Detection Pipeline

```mermaid
flowchart TD
    INPUT["User Message"] --> LG

    LG{"Language Guard\nStep 1: Unicode ranges\nStep 2: langdetect (3+ words)"}
    LG -- Non-English --> UL["UNSUPPORTED_LANGUAGE ❌"]
    LG -- English --> MT

    MT{"_has_meaningful_text()\n>= 2 alphabetic chars?"}
    MT -- No --> UNK1["UNKNOWN ❌"]
    MT -- Yes --> STEM

    STEM["Tokenise + Lancaster Stem\nBag-of-Words vector (|vocab| dims)"]
    STEM --> ANN

    ANN["TensorFlow ANN\nDense(256)→BN→Dropout(0.4)\nDense(128)→BN→Dropout(0.3)\nDense(64)→Dropout\nDense(22, softmax)"]
    ANN --> CONF

    CONF{"Top-1 confidence\n>= 0.40?"}
    CONF -- Yes --> RETURN_ANN["Return (intent, confidence) ✅"]
    CONF -- No --> KFB

    KFB["NLTK Keyword Fallback\nWeighted keyword match\nacross all intents"]
    KFB --> AGREE

    AGREE{"ANN and keyword\nagree AND ANN >= 0.25?"}
    AGREE -- Yes --> RETURN_ANN2["Return (intent, ANN_confidence) ✅"]
    AGREE -- No --> RETURN_KW["Return (keyword_intent, keyword_score) ✅"]
```

---

## Layered Architecture Summary

```mermaid
graph LR
    subgraph L1["Layer 1: Presentation"]
        R1["routes/chat.py"]
        R2["routes/account.py"]
    end

    subgraph L2["Layer 2: Business Logic"]
        S1["chat_service.py\n19 intent handlers"]
        S2["email_service.py"]
    end

    subgraph L3["Layer 3: Intelligence"]
        N1["nlp.py\nANN + keyword fallback + language guard"]
        N2["models/chatbot_model.keras\nwords.pkl · classes.pkl"]
    end

    subgraph L4["Layer 4: Data Access"]
        D1["db.py\nParameterised SQL"]
    end

    subgraph L5["Layer 5: Storage"]
        M1[("MySQL\nbanking_chatbot")]
    end

    L1 --> L2
    L2 --> L3
    L2 --> L4
    L3 <--> N2
    L4 --> L5
```

---

## Technology Stack Summary

| Layer              | Technology                    | Version   |
| ------------------ | ----------------------------- | --------- |
| Runtime            | Python / CPython              | 3.10+     |
| ASGI Server        | Uvicorn                       | ≥ 0.30.0  |
| Web Framework      | FastAPI                       | ≥ 0.115.0 |
| Data Validation    | Pydantic                      | ≥ 2.10.0  |
| NLP Preprocessing  | NLTK (Lancaster stemmer)      | ≥ 3.8.1   |
| ANN Model          | TensorFlow / Keras 3          | ≥ 2.16.0  |
| Numerical Arrays   | NumPy                         | ≥ 1.26.0  |
| ML Utilities       | scikit-learn                  | ≥ 1.4.0   |
| Language Detection | langdetect                    | ≥ 1.0.9   |
| Database Driver    | mysql-connector-python        | 8.3.0     |
| Database Engine    | MySQL                         | 8.x       |
| Email Delivery     | smtplib (stdlib) + Gmail SMTP | built-in  |
| Config Management  | python-dotenv                 | 1.0.0     |
