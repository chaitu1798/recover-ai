from typing import Dict, Any, Tuple
from app.models.recovery_case import RecoveryCase
from app.models.payment import Payment

def calculate_priority(
    recovery_probability: float, 
    amount_at_risk: int, 
    attempt_number: int
) -> Tuple[float, str, str]:
    """
    Deterministic Priority Engine.
    
    Factors:
    - Expected Recovery Value = amount_at_risk * recovery_probability
    - Decaying factor based on attempt_number (each attempt reduces priority score multiplier)
    
    Outputs:
    - priority_score (float)
    - priority_level (HIGH, MEDIUM, LOW)
    - explanation (str)
    """
    if recovery_probability < 0 or recovery_probability > 1:
        recovery_probability = 0.0
        
    expected_value = amount_at_risk * recovery_probability
    
    # Penalize repeated attempts (e.g., attempt 1 = 1.0, attempt 2 = 0.8, attempt 3 = 0.6)
    attempt_multiplier = max(0.2, 1.0 - (0.2 * (attempt_number - 1)))
    
    priority_score = float(expected_value * attempt_multiplier)
    
    # Thresholds for priority levels (in minor units, e.g. 100000 = 1000 INR)
    if priority_score > 50000 and recovery_probability > 0.5:
        priority_level = "HIGH"
    elif priority_score > 10000:
        priority_level = "MEDIUM"
    else:
        priority_level = "LOW"
        
    explanation = f"Calculated based on expected value ({expected_value}) and attempt multiplier ({attempt_multiplier})"
    
    return priority_score, priority_level, explanation
