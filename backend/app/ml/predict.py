import os
import joblib
import pandas as pd
from typing import Dict, Any
from .model_registry import get_active_model

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../../models/recovery_model.joblib")

_model_cache = None

def load_model():
    global _model_cache
    if _model_cache is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache

def predict_recovery(payment_features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predicts the probability of recovery for a given payment.
    """
    model = load_model()
    metadata = get_active_model()
    threshold = metadata.get("threshold", 0.5)
    
    # Convert input to DataFrame
    df = pd.DataFrame([payment_features])
    
    # Check for leaky columns
    leaky_columns = [
        "expected_recovery_action",
        "simulated_recovery_outcome",
        "simulated_recovered_amount",
        "recoverable_ground_truth"
    ]
    if any(col in df.columns for col in leaky_columns):
        raise ValueError("Input features contain leaky columns that are not allowed.")
        
    # Get probability of class 1 (recoverable)
    prob = float(model.predict_proba(df)[0][1])
    
    # Make decision based on threshold
    predicted_recoverable = bool(prob >= threshold)
    
    return {
        "recovery_probability": round(prob, 4),
        "predicted_recoverable": predicted_recoverable,
        "model_name": metadata.get("model_name", "unknown"),
        "model_version": metadata.get("model_version", "unknown"),
        "threshold": threshold
    }
