"""
Chat service - Core business logic for chat processing
"""
import re
import logging
from typing import Dict, Any, Optional
from langdetect import detect as _lang_detect, LangDetectException
from nlp import detect_intent
from db import (
    get_account_balance,
    get_recent_transactions,
    save_unknown_question,
    save_chat_log,
    get_user_by_email_and_account,
    get_user_fixed_deposits,
    get_user_pawning,
)

logger = logging.getLogger(__name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _detect_subtopic(message: str, subtopic_keywords: dict) -> Optional[str]:
    """Return the best-matching subtopic key or None."""
    message_lower = message.lower()
    best, best_score = None, 0
    for topic, keywords in subtopic_keywords.items():
        score = sum(1 for kw in keywords if kw in message_lower)
        if score > best_score:
            best_score, best = score, topic
    return best if best_score > 0 else None


def _is_action_request(message: str) -> bool:
    """Return True if the user explicitly wants to perform a banking action (not just ask for info)."""
    message_lower = message.lower().strip()
    # Question/info starters → not an action
    info_starters = (
        "what", "how", "which", "when", "where", "who", "why",
        "tell me", "explain", "describe", "can you tell", "could you tell",
        "do you", "is there", "are there", "what's", "whats", "is it",
        "show me", "list", "give me info", "give me information"
    )
    if any(message_lower.startswith(s) for s in info_starters):
        return False
    action_patterns = [
        r"\bi (want|wish|need|would like) to (open|create|apply|get|take|make|start)\b",
        r"\bi'?d like to (open|create|apply|get|take|start)\b",
        r"\bi would like to (open|create|apply|get|take|start)\b",
        r"\bi need (a|an) (loan|account|card|mortgage)\b",
        r"\bplease (open|create|apply|register)\b",
        r"\bapply for (a |an )?(loan|account|card|mortgage)\b",
        r"\b(open|create|start) (a |an |new )?(account|loan)\b",
        r"\bsign me up\b",
        r"\bi want (a|an|to get) (loan|account|mortgage|card)\b",
    ]
    return any(re.search(p, message_lower) for p in action_patterns)


def _try_context_fallback(message: str, last_intent: str) -> Optional[Dict[str, Any]]:
    """Try to give a context-aware answer when current intent is UNKNOWN."""
    message_lower = message.lower()
    if last_intent == "ACCOUNT_SERVICES":
        if any(w in message_lower for w in ["detail", "required", "requirement", "document", "need", "what", "more", "else"]):
            return handle_account_services_intent("required details " + message, last_intent)
    if last_intent == "LOAN":
        if any(w in message_lower for w in ["lowest", "cheapest", "best", "which", "rate", "interest", "more"]):
            return handle_loan_intent(message)
    if last_intent == "FIXED_DEPOSIT":
        if any(w in message_lower for w in ["rate", "interest", "maturity", "renew", "break", "more", "detail"]):
            return handle_fixed_deposit_intent(message)
    if last_intent == "PAWNING":
        if any(w in message_lower for w in ["rate", "interest", "redeem", "extend", "more", "detail", "due"]):
            return handle_pawning_intent(message)
    if last_intent == "GENERAL":
        if any(w in message_lower for w in ["hour", "time", "open", "close", "contact", "branch", "atm"]):
            return handle_general_intent(message)
    return None


# ── Response formatters ───────────────────────────────────────────────────────

def format_balance_response(balance: float) -> str:
    """Format balance as currency string"""
    return f"${balance:,.2f}"


def format_transactions_response(transactions: list) -> str:
    """Format transaction list into readable string"""
    if not transactions:
        return "No recent transactions found."

    response = "Here are your recent transactions:\n\n"

    for idx, txn in enumerate(transactions, 1):
        amount = txn['amount']
        txn_type = txn['type']
        date = txn['date'].strftime('%Y-%m-%d') if hasattr(txn['date'], 'strftime') else str(txn['date'])
        description = txn.get('description', 'N/A')

        amount_str = f"+${amount:,.2f}" if txn_type == 'credit' else f"-${amount:,.2f}"

        response += f"{idx}. {amount_str} ({txn_type.upper()}) - {date}\n"
        response += f"   {description}\n\n"

    return response.strip()


# ── Intent handlers ───────────────────────────────────────────────────────────

# Personal-data intents that require an account to be selected
_ACCOUNT_REQUIRED_INTENTS = frozenset(["BALANCE", "TRANSACTIONS", "FIXED_DEPOSIT", "PAWNING"])


def _require_account_selection() -> Dict[str, Any]:
    """Reply telling the user to verify their account first."""
    return {
        "reply": (
            "🔒 This information is personal to your account.\n\n"
            "To view your account details, please verify your identity first:\n\n"
            "1️⃣  Click the 👤 **Account** button in the top-right of the chat\n"
            "2️⃣  Enter your registered Email, National ID Number, and Account Number\n"
            "3️⃣  Enter the 6-digit OTP sent to your email\n\n"
            "Once verified, I can show you your personal banking information."
        ),
        "intent": "ACCOUNT_REQUIRED",
        "confidence": 1.0,
    }


def handle_greeting_intent() -> Dict[str, Any]:
    """Handle GREETING intent"""
    import random
    replies = [
        "Hello! How can I help you with your banking today?",
        "Hi there! What can I do for you today?",
        "Hey! How can I assist you with your banking needs?",
        "Good day! How can I help you today?",
        "Hello! Feel free to ask me about your account, loans, transfers, or any other banking service.",
    ]
    return {
        "reply": random.choice(replies),
        "intent": "GREETING",
        "confidence": 1.0
    }


def handle_goodbye_intent() -> Dict[str, Any]:
    """Handle GOODBYE intent — farewell, thank you, end of chat"""
    import random
    replies = [
        (
            "Thank you for banking with us! It was a pleasure assisting you today. "
            "Have a wonderful day, and feel free to come back anytime you need help! 😊"
        ),
        (
            "You're very welcome! It was great helping you. "
            "Take care and have a fantastic day! Goodbye! 👋"
        ),
        (
            "Thank you for reaching out — glad I could help! "
            "Wishing you a great day ahead. Don't hesitate to come back if you have any questions. 😊"
        ),
        (
            "It was my pleasure assisting you! "
            "Have a wonderful day and stay safe. Goodbye! 👋"
        ),
        (
            "Thank you for using our Smart Banking Assistant! "
            "Feel free to chat with us anytime. Have a great day! 😊"
        ),
    ]
    return {
        "reply": random.choice(replies),
        "intent": "GOODBYE",
        "confidence": 1.0
    }


def handle_balance_intent(user_id: int = 1) -> Dict[str, Any]:
    """Handle BALANCE intent"""
    balance = get_account_balance(user_id)

    if balance is not None:
        formatted_balance = format_balance_response(balance)
        return {
            "reply": f"Your current account balance is {formatted_balance}. Is there anything else I can help you with?",
            "intent": "BALANCE",
            "confidence": 0.9,
            "data": {"balance": balance}
        }
    else:
        return {
            "reply": "I'm sorry, I wasn't able to retrieve your balance at the moment. Please try again shortly, or call us at 1-800-BANKING for immediate assistance.",
            "intent": "BALANCE",
            "confidence": 0.9,
            "data": None
        }


def handle_transactions_intent(user_id: int = 1, limit: int = 5) -> Dict[str, Any]:
    """Handle TRANSACTIONS intent"""
    transactions = get_recent_transactions(user_id, limit)

    if transactions:
        formatted_txns = format_transactions_response(transactions)
        return {
            "reply": formatted_txns + "\n\nIs there anything else I can help you with?",
            "intent": "TRANSACTIONS",
            "confidence": 0.9,
            "data": {"transactions": transactions}
        }
    else:
        return {
            "reply": "It looks like you don't have any recent transactions. Is there anything else I can help you with?",
            "intent": "TRANSACTIONS",
            "confidence": 0.9,
            "data": {"transactions": []}
        }


def handle_loan_intent(message: str = "") -> Dict[str, Any]:
    """Handle LOAN intent with focused sub-topic responses"""
    message_lower = message.lower()

    if any(w in message_lower for w in [
        "required", "requirement", "document", "what do i need", "what is needed",
        "criteria", "eligibility", "details needed", "needed to apply", "apply for",
        "how to apply", "application process", "what are the required"
    ]):
        reply = (
            "To apply for a loan at Smart Bank, you will need the following:\n\n"
            "📋 **Required Documents:**\n"
            "• Valid government-issued photo ID (Passport, NIC, or Driving License)\n"
            "• Proof of address (utility bill or bank statement — within the last 3 months)\n"
            "• Proof of income (recent pay slips, employment letter, or bank statements for 3–6 months)\n"
            "• For business loans: business registration documents and financial statements\n\n"
            "✅ **Basic Eligibility:**\n"
            "• Minimum age: 18 years\n"
            "• Must be a Smart Bank account holder\n"
            "• Stable source of income\n"
            "• Good credit history\n\n"
            "📍 To apply, visit your nearest branch or call **1-800-BANKING** to schedule an appointment.\n\n"
            "Would you like to know about our loan interest rates or types of loans available?"
        )
        return {"reply": reply, "intent": "LOAN", "confidence": 0.9}

    if any(w in message_lower for w in ["lowest", "cheapest", "minimum", "best rate", "low interest", "minimum rate", "lowest rate", "best interest"]):
        reply = (
            "Great question! Among all our loan options, the Home Loan offers the lowest interest rate:\n\n"
            "• Home Loans: 6% – 9% per annum (lowest available)\n"
            "• Car Loans: 7% – 11% per annum\n"
            "• Personal Loans: 8% – 12% per annum\n\n"
            "Home loans offer competitive rates as they are secured by the property. "
            "Would you like more details about eligibility or repayment terms?"
        )
    else:
        reply = (
            "We offer a range of loan options to suit your needs:\n\n"
            "• Personal Loans: 8% – 12% interest rate per annum\n"
            "• Home Loans: 6% – 9% interest rate per annum\n"
            "• Car Loans: 7% – 11% interest rate per annum\n\n"
            "Each loan has different eligibility criteria and repayment terms. "
            "Is there a specific loan type you'd like to know more about?"
        )

    return {"reply": reply, "intent": "LOAN", "confidence": 0.9}


def handle_action_request(message: str = "") -> Dict[str, Any]:
    """Handle requests to perform banking actions — redirect to a branch."""
    message_lower = message.lower()

    if any(w in message_lower for w in ["loan", "borrow", "mortgage", "financing"]):
        reply = (
            "Thank you for your interest in our loan services!\n\n"
            "I'm an AI assistant and can provide you with information, "
            "but to actually apply for a loan you'll need to speak with one of our loan specialists.\n\n"
            "Here's how to get started:\n"
            "• Visit your nearest branch with a valid ID and proof of income\n"
            "• Call us at 1-800-BANKING to schedule an appointment\n"
            "• Email us at support@smartbank.com\n\n"
            "Our team will be happy to guide you through the entire process. "
            "In the meantime, would you like to know about our loan options or interest rates?"
        )
    else:
        reply = (
            "Thank you for choosing Smart Bank!\n\n"
            "I'm an AI assistant and can provide guidance, "
            "but to actually open a new account you'll need to visit us in person.\n\n"
            "Here's what to bring:\n"
            "• A valid government-issued photo ID (Passport, NIC, or Driving License)\n"
            "• Proof of address (utility bill or bank statement within the last 3 months)\n"
            "• Your active mobile number and email address\n\n"
            "Please visit any branch during working hours (Mon–Fri: 9AM–5PM, Sat: 9AM–1PM). "
            "Our staff will be delighted to assist you! Is there anything else I can help you with?"
        )

    return {"reply": reply, "intent": "ACTION_REQUEST", "confidence": 0.95}


def handle_account_services_intent(message: str = "", last_intent: str = "") -> Dict[str, Any]:
    """Handle ACCOUNT_SERVICES intent with context-aware sub-topic detection"""
    subtopics = {
        "requirements": [
            "required", "requirement", "document", "need to bring", "what do i need",
            "what is needed", "what details", "needed detail", "details needed",
            "required detail", "need for", "what are the", "necessary"
        ],
        "open_account": [
            "open account", "create account", "new account", "how to open",
            "how to create", "start account", "opening a", "account opening"
        ],
        "close_account": ["close account", "closing", "close my account", "terminate account"],
        "update": [
            "update", "change phone", "change email", "update email",
            "update phone", "change number", "update detail", "change detail"
        ],
        "statement": ["statement", "account statement", "my statement"],
        "activate": ["activate", "activation"],
    }

    subtopic = _detect_subtopic(message, subtopics)

    # Context-aware: follow-up on ACCOUNT_SERVICES with a vague "details" query
    if subtopic is None and last_intent == "ACCOUNT_SERVICES":
        message_lower = message.lower()
        if any(w in message_lower for w in ["detail", "more", "what else", "requirement", "and", "also", "need"]):
            subtopic = "requirements"

    if subtopic == "requirements":
        reply = (
            "To open a new account with Smart Bank, you'll need to bring the following:\n\n"
            "• A valid government-issued photo ID (Passport, NIC, or Driving License)\n"
            "• Proof of address (utility bill or bank statement — within the last 3 months)\n"
            "• Your active mobile number\n"
            "• Your email address\n\n"
            "That's all! Our friendly staff at any branch will guide you through the rest. "
            "Is there anything else I can help you with?"
        )
    elif subtopic == "open_account":
        reply = (
            "Opening a new account with Smart Bank is easy!\n\n"
            "• Visit any of our branches with a valid ID and proof of address\n"
            "• Our staff will assist you through the account opening process\n"
            "• It typically takes about 15–20 minutes\n\n"
            "Would you like to know what specific documents you need to bring?"
        )
    elif subtopic == "close_account":
        reply = (
            "We're sorry to hear you'd like to close your account. If you do need to proceed:\n\n"
            "• Visit any branch in person with your valid ID\n"
            "• Or call us at 1-800-BANKING for further assistance\n\n"
            "Please ensure there are no pending transactions before closure. "
            "Is there anything else I can help you with?"
        )
    elif subtopic == "update":
        reply = (
            "Updating your account details is quick and easy!\n\n"
            "• Online Banking: Log in at www.smartbank.com > Settings > Profile\n"
            "• Mobile App: Settings > Profile > Update Details\n"
            "• Branch: Visit any branch with your valid ID\n\n"
            "Some changes may require in-branch verification for your security. "
            "Is there anything else I can help you with?"
        )
    elif subtopic == "statement":
        reply = (
            "Your account statements are available in multiple ways:\n\n"
            "• Mobile App: Accounts > Statements\n"
            "• Online Banking: Log in at www.smartbank.com > Statements\n"
            "• Branch: Request a printed copy at any branch\n\n"
            "Statements are available for up to 12 months. "
            "Is there anything else I can help you with?"
        )
    elif subtopic == "activate":
        reply = (
            "Activating your account is straightforward:\n\n"
            "• Call our 24/7 helpline at 1-800-BANKING\n"
            "• Or visit any branch with your valid ID\n\n"
            "Activation is usually instant once your identity is verified. "
            "Is there anything else I can help you with?"
        )
    else:
        reply = (
            "Here's an overview of our account services:\n\n"
            "• Open Account: Visit any branch with a valid ID and proof of address\n"
            "• Close Account: Visit a branch or call 1-800-BANKING\n"
            "• Update Details: Log in to online banking or visit a branch\n"
            "• Activate Account: Call 1-800-BANKING or visit any branch\n"
            "• Account Statement: Available via mobile app, online banking, or branch\n\n"
            "Is there a specific service you need help with? I'm happy to assist!"
        )

    return {"reply": reply, "intent": "ACCOUNT_SERVICES", "confidence": 0.9}


def handle_security_intent(message: str = "") -> Dict[str, Any]:
    """Handle SECURITY intent with focused sub-topic responses"""
    subtopics = {
        "password": ["password", "forgot password", "reset password", "pin", "change password"],
        "lost_card": ["lost", "stolen", "missing card", "card lost", "card stolen"],
        "block_card": ["block", "freeze", "cancel card", "lock card"],
        "fraud": ["fraud", "scam", "unauthorized", "suspicious", "hacked", "hack", "report fraud"],
        "otp": ["otp", "two factor", "2fa", "verification code", "sms code", "one time"],
    }

    subtopic = _detect_subtopic(message, subtopics)

    if subtopic == "password":
        reply = (
            "No worries, resetting your password is quick!\n\n"
            "• Online/Mobile App: Click or tap 'Forgot Password' on the login screen and follow the steps\n"
            "• Phone: Call 1-800-BANKING (available 24/7) for assistance\n\n"
            "You'll need your registered mobile number to verify your identity. "
            "Is there anything else I can help you with?"
        )
    elif subtopic in ("lost_card", "block_card"):
        reply = (
            "Please act quickly to protect your funds!\n\n"
            "• Call 1-800-BANKING immediately (24/7 helpline) to block your card\n"
            "• Or use the Mobile App: Cards > Block Card\n\n"
            "Once blocked, a replacement card can be arranged at your nearest branch. "
            "Is there anything else I can help you with?"
        )
    elif subtopic == "fraud":
        reply = (
            "Your account security is our top priority. Please act immediately:\n\n"
            "• Call 1-800-FRAUD (our dedicated fraud helpline, available 24/7)\n"
            "• Or call 1-800-BANKING to secure your account right away\n"
            "• Visit your nearest branch if preferred\n\n"
            "Please do not share any passwords or OTPs with anyone. "
            "Is there anything else I can assist you with?"
        )
    elif subtopic == "otp":
        reply = (
            "Enabling Two-Factor Authentication (OTP) is a great way to secure your account!\n\n"
            "• Mobile App: Settings > Security > Two-Factor Authentication\n"
            "• Or call 1-800-BANKING for assistance\n\n"
            "We strongly recommend enabling OTP for all transactions. "
            "Is there anything else I can help you with?"
        )
    else:
        reply = (
            "Your security is very important to us! Here's how we can help:\n\n"
            "• Forgot Password: Click 'Forgot Password' on the login page\n"
            "• Lost/Stolen Card: Call 1-800-BANKING immediately (24/7)\n"
            "• Block Card: Mobile App > Cards > Block Card, or call our helpline\n"
            "• Report Fraud: Call 1-800-FRAUD (24/7)\n"
            "• Enable OTP: Settings > Security in the mobile app\n\n"
            "For urgent matters, our 24/7 helpline is always available. "
            "Is there a specific issue I can help you with?"
        )

    return {"reply": reply, "intent": "SECURITY", "confidence": 0.9}


def handle_foreign_exchange_intent(message: str = "") -> Dict[str, Any]:
    """Handle FOREIGN_EXCHANGE intent"""
    message_lower = message.lower()

    if any(w in message_lower for w in ["buy", "purchase", "sell", "exchange", "convert", "how to"]):
        reply = (
            "Smart Bank offers convenient foreign currency exchange services!\n\n"
            "**How to exchange currency:**\n"
            "• Visit any branch during working hours\n"
            "• Present your valid ID\n"
            "• State the currency and amount you need\n"
            "• Exchange rates are applied at the time of transaction\n\n"
            "**Available Currencies:** USD, EUR, GBP, AUD, CAD, JPY, and more\n\n"
            "For large amounts, we recommend calling ahead to confirm availability: **1-800-BANKING**\n\n"
            "Is there anything else I can help you with?"
        )
    else:
        reply = (
            "Here are our indicative foreign exchange rates (rates updated daily):\n\n"
            "• USD (US Dollar):     Buy 299.50 / Sell 305.00\n"
            "• EUR (Euro):          Buy 325.00 / Sell 332.00\n"
            "• GBP (British Pound): Buy 380.00 / Sell 388.00\n"
            "• AUD (Australian Dollar): Buy 195.00 / Sell 200.00\n"
            "• JPY (Japanese Yen):  Buy 2.00 / Sell 2.10\n\n"
            "ℹ️ Rates are indicative and subject to change. Please visit any branch or call "
            "**1-800-BANKING** for the latest rates.\n\n"
            "Would you like to know how to exchange currency?"
        )

    return {"reply": reply, "intent": "FOREIGN_EXCHANGE", "confidence": 0.9}


def handle_forgot_email_intent() -> Dict[str, Any]:
    """Handle FORGOT_EMAIL intent — user forgot their email or wants to change it"""
    reply = (
        "No problem! Here's how you can recover or update your registered email address:\n\n"
        "**Option 1 — Via Mobile App** *(if you can still log in)*\n"
        "• Go to **Settings > Profile > Edit Email**\n"
        "• Verify with the OTP sent to your registered phone number\n\n"
        "**Option 2 — Visit a Branch**\n"
        "• Bring a valid government-issued ID (Passport, NIC, or Driving License)\n"
        "• Our staff will verify your identity and update your email securely\n\n"
        "**Option 3 — Call Our Helpline**\n"
        "• Call **1-800-BANKING** (available 24/7)\n"
        "• Have your account number and ID details ready\n\n"
        "⚠️ For your security, email changes require identity verification.\n\n"
        "Is there anything else I can help you with?"
    )
    return {"reply": reply, "intent": "FORGOT_EMAIL", "confidence": 0.9}


def handle_profanity_intent() -> Dict[str, Any]:
    """Handle PROFANITY_RESPONSE intent — respond with empathy and de-escalation"""
    import random
    replies = [
        (
            "I understand you're frustrated, and I'm truly sorry for the inconvenience. "
            "I'm here to help you resolve this as quickly as possible.\n\n"
            "Could you please describe the issue you're experiencing so I can assist you better?"
        ),
        (
            "I'm sorry to hear you're having a difficult experience. I genuinely want to help — "
            "please let me know what's going wrong and I'll do my best to sort it out for you."
        ),
        (
            "I can see this is causing you frustration, and I apologize for that. "
            "Let's work through this together.\n\nWhat exactly is the problem you're experiencing?"
        ),
        (
            "Your feelings are valid, and I'm sorry things aren't going smoothly. "
            "I'm here to help — please share the details of your issue and "
            "I'll get it resolved for you right away."
        ),
    ]
    return {"reply": random.choice(replies), "intent": "PROFANITY_RESPONSE", "confidence": 1.0}


def handle_capabilities_intent() -> Dict[str, Any]:
    """Handle CAPABILITIES intent — tell the user everything the chatbot can help with"""
    reply = (
        "I'm the **Smart Banking Assistant** and I'm here to help you with a wide range of banking services!\n\n"
        "Here's everything I can assist you with:\n\n"
        "\U0001f4b0 **Account & Balance**\n"
        "  • Check your account balance\n"
        "  • View recent transactions\n"
        "  • Account opening, closing, and management\n\n"
        "\U0001f3e6 **Loans**\n"
        "  • Loan types and interest rates\n"
        "  • Loan application requirements\n"
        "  • Eligibility criteria\n\n"
        "\U0001f4b3 **Cards**\n"
        "  • Credit and debit card services\n"
        "  • Block or replace a lost/stolen card\n\n"
        "\U0001f4e4 **Transfers & Payments**\n"
        "  • Domestic and international transfers\n"
        "  • Bill payments\n\n"
        "\U0001f4c5 **Fixed Deposits**\n"
        "  • FD rates and plans\n"
        "  • View your existing FD accounts\n\n"
        "\U0001f48e **Pawning**\n"
        "  • Pawning service details and rates\n"
        "  • View your pawn tickets\n\n"
        "\U0001f310 **Foreign Exchange**\n"
        "  • Currency exchange rates\n"
        "  • How to exchange currency\n\n"
        "\U0001f4f1 **Digital Banking**\n"
        "  • Mobile app and internet banking help\n"
        "  • Login issues and registration\n\n"
        "\U0001f512 **Security**\n"
        "  • Password reset and PIN issues\n"
        "  • Fraud reporting and account security\n\n"
        "\U0001f4b5 **Fees & Limits**\n"
        "  • ATM limits and withdrawal fees\n"
        "  • Account maintenance charges\n\n"
        "\U0001f4e7 **Email & Profile**\n"
        "  • Forgot or want to change your registered email\n\n"
        "\U0001f4cd **General Info**\n"
        "  • Branch working hours and locations\n"
        "  • Contact numbers and support\n\n"
        "Just type your question and I'll do my best to help! What would you like to know?"
    )
    return {"reply": reply, "intent": "CAPABILITIES", "confidence": 1.0}


def handle_transfers_intent(message: str = "") -> Dict[str, Any]:
    """Handle TRANSFERS intent with focused sub-topic responses"""
    subtopics = {
        "international": ["international", "swift", "foreign", "abroad", "overseas", "remittance", "wire"],
        "bill_payment": ["bill", "pay bill", "utility", "electricity", "phone bill", "water bill"],
    }

    subtopic = _detect_subtopic(message, subtopics)

    if subtopic == "international":
        reply = (
            "For international transfers, here's what you need to know:\n\n"
            "• Visit any branch with the beneficiary's full bank details (SWIFT code / IBAN)\n"
            "• Processing time: 3–5 business days\n"
            "• Fee: $25 per international transaction\n\n"
            "Please have the recipient's bank name, account number, SWIFT code, and country ready. "
            "Is there anything else I can help you with?"
        )
    elif subtopic == "bill_payment":
        reply = (
            "Paying your bills with Smart Bank is very convenient!\n\n"
            "• Online Banking: Log in > Bill Pay > Select your biller\n"
            "• Mobile App: Payments > Bill Pay\n\n"
            "Most bill payments are processed on the same business day. "
            "Is there anything else I can help you with?"
        )
    else:
        reply = (
            "Transferring money is simple with Smart Bank!\n\n"
            "• Online Banking: Log in > Transfers > New Transfer\n"
            "• Mobile App: Payments > Transfer Money\n"
            "• Domestic transfers: processed same business day\n"
            "• International transfers: 3–5 business days ($25 fee applies)\n\n"
            "Transfer limits may apply. For more details, call 1-800-BANKING. "
            "Is there anything else I can help you with?"
        )

    return {"reply": reply, "intent": "TRANSFERS", "confidence": 0.9}


def handle_fees_intent(message: str = "") -> Dict[str, Any]:
    """Handle FEES intent with focused sub-topic responses"""
    subtopics = {
        "atm": ["atm", "withdrawal limit", "daily limit", "atm limit", "daily withdrawal"],
        "maintenance": ["maintenance", "monthly fee", "monthly charge", "service charge", "minimum balance"],
        "overdraft": ["overdraft"],
        "interest_rate": ["interest rate", "savings interest", "interest on saving", "saving rate"],
        "transfer_fee": ["transfer fee", "international fee", "wire fee", "transfer charge"],
    }

    subtopic = _detect_subtopic(message, subtopics)

    if subtopic == "atm":
        reply = (
            "Here are the withdrawal and transaction limits:\n\n"
            "• Daily ATM Withdrawal Limit: $1,000\n"
            "• Daily Transaction Limit: $5,000\n\n"
            "If you need a higher limit, please visit your nearest branch or call 1-800-BANKING. "
            "Is there anything else I can help you with?"
        )
    elif subtopic == "maintenance":
        reply = (
            "Here are our account maintenance details:\n\n"
            "• Minimum Balance (Savings Account): $100\n"
            "• Minimum Balance (Checking Account): $500\n"
            "• Monthly Maintenance Fee: $5 (waived if balance exceeds $500)\n\n"
            "Is there anything else I can help you with?"
        )
    elif subtopic == "overdraft":
        reply = (
            "Our overdraft fee is $35 per occurrence.\n\n"
            "We recommend setting up low-balance alerts to help avoid overdrafts. "
            "You can enable these through the mobile app or online banking. "
            "Is there anything else I can help you with?"
        )
    elif subtopic == "interest_rate":
        reply = (
            "Our current savings account interest rate is:\n\n"
            "• Savings Account: 2.5% per annum\n\n"
            "Interest is calculated daily and credited to your account monthly. "
            "Is there anything else I can help you with?"
        )
    elif subtopic == "transfer_fee":
        reply = (
            "Here are our transfer fees:\n\n"
            "• Domestic Transfers: Free\n"
            "• International Transfers: $25 per transaction\n\n"
            "Is there anything else I can help you with?"
        )
    else:
        reply = (
            "Here's an overview of our fees and limits:\n\n"
            "• Daily ATM Withdrawal Limit: $1,000\n"
            "• Daily Transaction Limit: $5,000\n"
            "• Minimum Balance (Savings): $100\n"
            "• Minimum Balance (Checking): $500\n"
            "• Monthly Maintenance Fee: $5 (waived if balance > $500)\n"
            "• Overdraft Fee: $35 per occurrence\n"
            "• International Transfer Fee: $25 per transaction\n"
            "• Savings Interest Rate: 2.5% per annum\n\n"
            "Is there a specific fee you'd like to know more about?"
        )

    return {"reply": reply, "intent": "FEES", "confidence": 0.9}


def handle_digital_banking_intent(message: str = "") -> Dict[str, Any]:
    """Handle DIGITAL_BANKING intent with focused sub-topic responses"""
    subtopics = {
        "download": ["download", "install", "get the app", "where to download", "find the app"],
        "register": ["register", "sign up", "how to register", "enrollment", "enrol", "create online"],
        "login_issue": ["login issue", "can't login", "login problem", "not working", "locked out", "can't access"],
    }

    subtopic = _detect_subtopic(message, subtopics)

    if subtopic == "download":
        reply = (
            "Downloading our mobile app is very easy!\n\n"
            "• iOS: Search 'Smart Bank' on the App Store\n"
            "• Android: Search 'Smart Bank' on Google Play\n\n"
            "The app is completely free. Once installed, register using your account number "
            "and mobile number to get started. Is there anything else I can help you with?"
        )
    elif subtopic == "register":
        reply = (
            "Registering for digital banking is quick and simple!\n\n"
            "You'll need:\n"
            "• Your account number\n"
            "• Your registered mobile number\n\n"
            "• Internet Banking: Visit www.smartbank.com/online and click 'Register'\n"
            "• Mobile App: Download 'Smart Bank', tap 'Register', and follow the steps\n\n"
            "Registration takes just a few minutes! Is there anything else I can help you with?"
        )
    elif subtopic == "login_issue":
        reply = (
            "I'm sorry you're having trouble accessing your account. Here's how to resolve it:\n\n"
            "• Forgot Password: Click 'Forgot Password' on the login screen\n"
            "• Locked Account: Call 1-800-BANKING (24/7) to unlock\n"
            "• Other Issues: Email support@smartbank.com or call 1-800-BANKING\n\n"
            "Our support team is available 24/7 and will be happy to help you. "
            "Is there anything else I can assist you with?"
        )
    else:
        reply = (
            "Our digital banking services make managing your finances easy!\n\n"
            "• Mobile App: Download 'Smart Bank' from the App Store or Google Play\n"
            "• Internet Banking: Register at www.smartbank.com/online\n"
            "• Available Features: Balance check, transfers, bill pay, statements, card controls\n\n"
            "You'll need your account number and registered mobile number to register. "
            "For technical support, call 1-800-BANKING or email support@smartbank.com. "
            "Is there anything else I can help you with?"
        )

    return {"reply": reply, "intent": "DIGITAL_BANKING", "confidence": 0.9}


def handle_general_intent(message: str = "") -> Dict[str, Any]:
    """Handle GENERAL intent with focused sub-topic responses"""
    subtopics = {
        "working_hours": [
            "working hour", "working time", "office hour", "open hour", "bank hour",
            "bank time", "work hour", "work time", "hours", "times", "what time",
            "when open", "when do you open", "open time", "closing time", "working day",
            "work day", "open day", "bank open", "bank close"
        ],
        "contact": [
            "contact", "phone number", "call", "email", "helpline",
            "customer service number", "support number", "reach", "get in touch", "speak to"
        ],
        "location": [
            "branch", "atm", "location", "nearest", "locate", "find a",
            "address", "where is", "where are", "near me"
        ],
    }

    subtopic = _detect_subtopic(message, subtopics)

    if subtopic == "working_hours":
        reply = (
            "Thank you for asking! Our branch working hours are:\n\n"
            "• Monday – Friday: 9:00 AM – 5:00 PM\n"
            "• Saturday: 9:00 AM – 1:00 PM\n"
            "• Sunday & Public Holidays: Closed\n\n"
            "Our Customer Service helpline is available 24/7 at 1-800-BANKING, "
            "so you can always reach us! Is there anything else I can help you with?"
        )
    elif subtopic == "contact":
        reply = (
            "I'd be happy to share our contact information!\n\n"
            "• Phone: 1-800-BANKING (available 24/7)\n"
            "• Email: support@smartbank.com\n\n"
            "We're always here to assist you. Is there anything else you need?"
        )
    elif subtopic == "location":
        reply = (
            "You can find your nearest branch or ATM using our locator:\n\n"
            "• Branch & ATM Locator: www.smartbank.com/branches\n\n"
            "Simply enter your location to find the nearest option. "
            "Is there anything else I can help you with?"
        )
    else:
        reply = (
            "Thank you for reaching out to Smart Banking!\n\n"
            "• Working Hours: Mon–Fri 9AM–5PM, Sat 9AM–1PM\n"
            "• Customer Service: 1-800-BANKING (24/7)\n"
            "• Email: support@smartbank.com\n"
            "• Branch/ATM Locator: www.smartbank.com/branches\n\n"
            "How can I assist you today?"
        )

    return {"reply": reply, "intent": "GENERAL", "confidence": 0.9}


def handle_fixed_deposit_intent(message: str = "", user_id: int = 1) -> Dict[str, Any]:
    """Handle FIXED_DEPOSIT intent — show user's FDs or general FD information."""
    message_lower = message.lower()

    # Sub-topic: general rates / how-to (no personal data needed)
    if any(w in message_lower for w in [
        "what is", "how does", "how do", "rate", "interest", "how to open",
        "minimum", "plan", "offer", "available", "tenure", "term", "options"
    ]):
        reply = (
            "We offer competitive Fixed Deposit (FD) plans to grow your savings:\n\n"
            "• 6-month FD:  4.50% per annum\n"
            "• 12-month FD: 5.00% per annum\n"
            "• 24-month FD: 5.50% per annum\n"
            "• 36-month FD: 6.00% per annum\n\n"
            "Minimum deposit: $1,000 | Interest is paid at maturity.\n"
            "Auto-renewal is available — your FD can roll over automatically.\n"
            "Early withdrawal is permitted with a reduced interest rate.\n\n"
            "Would you like to open an FD or see your existing deposits?"
        )
        return {"reply": reply, "intent": "FIXED_DEPOSIT", "confidence": 0.9}

    # Sub-topic: my FD / personal data
    deposits = get_user_fixed_deposits(user_id)
    if not deposits:
        reply = (
            "You don't currently have any Fixed Deposit accounts.\n\n"
            "Our FD plans offer rates from 4.50% to 6.00% p.a. "
            "Would you like to know how to open one?"
        )
        return {"reply": reply, "intent": "FIXED_DEPOSIT", "confidence": 0.9}

    lines = ["Here are your Fixed Deposit account(s):\n"]
    for fd in deposits:
        start = fd['start_date'].strftime('%Y-%m-%d') if hasattr(fd['start_date'], 'strftime') else str(fd['start_date'])
        maturity = fd['maturity_date'].strftime('%Y-%m-%d') if hasattr(fd['maturity_date'], 'strftime') else str(fd['maturity_date'])
        renew = "Yes" if fd['auto_renew'] else "No"
        status = fd['status'].upper()
        lines.append(
            f"📋 FD Number: {fd['fd_number']}\n"
            f"   Principal:      ${fd['principal']:,.2f}\n"
            f"   Interest Rate:  {fd['interest_rate']}% p.a.\n"
            f"   Term:           {fd['term_months']} months\n"
            f"   Maturity Amount: ${fd['maturity_amount']:,.2f}\n"
            f"   Start Date:     {start}\n"
            f"   Maturity Date:  {maturity}\n"
            f"   Auto-Renew:     {renew}\n"
            f"   Status:         {status}\n"
        )
    lines.append("Is there anything else I can help you with?")
    return {"reply": "\n".join(lines), "intent": "FIXED_DEPOSIT", "confidence": 0.9}


def handle_pawning_intent(message: str = "", user_id: int = 1) -> Dict[str, Any]:
    """Handle PAWNING intent — show user's pawn tickets or general pawning information."""
    message_lower = message.lower()

    # Sub-topic: general info (no personal data needed)
    if any(w in message_lower for w in [
        "what is", "how does", "how do", "how to", "eligib", "item", "accept",
        "rate", "interest", "plan", "offer", "available", "service", "work"
    ]):
        reply = (
            "Our Pawning Service lets you obtain a quick loan against your valuables:\n\n"
            "📦 Accepted items:\n"
            "   • Gold & Jewelry  — up to 75% of appraised value\n"
            "   • Electronics     — up to 60% of appraised value\n"
            "   • Vehicles        — up to 70% of appraised value\n"
            "   • Silver & Others — assessed case by case\n\n"
            "💰 Interest Rates (monthly):\n"
            "   • Gold / Jewelry: 2.50% per month\n"
            "   • Electronics:    3.00% per month\n"
            "   • Vehicles:       2.00% per month\n\n"
            "📅 Standard loan period: 3 months (extendable)\n"
            "🔑 To redeem: repay the outstanding amount + interest at any branch.\n\n"
            "Would you like to check your existing pawn tickets?"
        )
        return {"reply": reply, "intent": "PAWNING", "confidence": 0.9}

    # Sub-topic: my pawn tickets / personal data
    tickets = get_user_pawning(user_id)
    if not tickets:
        reply = (
            "You don't currently have any active pawn tickets.\n\n"
            "Our pawning service accepts gold, jewelry, electronics, and vehicles. "
            "Visit any branch to get started. Is there anything else I can help you with?"
        )
        return {"reply": reply, "intent": "PAWNING", "confidence": 0.9}

    lines = ["Here are your pawn ticket(s):\n"]
    for ticket in tickets:
        pledged = ticket['pledged_at'].strftime('%Y-%m-%d') if hasattr(ticket['pledged_at'], 'strftime') else str(ticket['pledged_at'])
        due = ticket['due_date'].strftime('%Y-%m-%d') if hasattr(ticket['due_date'], 'strftime') else str(ticket['due_date'])
        status = ticket['status'].upper()
        lines.append(
            f"🏷️ Ticket: {ticket['ticket_number']}\n"
            f"   Item:            {ticket['item_description']} ({ticket['item_category'].title()})\n"
            f"   Appraised Value: ${ticket['appraised_value']:,.2f}\n"
            f"   Loan Amount:     ${ticket['loan_amount']:,.2f}\n"
            f"   Outstanding:     ${ticket['outstanding']:,.2f}\n"
            f"   Interest Rate:   {ticket['interest_rate']}% per month\n"
            f"   Pledged On:      {pledged}\n"
            f"   Due Date:        {due}\n"
            f"   Status:          {status}\n"
        )
    lines.append("To redeem, visit any branch with your ticket. Is there anything else I can help you with?")
    return {"reply": "\n".join(lines), "intent": "PAWNING", "confidence": 0.9}


def handle_unknown_intent(user_message: str) -> Dict[str, Any]:
    """
    Handle UNKNOWN intent — save question and return help message.
    """
    save_unknown_question(user_message)
    logger.info(f"Saved unknown question: {user_message}")

    return {
        "reply": (
            "I'm sorry, I didn't quite understand that. Could you please rephrase your question?\n\n"
            "I can help you with:\n"
            "• Account balance and transactions\n"
            "• Loan information, rates, and requirements\n"
            "• Fixed deposits and pawning services\n"
            "• Transfers and bill payments\n"
            "• Foreign exchange rates\n"
            "• Account services and email updates\n"
            "• Fees, limits, and digital banking\n"
            "• Security — lost cards, fraud, password reset\n\n"
            "💡 Type **'What can you do?'** to see a full list of available services."
        ),
        "intent": "UNKNOWN",
        "confidence": 0.0
    }


# ── Main processor ────────────────────────────────────────────────────────────

def process_chat_message(
    message: str,
    user_id: int = 1,
    last_intent: str = None,
    account_number: str = None,
) -> Dict[str, Any]:
    """
    Main function to process chat messages.

    Args:
        message: User input message
        user_id: User ID (resolved from account_number when provided)
        last_intent: Intent from the previous turn (for context-aware follow-ups)
        account_number: Verified account number supplied by the frontend

    Returns:
        Dictionary with reply and metadata
    """
    try:
        logger.info(f"Processing message from user {user_id}: {message}")

        # ── Language guard: English-only chatbot ─────────────────────────────
        # Step 1: detect non-Latin scripts via Unicode ranges (catches Sinhala,
        #         Arabic, CJK, Cyrillic, Devanagari, etc. reliably)
        # Step 2: for Latin-script text, use langdetect (French, Spanish, etc.)
        _NON_LATIN_RANGES = [
            (0x0600, 0x06FF),   # Arabic
            (0x0900, 0x097F),   # Devanagari (Hindi)
            (0x0980, 0x09FF),   # Bengali
            (0x0A00, 0x0A7F),   # Gurmukhi (Punjabi)
            (0x0A80, 0x0AFF),   # Gujarati
            (0x0B00, 0x0B7F),   # Oriya
            (0x0B80, 0x0BFF),   # Tamil
            (0x0C00, 0x0C7F),   # Telugu
            (0x0C80, 0x0CFF),   # Kannada
            (0x0D00, 0x0D7F),   # Malayalam
            (0x0D80, 0x0DFF),   # Sinhala
            (0x0E00, 0x0E7F),   # Thai
            (0x0E80, 0x0EFF),   # Lao
            (0x0F00, 0x0FFF),   # Tibetan
            (0x1000, 0x109F),   # Myanmar
            (0x10A0, 0x10FF),   # Georgian
            (0x1100, 0x11FF),   # Hangul Jamo (Korean)
            (0x3040, 0x309F),   # Hiragana (Japanese)
            (0x30A0, 0x30FF),   # Katakana (Japanese)
            (0x4E00, 0x9FFF),   # CJK Unified (Chinese/Japanese/Korean)
            (0xAC00, 0xD7AF),   # Hangul Syllables (Korean)
            (0x0400, 0x04FF),   # Cyrillic (Russian, etc.)
            (0x0370, 0x03FF),   # Greek
            (0x0590, 0x05FF),   # Hebrew
            (0x0530, 0x058F),   # Armenian
        ]
        def _has_non_latin(text: str) -> bool:
            for ch in text:
                cp = ord(ch)
                if any(lo <= cp <= hi for lo, hi in _NON_LATIN_RANGES):
                    return True
            return False

        is_non_english = False
        detected_lang = "en"

        if _has_non_latin(message):
            is_non_english = True
            detected_lang = "non-latin"
        elif len(message.split()) >= 3:
            # Only run langdetect on phrases (3+ words) to avoid false positives
            try:
                detected_lang = _lang_detect(message)
                if detected_lang not in ("en",):
                    is_non_english = True
            except LangDetectException:
                pass  # ambiguous input — treat as English

        if is_non_english:
            return {
                "reply": (
                    "I'm sorry, I only support **English** at the moment.\n\n"
                    "Please rephrase your question in English and I'll be happy to help you! 😊\n\n"
                    "_(Example: \"What is my account balance?\")_"
                ),
                "intent": "UNSUPPORTED_LANGUAGE",
                "confidence": 1.0,
                "detected_language": detected_lang,
            }
        # ─────────────────────────────────────────────────────────────────────

        # Check for action request first (before NLP), e.g. "I want to open an account"
        if _is_action_request(message):
            return handle_action_request(message)

        # Detect intent using NLP
        intent, confidence = detect_intent(message)

        # Route to appropriate handler based on intent
        if intent == 'GREETING':
            response = handle_greeting_intent()

        elif intent == 'GOODBYE':
            response = handle_goodbye_intent()

        elif intent == 'BALANCE':
            if not account_number:
                response = _require_account_selection()
            else:
                response = handle_balance_intent(user_id)

        elif intent == 'TRANSACTIONS':
            if not account_number:
                response = _require_account_selection()
            else:
                response = handle_transactions_intent(user_id)

        elif intent == 'LOAN':
            response = handle_loan_intent(message)

        elif intent == 'ACCOUNT_SERVICES':
            response = handle_account_services_intent(message, last_intent or "")

        elif intent == 'SECURITY':
            response = handle_security_intent(message)

        elif intent == 'TRANSFERS':
            response = handle_transfers_intent(message)

        elif intent == 'FEES':
            response = handle_fees_intent(message)

        elif intent == 'DIGITAL_BANKING':
            response = handle_digital_banking_intent(message)

        elif intent == 'GENERAL':
            response = handle_general_intent(message)

        elif intent == 'FIXED_DEPOSIT':
            # General FD info queries don't require auth; personal data queries do
            _FD_GENERAL_KEYWORDS = (
                "what is", "how does", "how do", "rate", "interest", "how to open",
                "how to apply", "minimum", "plan", "offer", "available", "tenure",
                "term", "options", "about", "detail", "info", "tell me", "explain",
                "benefit", "calculator", "compare", "vs", "difference", "open",
            )
            msg_lower_fd = message.lower()
            is_general_fd = any(kw in msg_lower_fd for kw in _FD_GENERAL_KEYWORDS)
            if is_general_fd or account_number:
                response = handle_fixed_deposit_intent(message, user_id)
            else:
                response = _require_account_selection()

        elif intent == 'PAWNING':
            # General pawning info queries don't require auth; personal ticket queries do
            _PAWNING_GENERAL_KEYWORDS = (
                "what is", "how does", "how do", "rate", "interest", "how to",
                "about", "service", "info", "tell me", "explain", "detail",
                "item", "accept", "eligib", "work",
            )
            msg_lower_pawn = message.lower()
            is_general_pawn = any(kw in msg_lower_pawn for kw in _PAWNING_GENERAL_KEYWORDS)
            if is_general_pawn or account_number:
                response = handle_pawning_intent(message, user_id)
            else:
                response = _require_account_selection()

        elif intent == 'FOREIGN_EXCHANGE':
            response = handle_foreign_exchange_intent(message)

        elif intent == 'FORGOT_EMAIL':
            response = handle_forgot_email_intent()

        elif intent == 'PROFANITY_RESPONSE':
            response = handle_profanity_intent()

        elif intent == 'CAPABILITIES':
            response = handle_capabilities_intent()

        else:  # UNKNOWN — try context-aware fallback first
            context_response = _try_context_fallback(message, last_intent or "")
            response = context_response if context_response else handle_unknown_intent(message)

        # Add confidence to response if not already present
        if 'confidence' not in response:
            response['confidence'] = confidence

        # Log every request and response for developer review
        save_chat_log(
            user_id=user_id,
            request_message=message,
            response=response.get('reply', ''),
            intent=response.get('intent', intent),
            confidence=response.get('confidence', confidence)
        )

        logger.info(f"Generated response for intent {intent}")
        return response

    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        return {
            "reply": "I apologize, something went wrong on my end. Please try again in a moment, or call us at 1-800-BANKING.",
            "intent": "ERROR",
            "confidence": 0.0
        }
