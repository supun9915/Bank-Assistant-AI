"""
ANN Training Script — Smart Banking Assistant
==============================================
Trains a TensorFlow/Keras Artificial Neural Network for intent classification.

Architecture:
  Input (Bag-of-Words)
  → Dense(256, ReLU) + BatchNorm + Dropout(0.5)
  → Dense(128, ReLU) + BatchNorm + Dropout(0.4)
  → Dense(64,  ReLU) + Dropout(0.2)
  → Dense(num_classes, Softmax)

Usage:
  python train_model.py

Outputs (saved to models/):
  chatbot_model.keras  — trained Keras model
  words.pkl            — stemmed vocabulary list
  classes.pkl          — intent label list
"""

import json
import pickle
import logging
import random
import numpy as np
from pathlib import Path
from collections import Counter

import nltk
from nltk.stem import LancasterStemmer
from nltk.tokenize import word_tokenize

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
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

stemmer = LancasterStemmer()

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
TRAINING_DATA_PATH = BASE_DIR / "intents" / "intents.json"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

MODEL_PATH   = MODELS_DIR / "chatbot_model.keras"
WORDS_PATH   = MODELS_DIR / "words.pkl"
CLASSES_PATH = MODELS_DIR / "classes.pkl"


# ── Data helpers ───────────────────────────────────────────────────────────────

