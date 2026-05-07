"""
Natural Language Processing module — TensorFlow/Keras ANN
=========================================================
Intent detection is performed by a trained Artificial Neural Network.
Text is pre-processed with NLTK (tokenisation + Lancaster stemming) and
encoded as a bag-of-words vector before being passed to the ANN.

If the trained model artefacts are not yet present (models/chatbot_model.keras,
models/words.pkl, models/classes.pkl), the module falls back to the original
keyword-matching logic so the API remains functional.  Run `python train_model.py`
once to build and persist the model.
"""
import json
import pickle
import logging
import re
import numpy as np
from pathlib import Path
from typing import Tuple

import nltk
from nltk.stem import LancasterStemmer
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)

# ── NLTK bootstrap ─────────────────────────────────────────────────────────────
_NLTK_RESOURCES = {
    "punkt":     "tokenizers/punkt",
    "punkt_tab": "tokenizers/punkt_tab",
    "stopwords": "corpora/stopwords",
}

for _name, _path in _NLTK_RESOURCES.items():
    try:
        nltk.data.find(_path)
    except (LookupError, OSError):
        logger.info(f"Downloading NLTK resource: {_name}")
        nltk.download(_name, quiet=True)

_stemmer = LancasterStemmer()
logger.info("NLTK stemmer initialised")


# ── Paths ──────────────────────────────────────────────────────────────────────
_BASE_DIR    = Path(__file__).parent
_INTENTS_DIR = _BASE_DIR / "intents"
_MODELS_DIR  = _BASE_DIR / "models"


