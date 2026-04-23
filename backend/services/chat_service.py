"""
Chat service - Core business logic for chat processing
"""
import logging
from typing import Dict, Any
from nlp import detect_intent
from db import (
    get_account_balance,
    get_recent_transactions,
    get_answer_from_knowledge,
    search_knowledge_base,
    save_unknown_question
)

logger = logging.getLogger(__name__)


def format_balance_response(balance: float) -> str:
    """Format balance as currency string"""
    return f"${balance:,.2f}"


def format_transactions_response(transactions: list) -> str:
    """
    Format transaction list into readable string
    
    Args:
        transactions: List of transaction dictionaries
        
    Returns:
        Formatted string of transactions
    """
    if not transactions:
        return "No recent transactions found."
    
    response = "Here are your recent transactions:\n\n"
    
    for idx, txn in enumerate(transactions, 1):
        amount = txn['amount']
        txn_type = txn['type']
        date = txn['date'].strftime('%Y-%m-%d') if hasattr(txn['date'], 'strftime') else str(txn['date'])
        description = txn.get('description', 'N/A')
        
        # Format amount with sign
        amount_str = f"+${amount:,.2f}" if txn_type == 'credit' else f"-${amount:,.2f}"
        
        response += f"{idx}. {amount_str} ({txn_type.upper()}) - {date}\n"
        response += f"   {description}\n\n"
    
    return response.strip()


def handle_greeting_intent() -> Dict[str, Any]:
    """Handle GREETING intent"""
    return {
        "reply": "Hello! Welcome to Smart Banking Assistant. How can I help you today?",
        "intent": "GREETING",
        "confidence": 1.0
    }


def handle_balance_intent(user_id: int = 1) -> Dict[str, Any]:
    """
    Handle BALANCE intent
    
    Args:
        user_id: User ID to fetch balance for
        
    Returns:
        Response dictionary
    """
    balance = get_account_balance(user_id)
    
    if balance is not None:
        formatted_balance = format_balance_response(balance)
        return {
            "reply": f"Your current account balance is {formatted_balance}.",
            "intent": "BALANCE",
            "confidence": 0.9,
            "data": {"balance": balance}
        }
    else:
        return {
            "reply": "Sorry, I couldn't retrieve your balance at the moment. Please try again later.",
            "intent": "BALANCE",
            "confidence": 0.9,
            "data": None
        }


def handle_transactions_intent(user_id: int = 1, limit: int = 5) -> Dict[str, Any]:
    """
    Handle TRANSACTIONS intent
    
    Args:
        user_id: User ID to fetch transactions for
        limit: Number of transactions to retrieve
        
    Returns:
        Response dictionary
    """
    transactions = get_recent_transactions(user_id, limit)
    
    if transactions:
        formatted_txns = format_transactions_response(transactions)
        return {
            "reply": formatted_txns,
            "intent": "TRANSACTIONS",
            "confidence": 0.9,
            "data": {"transactions": transactions}
        }
    else:
        return {
            "reply": "You don't have any recent transactions.",
            "intent": "TRANSACTIONS",
            "confidence": 0.9,
            "data": {"transactions": []}
        }


def handle_loan_intent() -> Dict[str, Any]:
    """Handle LOAN intent with predefined response"""
    return {
        "reply": (
            "We offer various loan options:\n\n"
            "• Personal Loans: 8-12% interest rate\n"
            "• Home Loans: 6-9% interest rate\n"
            "• Car Loans: 7-11% interest rate\n\n"
            "Would you like to apply for a loan or speak with a loan officer? "
            "Please call us at 1-800-BANKING or visit your nearest branch."
        ),
        "intent": "LOAN",
        "confidence": 0.9
    }


def handle_unknown_intent(user_message: str) -> Dict[str, Any]:
    """
    Handle UNKNOWN intent
    Check knowledge base and save question if not found
    
    Args:
        user_message: Original user message
        
    Returns:
        Response dictionary
    """
    # First, check if exact answer exists in knowledge base
    answer = get_answer_from_knowledge(user_message)
    
    if answer:
        logger.info(f"Found answer in knowledge base for: {user_message}")
        return {
            "reply": answer,
            "intent": "KNOWLEDGE",
            "confidence": 0.8
        }
    
    # Try keyword-based search
    answer = search_knowledge_base(user_message)
    
    if answer:
        logger.info(f"Found related answer in knowledge base for: {user_message}")
        return {
            "reply": answer,
            "intent": "KNOWLEDGE",
            "confidence": 0.7
        }
    
    # Save unknown question for learning
    save_unknown_question(user_message)
    logger.info(f"Saved unknown question: {user_message}")
    
    return {
        "reply": (
            "I'm sorry, I didn't understand that. "
            "Could you please rephrase your question? "
            "You can ask me about your account balance, recent transactions, or loan options."
        ),
        "intent": "UNKNOWN",
        "confidence": 0.0
    }


def process_chat_message(message: str, user_id: int = 1) -> Dict[str, Any]:
    """
    Main function to process chat messages
    Coordinates intent detection and response generation
    
    Args:
        message: User input message
        user_id: User ID for personalized responses
        
    Returns:
        Dictionary with reply and metadata
    """
    try:
        logger.info(f"Processing message from user {user_id}: {message}")
        
        # Detect intent using NLP
        intent, confidence = detect_intent(message)
        
        # Route to appropriate handler based on intent
        if intent == 'GREETING':
            response = handle_greeting_intent()
        
        elif intent == 'BALANCE':
            response = handle_balance_intent(user_id)
        
        elif intent == 'TRANSACTIONS':
            response = handle_transactions_intent(user_id)
        
        elif intent == 'LOAN':
            response = handle_loan_intent()
        
        else:  # UNKNOWN or any other intent
            response = handle_unknown_intent(message)
        
        # Add confidence to response if not already present
        if 'confidence' not in response:
            response['confidence'] = confidence
        
        logger.info(f"Generated response for intent {intent}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        return {
            "reply": "Sorry, something went wrong. Please try again.",
            "intent": "ERROR",
            "confidence": 0.0
        }
