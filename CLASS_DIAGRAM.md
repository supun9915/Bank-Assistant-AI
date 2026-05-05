# Class Diagram — Smart Banking Assistant

## Overview

The project is structured around five main logical units: **API Models**, **Routes**, **Services**, **NLP Engine**, and **Data Access Layer**. Python does not enforce strict class-based OOP for every module — service logic is implemented as module-level functions rather than class instances — but the class diagram below accurately maps each module's public interface and relationships.

---

## Full Class Diagram

```mermaid
classDiagram

    %% ─────────────────────────────────────────────
    %% Pydantic Models  (models/chat_models.py)
    %% ─────────────────────────────────────────────

    class ChatRequest {
        +str message
        +int user_id
        +Optional~str~ last_intent
        +Optional~str~ account_number
        +validate_message() str
    }

    class ChatResponse {
        +str reply
        +Optional~str~ intent
        +Optional~float~ confidence
        +Optional~dict~ data
    }

    class OTPSendRequest {
        +str account_number
        +str id_number
        +str email
    }

    class OTPVerifyRequest {
        +str account_number
        +str otp
    }

    class OTPVerifyResponse {
        +str message
        +int user_id
        +str account_number
        +str account_holder
        +str account_type
    }

    %% ─────────────────────────────────────────────
    %% Routes  (routes/)
    %% ─────────────────────────────────────────────

    class ChatRouter {
        <<FastAPI Router>>
        +POST_api_chat(request: ChatRequest) ChatResponse
        +GET_api_chat_health() dict
    }

    class AccountRouter {
        <<FastAPI Router>>
        -_otp_store: dict
        +POST_send_otp(request: OTPSendRequest) dict
        +POST_verify_otp(request: OTPVerifyRequest) OTPVerifyResponse
        -_generate_otp() str
        -_is_otp_valid(account_number, otp) bool
    }

    %% ─────────────────────────────────────────────
    %% Chat Service  (services/chat_service.py)
    %% ─────────────────────────────────────────────

    class ChatService {
        <<Service Module>>
        +process_chat_message(request: ChatRequest) ChatResponse
        +handle_greeting_intent() str
        +handle_goodbye_intent() str
        +handle_balance_intent(user_id, account_number) dict
        +handle_transactions_intent(user_id, account_number) dict
        +handle_loan_intent(message) str
        +handle_account_services_intent(message) str
        +handle_security_intent(message) str
        +handle_transfers_intent(message) str
        +handle_fees_intent(message) str
        +handle_digital_banking_intent(message) str
        +handle_general_intent(message) str
        +handle_fixed_deposit_intent(user_id, account_number) dict
        +handle_pawning_intent(user_id, account_number) dict
        +handle_foreign_exchange_intent() str
        +handle_forgot_email_intent() str
        +handle_profanity_intent() str
        +handle_capabilities_intent() str
        +handle_unknown_intent(message, user_id) str
        +handle_action_request(message) str
        -_require_account_selection() str
        -_is_action_request(message) bool
        -_try_context_fallback(message, last_intent) str
        -_detect_subtopic(message, subtopics) str
        -format_balance_response(balance) str
        -format_transactions_response(transactions) str
    }

    %% ─────────────────────────────────────────────
    %% Email Service  (services/email_service.py)
    %% ─────────────────────────────────────────────

    class EmailService {
        <<Service Module>>
        +send_otp_email(recipient_email, otp, account_holder_name) bool
        -_build_html_body(otp, name) str
    }

    %% ─────────────────────────────────────────────
    %% NLP Engine  (nlp.py)
    %% ─────────────────────────────────────────────

    class NLPEngine {
        <<NLP Module>>
        -THRESHOLD: float = 0.40
        -HYBRID_MIN: float = 0.25
        -_model: keras.Model
        -_words: list
        -_classes: list
        -_intents: list
        -_stemmer: LancasterStemmer
        +detect_intent(message) tuple~str, float~
        +extract_entities(message) dict
        +reload_intents() void
        -preprocess_text(text) str
        -_tokenize_and_stem(text) list
        -_bag_of_words(text) ndarray
        -_has_meaningful_text(text) bool
        -_keyword_fallback(text) tuple~str, float~
        -_language_guard(text) Optional~str~
        -_unicode_range_check(text) bool
        -_langdetect_check(text) bool
    }

    %% ─────────────────────────────────────────────
    %% Data Access Layer  (db.py)
    %% ─────────────────────────────────────────────

    class Database {
        <<Data Access Module>>
        +get_db_connection() ContextManager~Connection~
        +get_user_by_id(user_id) Optional~dict~
        +get_user_by_email_and_account(email, id_number, account_number) Optional~dict~
        +save_verified_user(email, id_number) void
        +get_account_balance(account_number) Optional~decimal~
        +get_recent_transactions(account_number, limit) list~dict~
        +get_user_loans(user_id) list~dict~
        +get_user_fixed_deposits(user_id) list~dict~
        +get_user_pawning(user_id) list~dict~
        +save_chat_log(user_id, message, response, intent, confidence) void
        +save_unknown_question(question) void
        +get_all_unknown_questions() list~dict~
        +test_connection() bool
    }

    %% ─────────────────────────────────────────────
    %% FastAPI Application  (main.py)
    %% ─────────────────────────────────────────────

    class FastAPIApp {
        <<Application>>
        +app: FastAPI
        +title: str = "Smart Banking Assistant API"
        +version: str
        +CORS_middleware()
        +include_router(ChatRouter)
        +include_router(AccountRouter)
        +root_health_check() dict
        +detailed_health_check() dict
    }

    %% ─────────────────────────────────────────────
    %% Relationships
    %% ─────────────────────────────────────────────

    FastAPIApp "1" --> "1" ChatRouter        : registers
    FastAPIApp "1" --> "1" AccountRouter     : registers

    ChatRouter ..> ChatRequest              : validates input
    ChatRouter ..> ChatResponse             : returns
    ChatRouter "1" --> "1" ChatService      : delegates to

    AccountRouter ..> OTPSendRequest        : validates
    AccountRouter ..> OTPVerifyRequest      : validates
    AccountRouter ..> OTPVerifyResponse     : returns
    AccountRouter "1" --> "1" EmailService  : sends OTP via
    AccountRouter "1" --> "1" Database      : verifies identity via

    ChatService "1" --> "1" NLPEngine       : detect_intent()
    ChatService "1" --> "1" Database        : queries & logs

    NLPEngine ..> ChatRequest               : reads message

    EmailService ..> Database               : (indirect — account validated in router)
```

