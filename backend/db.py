"""
Database connection and query functions for Smart Banking Assistant
"""
import os
import logging
from typing import Optional, List, Dict, Any
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'mysql'),
    'database': os.getenv('DB_NAME', 'banking_chatbot'),
    'port': int(os.getenv('DB_PORT', '3306'))
}


@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    Ensures proper connection cleanup
    """
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        yield connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()


def execute_query(query: str, params: tuple = None, fetch_one: bool = False, 
                  fetch_all: bool = False) -> Optional[Any]:
    """
    Execute a database query with proper error handling
    
    Args:
        query: SQL query string
        params: Query parameters
        fetch_one: Return single row
        fetch_all: Return all rows
        
    Returns:
        Query results or None
    """
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                connection.commit()
                result = cursor.lastrowid
                
            cursor.close()
            return result
            
    except Error as e:
        logger.error(f"Query execution error: {e}")
        return None


# ============= User & Account Queries =============

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Fetch user details by user ID"""
    query = "SELECT * FROM users WHERE id = %s"
    return execute_query(query, (user_id,), fetch_one=True)


def get_user_by_email_and_account(email: str, id_number: str, account_number: str) -> Optional[Dict[str, Any]]:
    """
    Validate that the given email + id_number + account_number all belong to the same user.
    Returns account info dict or None.
    """
    query = """
        SELECT u.id AS user_id, u.name AS account_holder,
               a.account_number, a.account_type, a.status
        FROM users u
        JOIN accounts a ON a.user_id = u.id
        WHERE LOWER(u.email) = LOWER(%s)
          AND u.id_number = %s
          AND a.account_number = %s
          AND a.status = 'active'
        LIMIT 1
    """
    return execute_query(query, (email.strip(), id_number.strip(), account_number.strip()), fetch_one=True)


def save_verified_user(email: str, id_number: str) -> bool:
    """
    Insert or update a verified user's email + id_number in the verified_users table.
    """
    try:
        query = """
            INSERT INTO verified_users (email, id_number)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE id_number = VALUES(id_number), updated_at = NOW()
        """
        result = execute_query(query, (email.strip().lower(), id_number.strip()))
        if result is not None:
            logger.info(f"Saved verified user: {email}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error saving verified user: {e}")
        return False



def get_account_balance(user_id: int = 1) -> Optional[float]:
    """
    Fetch account balance for a user
    Default user_id=1 for demo purposes
    """
    query = """
        SELECT balance 
        FROM accounts 
        WHERE user_id = %s
        LIMIT 1
    """
    result = execute_query(query, (user_id,), fetch_one=True)
    return result['balance'] if result else None


# ============= Transaction Queries =============

def get_recent_transactions(user_id: int = 1, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch recent transactions for a user
    
    Args:
        user_id: User ID
        limit: Number of transactions to fetch
        
    Returns:
        List of transaction dictionaries
    """
    query = """
        SELECT t.id, t.amount, t.type, t.date, t.description
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        WHERE a.user_id = %s
        ORDER BY t.date DESC
        LIMIT %s
    """
    result = execute_query(query, (user_id, limit), fetch_all=True)
    return result if result else []


# ============= Chat Log Queries =============

def save_chat_log(user_id: int, request_message: str, response: str, intent: str, confidence: float) -> bool:
    """
    Save every chat request and its response to the chat_logs table.
    Developers can review rows where reviewed = FALSE.
    """
    try:
        query = """
            INSERT INTO chat_logs (user_id, request_message, response, intent, confidence)
            VALUES (%s, %s, %s, %s, %s)
        """
        result = execute_query(query, (user_id, request_message.strip(), response.strip(), intent, round(confidence, 4)))
        if result:
            logger.info(f"Saved chat log for user {user_id}, intent={intent}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error saving chat log: {e}")
        return False


# ============= Learning Feature Queries =============

def save_unknown_question(question: str) -> bool:
    """
    Save unknown question to database for future learning
    Avoids duplicates
    
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Check if question already exists
        check_query = """
            SELECT id FROM unknown_questions 
            WHERE LOWER(question) = LOWER(%s)
        """
        existing = execute_query(check_query, (question.strip(),), fetch_one=True)
        
        if existing:
            logger.info(f"Question already exists: {question}")
            return True
        
        # Insert new unknown question
        insert_query = """
            INSERT INTO unknown_questions (question, created_at) 
            VALUES (%s, NOW())
        """
        result = execute_query(insert_query, (question.strip(),))
        
        if result:
            logger.info(f"Saved unknown question: {question}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Error saving unknown question: {e}")
        return False


def get_all_unknown_questions() -> List[Dict[str, Any]]:
    """Fetch all unknown questions for admin review"""
    query = """
        SELECT id, question, created_at 
        FROM unknown_questions 
        ORDER BY created_at DESC
    """
    result = execute_query(query, fetch_all=True)
    return result if result else []


# ============= Fixed Deposit Queries =============

def get_user_fixed_deposits(user_id: int) -> List[Dict[str, Any]]:
    """
    Fetch all fixed deposits for a user.

    Args:
        user_id: User ID

    Returns:
        List of fixed deposit dictionaries
    """
    query = """
        SELECT fd_number, principal, interest_rate, term_months,
               maturity_amount, start_date, maturity_date, auto_renew, status
        FROM fixed_deposits
        WHERE user_id = %s
        ORDER BY start_date DESC
    """
    result = execute_query(query, (user_id,), fetch_all=True)
    return result if result else []


# ============= Pawning Queries =============

def get_user_pawning(user_id: int) -> List[Dict[str, Any]]:
    """
    Fetch all active/pending pawn tickets for a user.

    Args:
        user_id: User ID

    Returns:
        List of pawning dictionaries
    """
    query = """
        SELECT ticket_number, item_description, item_category,
               appraised_value, loan_amount, interest_rate,
               pledged_at, due_date, outstanding, status
        FROM pawning
        WHERE user_id = %s
        ORDER BY pledged_at DESC
    """
    result = execute_query(query, (user_id,), fetch_all=True)
    return result if result else []


# ============= Database Health Check =============

def test_connection() -> bool:
    """Test database connection"""
    try:
        with get_db_connection() as connection:
            if connection.is_connected():
                logger.info("Database connection successful")
                return True
        return False
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
