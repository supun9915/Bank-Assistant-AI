"""
Chat service - Core business logic for chat processing
"""
import re
import logging
from typing import Dict, Any, Optional
from nlp import detect_intent
from db import (
    get_account_balance,
    get_recent_transactions,
    save_unknown_question,
    save_chat_log,
    get_user_by_email_and_account,
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
_ACCOUNT_REQUIRED_INTENTS = frozenset(["BALANCE", "TRANSACTIONS"])


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
    return {
        "reply": (
            "Hello! Welcome to Smart Banking Assistant.\n\n"
            "I'm here to help make your banking experience as easy as possible. "
            "You can ask me about:\n\n"
            "• Account balance and recent transactions\n"
            "• Loan options and interest rates\n"
            "• Transfers and payments\n"
            "• Account services and fees\n"
            "• Digital banking support\n\n"
            "How can I assist you today?"
        ),
        "intent": "GREETING",
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
            "• Loan information and options\n"
            "• Transfers and payments\n"
            "• Account services\n"
            "• Fees and limits\n"
            "• Digital banking\n\n"
            "Feel free to ask anything related to your banking needs!"
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

        # Check for action request first (before NLP), e.g. "I want to open an account"
        if _is_action_request(message):
            return handle_action_request(message)

        # Detect intent using NLP
        intent, confidence = detect_intent(message)

        # Route to appropriate handler based on intent
        if intent == 'GREETING':
            response = handle_greeting_intent()

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