---

## Simplified Relationship View

```mermaid
classDiagram

    class FastAPIApp {
        +app FastAPI
        +routers list
    }

    class ChatRouter {
        +POST /api/chat
    }

    class AccountRouter {
        +POST /api/account/send-otp
        +POST /api/account/verify-otp
    }

    class ChatService {
        +process_chat_message()
        +19 handle_* methods
    }

    class NLPEngine {
        +detect_intent()
        +language_guard()
        +keyword_fallback()
    }

    class Database {
        +get_account_balance()
        +get_recent_transactions()
        +save_chat_log()
    }

    class EmailService {
        +send_otp_email()
    }

    class ChatRequest {
        +message str
        +user_id int
        +account_number str
    }

    class ChatResponse {
        +reply str
        +intent str
        +confidence float
        +data dict
    }

    FastAPIApp --> ChatRouter
    FastAPIApp --> AccountRouter
    ChatRouter --> ChatService : uses
    ChatService --> NLPEngine : calls detect_intent()
    ChatService --> Database : queries & logs
    AccountRouter --> EmailService : sends OTP
    AccountRouter --> Database : validates identity
    ChatRouter ..> ChatRequest : input model
    ChatRouter ..> ChatResponse : output model
```

---

## Module Dependency Graph

```mermaid
graph TD
    main["main.py\n(FastAPI App)"]

    chat_route["routes/chat.py"]
    account_route["routes/account.py"]

    chat_service["services/chat_service.py"]
    email_service["services/email_service.py"]

    nlp["nlp.py\n(NLP Engine)"]
    db["db.py\n(Data Access)"]

    models_dir["models/chat_models.py\n(Pydantic Models)"]
    keras_model["models/chatbot_model.keras\n(Trained ANN)"]
    intents_json["intents/intents.json\n(Training Data)"]

    mysql[("MySQL\nbanking_chatbot")]
    smtp["SMTP Server"]

    main --> chat_route
    main --> account_route

    chat_route --> chat_service
    chat_route --> models_dir

    account_route --> email_service
    account_route --> db

    chat_service --> nlp
    chat_service --> db

    nlp --> keras_model
    nlp --> intents_json

    db --> mysql
    email_service --> smtp
```

---

## Intent Handler Dispatch Table

The `process_chat_message()` function routes detected intents to handlers in the following order:

| Priority | Intent                                                  | Handler                            | Auth Required              |
| -------- | ------------------------------------------------------- | ---------------------------------- | -------------------------- |
| 1        | Language guard                                          | _(returns early)_                  | No                         |
| 2        | Action request                                          | `handle_action_request()`          | No                         |
| 3        | `GREETING`                                              | `handle_greeting_intent()`         | No                         |
| 4        | `GOODBYE`                                               | `handle_goodbye_intent()`          | No                         |
| 5        | `BALANCE`                                               | `handle_balance_intent()`          | **Yes**                    |
| 6        | `TRANSACTIONS`                                          | `handle_transactions_intent()`     | **Yes**                    |
| 7        | `LOAN`                                                  | `handle_loan_intent()`             | No                         |
| 8        | `ACCOUNT_SERVICES`                                      | `handle_account_services_intent()` | No                         |
| 9        | `SECURITY`                                              | `handle_security_intent()`         | No                         |
| 10       | `TRANSFERS`                                             | `handle_transfers_intent()`        | No                         |
| 11       | `FEES`                                                  | `handle_fees_intent()`             | No                         |
| 12       | `DIGITAL_BANKING`                                       | `handle_digital_banking_intent()`  | No                         |
| 13       | `GENERAL`                                               | `handle_general_intent()`          | No                         |
| 14       | `FIXED_DEPOSIT`                                         | `handle_fixed_deposit_intent()`    | **Yes** (personal FDs)     |
| 15       | `PAWNING`                                               | `handle_pawning_intent()`          | **Yes** (personal tickets) |
| 16       | `FOREIGN_EXCHANGE`                                      | `handle_foreign_exchange_intent()` | No                         |
| 17       | `FORGOT_EMAIL`                                          | `handle_forgot_email_intent()`     | No                         |
| 18       | `PROFANITY_RESPONSE`                                    | `handle_profanity_intent()`        | No                         |
| 19       | `CAPABILITIES`                                          | `handle_capabilities_intent()`     | No                         |
| 20       | `UNKNOWN`                                               | `handle_unknown_intent()`          | No                         |
| 21       | `CARDS` / `INVESTMENTS` / `CREDIT_SCORE` / `COMPLAINTS` | _(via NLP → general handler)_      | No                         |
