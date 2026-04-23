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


# ============= Knowledge Base Queries =============

def get_answer_from_knowledge(question: str) -> Optional[str]:
    """
    Search for answer in knowledge base
    Uses case-insensitive matching
    """
    query = """
        SELECT answer 
        FROM knowledge 
        WHERE LOWER(question) = LOWER(%s)
        LIMIT 1
    """
    result = execute_query(query, (question.strip(),), fetch_one=True)
    return result['answer'] if result else None


def search_knowledge_base(keywords: str) -> Optional[str]:
    """
    Search knowledge base using keyword matching
    """
    query = """
        SELECT answer 
        FROM knowledge 
        WHERE LOWER(question) LIKE LOWER(%s)
        LIMIT 1
    """
    result = execute_query(query, (f"%{keywords}%",), fetch_one=True)
    return result['answer'] if result else None


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
