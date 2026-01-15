import json
import logging
import os
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)

HISTORY_DIR = "data/history"
HISTORY_FILE = os.path.join(HISTORY_DIR, "attempts.json")

# Ensure directory exists
os.makedirs(HISTORY_DIR, exist_ok=True)

# Thread safety lock for file writes
_lock = Lock()

def _ensure_file_exists():
    """Create the history file with an empty list if it doesn't exist."""
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def save_attempt(attempt: dict) -> None:
    """
    Persist a single explanation attempt.

    Input dict is expected to contain:
    - attempt_id (str)
    - timestamp (str/iso)
    - concept (str)
    - target_audience (str) 
    - explanation_text (str)
    - analysis_result (dict)
    - referenced_chunk_ids (list)
    """
    _ensure_file_exists()

    # Normalize timestamp if not present
    if "timestamp" not in attempt:
        attempt["timestamp"] = datetime.utcnow().isoformat()
    
    # Simple validation log
    logger.info(f"Saving attempt for concept: {attempt.get('concept', 'Unknown')}")

    with _lock:
        try:
            # Read existing
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    history = []
            
            # Append new
            history.append(attempt)
            
            # Write back
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save attempt: {e}")
            raise e

def load_attempts(limit: int | None = None) -> list[dict]:
    """
    Load past explanation attempts, most recent first.
    """
    _ensure_file_exists()

    with _lock:
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                try:
                    history = json.load(f)
                except json.JSONDecodeError:
                    return []
            
            # Sort by timestamp descending (newest first)
            # Assuming "timestamp" is ISO string which sorts lexicographically correctly
            history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            if limit:
                return history[:limit]
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to load attempts: {e}")
            return []

def load_attempt(attempt_id: str) -> dict | None:
    """
    Retrieve a specific attempt by ID.
    """
    attempts = load_attempts()
    for att in attempts:
        if att.get("attempt_id") == attempt_id:
            return att
    return None