def load_training_data() -> dict:
    logger.info(f"Loading training data from {TRAINING_DATA_PATH}")
    with open(TRAINING_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def tokenize_and_stem(sentence: str) -> list[str]:
    """Lower-case tokenize then Lancaster-stem, keeping only alpha tokens."""
    tokens = word_tokenize(sentence.lower())
    return [stemmer.stem(t) for t in tokens if t.isalpha()]


def preprocess(data: dict) -> tuple[list, list, list]:
    """
    Returns:
        words     – sorted unique stemmed vocabulary
        classes   – sorted unique intent tags
        documents – list of (stemmed_tokens, tag)
    """
    words: list[str] = []
    classes: list[str] = []
    documents: list[tuple] = []

    for intent in data["intents"]:
        tag = intent["tag"]
        if tag not in classes:
            classes.append(tag)

        for pattern in intent["patterns"]:
            stems = tokenize_and_stem(pattern)
            words.extend(stems)
            documents.append((stems, tag))

    words = sorted(set(words))
    classes = sorted(classes)

    logger.info(
        f"Preprocessed  →  {len(words)} unique stems  |  "
        f"{len(classes)} classes  |  {len(documents)} samples"
    )
    return words, classes, documents


def create_training_set(
    words: list, classes: list, documents: list
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Convert documents to BoW features and one-hot label vectors.
    Returns stratified train/val splits: X_train, X_val, y_train, y_val.
    """
    from sklearn.model_selection import train_test_split

    X, y_indices = [], []

    for stems, tag in documents:
        stems_set = set(stems)
        bow = [1.0 if w in stems_set else 0.0 for w in words]
        X.append(bow)
        y_indices.append(classes.index(tag))

    X_arr = np.array(X, dtype=np.float32)
    y_arr = np.array(y_indices, dtype=np.int32)

    # Stratified split: ensures every class appears in both train and val
    X_train, X_val, y_train_idx, y_val_idx = train_test_split(
        X_arr, y_arr, test_size=0.15, random_state=42, stratify=y_arr
    )

    # One-hot encode labels
    def to_onehot(indices):
        oh = np.zeros((len(indices), len(classes)), dtype=np.float32)
        oh[np.arange(len(indices)), indices] = 1.0
        return oh

    return X_train, X_val, to_onehot(y_train_idx), to_onehot(y_val_idx), y_train_idx


def compute_class_weights(y_train_indices: np.ndarray, num_classes: int) -> dict:
    """Compute balanced class weights to handle unequal class frequencies."""
    counts = Counter(y_train_indices.tolist())
    total = len(y_train_indices)
    weights = {
        cls: total / (num_classes * max(count, 1))
        for cls, count in counts.items()
    }
    # Ensure all classes are represented even if absent from training split
    for cls in range(num_classes):
        if cls not in weights:
            weights[cls] = 1.0
    return weights


# ── Model builder ──────────────────────────────────────────────────────────────

def build_model(input_size: int, output_size: int):
    """
    Feedforward ANN for multi-class intent classification.

    Layers:
      Dense(256) → BatchNorm → Dropout(0.5)
      Dense(128) → BatchNorm → Dropout(0.4)
      Dense(64)              → Dropout(0.2)
      Dense(output_size, softmax)

    Regularisation: L2(1e-3) on first two dense layers + Dropout.
    Optimiser: Adam with cosine-decay learning rate schedule.
    """
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.regularizers import l2

    model = Sequential(
        [
            Dense(
                256,
                input_shape=(input_size,),
                activation="relu",
                kernel_regularizer=l2(5e-4),
                name="hidden_1",
            ),
            BatchNormalization(name="bn_1"),
            Dropout(0.4, name="drop_1"),
            Dense(
                128,
                activation="relu",
                kernel_regularizer=l2(5e-4),
                name="hidden_2",
            ),
            BatchNormalization(name="bn_2"),
            Dropout(0.3, name="drop_2"),
            Dense(64, activation="relu", name="hidden_3"),
            Dropout(0.2, name="drop_3"),
            Dense(output_size, activation="softmax", name="output"),
        ],
        name="banking_intent_ann",
    )

    lr_schedule = tf.keras.optimizers.schedules.CosineDecayRestarts(
        initial_learning_rate=1e-3,
        first_decay_steps=50,
        t_mul=2.0,
        m_mul=0.9,
    )

    model.compile(
        optimizer=Adam(learning_rate=lr_schedule),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


# ── Training entry point ───────────────────────────────────────────────────────

def train():
    import tensorflow as tf
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

    logger.info(f"TensorFlow version: {tf.__version__}")

    # ── 1. Load & preprocess ───────────────────────────────────────────────────
    data = load_training_data()
    words, classes, documents = preprocess(data)
    X_train, X_val, y_train, y_val, y_train_idx = create_training_set(words, classes, documents)

    logger.info(
        f"Training matrix shape: X_train={X_train.shape}  X_val={X_val.shape}"
    )

    class_weights = compute_class_weights(y_train_idx, len(classes))
    logger.info(f"Class weights computed for {len(class_weights)} classes")

    # ── 2. Build model ─────────────────────────────────────────────────────────
    model = build_model(len(words), len(classes))
    model.summary(print_fn=logger.info)

    # ── 3. Callbacks ───────────────────────────────────────────────────────────
    callbacks = [
        EarlyStopping(
            monitor="val_accuracy",
            patience=40,
            restore_best_weights=True,
            verbose=1,
        ),
        # ReduceLROnPlateau removed: incompatible with CosineDecayRestarts
        # schedule — Keras 3 forbids setting lr on a schedule-backed optimizer.
        ModelCheckpoint(
            filepath=str(MODEL_PATH),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=0,
        ),
    ]

    # ── 4. Train ───────────────────────────────────────────────────────────────
    logger.info("Starting training …")
    history = model.fit(
        X_train,
        y_train,
        epochs=400,
        batch_size=8,
        validation_data=(X_val, y_val),
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1,
    )

    # ── 5. Final evaluation ────────────────────────────────────────────────────
    loss, accuracy = model.evaluate(X_train, y_train, verbose=0)
    logger.info(f"Training set  →  accuracy: {accuracy:.4f}  |  loss: {loss:.4f}")

    val_acc = max(history.history.get("val_accuracy", [0.0]))
    logger.info(f"Best validation accuracy: {val_acc:.4f}")

    # ── 6. Persist artefacts ───────────────────────────────────────────────────
    # ModelCheckpoint already saved the best model; save again explicitly to
    # ensure the final best-weights version is on disk.
    model.save(str(MODEL_PATH))
    logger.info(f"Model saved  → {MODEL_PATH}")

    with open(WORDS_PATH, "wb") as f:
        pickle.dump(words, f)
    logger.info(f"Vocabulary saved  → {WORDS_PATH}  ({len(words)} stems)")

    with open(CLASSES_PATH, "wb") as f:
        pickle.dump(classes, f)
    logger.info(f"Classes saved  → {CLASSES_PATH}  ({len(classes)} intents)")

    logger.info(
        "\n"
        "═══════════════════════════════════════════════════\n"
        "  Training complete!\n"
        f"  Model:   {MODEL_PATH}\n"
        f"  Classes: {classes}\n"
        "  Start the FastAPI server to use the ANN model.\n"
        "═══════════════════════════════════════════════════"
    )
    return history


if __name__ == "__main__":
    train()
