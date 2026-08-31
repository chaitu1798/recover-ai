import json
import os
from typing import Dict, Any

METADATA_PATH = os.path.join(os.path.dirname(__file__), "../../../models/model_metadata.json")

def save_model_metadata(metadata: Dict[str, Any]):
    """
    Saves model metadata to a JSON file.
    """
    os.makedirs(os.path.dirname(METADATA_PATH), exist_ok=True)
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=4)

def load_model_metadata() -> Dict[str, Any]:
    """
    Loads model metadata from a JSON file.
    """
    if not os.path.exists(METADATA_PATH):
        return {}
    with open(METADATA_PATH, "r") as f:
        return json.load(f)

def get_active_model() -> Dict[str, Any]:
    """
    Returns the active model metadata.
    """
    return load_model_metadata()
