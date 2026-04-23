"""
Natural Language Processing module using spaCy
Handles intent detection and text processing
"""
import json
import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


def _load_spacy_model():
    import spacy
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        logger.info("Downloading spaCy model en_core_web_sm...")
        from spacy.cli import download
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")


_nlp = _load_spacy_model()
logger.info("spaCy NLP components loaded successfully")


# ── JSON-driven intent data ─────────────────────────────────────────────────
_INTENTS_DIR = Path(__file__).parent / 'intents'


def _load_json(filename: str) -> dict:
    """Load a JSON file from the intents directory."""
    path = _INTENTS_DIR / filename
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Intent file not found: {path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        raise


def reload_intents() -> None:
    """Reload intent data from JSON files at runtime (call after editing JSONs)."""
    global INTENT_KEYWORDS, _INTENT_INFO
    INTENT_KEYWORDS = _load_json('intent_keywords.json')
    _INTENT_INFO = _load_json('intent_info.json')
    logger.info(f"Loaded {len(INTENT_KEYWORDS)} intents from JSON files")


# Load on startup
INTENT_KEYWORDS: dict = _load_json('intent_keywords.json')
_INTENT_INFO: dict = _load_json('intent_info.json')
logger.info(f"Loaded {len(INTENT_KEYWORDS)} intents from JSON files")


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
    Extract lemmatized tokens from text using spaCy
    
    Args:
        text: Input text
        
    Returns:
        List of lemmatized tokens
    """
    doc = _nlp(text)
    lemmas = [
        token.lemma_.lower()
        for token in doc
        if token.is_alpha and not token.is_stop
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
    Extract entities from text using spaCy NER
    
    Args:
        text: Input text
        
    Returns:
        Dictionary of entity types and values
    """
    import re
    entities = {}

    # Use spaCy named entity recognition
    doc = _nlp(text)
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        entities[ent.label_].append(ent.text)

    # Regex fallback for numbers not caught by NER
    if 'CARDINAL' not in entities:
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        if numbers:
            entities['CARDINAL'] = numbers

    # Regex fallback for currency values
    if 'MONEY' not in entities:
        currency = re.findall(r'\$\s?\d+(?:,\d{3})*(?:\.\d+)?', text)
        if currency:
            entities['MONEY'] = currency

    return entities


def get_intent_info(intent: str) -> dict:
    """
    Get metadata about an intent.
    Data is loaded from intents/intent_info.json — edit that file to add details.
    """
    return _INTENT_INFO.get(intent, _INTENT_INFO.get('UNKNOWN', {}))