def _load_json(filename: str) -> dict:
    """Load a JSON file from the intents directory."""
    path = _INTENTS_DIR / filename
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Intent file not found: {path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {path}: {e}")
        raise


def _parse_intents(data: dict) -> tuple[dict, dict]:
    """Derive INTENT_KEYWORDS and _INTENT_INFO dicts from intents.json data."""
    keywords: dict = {}
    info: dict = {}
    for intent in data["intents"]:
        tag = intent["tag"]
        keywords[tag] = intent.get("keywords", [])
        info[tag] = {
            "description": intent.get("description", ""),
            "requires_db":  intent.get("requires_db", False),
            "examples":     intent.get("examples", []),
        }
    return keywords, info


# ── Intent metadata (keywords + info) ─────────────────────────────────────────
INTENT_KEYWORDS, _INTENT_INFO = _parse_intents(_load_json("intents.json"))
logger.info(f"Loaded {len(INTENT_KEYWORDS)} intents from intents.json")


def reload_intents() -> None:
    """Reload intent metadata from intents.json at runtime."""
    global INTENT_KEYWORDS, _INTENT_INFO
    INTENT_KEYWORDS, _INTENT_INFO = _parse_intents(_load_json("intents.json"))
    logger.info(f"Reloaded {len(INTENT_KEYWORDS)} intents")


# ── ANN model loading ──────────────────────────────────────────────────────────
_ann_model  = None
_ann_words:   list = []
_ann_classes: list = []


def _load_ann_model() -> bool:
    """
    Attempt to load the trained Keras model + vocabulary artefacts.
    Returns True on success, False if artefacts are missing or corrupt.
    """
    global _ann_model, _ann_words, _ann_classes

    model_path   = _MODELS_DIR / "chatbot_model.keras"
    words_path   = _MODELS_DIR / "words.pkl"
    classes_path = _MODELS_DIR / "classes.pkl"

    if not (model_path.exists() and words_path.exists() and classes_path.exists()):
        logger.warning(
            "ANN model artefacts not found in models/. "
            "Run  python train_model.py  to train the model. "
            "Falling back to keyword matching."
        )
        return False

    try:
        from tensorflow.keras.models import load_model  # type: ignore
        _ann_model = load_model(str(model_path))
        with open(words_path, "rb") as f:
            _ann_words = pickle.load(f)
        with open(classes_path, "rb") as f:
            _ann_classes = pickle.load(f)
        logger.info(
            f"ANN model loaded — vocabulary: {len(_ann_words)} stems, "
            f"classes: {len(_ann_classes)}"
        )
        return True
    except Exception as exc:
        logger.error(f"Failed to load ANN model: {exc}")
        return False


_ann_ready: bool = _load_ann_model()


# ── Text preprocessing ─────────────────────────────────────────────────────────

def preprocess_text(text: str) -> str:
    """Lower-case and normalise whitespace."""
    if not text:
        return ""
    return " ".join(text.lower().strip().split())


def _tokenize_and_stem(text: str) -> list[str]:
    """Tokenise *text* and return Lancaster-stemmed alpha tokens."""
    tokens = word_tokenize(text.lower())
    return [_stemmer.stem(t) for t in tokens if t.isalpha()]


def _bag_of_words(text: str, words: list) -> np.ndarray:
    """Encode *text* as a binary bag-of-words vector over *words*."""
    stems = set(_tokenize_and_stem(text))
    return np.array(
        [1.0 if w in stems else 0.0 for w in words], dtype=np.float32
    )


# ── Keyword-matching fallback ──────────────────────────────────────────────────

def _keyword_fallback(user_input: str) -> Tuple[str, float]:
    """
    Original rule-based intent detection.
    Used when the ANN model has not been trained yet.
    """
    processed = preprocess_text(user_input)
    text_tokens = set(processed.split())
    intent_scores: dict = {}

    for intent, keywords in INTENT_KEYWORDS.items():
        score = 0
        matched = 0
        for keyword in keywords:
            kw = keyword.lower()
            if kw in processed:
                score += 2
                matched += 1
            elif any(part in text_tokens for part in kw.split()):
                score += 1
                matched += 1
        if matched:
            intent_scores[intent] = (score, min(score / len(keywords), 1.0))

    if not intent_scores:
        return "UNKNOWN", 0.0

    best = max(intent_scores.items(), key=lambda x: x[1][0])
    return best[0], best[1][1]


# ── Primary intent detection (ANN) ────────────────────────────────────────────

def _has_meaningful_text(text: str) -> bool:
    """Return True only when *text* contains at least 2 alphabetic characters."""
    return sum(1 for c in text if c.isalpha()) >= 2


def detect_intent(user_input: str) -> Tuple[str, float]:
    """
    Detect the intent of *user_input*.

    Primary path  — ANN softmax classifier (TensorFlow/Keras).
    Fallback path — keyword matching (used before the model is trained).

    Returns:
        (intent_tag, confidence)  e.g. ("BALANCE", 0.97)
    """
    if not user_input:
        return "UNKNOWN", 0.0

    # Reject messages that contain no real words (pure numbers / symbols)
    if not _has_meaningful_text(user_input):
        logger.info(f"Input rejected as non-text: {user_input!r}")
        return "UNKNOWN", 0.0

    # ── ANN path ───────────────────────────────────────────────────────────────
    if _ann_ready and _ann_model is not None:
        try:
            bow = _bag_of_words(user_input, _ann_words).reshape(1, -1)
            predictions: np.ndarray = _ann_model.predict(bow, verbose=0)[0]

            # Collect predictions above a minimum threshold
            THRESHOLD = 0.40
            results = [
                (_ann_classes[i], float(predictions[i]))
                for i in range(len(predictions))
                if predictions[i] >= THRESHOLD
            ]

            if results:
                results.sort(key=lambda x: x[1], reverse=True)
                intent, confidence = results[0]
                logger.info(
                    f"ANN → intent: {intent} ({confidence:.2f})  input: {user_input!r}"
                )
                return intent, confidence
            # ANN not confident enough — try keyword matching before giving up
            kw_intent, kw_conf = _keyword_fallback(user_input)
            if kw_intent != "UNKNOWN" and kw_conf > 0.0:
                top_ann = max(float(p) for p in predictions)
                # Use ANN top intent if it partially agrees with keyword match
                top_ann_intent = _ann_classes[int(np.argmax(predictions))]
                if top_ann_intent == kw_intent and top_ann >= 0.25:
                    logger.info(
                        f"ANN+KW hybrid \u2192 intent: {kw_intent} ({top_ann:.2f})  input: {user_input!r}"
                    )
                    return kw_intent, top_ann
                logger.info(
                    f"KW fallback (low ANN conf {top_ann:.2f}) \u2192 {kw_intent} ({kw_conf:.2f})"
                )
                return kw_intent, kw_conf
        except Exception as exc:
            logger.error(f"ANN prediction error: {exc}")

    # ── Keyword fallback ───────────────────────────────────────────────────────
    intent, confidence = _keyword_fallback(user_input)
    logger.info(
        f"Keyword fallback → intent: {intent} ({confidence:.2f})  input: {user_input!r}"
    )
    return intent, confidence


# ── Entity extraction (regex-based) ───────────────────────────────────────────

def extract_entities(text: str) -> dict:
    """
    Extract numeric and monetary entities from *text* using regex patterns.

    Returns a dict with optional keys:
      CARDINAL — plain numbers
      MONEY    — currency values prefixed with $
    """
    entities: dict = {}

    numbers = re.findall(r"\b\d+(?:\.\d+)?\b", text)
    if numbers:
        entities["CARDINAL"] = numbers

    currency = re.findall(r"\$\s?\d+(?:,\d{3})*(?:\.\d+)?", text)
    if currency:
        entities["MONEY"] = currency

    return entities


# ── Intent metadata lookup ─────────────────────────────────────────────────────

def get_intent_info(intent: str) -> dict:
    """
    Return metadata for *intent* from intents/intent_info.json.
    Falls back to the UNKNOWN entry if the tag is not found.
    """
    return _INTENT_INFO.get(intent, _INTENT_INFO.get("UNKNOWN", {}))
