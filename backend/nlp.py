"""
Natural Language Processing module using NLTK
Handles intent detection and text processing
"""
import logging
import nltk
from typing import Tuple

logger = logging.getLogger(__name__)

# Download required NLTK data on first use
def _ensure_nltk_data():
    resources = [
        ('tokenizers/punkt_tab', 'punkt_tab'),
        ('tokenizers/punkt', 'punkt'),
        ('corpora/stopwords', 'stopwords'),
        ('corpora/wordnet', 'wordnet'),
    ]
    for path, name in resources:
        try:
            nltk.data.find(path)
        except (LookupError, OSError):
            nltk.download(name, quiet=True)

_ensure_nltk_data()

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

_lemmatizer = WordNetLemmatizer()
_stop_words = set(stopwords.words('english'))

logger.info("NLTK NLP components loaded successfully")


# Intent definitions with keywords
INTENT_KEYWORDS = {
    'GREETING': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 
                 'good evening', 'howdy', 'hola', 'namaste'],
    
    'BALANCE': ['balance', 'money', 'account', 'amount', 'fund', 'cash', 
                'saving', 'checking', 'total', 'available'],
    
    'TRANSACTIONS': ['transaction', 'history', 'statement', 'record', 'activity', 
                     'purchase', 'payment', 'transfer', 'withdrawal', 'deposit', 
                     'recent', 'last', 'previous'],
    
    'LOAN': ['loan', 'credit', 'borrow', 'mortgage', 'emi', 'installment', 
             'lending', 'debt', 'financing', 'advance']
}


def preprocess_text(text: str) -> str:
    """
    Clean and normalize input text
    
    Args:
        text: Raw user input
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Convert to lowercase and strip whitespace
    text = text.lower().strip()
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    return text


def extract_lemmas(text: str) -> list:
    """
    Extract lemmatized tokens from text using NLTK
    
    Args:
        text: Input text
        
    Returns:
        List of lemmatized tokens
    """
    tokens = word_tokenize(text)
    lemmas = [
        _lemmatizer.lemmatize(token.lower())
        for token in tokens
        if token.isalpha() and token.lower() not in _stop_words
    ]
    return lemmas


def detect_intent(user_input: str) -> Tuple[str, float]:
    """
    Detect user intent from input using keyword matching and lemmatization
    
    Args:
        user_input: Raw user message
        
    Returns:
        Tuple of (intent, confidence_score)
    """
    if not user_input:
        return 'UNKNOWN', 0.0
    
    # Preprocess input
    processed_text = preprocess_text(user_input)
    
    # Extract lemmas
    lemmas = extract_lemmas(processed_text)
    
    # Also check the original processed text for exact phrase matches
    text_tokens = processed_text.split()
    all_tokens = set(lemmas + text_tokens)
    
    # Score each intent
    intent_scores = {}
    
    for intent, keywords in INTENT_KEYWORDS.items():
        score = 0
        matched_keywords = 0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # Check for exact phrase match in original text
            if keyword_lower in processed_text:
                score += 2  # Higher weight for exact matches
                matched_keywords += 1
            
            # Check for keyword presence in lemmas/tokens
            keyword_parts = keyword_lower.split()
            if any(part in all_tokens for part in keyword_parts):
                score += 1
                matched_keywords += 1
        
        if matched_keywords > 0:
            # Calculate confidence based on matches
            confidence = min(score / len(keywords), 1.0)
            intent_scores[intent] = (score, confidence)
    
    # If no intent matched, return UNKNOWN
    if not intent_scores:
        logger.info(f"No intent detected for: {user_input}")
        return 'UNKNOWN', 0.0
    
    # Return intent with highest score
    best_intent = max(intent_scores.items(), key=lambda x: x[1][0])
    intent_name = best_intent[0]
    confidence = best_intent[1][1]
    
    logger.info(f"Detected intent: {intent_name} (confidence: {confidence:.2f}) for: {user_input}")
    
    return intent_name, confidence


def extract_entities(text: str) -> dict:
    """
    Extract simple entities from text using regex patterns
    
    Args:
        text: Input text
        
    Returns:
        Dictionary of entity types and values
    """
    import re
    entities = {}

    # Extract numbers (e.g., amounts)
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
    if numbers:
        entities['CARDINAL'] = numbers

    # Extract currency-like values
    currency = re.findall(r'\$\s?\d+(?:,\d{3})*(?:\.\d+)?', text)
    if currency:
        entities['MONEY'] = currency

    return entities


def get_intent_info(intent: str) -> dict:
    """
    Get metadata about an intent
    
    Args:
        intent: Intent name
        
    Returns:
        Dictionary with intent information
    """
    intent_info = {
        'GREETING': {
            'description': 'User greeting or salutation',
            'requires_db': False
        },
        'BALANCE': {
            'description': 'Query about account balance',
            'requires_db': True
        },
        'TRANSACTIONS': {
            'description': 'Query about transaction history',
            'requires_db': True
        },
        'LOAN': {
            'description': 'Query about loans or credit',
            'requires_db': False
        },
        'UNKNOWN': {
            'description': 'Intent not recognized',
            'requires_db': False
        }
    }
    
    return intent_info.get(intent, intent_info['UNKNOWN'])
